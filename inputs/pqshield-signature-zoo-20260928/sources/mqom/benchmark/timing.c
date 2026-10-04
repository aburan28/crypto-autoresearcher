#if defined(__linux__) && (defined(BENCHMARK_TIME) || defined(BENCHMARK_CYCLES))
#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
static inline void set_cpu_affinity(int cpu) {
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(cpu, &set);
	if (sched_setaffinity(getpid(), sizeof(set), &set) == -1) {
		fprintf(stderr, "Error: error when setting affinity to CPU 0 ...\n");
		exit(-1);
	}
}

/* Pin to CPU 0 for every timed run, wall-clock (BENCHMARK_TIME) or cycles
 * (BENCHMARK_CYCLES) alike: avoids scheduling noise and migration issues
 * (in particular P/E-core migration on recent Intel CPUs). Explicit
 * priority 101 (lowest allowed for user constructors) guarantees this runs
 * before the unprioritized ticks_setup() constructor below, regardless of
 * link order, so the perf-event setup there also benefits from a stable
 * affinity. Runs before main() so it covers the whole process, not just
 * the timed region. */
__attribute__((constructor(101))) void timing_cpu_pin_setup(void) {
	set_cpu_affinity(0);
}
#elif defined(__APPLE__) && (defined(BENCHMARK_TIME) || defined(BENCHMARK_CYCLES))
#include <stdio.h>
#include <pthread.h>
#include <pthread/qos.h>

/* macOS has no equivalent of Linux's sched_setaffinity: hard core pinning
 * is not exposed to third-party processes (deliberate scheduler design on
 * Apple's part). The closest available lever is a QoS class hint, which
 * strongly biases the scheduler toward keeping this thread on a
 * Performance core rather than an Efficiency core. On Apple Silicon's
 * heterogeneous P/E design this matters more than classic turbo-boost
 * frequency ramping: P and E cores differ in throughput by roughly 2-3x
 * for the same workload, not just clock speed, so a mid-run P/E migration
 * dwarfs ordinary DVFS noise. This is a strong hint, not a hard guarantee
 * like Linux's CPU pin - the OS can still override it under thermal or
 * power constraints - but it is the best tool actually available here.
 * Runs before main() so it covers the whole process, not just the timed
 * region. */
__attribute__((constructor(101))) void timing_cpu_pin_setup(void) {
	if (pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0) != 0) {
		fprintf(stderr, "Warning: failed to set QoS class to USER_INTERACTIVE; "
		                "timing measurements may be noisier due to P/E core migration.\n");
	}
}
#endif

#include "timing.h"

#ifdef BENCHMARK_CYCLES
/* ====================================================== */
/* Getting cycles primitives depending on the platform */

/* ---- Free-running counter fallback, per architecture ----
 * Used directly on non-Linux OSes below, and as the last-resort fallback
 * on Linux (further down) when perf_event_open() is unavailable. None of
 * these are real per-cycle PMU counts: x86's TSC and ARM's Generic Timer
 * virtual counter (CNTVCT) both tick at a fixed reference frequency,
 * invariant to the CPU core's actual (dynamically-scaled) clock - closer
 * to a fine-grained wall clock than to literal executed cycles. */
