#include "id2iso_tests.h"

static void
random_scalar(ibz_t *k)
{
    ibz_mul_2exp(k, &ibz_const_one, 123);
    ibz_rand_interval(k, &ibz_const_zero, k);
}

int
id2iso_test_ker2id_once(void)
{
    int res = 1;

    ibz_vec_2_t vec2;
    quat_ideal_t I;
    quat_alg_elem_t split;
    quat_alg_elem_init(&split);
    quat_ideal_init(&I);
    ibz_vec_2_init(&vec2);

    do {
        random_scalar(&vec2.v[0]);
        random_scalar(&vec2.v[1]);

    } while (ibz_is_even(&vec2.v[1]) || ibz_is_even(&vec2.v[0]));

    id2iso_kernel_dlogs_to_ideal_even(&I, &split, &vec2, TORSION_EVEN_POWER);

    return res;
}

int
id2iso_test_ker2id(void)
{
    int res = 1;
    printf("\n \nRunning id2iso tests for kernel_dlogs_to_ideal \n \n");

    for (int i = 0; i < 10; i++) {
        res &= id2iso_test_ker2id_once();
    }

    if (!res) {
        printf("ID2ISO unit test kernel_dlogs_to_ideal() failed\n");
    }

    return res;
}
