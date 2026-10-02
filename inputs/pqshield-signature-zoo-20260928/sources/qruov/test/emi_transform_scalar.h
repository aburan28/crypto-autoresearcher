#ifndef EMI_TRANSFORM_SCALAR_H
#define EMI_TRANSFORM_SCALAR_H

#include "qruov.h"

static inline void emi_transform_apply_scalar(uint8_t *output, int plane_out,
                                              const uint8_t *input, int plane_in,
                                              int size, const int *mat,
                                              int rows, int cols)
{
    for (int i = 0; i < size; i++) {
        for (int r = 0; r < rows; r++) {
            int val = 0;
            for (int c = 0; c < cols; c++) {
                val += mat[r * cols + c] * input[c * plane_in + i];
            }
            output[r * plane_out + i] = (uint8_t)(val % QRUOV_q);
        }
    }
}

#endif // EMI_TRANSFORM_SCALAR_H