#if defined(__amd64__) || defined(__x86_64__) || defined(__i386__)
#include <x86intrin.h>
static inline uint64_t read_fallback_counter(void) {
	unsigned int garbage;
	return (uint64_t) __rdtscp(&garbage);
}
#define CYCLES_FALLBACK_NAME "rdtsc"
#elif defined(__aarch64__)
static inline uint64_t read_fallback_counter(void) {
	uint64_t result;
	asm volatile ("isb \n mrs %0, CNTVCT_EL0" : "=r" (result));
	return result;
}
#define CYCLES_FALLBACK_NAME "CNTVCT_EL0"
#elif defined(__arm__) && !(defined(__ARM_ARCH_PROFILE) && (__ARM_ARCH_PROFILE == 'M'))
/* ARMv7-A Generic Timer virtual counter, a 64-bit register pair read via
 * mrrc (the AArch32 counterpart of AArch64's "mrs ..., CNTVCT_EL0").
 * Requires the Generic Timer / Virtualization Extensions, present on
 * Cortex-A7 and later (Raspberry Pi 2 onward); NOT available on ARMv6
 * cores (original Raspberry Pi 1 / Zero, BCM2835), which have no such
 * counter at all - not checked for at compile or run time.
 *
 * Excluded for Cortex-M (__ARM_ARCH_PROFILE == 'M', GCC's standard ACLE
 * profile macro - 'A'/'R'/'M' for Cortex-A/R/M): __arm__ alone is not
 * enough to select this branch, since arm-none-eabi-gcc defines it for
 * every ARM target, M-profile included, and M-profile has no such CP15
 * coprocessor/mrrc instruction at all - a build for e.g. Cortex-M4 would
 * either fail to assemble or (worse) execute UNDEFINED, not just be
 * imprecise. Every Cortex-M target in this tree already has a per-board HAL
 * providing platform_get_cycles() externally (see mqom-embedded/
 * embedded_CM4/platform.c, itself backed by a real cycle counter -
 * hal_get_cycles(), DWT_CYCCNT-based), so falling through to the
 * "externally defined" branch below is correct, not just a fallback. */
static inline uint64_t read_fallback_counter(void) {
	uint32_t lo, hi;
	asm volatile ("isb \n mrrc p15, 1, %0, %1, c14" : "=r" (lo), "=r" (hi));
	return ((uint64_t) hi << 32) | lo;
}
#define CYCLES_FALLBACK_NAME "CNTVCT"
#endif

#if defined(__linux__)
/* On Linux, perf_event_open() + PERF_COUNT_HW_CPU_CYCLES is an
 * architecture-independent kernel interface (x86, ARM, RISC-V, PowerPC,
 * ...): real hardware PMU cycles, not a fixed-frequency proxy like the
 * fallback counters above. A direct userspace register read (RDPMC on
 * x86) is an optional fast path layered on top where implemented here -
 * x86-64 only for now: ARM64 self-monitoring needs an index->register
 * jump table not yet verified against the kernel ABI, and ARM32 has no
 * such fast path in mainline Linux at all. Everywhere else (including
 * i386) falls back to one read() syscall per sample - slower than RDPMC,
 * but still real PMU-measured cycles, not a fixed-frequency proxy.
 * NOTE: the RDPMC fast path is stolen and adapted from
 * https://cpucycles.cr.yp.to/libcpucycles-20240318/cpucycles/amd64-pmc.c.html */
#include <sys/types.h>
#include <sys/syscall.h>
#include <linux/perf_event.h>
#include <unistd.h>

#if defined(__amd64__) || defined(__x86_64__)
#include <sys/mman.h>
#define CYCLES_HAVE_RDPMC 1
#endif

struct perf_event_attr attr;
int fdperf = -1;
#ifdef CYCLES_HAVE_RDPMC
struct perf_event_mmap_page *buf = 0;
#endif

/* Cycle source actually in use, decided once in ticks_setup():
 *   RDPMC    - fast direct userspace register read (x86-64 only, best case)
 *   READ     - perf fd works: real PMU cycles, one syscall per read
 *   FALLBACK - perf_event_open() itself failed: architecture-specific
 *              free-running counter (read_fallback_counter() above, when
 *              the target architecture has one), not real PMU cycles.
 * READ and FALLBACK are both silent precision downgrades from RDPMC;
 * under STRICT_CYCLES (default) ticks_setup() refuses them and exits
 * instead - see the Makefile comment on STRICT_CYCLES. */
enum { CYCLES_SRC_RDPMC, CYCLES_SRC_READ, CYCLES_SRC_FALLBACK } cycles_src =
#ifdef CYCLES_HAVE_RDPMC
	CYCLES_SRC_RDPMC;
#else
	CYCLES_SRC_READ;
#endif

