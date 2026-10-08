#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdarg.h>

#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/gpio.h>
#include <libopencm3/stm32/usart.h>
#include <libopencm3/stm32/flash.h>

#include "timing.h"

/* Send len copies of character c onto the output UART. */
static void
send_mult_chars(char c, size_t len)
{
	size_t u;

	for (u = 0; u < len; u ++) {
		usart_send_blocking(USART2, c);
	}
}

/* Send a string (len characters, starting at s) to the UART. If
   len < olen, then padding is added, consisting olen-len copies
   of pad. If pad_left is non-zero then the padding is sent before
   the string, otherwise it is sent after the string. */
static void
send_string(const char *s, size_t len, size_t olen, char pad, int pad_left)
{
	size_t u;

	if (len < olen && pad_left) {
		send_mult_chars(pad, olen - len);
	}
	for (u = 0; u < len; u ++) {
		usart_send_blocking(USART2, s[u]);
	}
	if (len < olen && !pad_left) {
		send_mult_chars(pad, olen - len);
	}
}

/* Convert unsigned intger x to characters, using the provided base.
   Base can be up to 36; ASCII letters 'A' to 'Z' are used for digit
   values 10 to 35 (if upper is zero, then lowercase letters 'a' to 'z'
   are used instead). Output is written into buf[] (with no terminating
   zero) and the number of produced characters is returned. */
static size_t
to_digits(char *buf, uint64_t x, unsigned base, int upper)
{
	size_t u, v;

	u = 0;
	while (x != 0) {
		unsigned d;

		d = (x % base);
		x /= base;
		if (d >= 10) {
			if (upper) {
				d += 'A' - 10;
			} else {
				d += 'a' - 10;
			}
		} else {
			d += '0';
		}
		buf[u ++] = d;
	}
	if (u == 0) {
		buf[u ++] = '0';
	}
	for (v = 0; (v + v) < u; v ++) {
		char t;

		t = buf[v];
		buf[v] = buf[u - 1 - v];
		buf[u - 1 - v] = t;
	}
	return u;
}

/* Send an unsigned 64-bit integer to the UART. The integer is converted
   to digits with the provided base and 'upper' flag (see to_digits()).
   If the converted value is shorter than olen characters, then padding
   is applied, with enough '0' characters (if pad0 != 0) or spaces (if
   pad0 == 0). The pad_left flag determines if the padding comes before
   (pad_left != 0) or after (pad_left == 0) the converted integer.
   When trailing padding is used (pad_left == 0), the padding always
   uses spaces. */
static void
send_uint64(uint64_t x, unsigned base, int upper,
	size_t olen, int pad0, int pad_left)
{
	char buf[65];
	size_t u;

	u = to_digits(buf, x, base, upper);
	send_string(buf, u, olen, (pad0 && pad_left) ? '0' : ' ', pad_left);
}

/* Same as send_uint64() but for a signed integer. A leading '-' is used
   if necessary; leading padding (if any) is put before the '-' sign if
   it uses spaces, but after the '-' sign if it uses zeros. Trailing padding
   always consists of spaces regardless of 'pad0'. */
static void
send_int64(int64_t x, unsigned base, int upper,
	size_t olen, int pad0, int pad_left)
{
	char buf[65];
	size_t u;

	if (x < 0) {
		u = to_digits(buf, -(uint64_t)x, base, upper);
		if (pad_left) {
			if (pad0) {
				usart_send_blocking(USART2, '-');
				if (olen > (u + 1)) {
					send_mult_chars('0', olen - (u + 1));
				}
			} else {
				if (olen > (u + 1)) {
					send_mult_chars(' ', olen - (u + 1));
				}
				usart_send_blocking(USART2, '-');
			}
			send_string(buf, u, 0, 0, 0);
		} else {
			usart_send_blocking(USART2, '-');
			if (olen > 0) {
				olen --;
			}
			send_string(buf, u, olen, ' ', 0);
		}
	} else {
		u = to_digits(buf, x, base, upper);
		send_string(buf, u, olen, pad0 ? '0' : ' ', pad_left);
	}
}

