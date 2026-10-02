#! /usr/bin/env python3

# This script loads the ELF binary into the target microcontroller. It
# is specific to the STM32F407 "Discovery" board. This script is meant to
# be used for loading the binary into SRAM1, without using the Flash space
# at all; this allows running at maximum frequency (168 MHz) without
# extra wait states. On the other hand, this consumes some RAM space, which
# cannot be used by the application. The loading incurs no modification
# to the Flash and is thus non-permanent.
#
# Usage:
#    m4load.py [ -p port ] file.elf
# If not specified, the port is the default used by st-util (4242).
#
# The script loads the file and runs it; it waits for the program to
# terminate (i.e. to hit a trap condition). The script can be killed
# (Ctrl-C) at any time; the program will continue running on the
# microcontroller, and st-util will not exit.

import importlib
import sys
import socket
import time

# Append nonnegative integer x to the binary object d, in hexadecimal,
# with outlen digits produced. If outlen is negative (or unspecified),
# then the minimum length is used (leading zeros are removed, but if the
# integer x is zero, then a single zero is produced).
def append_hex(d, x, outlen=-1):
    hd = b'0123456789abcdef'
    if outlen < 0:
        outlen = (x.bit_length() + 3) >> 2
        if outlen == 0:
            outlen = 1
    for i in range(outlen - 1, -1, -1):
        d.append(hd[(x >> (4*i)) & 0x0F])

# Connect to the remote debugging port maintained by st-util. This is
# normally used by gdb; we use the same protocol to load the binary into
# RAM.
def connect_stlink(port=4242):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", port))
    # Set extended mode, which also makes st-util remanent (i.e. not to
    # exit if the connection is broken).
    packet_send(s, b'!')
    r = packet_recv(s)
    if r != b'OK':
        raise RuntimeError("set persistency failed: " + response_to_string(r))
    return s

# Send a packet to st-util; this also waits for the acknowledgement ('+').
# This function handles escaping special characters ('#', '$', '}') and
# adds the needed decorations (header, checksum...).
def packet_send(s, data):
    d = bytearray()
    d.extend(b'$')
    ck = 0
    for i in range(0, len(data)):
        x = data[i]
        match x:
            case 0x23 | 0x24 | 0x7D:
                d.append(0x7D)
                ck = (ck + 0x7D) & 0xFF
                x ^= 0x20
        ck = (ck + x) & 0xFF
        d.append(x)
    d.extend(b'#')
    append_hex(d, ck, 2)
    dlen = len(d)
    slen = 0
    while slen < dlen:
        wlen = s.send(d[slen:])
        if wlen <= 0:
            raise RuntimeError("socket broke (send packet)")
        slen += wlen
    ack = s.recv(1)
    if len(ack) == 0:
        raise RuntimeError("socket broke (receive ack)")
    if ack[0] != 0x2B:
        raise RuntimeError("invalid ack: 0x%02X" % ack[0])

# Receive a packet from st-util. The packet payload is returned.
# This function verifies and removes the header and checksum, and also
# interprets escaped special characters.
def packet_recv(s):
    chunks = []
    cc = -1
    ckd = bytearray()
    while cc < 2:
        chunk = s.recv(2048)
        if len(chunk) == 0:
            raise RuntimeError("socket broke (receive packet)")
        if len(chunks) == 0:
            if chunk[0] != 0x24:
                raise RuntimeError("invalid response (no '$')")
            chunk = chunk[1:]
        if cc < 0:
            for i in range(0, len(chunk)):
                if chunk[i] == 0x23:
                    cc = len(chunk) - i - 1
                    ckd.extend(chunk[(i + 1):])
                    chunk = chunk[:i]
                    break
            chunks.append(chunk)
        else:
            cc += len(chunk)
            ckd.extend(chunk)
    if cc > 2:
        raise RuntimeError("invalid response (too many checksum bytes)")
    msg = b''.join(chunks)
    mlen = len(msg)
    d = bytearray()
    i = 0
    ck = 0
    while i < mlen:
        x = msg[i]
        ck = (ck + x) & 0xFF
        if x == 0x7D and (i + 1) < mlen:
            i += 1
            x = msg[i]
            ck = (ck + x) & 0xFF
            x ^= 0x20
        d.append(x)
        i += 1
    if ck != int(ckd, base=16):
        raise RuntimeError("incorrect checksum")
    if s.send(b'+') != 1:
        raise RuntimeError("socket broke (send ack)")
    return d

