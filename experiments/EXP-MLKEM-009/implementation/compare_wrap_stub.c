/*
 * Stub counters for unmodified (non-wrap) EXP-MLKEM-009 probes.
 * Never provides __wrap_mlkem_cmp*; wrap-attest must fail on these binaries.
 */
#include <stddef.h>

unsigned long mlkem_wrap_call_count_mlkem_cmp(void) { return 0; }
unsigned long mlkem_wrap_call_count_mlkem_cmp_avx2(void) { return 0; }
unsigned long mlkem_wrap_call_count_mlkem_cmp_neon(void) { return 0; }
void mlkem_wrap_reset_call_counts(void) {}
const char *mlkem_wrap_control_id(void) { return "none"; }
const char *mlkem_wrap_link_method(void) { return "none"; }