/* see timing.h */
void
prf(const char *fmt, ...)
{
	va_list ap;
	const char *c;

	va_start(ap, fmt);
	c = fmt;
	for (;;) {
		int d;
		int pad0, wide, pad_left;
		unsigned olen;

		d = *c ++;
		if (d == 0) {
			break;
		}
		if (d != '%') {
			usart_send_blocking(USART2, d);
			continue;
		}
		d = *c ++;
		pad0 = 0;
		olen = 0;
		wide = 0;
		pad_left = 1;
		if (d == '-') {
			pad_left = 0;
			d = *c ++;
		}
		if (d >= '0' && d <= '9') {
			if (d == '0') {
				pad0 = 1;
			}
			while (d >= '0' && d <= '9') {
				olen = 10 * olen + (d - '0');
				d = *c ++;
			}
		}
		if (d == 'w') {
			wide = 1;
			d = *c ++;
		}
		if (pad0 && !pad_left) {
			pad0 = 0;
		}
		switch (d) {
		case 'd': {
			int64_t x;

			if (wide) {
				x = va_arg(ap, int64_t);
			} else {
				x = va_arg(ap, int32_t);
			}
			send_int64(x, 10, 0, olen, pad0, pad_left);
			break;
		}
		case 'u': {
			uint64_t x;

			if (wide) {
				x = va_arg(ap, uint64_t);
			} else {
				x = va_arg(ap, uint32_t);
			}
			send_uint64(x, 10, 0, olen, pad0, pad_left);
			break;
		}
		case 'x': {
			uint64_t x;

			if (wide) {
				x = va_arg(ap, uint64_t);
			} else {
				x = va_arg(ap, uint32_t);
			}
			send_uint64(x, 16, 0, olen, pad0, pad_left);
			break;
		}
		case 'X': {
			uint64_t x;

			if (wide) {
				x = va_arg(ap, uint64_t);
			} else {
				x = va_arg(ap, uint32_t);
			}
			send_uint64(x, 16, 1, olen, pad0, pad_left);
			break;
		}
		case 's': {
			const char *s;

			s = va_arg(ap, const char *);
			send_string(s, strlen(s), olen, ' ', pad_left);
			break;
		}
		case 0:
			break;
		default:
			usart_send_blocking(USART2, '%');
			break;
		}
		if (d == 0) {
			break;
		}
	}
	va_end(ap);
}

#if FREQ == 24
/* 24 MHz */
static const struct rcc_clock_scale benchmarkclock = {
	.pllm = 8, //VCOin = HSE / PLLM = 1 MHz
	.plln = 192, //VCOout = VCOin * PLLN = 192 MHz
	.pllp = 8, //PLLCLK = VCOout / PLLP = 24 MHz (low to have 0WS)
	.pllq = 4, //PLL48CLK = VCOout / PLLQ = 48 MHz (required for USB, RNG)
	.pllr = 0,
	.pll_source = RCC_CFGR_PLLSRC_HSE_CLK,
	.hpre = RCC_CFGR_HPRE_DIV_NONE,
	.ppre1 = RCC_CFGR_PPRE_DIV_2,
	.ppre2 = RCC_CFGR_PPRE_DIV_NONE,
	.voltage_scale = PWR_SCALE1,
	.flash_config = FLASH_ACR_DCEN | FLASH_ACR_ICEN | FLASH_ACR_LATENCY_0WS,
	.ahb_frequency  = 24000000,
	.apb1_frequency = 12000000,
	.apb2_frequency = 24000000,
};
#endif

/* Enable the cycle counter. */
static void
enable_cyccnt(void)
{
	volatile uint32_t *DWT_CONTROL = (volatile uint32_t *)0xE0001000;
	volatile uint32_t *DWT_CYCCNT = (volatile uint32_t *)0xE0001004;
	volatile uint32_t *DEMCR = (volatile uint32_t *)0xE000EDFC;
	volatile uint32_t *LAR  = (volatile uint32_t *)0xE0001FB0;

	*DEMCR = *DEMCR | 0x01000000;
	*LAR = 0xC5ACCE55;
	*DWT_CYCCNT = 0;
	*DWT_CONTROL = *DWT_CONTROL | 1;
}

