#include "quaternion_tests.h"
#include <rng.h>

// void ibz_sum_two_squares(ibz_t *sum, const ibz_t *a, const ibz_t *b;
int
quat_test_ibz_sum_two_squares()
{
    int res = 0;
    ibz_t r, s, t, c;
    ibz_init(&r);
    ibz_init(&s);
    ibz_init(&t);
    ibz_init(&c);
    ibz_set(&r, 2, 3);
    ibz_set(&s, -3, 3);
    ibz_set(&c, 13, 5);
    ibz_sum_two_squares(&t, &s, &r);
    res = res || !(ibz_cmp(&c, &t) == 0);
    ibz_set(&r, 4, 4);
    ibz_set(&s, -3, 3);
    ibz_set(&c, 25, 6);
    ibz_sum_two_squares(&r, &s, &r);
    res = res || !(ibz_cmp(&c, &r) == 0);
    ibz_set(&r, -2, 3);
    ibz_set(&s, 3, 3);
    ibz_set(&c, 13, 5);
    ibz_sum_two_squares(&s, &s, &r);
    res = res || !(ibz_cmp(&c, &s) == 0);

    if (res) {
        printf("Quaternion unit test ibz_sum_two_squares failed\n");
    }
    return (res);
}

// void ibz_rounded_div(ibz_t *q, const ibz_t *a, const ibz_t *b);
int
quat_test_ibz_rounded_div()
{
    int res = 0;
    ibz_t q, a, b;
    ibz_init(&a);
    ibz_init(&b);
    ibz_init(&q);

    // basic tests
    ibz_set(&a, 15, 5);
    ibz_set(&b, 3, 3);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 5);
    ibz_set(&a, 16, 6);
    ibz_set(&b, 3, 3);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 5);
    ibz_set(&a, 17, 6);
    ibz_set(&b, 3, 3);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 6);
    ibz_set(&a, 37, 7);
    ibz_set(&b, 5, 4);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 7);
    // test sign combination
    ibz_set(&a, 149, 9);
    ibz_set(&b, 12, 5);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 12);
    ibz_set(&a, 149, 9);
    ibz_set(&b, -12, 5);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == -12);
    ibz_set(&a, -149, 9);
    ibz_set(&b, -12, 5);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 12);
    ibz_set(&a, -149, 9);
    ibz_set(&b, 12, 5);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == -12);
    ibz_set(&a, 151, 9);
    ibz_set(&b, 12, 5);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 13);
    ibz_set(&a, -151, 9);
    ibz_set(&b, -12, 5);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 13);
    ibz_set(&a, 151, 9);
    ibz_set(&b, -12, 5);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == -13);
    ibz_set(&a, -151, 9);
    ibz_set(&b, 12, 5);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == -13);
    // divisibles with sign
    ibz_set(&a, 144, 9);
    ibz_set(&b, 12, 5);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 12);
    ibz_set(&a, -144, 9);
    ibz_set(&b, -12, 5);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 12);
    ibz_set(&a, 144, 9);
    ibz_set(&b, -12, 5);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == -12);
    ibz_set(&a, -144, 9);
    ibz_set(&b, 12, 5);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == -12);
    // tests close to 0
    ibz_set(&a, -12, 5);
    ibz_set(&b, -25, 6);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 0);
    ibz_set(&a, 12, 5);
    ibz_set(&b, 25, 6);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 0);
    ibz_set(&a, -12, 5);
    ibz_set(&b, 25, 6);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 0);
    ibz_set(&a, 12, 5);
    ibz_set(&b, -25, 6);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 0);
    ibz_set(&a, -12, 5);
    ibz_set(&b, -23, 6);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 1);
    ibz_set(&a, 12, 5);
    ibz_set(&b, 23, 6);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == 1);
    ibz_set(&a, -12, 5);
    ibz_set(&b, 23, 6);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == -1);
    ibz_set(&a, 12, 5);
    ibz_set(&b, -23, 6);
    ibz_rounded_div(&q, &a, &b);
    res = res || !(ibz_get(&q) == -1);
    // test output equal input
    ibz_set(&a, -151, 9);
    ibz_set(&b, 12, 5);
    ibz_rounded_div(&a, &a, &b);
    res = res || !(ibz_get(&a) == -13);
    ibz_set(&a, -151, 9);
    ibz_set(&b, 12, 5);
    ibz_rounded_div(&b, &a, &b);
    res = res || !(ibz_get(&b) == -13);

    if (res != 0) {
        printf("Quaternion unit test integer_ibz_rounded_div failed\n");
    }
    return (res);
}

// int ibz_generate_random_prime(ibz_t *p, int is3mod4, int bitsize);
int
quat_test_ibz_generate_random_prime()
{
    int res = 0;
    int bitsize, is3mod4;
    ibz_t p;
    ibz_init(&p);
    bitsize = 20;
    is3mod4 = 1;
    res = res || !ibz_generate_random_prime(&p, is3mod4, bitsize);
    res = res || (ibz_probab_prime(&p, 20) == 0);
    res = res || (ibz_bitsize(&p) < bitsize);
    res = res || (is3mod4 && (ibz_get(&p) % 4 != 3));
    bitsize = 30;
    is3mod4 = 0;
    res = res || !ibz_generate_random_prime(&p, is3mod4, bitsize);
    res = res || (ibz_probab_prime(&p, 20) == 0);
    res = res || (ibz_bitsize(&p) < bitsize);
    res = res || (is3mod4 && (ibz_get(&p) % 4 != 3));
    is3mod4 = 1;
    res = res || !ibz_generate_random_prime(&p, is3mod4, bitsize);
    res = res || (ibz_probab_prime(&p, 20) == 0);
    res = res || (ibz_bitsize(&p) < bitsize);
    res = res || (is3mod4 && (ibz_get(&p) % 4 != 3));
    if (res) {
        printf("Quaternion unit test ibz_generate_random_prime failed\n");
    }
    return (res);
}