# Convert a (binary) response to a printable string.
def response_to_string(r):
    rs = ''
    for i in range(0, len(r)):
        x = r[i]
        if x >= 32 and x <= 126 and x != 0x5C:
            rs += chr(x)
        else:
            rs += '\\x%02X' % x
    return rs

# Send a reset command.
def reset(s):
    print('<reset>')
    packet_send(s, b'R00')
    r = packet_recv(s)
    if r != b'OK':
        raise RuntimeError("reset failed: " + response_to_string(r))

# Send a write memory command, for the provided data and target address.
# st-util has some alignment requirements (address must be multiple of 4,
# data length must be multiple of 4). If the data is too long, then it
# it split into several commands, each for a maximum size of 4096 bytes.
def write_mem(s, addr, data):
    dlen = len(data)
    print('<write_mem: addr=0x%08X len=0x%08X>' % (addr, dlen))
    off = 0
    while off < dlen:
        clen = min(dlen - off, 4096)
        msg = bytearray()
        msg.extend(b'M%08x,%08x:' % (addr + off, clen))
        for i in range(0, clen):
            append_hex(msg, data[off + i], 2)
        packet_send(s, msg)
        r = packet_recv(s)
        if r != b'OK':
            raise RuntimeError("write failed: " + response_to_string(r))
        off += clen

# Read memory from the provided address. 'dlen' bytes are read. As in
# write_mem(), there are some alignment requirements (enforced by st-util)
# and long runs of data are split into several commands. Read data is
# returned.
def read_mem(s, addr, dlen):
    print('<read_mem: addr=0x%08X len=0x%08X>' % (addr, dlen))
    data = bytearray()
    off = 0
    while off < dlen:
        clen = min(dlen - off, 4096)
        msg = b'm%08x,%08x' % (addr + off, clen)
        packet_send(s, msg)
        r = packet_recv(s)
        rlen = len(r)
        i = 0
        while (i + 1) < rlen:
            data.append(int(r[i:(i + 2)], base=16))
            i += 2
        off += clen
    return data

# Byte-swap 32-bit value x and encode it in hexadecimal (binary string).
def w32hex_lsb(x):
    d = bytearray()
    append_hex(d, x & 0xFF, 2)
    append_hex(d, (x >> 8) & 0xFF, 2)
    append_hex(d, (x >> 16) & 0xFF, 2)
    append_hex(d, (x >> 24) & 0xFF, 2)
    return d

# Send the "read all registers" command; the register values are returned
# as 16 32-bit integers.
def read_all_regs(s):
    packet_send(s, b'g')
    r = packet_recv(s)
    if len(r) < (8 * 16):
        raise RuntimeError("read_all_regs failed: " + response_to_string(r))
    rv = []
    for i in range(0, 16):
        v = 0
        for j in range(0, 4):
            off = 8 * i + 2 * j
            x = int(r[off:(off + 2)], base=16)
            v |= x << (j << 3)
        rv.append(v)
    return rv

def print_regs(rv):
    print('r0:  %08X   r1:  %08X   r2:  %08X   r3:  %08X' % (rv[0], rv[1], rv[2], rv[3]))
    print('r4:  %08X   r5:  %08X   r6:  %08X   r7:  %08X' % (rv[4], rv[5], rv[6], rv[7]))
    print('r8:  %08X   r9:  %08X   r10: %08X   r11: %08X' % (rv[8], rv[9], rv[10], rv[11]))
    print('r12: %08X   r13: %08X   r14: %08X   r15: %08X' % (rv[12], rv[13], rv[14], rv[15]))

# Send commands to set r15 (program counter) and r13 (stack pointer) to the
# provided values, then send a "continue" command to execute from the
# specified position.
def run_code(s, pc, sp=0x10010000):
    print('<set pc=0x%08X sp=0x%08X>' % (pc, sp))
    packet_send(s, b'P0d=' + w32hex_lsb(sp))
    r = packet_recv(s)
    if r != b'OK':
        raise RuntimeError("set SP failed: " + response_to_string(r))
    packet_send(s, b'P0f=' + w32hex_lsb(pc))
    r = packet_recv(s)
    if r != b'OK':
        raise RuntimeError("set PC failed: " + response_to_string(r))
    print('<running>')
    packet_send(s, b'c')
    r = packet_recv(s)
    print(response_to_string(r))

