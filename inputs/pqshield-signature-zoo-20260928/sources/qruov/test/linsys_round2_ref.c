#include <string.h>

#include "gf.h"
#include "linsys_round2_ref.h"

#define ROUND2_EQN(E, I, J) ((E)->eqn[(I)]->col[(J)])

/* Round 2 reference linear-algebra routines used by regression tests. */

static void round2_echelon_init(uint8_t *mat, round2_linsys_echelon *echelon)
{
    for (int i = 0; i < QRUOV_m; i++) {
        echelon->row[i].col = &mat[i * QRUOV_m];
        echelon->row[i].original_row_id = i;
        echelon->eqn[i] = echelon->row + i;
    }
    echelon->rank = 0;
    memset(echelon->index, 0xff, sizeof(echelon->index));
}

static void round2_row_swap(round2_linsys_row *eqn[QRUOV_m], int i, int j)
{
    round2_linsys_row *tmp = eqn[i];
    eqn[i] = eqn[j];
    eqn[j] = tmp;
}

void round2_linsys_lu_decompose(uint8_t *mat, round2_linsys_echelon *echelon)
{
    round2_echelon_init(mat, echelon);

    int c = -1;
    for (int i = 0; i < QRUOV_m; i++) {
        c++;
        if (c >= QRUOV_m) return;

        int j = i;
        while (ROUND2_EQN(echelon, j, c) == 0) {
            j++;
            if (j >= QRUOV_m) {
                c++;
                if (c >= QRUOV_m) return;
                j = i;
            }
        }

        round2_row_swap(echelon->eqn, i, j);
        echelon->index[echelon->rank++] = c;

        uint8_t pivot = ROUND2_EQN(echelon, i, c);
        uint8_t inv = gf_inv(pivot);

        ROUND2_EQN(echelon, i, i) = pivot;
        for (int k = c + 1; k < QRUOV_m; k++) {
            ROUND2_EQN(echelon, i, k) = gf_mul(inv, ROUND2_EQN(echelon, i, k));
        }

        for (int r = i + 1; r < QRUOV_m; r++) {
            uint8_t mul = ROUND2_EQN(echelon, r, c);
            ROUND2_EQN(echelon, r, i) = mul;
            for (int k = c + 1; k < QRUOV_m; k++) {
                ROUND2_EQN(echelon, r, k) =
                    gf_sub(ROUND2_EQN(echelon, r, k),
                           gf_mul(mul, ROUND2_EQN(echelon, i, k)));
            }
        }
    }
}

static void round2_identity(uint8_t *mat)
{
    memset(mat, 0, QRUOV_m * QRUOV_m);
    for (int i = 0; i < QRUOV_m; i++) {
        mat[i * QRUOV_m + i] = 1;
    }
}

static void round2_l_inverse(const round2_linsys_echelon *echelon, uint8_t *r)
{
    round2_identity(r);

    for (int i = 0; i < echelon->rank; i++) {
        uint8_t pivot = ROUND2_EQN(echelon, i, i);
        uint8_t inv = gf_inv(pivot);
        for (int k = 0; k <= i; k++) {
            r[i * QRUOV_m + k] = gf_mul(r[i * QRUOV_m + k], inv);
        }
        for (int j = i + 1; j < QRUOV_m; j++) {
            for (int k = 0; k <= i; k++) {
                r[j * QRUOV_m + k] = gf_sub(r[j * QRUOV_m + k],
                                            gf_mul(ROUND2_EQN(echelon, j, i),
                                                   r[i * QRUOV_m + k]));
            }
        }
    }
}

int round2_linsys_check_consistency(const round2_linsys_echelon *echelon, const uint8_t *b)
{
    if (echelon->rank == QRUOV_m) return 1;

    uint8_t r[QRUOV_m * QRUOV_m];
    round2_l_inverse(echelon, r);

    for (int i = echelon->rank; i < QRUOV_m; i++) {
        uint64_t acc = 0;
        for (int j = 0; j < echelon->rank; j++) {
            int k = echelon->eqn[j]->original_row_id;
            acc += (uint64_t)r[i * QRUOV_m + j] * b[k];
        }
        int k = echelon->eqn[i]->original_row_id;
        acc += (uint64_t)r[i * QRUOV_m + i] * b[k];
        if ((acc % QRUOV_q) != 0) return 0;
    }

    return 1;
}

void round2_linsys_sample_solution(const round2_linsys_echelon *echelon, const uint8_t *b,
                                   const uint8_t *free_x, uint8_t *x)
{
    uint8_t b2[QRUOV_m];
    memset(b2, 0, sizeof(b2));

    for (int i = 0; i < echelon->rank; i++) {
        uint64_t acc = 0;
        for (int j = 0; j < i; j++) {
            acc += (uint64_t)ROUND2_EQN(echelon, i, j) * b2[j];
        }
        int row_id = echelon->eqn[i]->original_row_id;
        uint8_t tmp = gf_sub(b[row_id], (uint8_t)(acc % QRUOV_q));
        b2[i] = gf_mul(tmp, gf_inv(ROUND2_EQN(echelon, i, i)));
    }

    int i = QRUOV_m - 1;
    int free_pos = 0;
    for (int j = echelon->rank - 1; j >= 0; j--) {
        int pivot_col = echelon->index[j];
        for (; i > pivot_col; i--) {
            x[i] = free_x[free_pos++];
        }

        uint64_t acc = 0;
        for (int k = pivot_col + 1; k < QRUOV_m; k++) {
            acc += (uint64_t)ROUND2_EQN(echelon, j, k) * x[k];
        }
        x[i] = gf_sub(b2[j], (uint8_t)(acc % QRUOV_q));
        i--;
    }

    for (; i >= 0; i--) {
        x[i] = free_x[free_pos++];
    }
}
