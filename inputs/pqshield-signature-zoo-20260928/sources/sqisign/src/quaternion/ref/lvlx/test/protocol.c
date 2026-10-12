#include <stdio.h>
#include <internal.h>
#include <prng.h>
#include "quaternion_tests.h"
#include <quaternion_data.h>
#include <quaternion_constants.h>
#include <encoded_sizes.h>

// void quat_response_element(quat_ideal_t *resp_ideal, quat_alg_elem_t *resp_quat, quat_alg_elem_t
// *resp_split, uint8_t back_and_even_deg, const quat_ideal_t *skideal, const quat_ideal_t *ideal_chall_two,
// const quat_ideal_t *ideal_commit, prng_domain_ctx_t *prng_domain, int e);
int
quat_test_protocol_response_element()
{
    int res = 0;
    int ret = 0;
    int e = RESPONSE_BITS - 1;
    int chall_len = CHALLENGE_BITS;
    quat_lattice_t lat;
    quat_ideal_t ideal_skchall, ideal_sk, ideal_chall, ideal_com;
    quat_alg_elem_t resp_quat, gen, gen_tmp;
    ibz_t p, tmp, n, d;
    ibz_init(&p);
    ibz_init(&tmp);
    ibz_init(&n);
    ibz_init(&d);
    quat_alg_elem_init(&gen);
    quat_alg_elem_init(&gen_tmp);
    quat_alg_elem_init(&resp_quat);
    quat_lattice_init(&lat);
    quat_ideal_init(&ideal_skchall);
    quat_ideal_init(&ideal_chall);
    quat_ideal_init(&ideal_sk);
    quat_ideal_init(&ideal_com);
    quat_lattice_O0_set(&lat);

    for (int i = 0; i < 10; i++) {
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p) / 2);
        ret = ret || !quat_random_ideal_O0_given_prime_norm(&ideal_sk, &p, &PRNG_default_domain);
        ret = ret || !quat_random_ideal_O0_given_prime_norm(&ideal_com, &p, &PRNG_default_domain);
        if (ret) {
            printf("Ideal sampling failed\n");
            return (res);
        }
        // sample random challenge?
        ibz_mul_2exp(&n, &ibz_const_one, chall_len);
        quat_alg_elem_set(&gen, 1, 0, 0, 0, 0);
        while (quat_alg_elem_is_zero(&gen)) {
            ibz_rand_interval_bits(&tmp, ibz_bitsize(&QUATALG_PINFTY.p) + 48 - chall_len - 1);
            ibz_add(&tmp, &tmp, &tmp);
            ibz_add(&tmp, &tmp, &ibz_const_one);
            ibz_abs(&tmp, &tmp);
            ibz_mul(&tmp, &tmp, &n);
            quat_represent_integer_even(&gen, &tmp);
            if (!quat_ideal_create_O0_pow_two(&ideal_chall, &gen, &n)) {
                quat_alg_elem_set(&gen, 1, 0, 0, 0, 0);
            }
        }
        quat_alg_elem_set(&gen, 1, 1, 0, 0, 0);
        quat_response_element(
            &ideal_skchall, &resp_quat, &n, NULL, &ideal_sk, &ideal_chall, &gen, &ideal_com, &PRNG_default_domain, e);

        res = res || (ibz_bitsize(&n) > e);

        // test suitable norm
        // quat_alg_elem_print(&resp_quat);

        quat_alg_norm(&tmp, &d, &resp_quat, &QUATALG_PINFTY);
        // ibz_print(&tmp, 10);
        // printf("\n");
        res = res || !ibz_is_one(&d);
        ibz_mul(&n, &n, &ideal_skchall.norm);
        ibz_mul(&n, &n, &ideal_com.norm);
        res = res || (ibz_cmp(&n, &tmp) != 0);

        // test that quat_resp is in ideal_com and the conjugate of ideal_skchall
        quat_to_lattice(&lat, &ideal_com);
        res = res || !(quat_lattice_contains(&gen.coord, &lat, &resp_quat));

        quat_to_lattice(&lat, &ideal_skchall);
        quat_alg_conj(&resp_quat, &resp_quat);
        res = res || !(quat_lattice_contains(&gen.coord, &lat, &resp_quat));

        // test that ideal_skchall is equivalent to sk inter chall
        quat_ideal_intersect_O0(&ideal_sk, &ideal_chall, &ideal_sk, NULL);
        res = res || !quat_ideals_equivalence(&ideal_sk, &ideal_skchall);
    }

    if (res) {
        printf("Quaternion unit test protocol_response_element failed\n");
    }
    return (res);
}

