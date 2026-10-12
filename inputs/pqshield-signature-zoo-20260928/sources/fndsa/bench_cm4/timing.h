#ifndef timing_h__
#define timing_h__

/* Initialize the system (sets the main clock, enable USART, enable cycle
   counter). This should be called from main() as first operation. */
void system_init(void);

/* Read the current cycle count. */
static inline uint32_t
get_system_ticks(void)
{
	return *(volatile uint32_t *)0xE0001004;
}

/* A printf()-lookalike. Each format element has the following format:
     %[-][0][len][w]type
   with:
      -      Padding is applied after the value instead of before the value
      0      Integer padding uses leading zeros instead of spaces
      len    Target output length (decimal)
      w      For an integer value: value is wide (64-bit)
      type   One of:
                d   signed integer (decimal)
                u   unsigned integer (decimal)
                x   unsigned integer (hexadecimal, lowercase)
                X   unsigned integer (hexadecimal, uppercase)
                s   nul-terminated character string
   The '0' flag is ignored for strings; padding, if any, always uses spaces.
   Conventionally, '%%' should be used to emit a '%' character. */
void prf(const char *fmt, ...);

/* Get address and size of free area in SRAM1+2. If the code is running
   from Flash, then this is the entire SRAM1+2 (128 kB); otherwise, this
   is the space not use by code. Returned pointer is 32-bit aligned. */
void *sram_free_area(size_t *len);

/* Terminate execution with a trap (does not return). */
void system_exit(void);

#endif
