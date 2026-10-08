#include <stdio.h>
#include "internal.h"
#include "lll_test_internals.h"

void
ibq_init(ibq_t *x)
{
    ibz_init(&(x->q[0]));
    ibz_init(&(x->q[1]));
    ibz_set(&(x->q[1]), 1, 2);
}

void
ibq_mat_4x4_init(ibq_mat_4x4_t *mat)
{
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibq_init(&mat->m[i].v[j]);
        }
    }
}

void
ibq_vec_4_init(ibq_vec_4_t *vec)
{
    for (int i = 0; i < 4; i++) {
        ibq_init(&vec->v[i]);
    }
}

void
ibq_mat_4x4_print(const ibq_mat_4x4_t *mat)
{
    printf("matrix: ");
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_print(&(mat->m[i].v[j].q[0]), 10);
            printf("/");
            ibz_print(&(mat->m[i].v[j].q[1]), 10);
            printf(" ");
        }
        printf("\n        ");
    }
    printf("\n");
}

void
ibq_vec_4_print(const ibq_vec_4_t *vec)
{
    printf("vector: ");
    for (int i = 0; i < 4; i++) {
        ibz_print(&(vec->v[i].q[0]), 10);
        printf("/");
        ibz_print(&(vec->v[i].q[1]), 10);
        printf(" ");
    }
    printf("\n\n");
}

// Put x in lowest terms with a strictly positive denominator.
void
ibq_reduce(ibq_t *x)
{
    ibz_t gcd, r;
    ibz_init(&gcd);
    ibz_init(&r);

    if (ibz_is_zero(&(x->q[0]))) {
        // 0/d == 0/1; ibz_gcd(0,0) is 0 and would divide by zero below.
        ibz_set(&(x->q[0]), 0, 0);
        ibz_set(&(x->q[1]), 1, 2);
        return;
    }

    ibz_gcd(&gcd, &(x->q[0]), &(x->q[1]));
    // ibz_gcd works on absolute values, so gcd > 0 here and both signs are preserved.
    ibz_div(&(x->q[0]), &r, &(x->q[0]), &gcd);
    assert(ibz_is_zero(&r));
    ibz_div(&(x->q[1]), &r, &(x->q[1]), &gcd);
    assert(ibz_is_zero(&r));

    if (ibz_cmp(&(x->q[1]), &ibz_const_zero) < 0) {
        ibz_neg(&(x->q[0]), &(x->q[0]));
        ibz_neg(&(x->q[1]), &(x->q[1]));
    }

    ibz_set_bound(&x->q[0], ibz_bitsize(&x->q[0]) + 1);
    ibz_set_bound(&x->q[1], ibz_bitsize(&x->q[1]) + 1);
}

void
ibq_denom(ibz_t *denom, const ibq_t *x)
{
    ibz_copy(denom, &(x->q[1]));
}

void
ibq_num(ibz_t *num, const ibq_t *x)
{
    ibz_copy(num, &(x->q[0]));
}

void
ibq_add(ibq_t *sum, const ibq_t *a, const ibq_t *b)
{
    ibz_t add, prod;
    ibz_init(&add);
    ibz_init(&prod);

    ibz_mul(&add, &(a->q[0]), &(b->q[1]));
    ibz_mul(&prod, &(b->q[0]), &(a->q[1]));
    ibz_add(&(sum->q[0]), &add, &prod);
    ibz_mul(&(sum->q[1]), &(a->q[1]), &(b->q[1]));
    ibz_set_bound(&sum->q[0], ibz_bitsize(&sum->q[0]) + 1);
    ibz_set_bound(&sum->q[1], ibz_bitsize(&sum->q[1]) + 1);
    ibq_reduce(sum);
}

void
ibq_neg(ibq_t *neg, const ibq_t *x)
{
    ibz_copy(&(neg->q[1]), &(x->q[1]));
    ibz_neg(&(neg->q[0]), &(x->q[0]));
}

void
ibq_sub(ibq_t *diff, const ibq_t *a, const ibq_t *b)
{
    ibq_t neg;
    ibq_init(&neg);
    ibq_neg(&neg, b);
    ibq_add(diff, a, &neg);
    ibz_set_bound(&diff->q[0], ibz_bitsize(&diff->q[0]) + 1);
    ibz_set_bound(&diff->q[1], ibz_bitsize(&diff->q[1]) + 1);
}