/* FREQ should be 24 or 168 (for 24 MHz or 168 MHz operations). Default
   is 24. At 24 MHz, memory accesses have minimal (1-cycle) latency and
   there are no prefetch or cache effects; it is the traditional speed
   used in the literature for benchmarking cryptographic algorithms.
   Note that in-CPU contention between instruction fetching and data
   accesses can still happen at 24 MHz. */
#ifndef FREQ
#define FREQ   24
#endif

void
system_init(void)
{
	/* Setup clock. */
#if FREQ == 24
	rcc_clock_setup_pll(&benchmarkclock);
#elif FREQ == 168
	rcc_clock_setup_pll(&rcc_hse_8mhz_3v3[RCC_CLOCK_3V3_168MHZ]);
#else
#error Unsupported frequency
#endif

	/* Configure I/O. */
	rcc_periph_clock_enable(RCC_GPIOD);
	rcc_periph_clock_enable(RCC_GPIOA);
	rcc_periph_clock_enable(RCC_USART2);

	gpio_mode_setup(GPIOD, GPIO_MODE_OUTPUT,
		GPIO_PUPD_NONE, GPIO12 | GPIO13 | GPIO14 | GPIO15);
	gpio_mode_setup(GPIOA, GPIO_MODE_AF, GPIO_PUPD_NONE, GPIO2);
	gpio_set_af(GPIOA, GPIO_AF7, GPIO2);

	usart_set_baudrate(USART2, 115200);
	usart_set_databits(USART2, 8);
	usart_set_stopbits(USART2, USART_STOPBITS_1);
	usart_set_mode(USART2, USART_MODE_TX);
	usart_set_parity(USART2, USART_PARITY_NONE);
	usart_set_flow_control(USART2, USART_FLOWCONTROL_NONE);

	/* Finally enable the USART. */
	usart_enable(USART2);

	/*
	 * Enable cycle counter.
	 */
	enable_cyccnt();

	/*
	 * Set Flash access flags.
	 *   0x000L   Flash access latency (L = 0 to 7)
	 *   0x0100   enable prefetch flag
	 *   0x0200   enable instruction cache flag
	 *   0x0400   enable data cache flag
	 * At 24 MHz, Flash reads work with minimal latency, so there is
	 * no need for caching, prefetching, or extra wait states.
	 * At 168 MHz, Flash reads need 5 wait states, so we should also
	 * enable caches and prefetching.
	 */
#if FREQ == 24
	uint32_t flash_acr = 0;
#elif FREQ == 168
	uint32_t flash_acr = 5 | 0x100 | 0x200 | 0x400;
#else
#error Unsupported frequency
#endif
	*(volatile uint32_t *)0x40023C00 = flash_acr;

	prf("-----------------------------------------\n");
	prf("Frequency: %u MHz\n", FREQ);
	prf("FLASH_ACR: 0x%08X\n", flash_acr);
	prf("-----------------------------------------\n");
}

/* see timing.h */
void *
sram_free_area(size_t *len)
{
	/* _etext symbol is set by libopencm3 at the end of the generated
	   ROM segment (with 32-bit alignment). */
	extern unsigned _etext;

	/* If _etext is in SRAM, or if it is in the low addresses, then
	   the code is assumed to be loaded in SRAM; otherwise, SRAM1+2
	   is free. */
	uint32_t addr = (uint32_t)&_etext;
	uint32_t off;
	if (addr >= 0x20000000 && addr < 0x20020000) {
		off = addr - 0x20000000;
	} else if (addr < 0x00020000) {
		off = addr;
	} else {
		off = 0;
	}
	*len = 0x20000 - off;
	return (void *)(0x20000000 + off);
}

/* see timing.h */
void
system_exit(void)
{
	prf("SYSTEM EXIT\n");
	__asm__ __volatile__ ("udf" : : : "memory", "cc");
}