long long ticks(void) {
#ifdef CYCLES_FALLBACK_NAME
	if (cycles_src == CYCLES_SRC_FALLBACK) {
		return (long long) read_fallback_counter();
	}
#endif
	if (cycles_src == CYCLES_SRC_READ) {
		uint64_t value = 0;
		if (read(fdperf, &value, sizeof(value)) != (ssize_t) sizeof(value)) {
			return 0;
		}
		return (long long) value;
	}

#ifdef CYCLES_HAVE_RDPMC
	{
		long long result;
		unsigned int seq;
		long long index;
		long long offset;

		if (buf == 0) {
			return 0;
		}
		do {
			seq = buf->lock;
			asm volatile("" ::: "memory");
			index = buf->index;
			/* index == 0 means the counter is not scheduled on this
			 * thread/CPU (perf_event_open with pid=0 follows the opening
			 * thread only). Executing rdpmc with index-1 = -1 would SIGSEGV. */
			if (index == 0) {
				return 0;
			}
			offset = buf->offset;
			asm volatile("rdpmc;shlq $32,%%rdx;orq %%rdx,%%rax"
			             : "=a"(result) : "c"(index-1) : "%rdx");
			asm volatile("" ::: "memory");
		} while (buf->lock != seq);

		result += offset;
		result &= 0xffffffffffff;
		return result;
	}
#else
	return 0;
#endif
}

/* NOTE: constructor attribute to be executed first among unprioritized
 * constructors; CPU affinity itself is pinned earlier still, by the
 * priority-101 timing_cpu_pin_setup() constructor above. */
__attribute__((constructor)) void ticks_setup(void) {
	if (fdperf == -1) {
		attr.type = PERF_TYPE_HARDWARE;
		attr.config = PERF_COUNT_HW_CPU_CYCLES;
		attr.exclude_kernel = 1;
		attr.exclude_hv = 1;
		fdperf = syscall(__NR_perf_event_open, &attr, 0, -1, -1, 0);
		if (fdperf == -1) {
			/* No fallback compiled in for this architecture at all: fail
			 * unconditionally, STRICT_CYCLES cannot offer a degraded mode
			 * that does not exist. */
#if defined(STRICT_CYCLES) || !defined(CYCLES_FALLBACK_NAME)
			fprintf(stderr, "Error: performance counters configuration failed ...\n");
			fprintf(stderr, "  => Please configure perf access with (as superuser) 'echo 2 > /proc/sys/kernel/perf_event_paranoid' (i.e. allow access from userland)\n");
#ifdef CYCLES_FALLBACK_NAME
			fprintf(stderr, "  => Or compile with STRICT_CYCLES=0 to accept a coarser " CYCLES_FALLBACK_NAME "-based cycle count instead of failing.\n");
#endif
			exit(-1);
#else
			fprintf(stderr, "Warning: performance counters unavailable, falling back to " CYCLES_FALLBACK_NAME "-based cycle counting (fixed-frequency reference clock, not real CPU cycles).\n");
			cycles_src = CYCLES_SRC_FALLBACK;
			return;
#endif
		}
#ifdef CYCLES_HAVE_RDPMC
		buf = mmap(NULL, sysconf(_SC_PAGESIZE), PROT_READ, MAP_SHARED, fdperf, 0);
		if ((buf == MAP_FAILED) || (buf->cap_user_rdpmc == 0)) {
#ifdef STRICT_CYCLES
			fprintf(stderr, "Error: direct RDPMC access unavailable (cap_user_rdpmc=0) ...\n");
			fprintf(stderr, "  => Please configure RDPMC access with (as superuser) 'echo 2 > /proc/sys/kernel/perf_event_paranoid' (i.e. allow access from userland)\n");
			fprintf(stderr, "  => Or compile with STRICT_CYCLES=0 to accept a slower syscall-based cycle count instead of failing.\n");
			exit(-1);
#else
			fprintf(stderr, "Warning: direct RDPMC access unavailable, falling back to syscall-based cycle counting (slower, noisier than RDPMC).\n");
			cycles_src = CYCLES_SRC_READ;
			if (buf == MAP_FAILED) {
				buf = 0;
			}
#endif
		}
#endif /* CYCLES_HAVE_RDPMC */
	}

	return;
}


long long platform_get_cycles(void) {
	return ticks();
}

#else /* !__linux__: no perf_event_open(), use the free-running counter directly */