int
quat_test_protocol_response_element_kat_stability()
{
    int res = 0;
    int ret = 0;
    int e = RESPONSE_BITS - 1;
    int chall_len = CHALLENGE_BITS;
    quat_ideal_t ideal_skchall, ideal_sk, ideal_chall, ideal_com, ideal_com_s, ideal_com1, ideal_com2, ideal_skchall1,
        ideal_skchall2, aux, aux1, aux2, cr, cr2, cp, cp1, cp2;
    quat_alg_elem_t resp_quat, gen, gen_tmp, resp_quat1, resp_quat2, skchall, skchall1, skchall2, split, split1, split2,
        s, s2;
    prng_domain_ctx_t com, resp, com1, resp1, com2, resp2;

    ibz_t p, tmp, n, n1, n2, d, aux_norm, twoe;
    ibz_init(&p);
    ibz_init(&tmp);
    ibz_init(&n);
    ibz_init(&n1);
    ibz_init(&n2);
    ibz_init(&d);
    ibz_init(&aux_norm);
    ibz_init(&twoe);
    quat_alg_elem_init(&gen);
    quat_alg_elem_init(&gen_tmp);
    quat_alg_elem_init(&resp_quat);
    quat_alg_elem_init(&resp_quat1);
    quat_alg_elem_init(&resp_quat2);
    quat_alg_elem_init(&skchall);
    quat_alg_elem_init(&skchall1);
    quat_alg_elem_init(&skchall2);
    quat_alg_elem_init(&split);
    quat_alg_elem_init(&split1);
    quat_alg_elem_init(&split2);
    quat_alg_elem_init(&s);
    quat_alg_elem_init(&s2);
    quat_ideal_init(&ideal_skchall);
    quat_ideal_init(&ideal_skchall1);
    quat_ideal_init(&ideal_skchall2);
    quat_ideal_init(&ideal_chall);
    quat_ideal_init(&ideal_sk);
    quat_ideal_init(&ideal_com_s);
    quat_ideal_init(&ideal_com);
    quat_ideal_init(&ideal_com1);
    quat_ideal_init(&ideal_com2);
    quat_ideal_init(&aux);
    quat_ideal_init(&aux1);
    quat_ideal_init(&aux2);
    quat_ideal_init(&cp);
    quat_ideal_init(&cp1);
    quat_ideal_init(&cp2);
    quat_ideal_init(&cr);
    quat_ideal_init(&cr2);

    prng_domain_seed(&com, "cmt");
    prng_domain_seed(&resp, "res");
    prng_domain_seed(&com1, "cmi");
    prng_domain_seed(&resp1, "res");
    prng_domain_seed(&com2, "cmt");
    prng_domain_seed(&resp2, "res");

    // check randomness behaves as expected
    ibz_rand_interval_minm_m_with_domain(&n, 200, &resp);
    ibz_rand_interval_minm_m_with_domain(&n1, 200, &resp1);
    ibz_rand_interval_minm_m_with_domain(&n2, 200, &resp2);
    assert(ibz_cmp(&n, &n1) == 0);
    assert(ibz_cmp(&n, &n2) == 0);
    ibz_rand_interval_minm_m_with_domain(&n, 200, &com);
    ibz_rand_interval_minm_m_with_domain(&n1, 200, &com1);
    ibz_rand_interval_minm_m_with_domain(&n2, 200, &com2);
    // assert(ibz_cmp(&n, &n1) != 0); // fails in 1/200 cases
    assert(ibz_cmp(&n, &n2) == 0);

    ibz_mul_2exp(&twoe, &ibz_const_one, RESPONSE_BITS);

    for (int i = 0; i < 10; i++) {
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p) * 2 - 50);
        ret = ret || !quat_random_ideal_O0_given_prime_norm(&ideal_sk, &p, &PRNG_default_domain);
        ret = ret || !quat_random_ideal_O0_given_prime_norm(&ideal_com_s, &p, &PRNG_default_domain);
        if (ret) {
            printf("Ideal sampling failed\n");
            goto fin;
        }
        // sample random challenge?
        ibz_mul_2exp(&n, &ibz_const_one, chall_len);
        quat_alg_elem_set(&gen, 1, 0, 0, 0, 0);
        while (quat_alg_elem_is_zero(&gen)) {
            ibz_rand_interval_bits(&tmp, ibz_bitsize(&QUATALG_PINFTY.p) + 48 - chall_len - 1);
            ibz_add(&tmp, &tmp, &tmp);
            ibz_add(&tmp, &tmp, &ibz_const_one);
            ibz_abs(&tmp, &tmp);
            ibz_mul(&tmp, &tmp, &n);
            quat_represent_integer_even(&gen, &tmp);
            if (!quat_ideal_create_O0_pow_two(&ideal_chall, &gen, &n)) {
                quat_alg_elem_set(&gen, 1, 0, 0, 0, 0);
            }
        }
        quat_alg_elem_set(&gen, 1, 1, 0, 0, 0);
        quat_ideal_small_equivalent_coprime(NULL, &ideal_sk, &ideal_sk, &ibz_const_zero, &PRNG_default_domain);

        // follow the sign implementation
        quat_ideal_small_equivalent_coprime(NULL, &ideal_com, &ideal_com_s, &ibz_const_zero, &com);
        quat_response_element(
            &ideal_skchall, &resp_quat, &n, &skchall, &ideal_sk, &ideal_chall, &gen, &ideal_com, &resp, e);
        ibz_sub(&aux_norm, &twoe, &n);
        ibz_set_bound(&aux_norm, RESPONSE_BITS + 1);
        quat_random_ideal_O0_given_arbitrary_odd_norm(&aux, &split, &aux_norm, &skchall, &resp);

        // vary com  equivalence randomness (skchall varies by itself since it reuses default)
        quat_ideal_small_equivalent_coprime(NULL, &ideal_com1, &ideal_com_s, &ibz_const_zero, &com1);
        quat_response_element(
            &ideal_skchall1, &resp_quat1, &n1, &skchall1, &ideal_sk, &ideal_chall, &gen, &ideal_com1, &resp1, e);
        ibz_sub(&aux_norm, &twoe, &n1);
        ibz_set_bound(&aux_norm, RESPONSE_BITS + 1);
        quat_random_ideal_O0_given_arbitrary_odd_norm(&aux1, &split1, &aux_norm, &skchall1, &resp1);

        // only modify skchall equivalence
        quat_ideal_small_equivalent_coprime(NULL, &ideal_com2, &ideal_com_s, &ibz_const_zero, &com2);
        quat_response_element(
            &ideal_skchall2, &resp_quat2, &n2, &skchall2, &ideal_sk, &ideal_chall, &gen, &ideal_com2, &resp2, e);
        ibz_sub(&aux_norm, &twoe, &n2);
        ibz_set_bound(&aux_norm, RESPONSE_BITS + 1);
        quat_random_ideal_O0_given_arbitrary_odd_norm(&aux2, &split2, &aux_norm, &skchall2, &resp2);

        // should be equivalent for same chall+equivalent com
        quat_ideal_intersect_O0(&cp, &aux, &ideal_skchall, &split);
        quat_ideal_intersect_O0(&cp2, &aux2, &ideal_skchall2, &split2);
        quat_ideal_intersect_O0(&cp1, &aux1, &ideal_skchall1, &split1);

        res = res || !quat_ideals_equivalence(&cp, &cp2);
        res = res || !quat_ideals_equivalence(&cp, &cp1);
    }