void
ibq_abs(ibq_t *abs, const ibq_t *x) // once
{
    ibq_t neg;
    ibq_init(&neg);
    ibq_neg(&neg, x);
    if (ibq_cmp(x, &neg) < 0)
        ibq_copy(abs, &neg);
    else
        ibq_copy(abs, x);
    ibz_set_bound(&abs->q[0], ibz_bitsize(&abs->q[0]) + 1);
    ibz_set_bound(&abs->q[1], ibz_bitsize(&abs->q[1]) + 1);
}

void
ibq_mul(ibq_t *prod, const ibq_t *a, const ibq_t *b)
{
    ibz_mul(&(prod->q[0]), &(a->q[0]), &(b->q[0]));
    ibz_mul(&(prod->q[1]), &(a->q[1]), &(b->q[1]));
    ibz_set_bound(&prod->q[0], ibz_bitsize(&prod->q[0]) + 1);
    ibz_set_bound(&prod->q[1], ibz_bitsize(&prod->q[1]) + 1);
    ibq_reduce(prod);
}

int
ibq_inv(ibq_t *inv, const ibq_t *x)
{
    int res = !ibq_is_zero(x);
    if (res) {
        ibz_copy(&(inv->q[0]), &(x->q[0]));
        ibz_copy(&(inv->q[1]), &(x->q[1]));
        ibz_swap(&(inv->q[1]), &(inv->q[0]));
        ibz_set_bound(&inv->q[0], ibz_bitsize(&inv->q[0]) + 1);
        ibz_set_bound(&inv->q[1], ibz_bitsize(&inv->q[1]) + 1);
        ibq_reduce(inv);
    }
    return (res);
}

int
ibq_div(ibq_t *frac, const ibq_t *x, const ibq_t *y)
{
    ibq_t tmp;
    ibq_init(&tmp);
    int res = ibq_inv(&tmp, y);
    ibq_mul(frac, x, &tmp);
    return (res);
}

int
ibq_cmp(const ibq_t *a, const ibq_t *b)
{
    ibz_t x, y;
    ibz_init(&x);
    ibz_init(&y);
    ibz_copy(&x, &(a->q[0]));
    ibz_copy(&y, &(b->q[0]));
    ibz_mul(&y, &y, &(a->q[1]));
    ibz_mul(&x, &x, &(b->q[1]));
    if (ibz_cmp(&(a->q[1]), &ibz_const_zero) > 0) {
        ibz_neg(&y, &y);
        ibz_neg(&x, &x);
    }
    if (ibz_cmp(&(b->q[1]), &ibz_const_zero) > 0) {
        ibz_neg(&y, &y);
        ibz_neg(&x, &x);
    }
    int res = ibz_cmp(&x, &y);
    return (res);
}

int
ibq_is_zero(const ibq_t *x)
{
    return (ibz_is_zero(&(x->q[0])));
}

int
ibq_is_one(const ibq_t *x)
{
    return (0 == ibz_cmp(&(x->q[0]), &(x->q[1])));
}

int
ibq_set(ibq_t *q, const ibz_t *a, const ibz_t *b)
{
    ibz_copy(&(q->q[0]), a);
    ibz_copy(&(q->q[1]), b);
    if (ibz_is_zero(b))
        return (0);
    ibq_reduce(q);
    return (1);
}

void
ibq_copy(ibq_t *target, const ibq_t *value) // once
{
    ibz_copy(&(target->q[0]), &(value->q[0]));
    ibz_copy(&(target->q[1]), &(value->q[1]));
    ibz_set_bound(&target->q[0], ibz_bitsize(&target->q[0]) + 1);
    ibz_set_bound(&target->q[1], ibz_bitsize(&target->q[1]) + 1);
}

int
ibq_is_ibz(const ibq_t *q)
{
    ibz_t r;
    ibz_init(&r);
    ibz_mod(&r, &(q->q[0]), &(q->q[1]));
    int res = ibz_is_zero(&r);
    return (res);
}

int
ibq_to_ibz(ibz_t *z, const ibq_t *q)
{
    ibz_t r;
    ibz_init(&r);
    ibz_div(z, &r, &(q->q[0]), &(q->q[1]));
    int res = ibz_is_zero(&r);
    return (res);
}
