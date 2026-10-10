/* Minimal C shim over libpari for the optional cross-checks. The Rust side passes a GP
   expression as a string and receives its printed value; nothing else of PARI is exposed. */
#include <pari/pari.h>
#include <stdlib.h>
#include <string.h>

static int initialised = 0;

void nfield_pari_init(size_t parisize) {
    if (!initialised) {
        pari_init_opts(parisize, 1000000, INIT_JMPm | INIT_DFTm);
        initialised = 1;
    }
}

/* Evaluate expr; returns a malloc'd string (caller frees with nfield_pari_free) or NULL on a
   PARI error. */
char *nfield_pari_eval(const char *expr) {
    if (!initialised) return NULL;
    pari_sp av = avma;
    char *out = NULL;
    pari_CATCH(CATCH_ALL) {
        out = NULL;
    }
    pari_TRY {
        GEN g = gp_read_str(expr);
        char *s = GENtostr(g);
        out = strdup(s);
        pari_free(s);
    }
    pari_ENDCATCH;
    set_avma(av);
    return out;
}

void nfield_pari_free(char *s) {
    free(s);
}

const char *nfield_pari_version(void) {
    return initialised ? paricfg_version : NULL;
}
