/*
 * ca_types.h - common types, status codes and version information.
 *
 * Part of libcryptanalysis.  See LICENSE for terms.
 */
#ifndef CA_TYPES_H
#define CA_TYPES_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32) && defined(CA_SHARED)
#  ifdef CA_BUILDING
#    define CA_API __declspec(dllexport)
#  else
#    define CA_API __declspec(dllimport)
#  endif
#elif defined(__GNUC__) && __GNUC__ >= 4
#  define CA_API __attribute__((visibility("default")))
#else
#  define CA_API
#endif

#define CA_VERSION_MAJOR 0
#define CA_VERSION_MINOR 1
#define CA_VERSION_PATCH 0
#define CA_VERSION_STRING "0.1.0"

/* Status codes returned by every fallible API call. */
typedef enum ca_status {
    CA_OK = 0,
    CA_ERR_INVALID = 1,      /* invalid argument (bad modulus, point not on curve, ...) */
    CA_ERR_NOT_FOUND = 2,    /* the search space was exhausted without a solution */
    CA_ERR_NOMEM = 3,        /* allocation failure */
    CA_ERR_LIMIT = 4,        /* an explicit work/memory/time limit was reached */
    CA_ERR_UNSUPPORTED = 5,  /* the operation is not supported for this group/params */
    CA_ERR_INTERNAL = 6,     /* internal consistency failure (should not happen) */
    CA_ERR_SINGULAR = 7      /* linear system had no usable solution */
} ca_status;

/*
 * A group element.  Fixed-size and POD so that it crosses FFI boundaries
 * unchanged.  The interpretation of the words depends on the group:
 *   Z_p^*  : w[0] = residue (in Montgomery form internally), w[1..3] = 0
 *   E(F_p) : w[0] = x, w[1] = y, w[2] = 1 if point at infinity, w[3] = 0
 * User code should never poke at the words directly; use ca_group_encode /
 * ca_group_decode (or the language bindings) which handle representation.
 */
typedef struct ca_elem {
    uint64_t w[4];
} ca_elem;

/* Work statistics common to all solvers.  Zeroed by the caller or by the
 * solver entry point; solvers only ever add to the counters. */
typedef struct ca_stats {
    uint64_t group_ops;      /* group operations performed (adds/muls) */
    uint64_t iterations;     /* algorithm-specific step counter */
    uint64_t table_entries;  /* entries stored in lookup tables */
    uint64_t collisions;     /* useful collisions / relations found */
    uint64_t bytes_peak;     /* approximate peak heap usage of tables */
    double   seconds;        /* wall-clock time spent */
    uint32_t threads;        /* threads used */
    uint32_t reserved;
} ca_stats;

CA_API const char *ca_version(void);
CA_API const char *ca_status_string(ca_status s);
/* Thread-local description of the last error raised by this thread.  The
 * flat FFI entry points clear it on entry, so after a failing ca_ffi_* or
 * ca_ctx_* call it describes that call (possibly empty for status-only
 * failures such as CA_ERR_NOT_FOUND). */
CA_API const char *ca_last_error(void);
CA_API void ca_clear_error(void);

#ifdef __cplusplus
}
#endif
#endif /* CA_TYPES_H */
