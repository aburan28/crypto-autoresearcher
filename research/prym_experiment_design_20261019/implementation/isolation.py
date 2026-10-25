"""Fail-closed Linux isolation for synthetic attack and selector workers.

Landlock permits code/libraries and public stdin, excluding run/census/secret
files and /proc. Seccomp refuses new sockets and process-memory inspection.
This is an experiment boundary, not a general hostile-code sandbox claim.
"""
import ctypes
import errno
import os
from pathlib import Path
import platform
import sys

ROOT=Path(__file__).resolve().parents[3]


def isolate():
    if sys.platform!='linux':raise RuntimeError('Linux Landlock/seccomp required; no isolation fallback')
    libc=ctypes.CDLL(None,use_errno=True)
    def checked(value,label):
        if value<0:raise OSError(ctypes.get_errno(),label)
        return value
    checked(libc.prctl(38,1,0,0,0),'PR_SET_NO_NEW_PRIVS')
    abi=checked(libc.syscall(444,0,0,1),'Landlock ABI query')
    if abi<4:raise RuntimeError('Landlock ABI>=4 required; no network-policy fallback')
    class Ruleset(ctypes.Structure):_fields_=[('fs',ctypes.c_uint64),('net',ctypes.c_uint64)]
    class Beneath(ctypes.Structure):_fields_=[('access',ctypes.c_uint64),('fd',ctypes.c_int32)]
    # Handle every filesystem operation up through ABI 3; no write permissions
    # are granted. All TCP bind/connect rights are handled and never granted.
    rights=(1<<15)-1;read=(1<<0)|(1<<2)|(1<<3)
    attr=Ruleset(rights,3)
    ruleset=checked(libc.syscall(444,ctypes.byref(attr),ctypes.sizeof(attr),0),'Landlock ruleset')
    paths=[Path('/usr'),Path('/lib'),Path('/lib64'),Path('/opt'),Path('/etc/ld.so.cache'),
           Path('/etc/localtime'),Path('/dev/null'),Path('/dev/urandom'),
           ROOT/'src',Path(__file__).resolve().parent]
    try:
        for path in paths:
            if not path.exists():continue
            fd=os.open(path,os.O_PATH|os.O_CLOEXEC)
            try:
                rule=Beneath(read if path.is_dir() else read&~(1<<3),fd)
                checked(libc.syscall(445,ruleset,1,ctypes.byref(rule),0),'Landlock path rule')
            finally:os.close(fd)
        checked(libc.syscall(446,ruleset,0),'Landlock restrict_self')
    finally:os.close(ruleset)
    # Deny sockets, ptrace, process_vm_readv/writev and pidfd_getfd. Inherited
    # descriptors are stdin/stdout/stderr only (Popen close_fds=True).
    numbers={'x86_64':[41,101,310,311,438],'aarch64':[198,117,270,271,438]}
    if platform.machine() not in numbers:raise RuntimeError('unsupported seccomp architecture')
    class Filter(ctypes.Structure):_fields_=[('code',ctypes.c_ushort),('jt',ctypes.c_ubyte),('jf',ctypes.c_ubyte),('k',ctypes.c_uint32)]
    class Program(ctypes.Structure):_fields_=[('length',ctypes.c_ushort),('filters',ctypes.POINTER(Filter))]
    instructions=[Filter(0x20,0,0,0)]  # load seccomp_data.nr
    for number in numbers[platform.machine()]:
        instructions.extend([Filter(0x15,0,1,number),Filter(0x06,0,0,0x00050000|errno.EPERM)])
    instructions.append(Filter(0x06,0,0,0x7fff0000))
    array=(Filter*len(instructions))(*instructions);program=Program(len(instructions),array)
    checked(libc.prctl(22,2,ctypes.byref(program),0,0),'seccomp filter')
    return {'landlock_abi':abi,'read_scope':['public code/libraries','stdin'],
            'write_scope':['stdout','stderr'],'network':'new sockets denied',
            'process_memory_inspection':'denied','fallback_used':False}