// int ibz_cornacchia_prime(ibz_t *x, ibz_t *y, const ibz_t *n, const ibz_t *p);
int
quat_test_integer_ibz_cornacchia_prime(void)
{
    int res = 0;
    ibz_t x, y, prod, c_res, p;
    ibz_init(&x);
    ibz_init(&y);
    ibz_init(&p);
    ibz_init(&prod);
    ibz_init(&c_res);

    // there is a solution in these cases
    ibz_set(&p, 1, 2);
    res = 0;
    if (ibz_cornacchia_prime(&x, &y, &p)) {
        res = res || !(ibz_cmp(&x, &y) <= 0);
        res = res || !(ibz_is_positive(&x));
        ibz_mul(&c_res, &x, &x);
        ibz_mul(&prod, &y, &y);
        ibz_add(&c_res, &c_res, &prod);
        res = res || ibz_cmp(&p, &c_res);
    } else {
        res = 1;
    }
    ibz_set(&p, 2, 3);
    res = 0;
    if (ibz_cornacchia_prime(&x, &y, &p)) {
        res = res || !(ibz_cmp(&x, &y) <= 0);
        res = res || !(ibz_is_positive(&x));
        ibz_mul(&c_res, &x, &x);
        ibz_mul(&prod, &y, &y);
        ibz_add(&c_res, &c_res, &prod);
        res = res || ibz_cmp(&p, &c_res);
    } else {
        res = 1;
    }
    ibz_set(&p, 5, 4);
    if (ibz_cornacchia_prime(&x, &y, &p)) {
        res = res || !(ibz_cmp(&x, &y) <= 0);
        res = res || !(ibz_is_positive(&x));
        ibz_mul(&c_res, &x, &x);
        ibz_mul(&prod, &y, &y);
        ibz_add(&c_res, &c_res, &prod);
        res = res || ibz_cmp(&p, &c_res);
    } else {
        res = 1;
    }
    ibz_set(&p, 2, 3);
    if (ibz_cornacchia_prime(&x, &y, &p)) {
        res = res || !(ibz_cmp(&x, &y) <= 0);
        res = res || !(ibz_is_positive(&x));
        ibz_mul(&c_res, &x, &x);
        ibz_mul(&prod, &y, &y);
        ibz_add(&c_res, &c_res, &prod);
        res = res || ibz_cmp(&p, &c_res);
    } else {
        res = 1;
    }
    ibz_set(&p, 41, 7);
    if (ibz_cornacchia_prime(&x, &y, &p)) {
        res = res || !(ibz_cmp(&x, &y) <= 0);
        res = res || !(ibz_is_positive(&x));
        ibz_mul(&c_res, &x, &x);
        ibz_mul(&prod, &y, &y);
        ibz_add(&c_res, &c_res, &prod);
        res = res || ibz_cmp(&p, &c_res);
    } else {
        res = 1;
    }
    // there is no solution in these cases
    ibz_set(&p, 7, 4);
    res = res || ibz_cornacchia_prime(&x, &y, &p);
    ibz_set(&p, 3, 3);
    res = res || ibz_cornacchia_prime(&x, &y, &p);

    if (res != 0) {
        printf("Quaternion unit test integer_ibz_cornacchia_prime failed\n");
    }
    return (res);
}

// int ibz_cornacchia_prime(ibz_t *x, ibz_t *y, const ibz_t *n, const ibz_t *p);
int
quat_test_randomized_ibz_cornacchia_prime(int bitsize, int n_bound, int iterations)
{
    (void)n_bound;
    int res = 0;
    ibz_t x, y, prod, c_res, p;
    int randret = 0;
    ibz_init(&x);
    ibz_init(&y);
    ibz_init(&p);
    ibz_init(&prod);
    ibz_init(&c_res);
    for (int iter = 0; iter < iterations; iter++) {
        randret = randret | !ibz_generate_random_prime(&p, 0, bitsize);
        if (randret != 0) {
            printf("Randomness failed in quaternion unit test with randomization for "
                   "ibz_cornacchia_prime\n");
            res = 1;
            break;
        }
        // If the legendre symbol is ok, Cornacchia should sometimes be able to solve
        if ((ibz_get(&p) & 3) == 1) {
            //  If there is output, check the output is correct
            if (ibz_cornacchia_prime(&x, &y, &p)) {
                res = res || !(ibz_cmp(&x, &y) <= 0);
                res = res || !(ibz_is_positive(&x));
                ibz_mul(&c_res, &x, &x);
                ibz_mul(&prod, &y, &y);
                ibz_add(&c_res, &c_res, &prod);
                res = res || (0 != ibz_cmp(&p, &c_res));
            }
        } else {
            // Otherwise Cornacchia should fail
            res = res || (ibz_cornacchia_prime(&x, &y, &p));
        }
    }
    if (res != 0) {
        printf("Quaternion unit test with randomization for ibz_cornacchia_prime failed\n");
    }
    return (res);
}

// run all previous tests
int
quat_test_integers(void)
{
    int res = 0;
    printf("\nRunning quaternion tests of integer functions\n");
    res = res | quat_test_ibz_sum_two_squares();
    res = res | quat_test_ibz_rounded_div();
    res = res | quat_test_ibz_generate_random_prime();
    res = res | quat_test_integer_ibz_cornacchia_prime();
    res = res | quat_test_randomized_ibz_cornacchia_prime(128, 6, 10);
    return (res);
}
