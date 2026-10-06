#ifndef MQOM_STACK_MEASURE_H
#define MQOM_STACK_MEASURE_H

#ifdef MEASURE_STACK

/* ---- platform guards ---- */

/* Windows has no pthread_attr_setstack or posix_memalign. */
#if defined(_WIN32) || defined(_WIN64) || defined(__MINGW32__) || defined(__MINGW64__)
#  error "MEASURE_STACK is not supported on Windows (no pthread_attr_setstack / posix_memalign)."
#endif

/* Require a known POSIX OS where pthread_attr_setstack is available. */
#if !defined(__linux__) && !defined(__APPLE__) && \
    !defined(__FreeBSD__) && !defined(__NetBSD__) && !defined(__OpenBSD__)
#  error "MEASURE_STACK requires a POSIX platform with pthread_attr_setstack " \
         "(Linux, macOS, or *BSD). Add your OS here if it provides that API."
#endif

/*
 * The canary scan assumes the stack grows downward (used region at high
 * addresses, intact canary at low addresses).  This is true on all
 * architectures listed below.  Add yours if it also grows downward.
 */
#if !defined(__x86_64__) && !defined(__amd64__)  && \
    !defined(__i386__)   && !defined(__i686__)    && \
    !defined(__aarch64__)                         && \
    !defined(__arm__)    && !defined(__armv7__)   && \
    !defined(__riscv)                             && \
    !defined(__powerpc__) && !defined(__powerpc64__) && \
    !defined(__ppc__)     && !defined(__ppc64__)  && \
    !defined(__mips__)    && !defined(__mips64__)
#  error "MEASURE_STACK: unknown architecture - stack-grows-downward not verified. " \
         "If your architecture grows the stack downward, add its predefined macro " \
         "to the whitelist in benchmark/stack_measure.h."
#endif

/* ---- end platform guards ---- */

#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

/* 8 MB custom stack - generous for all MQOM variants */
#define STACK_MEASURE_SIZE (8 * 1024 * 1024)

/* Canary byte used to paint the stack before the run */
#define STACK_CANARY 0xCD

typedef struct {
    void   (*fn)(void *);
    void    *arg;
    uint8_t *stack_buf;
    size_t   stack_size;
} _sm_thread_ctx_t;

static void *_sm_thread_entry(void *raw) {
    _sm_thread_ctx_t *ctx = (_sm_thread_ctx_t *)raw;
    ctx->fn(ctx->arg);
    return NULL;
}

/*
 * Run fn(arg) in a pthread with a custom, fully-painted stack.
 * Returns peak stack consumption in bytes, or 0 on error.
 *
 * Strategy: paint the buffer with STACK_CANARY, run the function,
 * then scan from address 0 (bottom) upward to find the first
 * non-canary byte.  The stack grows downward, so the used region
 * is at the top (high addresses) and the intact canary region is
 * at the bottom (low addresses).  Peak = stack_size - first_intact_offset.
 *
 * Works on Linux and macOS (both grow the stack downward).
 * posix_memalign and pthread_attr_setstack are POSIX; -lpthread is
 * needed only on Linux (macOS links pthread automatically).
 */
static size_t stack_measure_run(void (*fn)(void *), void *arg, size_t stack_size) {
    uint8_t *stack_buf = NULL;
    pthread_t thread;
    pthread_attr_t attr;
    _sm_thread_ctx_t ctx;
    size_t i, peak = 0;

    if (posix_memalign((void **)&stack_buf, 4096, stack_size) != 0) {
        return 0;
    }
    memset(stack_buf, STACK_CANARY, stack_size);

    ctx.fn         = fn;
    ctx.arg        = arg;
    ctx.stack_buf  = stack_buf;
    ctx.stack_size = stack_size;

    pthread_attr_init(&attr);
    pthread_attr_setstack(&attr, stack_buf, stack_size);

    if (pthread_create(&thread, &attr, _sm_thread_entry, &ctx) != 0) {
        pthread_attr_destroy(&attr);
        free(stack_buf);
        return 0;
    }
    pthread_join(thread, NULL);
    pthread_attr_destroy(&attr);

    /* Scan from the bottom to find first non-canary byte */
    for (i = 0; i < stack_size; i++) {
        if (stack_buf[i] != STACK_CANARY) {
            break;
        }
    }
    peak = stack_size - i;

    free(stack_buf);
    return peak;
}

#endif /* MEASURE_STACK */
#endif /* MQOM_STACK_MEASURE_H */
