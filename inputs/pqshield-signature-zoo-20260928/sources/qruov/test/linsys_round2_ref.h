#ifndef LINSYS_ROUND2_REF_H
#define LINSYS_ROUND2_REF_H

#include <stdint.h>

#include "qruov.h"

typedef struct {
    uint8_t *col;
    int original_row_id;
} round2_linsys_row;

typedef struct {
    round2_linsys_row row[QRUOV_m];
    round2_linsys_row *eqn[QRUOV_m];
    int rank;
    int index[QRUOV_m];
} round2_linsys_echelon;

void round2_linsys_lu_decompose(uint8_t *mat, round2_linsys_echelon *echelon);
int round2_linsys_check_consistency(const round2_linsys_echelon *echelon, const uint8_t *b);
void round2_linsys_sample_solution(const round2_linsys_echelon *echelon, const uint8_t *b,
                                   const uint8_t *free_x, uint8_t *x);

#endif // LINSYS_ROUND2_REF_H
