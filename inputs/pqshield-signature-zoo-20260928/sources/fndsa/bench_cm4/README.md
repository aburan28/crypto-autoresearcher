# Benchmarking on ARM Cortex-M4

This subdirectory contains some benchmarking code for an STM32F407-DISC1
board ("discovery" board featuring an STMicroelectronics microcontroller
with an ARM Cortex-M4F CPU).

## Run from Flash or from SRAM

The STM32F407 microcontroller includes Flash memory and also RAM blocks.
Flash is 1 MB (starting at address `0x08000000`). The three RAM blocks
are SRAM1 (112 kB, starting at address `0x20000000`), SRAM2 (16 kB,
starting at address `0x2001C000`, i.e. immediately after SRAM1), and
CCM (64 kB, starting at address `0x10000000`). The CCM has a dedicated
link to the CPU, making it efficient to store runtime data; however, it
is not amenable to DMA from peripheral, and bulk I/O needs to use buffers
in SRAM1 or SRAM2.

The microcontroller can run code present in either the Flash or in SRAM
(but not from the CCM). The main advantage of running code from SRAM is
that it is faster, since accesses to SRAM can be done with zero extra
wait state, even at the highest supported frequency (168 MHz). Flash can
be read with zero extra wait state only at clock frequencies up to 24
MHz; beyond that, Flash accesses become slower (5 extra wait states at
168 MHz). Some of the lost performance can be regained with the use of
prefetching, and by enabling the decided caches on Flash (this is done
with the `FLASH_ACR` system register). For benchmarking purposes,
though, we'd prefer avoiding both caches and wait states; this means
either running from Flash at 24 MHz, or from SRAM1 at 168 MHz. The
latter is 7 times faster (in wall clock time), hence preferable for
long-running tests.

**A poorly documented point** is that running code from SRAM incurs
extra delays unless a specific memory controller configuration is
applied. This is cryptically alluded to in the board [reference
manual](https://www.st.com/resource/en/reference_manual/dm00031020-stm32f405-415-stm32f407-417-stm32f427-437-and-stm32f429-439-advanced-arm-based-32-bit-mcus-stmicroelectronics.pdf),
under section 2.4 ("Boot configuration"). Footnote 1 of table 3 says:
*"In remap mode, the CPU can access the external memory via ICode bus
instead of System bus which boosts up the performance."* The CPU has
three busses: ICode, DCode and System. When accessing code or data, if
the target address is below `0x20000000`, then the CPU will do the fetch
over ICode (for instruction fetching) or DCode (for data reads and
writes); for target addresses above `0x20000000`, the System bus is
used. This implies that if running code from SRAM, then all instruction
fetches will use the System bus, which is slower than the other two. In
order to avoid the slowness of the System bus, SRAM1 can be aliased to
addresses `0x00000000` to `0x0001BFFF`, which the CPU can access through
ICode and DCode. This aliasing can be enabled by writing `0x00000003` to the
`SYSCFG_MEMRMP` register (which is located at address `0x40013800`); the
value of this register is by default loaded at power-up time from some
jumpers on the board, which also select the stand-alone boot source.

Note that the aliasing into low addresses works only for SRAM1, not
SRAM2; this limits the total size of "fast code" (when running from
SRAM) to 112 kB. CCM is only connected to DCode, thus unusable for code
(the CPU cannot fetch instructions from DCode, only from ICode and
System).

## Compiling

 1. Get an embedded toolchain. On Ubuntu system, try installing the
    `gcc-arm-none-eabi` and `binutils-arm-none-eabi` packages.

 2. Download and compile [libopencm3](https://github.com/libopencm3/libopencm3).

 3. Update the `INCDIR` and `LIBDIR` variable in the [Makefile](Makefile)
    to point to where you put libopencm3 on your system.

 4. Update the `INCLUDE` directive at the end of
    [stm32f4-sram1.ld](stm32f4-sram1.ld) to point to the relevant files in
    libopencm3. This is for compiling for running the code in SRAM1.
    If you want to run the code from Flash instead, then you need to
    update `INCLUDE` in [stm32f4-flash.ld](stm32f4-flash.ld) *and* to
    change the `LDSCRIPT` variable in the Makefile accordingly. You will
    also possibly want to lower the operating frequency from 168 to 24 MHz
    (`FREQ` variable in the Makefile).

 5. Type: `make`

    This should produce two binary files called `ttkgen.elf` and
    `ttsign.elf`, which are used to benchmark key pair generation,
    and signature generation/verification, respectively.

In the Makefile, you can change `-DFNDSA_ASM_CORTEXM4=1` into
`-DFNDSA_ASM_CORTEXM4=0` (in the `CFLAGS` variable) to disable use of
the assembly-optimized routines; in that case, you must also empty the
contents of the `OBJ_ASM` variable (otherwise you'll get errors with
multiple functions with the same name). Benchmarking the plain C version
highlights the benefits of assembly optimizations (namely, using
assembly makes signature generation twice faster; it also speeds up
signature verification, mostly by its use of an assembly-optimized
SHA3/SHAKE implementation).

## Running

 1. Install [stlink](https://github.com/stlink-org/stlink). On Ubuntu systems,
    a system package exists, called `stlink-tools`.

 2. For running in Flash, or for in-CPU debugging, install a
    "multi-architecture" version of GDB. On Ubuntu systems, you just
    install the `gdb-multiarch` package. This is not necessary if
    running the benchmarks from SRAM1.

 3. Plug a serial console to the board. I am using a basic USB-to-TTL
    adapter cable; TX and RX go to pins PA3 and PA2, respectively. That
    adapter, on the host side, shows up in Linux as `/dev/ttyUSB0`. Set
    the speed with: `stty -F /dev/ttyUSB0 speed 115200 raw`

    Then type `cat /dev/ttyUSB0` in a terminal and let it run; this is
    where the benchmark program output will show up.

 4. Plug the board itself with its USB cable to the host system.

 5. Run in a terminal: `st-util`

    This program should run as long as the board is in usage.

 6. **Run from SRAM1:** in another terminal, run: `./m4load.py ttkgen.elf`

    The `m4load.py` script connects to `st-util` to load the specified
    binary into SRAM1, and then run it. The script handles the proper
    setting of `SYSCFG_MEMRMP` for fast execution. You can interrupt
    the script at any time (with Ctrl-C); execution will continue on
    the board.

 7. **Run from Flash:** this assumes that the Makefile was configured
    for making binaries adapted for on-Flash execution. In another
    terminal, run `gdb-multiarch`. In the GDB command-line, use the
    following commands:

    ~~~
    set arch arm
    target ext :4242
    load ttkgen.elf
    run
    ~~~

    You can interrupt (and debug!) the program by typing Ctrl-C in the
    GDB command-line, then load a new version and run it again, and
    again.

Replace `ttkgen.elf` with `ttsign.elf` in the commands above to perform
signature generation and verification benchmarks. The benchmarks are
separate because signature generation at high FN-DSA degree (1024)
requires use of a large memory buffer (about 80 kB) which must be taken
from SRAM, and thus limits total code size to 48 kB when running from
SRAM.
