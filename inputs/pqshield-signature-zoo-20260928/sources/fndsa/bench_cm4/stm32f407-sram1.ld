/*
 * Device: STM32F407-DISCOVERY
 *
 * This file uses the libopencm3 library and link scripts. Make sure to
 * adjust the path to the libopencm3 installation below.
 */

MEMORY
{
	/*
	 * For RAM-based execution, the loader script configures the
	 * FMC remap register so that SRAM1 (112 kB) is aliased at
	 * addresses 0x00000000 - 0x0001BFFF (it remains accessible at
	 * its normal address 0x20000000). The low addresses can be used
	 * for efficient instruction fetching by the CPU (through the
	 * I-bus). This setup allows running the device at the top speed
	 * (168 MHz) without incurring any Flash-induced wait states.
	 * On the other hand, it consumes some of the SRAM1 space, which
	 * cannot be used by the application for storing data; also, it
	 * is non-permanent (not flashed) and must be reloaded by the
	 * m4load.py script every time.
	 *
	 * Actual RAM (i.e. data space for the app) is the CCM, which can
	 * be read and written without contention with DMA or instruction
	 * fetching. CCM is not DMA-accessible; for interacting with
	 * peripherals, the app must allocate buffers in SRAM1 or SRAM2.
	 */
	rom (rx) : ORIGIN = 0x00000000, LENGTH = 112K
	ram (rwx) : ORIGIN = 0x10000000, LENGTH = 64K
}

/* Include the common ld script.
   ADJUST PATH HERE */
INCLUDE ../../libopencm3/lib/cortex-m-generic.ld
