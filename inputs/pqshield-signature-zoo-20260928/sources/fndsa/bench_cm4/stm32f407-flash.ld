/*
 * Device: STM32F407-DISCOVERY
 *
 * This file uses the libopencm3 library and link scripts. Make sure to
 * adjust the path to the libopencm3 installation below.
 */

MEMORY
{
	/*
	 * Flash is at address 0x08000000, with length 1MB.
	 * For RAM, we use the CCM block, which can be accessed without
	 * any contention with peripherals. SRAM1+2 (128 kB), starting at
	 * address 0x20000000, may be used by the application explicitly
	 * for more RAM storage.
	 */
	rom (rx) : ORIGIN = 0x08000000, LENGTH = 1024K
	ram (rwx) : ORIGIN = 0x10000000, LENGTH = 64K
}

/* Include the common ld script.
   ADJUST PATH HERE */
INCLUDE ../../libopencm3/lib/cortex-m-generic.ld