#ifdef CYCLES_FALLBACK_NAME
#include <stdio.h>
/* perf_event_open() is Linux-only: this OS has no PMC access path at all in
 * this codebase, so platform_get_cycles() can only ever return
 * CYCLES_FALLBACK_NAME-based ticks - a fixed-frequency reference clock (see
 * read_fallback_counter() above), not real per-cycle PMU measurement. Warn
 * once at startup so this is never silently mistaken for real cycle counts:
 * they can look deceptively "too good" (e.g. a 24 MHz reference clock on
 * Apple Silicon, nowhere near the actual core frequency). */
__attribute__((constructor)) void cycles_fallback_warn_setup(void) {
	printf("[Warning:] no performance counter (PMC) access available on this OS, using " CYCLES_FALLBACK_NAME "-based cycle counting (fixed-frequency reference clock, not real CPU cycles).\n");
}

long long platform_get_cycles(void) {
	return (long long) read_fallback_counter();
}
#else
/* For other unknown platforms, the platform_get_cycles is externally defined by the user */
extern long long platform_get_cycles(void);
#endif

#endif /* __linux__ */
#endif /* BENCHMARK_CYCLES */

void btimer_init(btimer_t* timer) {
	if (timer != NULL) {
		timer->counter = 0;
		timer->nb_milliseconds = 0.;
		timer->nb_cycles = 0;
		timer->start.tv_sec = timer->start.tv_usec = 0;
		timer->stop.tv_sec = timer->stop.tv_usec = 0;
	}
}
void btimer_count(btimer_t *timer) {
	if (timer != NULL) {
		timer->counter++;
	}
}

void btimer_start(btimer_t *timer) {
	if (timer != NULL) {
#ifdef BENCHMARK_TIME
#if defined(CLOCK_MONOTONIC_COARSE) && !defined(BENCHMARK_USE_GETTIMEOFDAY)
		/* NOTE: when available, we use CLOCK_MONOTONIC_COARSE
		 * as it does not require a costly system call */
		struct timespec t;
		clock_gettime(CLOCK_MONOTONIC_COARSE, &t);
		timer->start.tv_sec  = t.tv_sec;
		timer->start.tv_usec = (double)t.tv_nsec * 0.001;
#else
		/* NOTE: on POSIX like systems, this usually requires a syscall, so this can
		 * incur a perfomance hit and perturb the measurements */
		gettimeofday(&timer->start, NULL);
#endif
#else
		(void)timer;
#endif /* BENCHMARK_TIME */
#ifdef BENCHMARK_CYCLES
		timer->cstart = platform_get_cycles();
#endif
	}
}
double btimer_diff(btimer_t *timer) {
	return ( (timer->stop.tv_sec - timer->start.tv_sec) * 1000000 + (timer->stop.tv_usec - timer->start.tv_usec) ) / 1000.;
}
uint64_t btimer_diff_cycles(btimer_t *timer) {
	return (timer->cstop - timer->cstart);
}
void btimer_end(btimer_t *timer) {
	if (timer != NULL) {
#ifdef BENCHMARK_TIME
#if defined(CLOCK_MONOTONIC_COARSE) && !defined(BENCHMARK_USE_GETTIMEOFDAY)
		/* NOTE: when available, we use CLOCK_MONOTONIC_COARSE
		 * as it does not require a costly system call */
		struct timespec t;
		clock_gettime(CLOCK_MONOTONIC_COARSE, &t);
		timer->stop.tv_sec  = t.tv_sec;
		timer->stop.tv_usec = (double)t.tv_nsec * 0.001;
#else
		/* NOTE: on POSIX like systems, this usually requires a syscall, so this can
		 * incur a perfomance hit and perturb the measurements */
		gettimeofday(&timer->stop, NULL);
#endif
		timer->nb_milliseconds += btimer_diff(timer);
#else
		(void)timer;
#endif /* BENCHMARK_TIME */
#ifdef BENCHMARK_CYCLES
		timer->cstop = platform_get_cycles();
		timer->nb_cycles += btimer_diff_cycles(timer);
#endif
	}
}
double btimer_get(btimer_t *timer) {
	return timer->nb_milliseconds / timer->counter;
}
double btimer_get_cycles(btimer_t *timer) {
	return (double)timer->nb_cycles / timer->counter;
}