fin:;
    prng_domain_clear(&com);
    prng_domain_clear(&resp);
    prng_domain_clear(&com1);
    prng_domain_clear(&resp1);
    prng_domain_clear(&com2);
    prng_domain_clear(&resp2);
    if (res) {
        printf("Quaternion unit test protocol_response_element_kat_stability failed\n");
    }
    return (res);
}

// void quat_response_element(quat_ideal_t *resp_ideal, quat_alg_elem_t *resp_quat, quat_alg_elem_t
// *resp_split, uint8_t back_and_even_deg, const quat_ideal_t *skideal, const quat_ideal_t *ideal_chall_two,
// const quat_ideal_t *ideal_commit prng_domain_ctx_t *prng_domain, int e);
int
quat_test_protocol_response_element_loop()
{
    int res = 0;
    int ret = 0;
    int e = RESPONSE_BITS - 1;
    int chall_len = CHALLENGE_BITS;
    quat_lattice_t lat;
    quat_ideal_t resp_ideal, ideal_skchall, ideal_sk, ideal_chall, ideal_com;
    quat_alg_elem_t resp_quat, gen, gen_tmp, split;
    ibz_t p, tmp, n, d, norm;
    ibz_init(&p);
    ibz_init(&tmp);
    ibz_init(&n);
    ibz_init(&norm);
    ibz_init(&d);
    quat_alg_elem_init(&gen);
    quat_alg_elem_init(&split);
    quat_alg_elem_init(&gen_tmp);
    quat_alg_elem_init(&resp_quat);
    quat_lattice_init(&lat);
    quat_ideal_init(&ideal_skchall);
    quat_ideal_init(&resp_ideal);
    quat_ideal_init(&ideal_chall);
    quat_ideal_init(&ideal_sk);
    quat_ideal_init(&ideal_com);
    quat_lattice_O0_set(&lat);

    for (int i = 0; i < 10; i++) {
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p) / 2);
        ret = ret || !quat_random_ideal_O0_given_prime_norm(&ideal_sk, &p, &PRNG_default_domain);
        ret = ret || !quat_random_ideal_O0_given_prime_norm(&ideal_com, &p, &PRNG_default_domain);
        if (ret) {
            printf("Ideal sampling failed\n");
            return (res);
        }
        // sample random challenge?
        ibz_mul_2exp(&n, &ibz_const_one, chall_len);
        quat_alg_elem_set(&gen, 1, 0, 0, 0, 0);
        // Needed because of some RI bug to investiagte
        while (quat_alg_elem_is_zero(&gen)) {
            ibz_rand_interval_bits(&tmp, ibz_bitsize(&QUATALG_PINFTY.p) + 48 - chall_len - 1);
            ibz_add(&tmp, &tmp, &tmp);
            ibz_add(&tmp, &tmp, &ibz_const_one);
            ibz_abs(&tmp, &tmp);
            ibz_mul(&tmp, &tmp, &n);
            quat_represent_integer_even(&gen, &tmp);
            if (!quat_ideal_create_O0_pow_two(&ideal_chall, &gen, &n)) {
                quat_alg_elem_set(&gen, 1, 0, 0, 0, 0);
            }
        }
        quat_alg_elem_set(&gen, 1, 1, 0, 0, 0);
        quat_response_element(&ideal_skchall,
                              &resp_quat,
                              &norm,
                              NULL,
                              &ideal_sk,
                              &ideal_chall,
                              &gen,
                              &ideal_com,
                              &PRNG_default_domain,
                              e);

        res = res || (ibz_bitsize(&n) > e);

        // test suitable norm
        quat_alg_norm(&tmp, &d, &resp_quat, &QUATALG_PINFTY);
        res = res || !ibz_is_one(&d);
        ibz_mul(&n, &norm, &ideal_skchall.norm);
        ibz_mul(&n, &n, &ideal_com.norm);
        res = res || (ibz_cmp(&n, &tmp) != 0);

        // test that quat_resp is in ideal_com and the conjugate of ideal_skchall
        quat_to_lattice(&lat, &ideal_com);
        res = res || !(quat_lattice_contains(&gen.coord, &lat, &resp_quat));

        quat_to_lattice(&lat, &ideal_skchall);
        quat_alg_conj(&resp_quat, &resp_quat);
        res = res || !(quat_lattice_contains(&gen.coord, &lat, &resp_quat));

        // test that ideal_skchall is equivalent to sk inter chall
        quat_ideal_intersect_O0(&ideal_sk, &ideal_chall, &ideal_sk, NULL);
        res = res || !quat_ideals_equivalence(&ideal_sk, &ideal_skchall);

        quat_lattice_O0_set(&lat);
        quat_alg_make_primitive(&resp_quat.coord, &tmp, &resp_quat, &lat);
        ibz_mat_4x4_eval(&resp_quat.coord, &lat.basis, &resp_quat.coord);
        ibz_copy(&resp_quat.denom, &lat.denom);
        ibz_gcd(&tmp, &tmp, &norm);
        ibz_mul(&tmp, &tmp, &tmp);
        ibz_div(&norm, &tmp, &norm, &tmp);
        res = res || !ibz_is_zero(&tmp);
        quat_alg_conj(&resp_quat, &resp_quat);
        quat_ideal_create_O0_odd(&resp_ideal, &split, &resp_quat, &norm);
        quat_ideal_intersect_O0(&resp_ideal, &resp_ideal, &ideal_com, &split);
        res = res || !quat_ideals_equivalence(&resp_ideal, &ideal_skchall);
    }

    if (res) {
        printf("Quaternion unit test response_element_loop failed\n");
    }
    return (res);
}

// run all previous tests
int
quat_test_protocol(void)
{
    int res = 0;
    printf("\nRunning tests for quaternion protocol functions\n");
    res = res | quat_test_protocol_response_element();
    res = res | quat_test_protocol_response_element_kat_stability();
    res = res | quat_test_protocol_response_element_loop();
    return (res);
}
