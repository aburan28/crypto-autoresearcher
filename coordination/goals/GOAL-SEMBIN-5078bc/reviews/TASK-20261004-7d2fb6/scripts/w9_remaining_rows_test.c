// w9_remaining_rows_test.c -- joint W9 (1)/(3), function-level only. Does mzd_remaining_rows_in_block (the inline function that upstream commit 34b1b56 changes) return the true
// number of rows left in the physical block for a ROW WINDOW of a multi-block matrix? Compile once against the headers/library of M4RI 0.0.20200125 (Ubuntu) and once against release-20240729.
// This isolates a function-level defect in one release; it does NOT show that this defect is what produced the bad rows at N = 44 (no elimination is run here).
#include <m4ri/m4ri.h>
#include <stdio.h>
int main(void) {
    rci_t ncols = 149986;   /* the window's column count (N = 44): rowstride 2344 words -> blockrows_log = 15, 32768 rows per block */
    rci_t nrows = (rci_t)((1u << 15) + 200);
    mzd_t *M = mzd_init(nrows, ncols);
    int log = M->blockrows_log; long per = 1L << log;
    printf("blockrows_log=%d rows_per_block=%ld multiple_blocks=%d\n", log, per, (M->flags & mzd_flag_multiple_blocks) ? 1 : 0);
    long r0 = per - 50;                                    // window starts 50 rows before the first block boundary
    mzd_t *W = mzd_init_window(M, (rci_t)r0, 0, (rci_t)(r0 + 400), ncols);
    printf("window: row_offset=%d multiple_blocks=%d\n", (int)W->row_offset, (W->flags & mzd_flag_multiple_blocks) ? 1 : 0);
    int bad = 0;
    long rs[] = {0, 10, 49, 50, 60, 399};
    for (unsigned q = 0; q < sizeof rs / sizeof *rs; q++) {
        long r = rs[q]; long phys = r0 + r; long block = phys >> log;
        long expected_to_block_end = ((block + 1) << log) - phys;     // rows from this row to the end of its physical block (parent coordinates)
        long exp_capped = expected_to_block_end < (400 - r) ? expected_to_block_end : (400 - r);
        long got = (long)mzd_remaining_rows_in_block(W, (rci_t)r);
        // M4RI returns the number of rows left in the block, not capped by the window height; compare with the uncapped value
        int ok = (got == expected_to_block_end);
        bad += !ok;
        printf("  window row %3ld (physical %ld, block %ld): function=%ld expected=%ld  %s\n", r, phys, block, got, expected_to_block_end, ok ? "ok" : "WRONG");
    }
    printf("RESULT %s\n", bad ? "function returns wrong counts for windows into a multi-block matrix" : "all counts correct");
    mzd_free(W); mzd_free(M);
    return bad != 0;
}
