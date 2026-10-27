/* Internal atomic snapshot helpers for single-thread interval solvers. */
#ifndef CA_DLOG_CHECKPOINT_INTERNAL_H
#define CA_DLOG_CHECKPOINT_INTERNAL_H

#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

typedef struct dlog_ckpt_file {
    const char *path;
    char *tmp;
    FILE *f;
} dlog_ckpt_file;

static inline uint64_t dlog_ckpt_hash(const void *data, size_t n, uint64_t h)
{
    const unsigned char *p = data;
    for (size_t i = 0; i < n; i++) { h ^= p[i]; h *= UINT64_C(1099511628211); }
    return h;
}

static inline char *dlog_ckpt_path(const char *path, const char *suffix)
{
    size_t n = strlen(path) + strlen(suffix) + 1;
    char *out = malloc(n);
    if (out) snprintf(out, n, "%s%s", path, suffix);
    return out;
}

static inline int dlog_ckpt_sync_parent(const char *path)
{
    char *dir = strdup(path);
    if (!dir) return 0;
    const char *parent = dir;
    char *slash = strrchr(dir, '/');
    if (slash) {
        if (slash == dir) slash[1] = '\0';
        else *slash = '\0';
    } else
        parent = ".";
    int fd = open(parent, O_RDONLY);
    int ok = fd >= 0 && fsync(fd) == 0;
    if (fd >= 0) close(fd);
    free(dir);
    return ok;
}

static inline int dlog_ckpt_begin(dlog_ckpt_file *w, const char *path)
{
    memset(w, 0, sizeof(*w));
    w->path = path;
    w->tmp = dlog_ckpt_path(path, ".tmp.XXXXXX");
    if (!w->tmp) return 0;
    int fd = mkstemp(w->tmp);
    w->f = fd >= 0 ? fdopen(fd, "wb+") : NULL;
    if (!w->f) {
        if (fd >= 0) {
            close(fd);
            unlink(w->tmp);
        }
        free(w->tmp);
        w->tmp = NULL;
    }
    return w->f != NULL;
}

static inline int dlog_ckpt_finish(dlog_ckpt_file *w, int ok)
{
    if (w->f) {
        if (ok) ok = fflush(w->f) == 0 && fsync(fileno(w->f)) == 0;
        if (fclose(w->f) != 0) ok = 0;
    } else ok = 0;
    if (ok) ok = rename(w->tmp, w->path) == 0 && dlog_ckpt_sync_parent(w->path);
    if (!ok && w->tmp) unlink(w->tmp);
    free(w->tmp);
    return ok;
}

static inline int dlog_ckpt_progress(const char *path, const char *alg,
                                      const char *phase, const char *status,
                                      double seconds, uint64_t ops,
                                      uint64_t iterations, size_t entries,
                                      int verbose)
{
    if (verbose) fprintf(stderr, "[%s] %s %.1fs ops=%" PRIu64
                         " steps=%" PRIu64 " entries=%zu\n",
                         alg, phase, seconds, ops, iterations, entries);
    if (!path) return 1;
    char *out = dlog_ckpt_path(path, ".progress.json");
    char *tmp = dlog_ckpt_path(path, ".progress.tmp.XXXXXX");
    if (!out || !tmp) { free(out); free(tmp); return 0; }
    int fd = mkstemp(tmp);
    int ok = fd >= 0 && dprintf(fd,
        "{\"status\":\"%s\",\"phase\":\"%s\",\"elapsed_seconds\":%.3f,"
        "\"group_ops\":%" PRIu64 ",\"steps\":%" PRIu64
        ",\"table_entries\":%zu}\n",
        status, phase, seconds, ops, iterations, entries) > 0 && fsync(fd) == 0;
    if (fd >= 0 && close(fd) != 0) ok = 0;
    if (ok) ok = rename(tmp, out) == 0 && dlog_ckpt_sync_parent(out);
    if (!ok) unlink(tmp);
    free(out); free(tmp);
    return ok;
}

#endif