def dec16le(buf):
    return buf[0] | (buf[1] << 8)

def dec32le(buf):
    return buf[0] | (buf[1] << 8) | (buf[2] << 16) | (buf[3] << 24)

# Parse data as an ELF 32-bit binary, load it into the target (RAM
# writes only, no Flash), and start execution.
def run_elf(s, data):
    # Soft-reset the core.
    reset(s)

    # Set FMC remap configuration so that addresses 0x00000000 - 0x0001BFFF
    # become an alias on SRAM1.
    write_mem(s, 0x40013800, b'\x03\x00\x00\x00')

    # Minimal ELF header parsing:
    #   e_ident must specify ELF, 32-bit, little-endian
    #   e_type must be ET_EXEC
    #   There must be a program header
    if len(data) < 52:
        raise RuntimeError("no ELF header (too short)")
    if data[0:4] != b'\x7fELF':
        raise RuntimeError("ELF magic missing")
    if data[4] != 0x01:
        raise RuntimeError("not 32-bit ELF")
    if data[5] != 0x01:
        raise RuntimeError("not little-endian ELF")
    e_type = dec16le(data[16:])
    if e_type != 0x02:
        raise RuntimeError("ELF type is not ET_EXEC")
    e_entry = dec32le(data[24:])
    if e_entry == 0:
        raise RuntimeError("ELF has no entry point")
    e_phoff = dec32le(data[28:])
    if e_phoff == 0:
        raise RuntimeError("ELF has no program header")
    e_shoff = dec32le(data[32:])
    e_phentsize = dec16le(data[42:])
    e_phnum = dec16le(data[44:])
    e_shentsize = dec16le(data[46:])
    e_shnum = dec16le(data[48:])

    # Initial stack pointer is set by the libopencm3 start code in the
    # special .vectors section, which is located at the start of the
    # .text segment, which is at the start of the ROM area; in other words,
    # that value is at address 0. When we load that segment, we set sp
    # accordingly. We initialize here variable sp with the default, which
    # is to put the stack at the end of the CCM.
    sp = 0x10010000

    # Load segments into RAM.
    # libopencm3 provides the program entry as the reset_handler() function,
    # which reinitializes the .data and .bss sections by copying the data
    # from their physical address, and appending zeros as necessary. Thus,
    # we must load the program by writing into the physical address (p_paddr)
    # and we can omit the padding with zeros.
    if e_phentsize < 32:
        raise RuntimeError("ELF program header entries are too small")
    for i in range(0, e_phnum):
        off = e_phoff + i * e_phentsize
        if off + e_phentsize > len(data):
            raise RuntimeError("ELF program header entry out of range")
        p_type = dec32le(data[off:])
        load = True
        match p_type:
            case 0 | 4:
                # PT_NULL or PT_NOTE, nothing to do
                load = False
            case 1:
                # PT_LOAD
                pass
            case 2 | 3 | 5 | 6:
                raise RuntimeError("cannot process dynamic linking segment")
            case _:
                if p_type < 0x70000000 or p_type > 0x7fffffff:
                    raise RuntimeError("unrecognized segment type")
                # It is not entirely clear what we should do with
                # architecture-specific segments; right now we load them.
        if load:
            p_offset = dec32le(data[(off + 4):])
            p_paddr = dec32le(data[(off + 12):])
            p_filesz = dec32le(data[(off + 16):])
            if (p_offset + p_filesz) > len(data):
                raise RuntimeError("unloadable segment")
            write_mem(s, p_paddr, data[p_offset : (p_offset + p_filesz)])
            # We read back memory to check the loading went well.
            bb = read_mem(s, p_paddr, p_filesz)
            if bb != data[p_offset : (p_offset + p_filesz)]:
                raise RuntimeError("read back memory failed")
            # If segment includes the first four bytes of the ROM space,
            # then it's the vector table, that starts with the requested
            # stack pointer.
            if p_paddr == 0 and p_filesz >= 4:
                sp = dec32le(data[p_offset:])

    run_code(s, e_entry, sp)

if len(sys.argv) < 2:
    raise RuntimeError("need file name")
f = open(sys.argv[1], 'rb')
data = f.read()
s = connect_stlink()
run_elf(s, data)
