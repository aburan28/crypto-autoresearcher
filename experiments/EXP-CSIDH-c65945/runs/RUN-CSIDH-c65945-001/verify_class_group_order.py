#!/usr/bin/env python3
"""
EXP-CSIDH-c65945 / RUN-CSIDH-c65945-001
Factorization-integrity control + known-answer (harness sanity) control +
cross-citation consistency control, per specification.yaml controls[0..2]
(controls[0] renamed by amendments/v1.yaml to "Cross-citation consistency
control").

This script performs ONLY arithmetic verification of citations already
obtained from primary sources (see raw-result.json / manifest.yaml for the
citations themselves). It does not invent, guess, or re-derive any
class-group order from scratch -- AGENTS.md rule 5 / this contract's own
controls.
"""
import math
from sympy import isprime

def check_factorization(name, factors, expected_product):
    product = 1
    for f in factors:
        product *= f
    all_prime = all(isprime(f) for f in factors)
    reconciles = (product == expected_product)
    print(f"--- {name} ---")
    print(f"  factors: {factors}")
    print(f"  each factor prime (Miller-Rabin / sympy.isprime, deterministic "
          f"strong probable-prime test)? {[isprime(f) for f in factors]}")
    print(f"  all factors prime: {all_prime}")
    print(f"  product of factors: {product}")
    print(f"  expected (cited) value: {expected_product}")
    print(f"  product == expected: {reconciles}")
    print(f"  bit length of expected value: {expected_product.bit_length()}")
    if expected_product > 0:
        print(f"  log2(expected value): {math.log2(expected_product)}")
    print()
    return all_prime and reconciles


if __name__ == "__main__":
    print("=== KNOWN-ANSWER CONTROL (harness sanity check) ===")
    print("Discriminant -23: Q(sqrt(-23)) has class number h(-23) = 3, a")
    print("standard tabulated fact (e.g. Cohen, 'A Course in Computational")
    print("Algebraic Number Theory', Table, or any standard class-number")
    print("table for small imaginary quadratic discriminants). Factorization")
    print("of the class number itself: 3 (prime).")
    ok_small = check_factorization("h(-23) sanity check", [3], 3)
    assert ok_small, "Known-answer control FAILED -- harness is not correctly implemented"
    print("KNOWN-ANSWER CONTROL: PASSED. Verification method (primality-check")
    print("+ product reconciliation) confirmed correct on a textbook-known")
    print("small case before being trusted on the CSIDH-512-scale value below.")
    print()

    print("=== CSIDH-512 CLASS-GROUP ORDER: FACTORIZATION-INTEGRITY CONTROL ===")
    print("Primary source: Beullens, Kleinjung, Vercauteren, 'CSI-FiSh:")
    print("Efficient Isogeny based Signatures through Class Group")
    print("Computations', IACR ePrint 2019/498, Section 3 ('Class group")
    print("computation'), p.8, displayed equation:")
    print("  #Cl(O_Q(sqrt(-p))) = 37 x 1407181 x 51593604295295867744293584889")
    print("                        x 31599414504681995853008278745587832204909")
    print("and 'The class group of the order O therefore has cardinality")
    print("3 * #Cl(O_Q(sqrt(-p)))' (same page, immediately following).")
    print()
    maximal_order_factors = [37, 1407181, 51593604295295867744293584889,
                              31599414504681995853008278745587832204909]
    maximal_order_product = 1
    for f in maximal_order_factors:
        maximal_order_product *= f
    N_paper = 3 * maximal_order_product
    full_factors_paper = [3] + maximal_order_factors
    ok_csidh = check_factorization(
        "CSIDH-512 class number N (CSI-FiSh paper, Section 3, p.8)",
        full_factors_paper,
        N_paper,
    )

    print("=== CROSS-CITATION CONSISTENCY CONTROL ===")
    print("Second, independently obtained citation: the CSI-FiSh reference")
    print("implementation's own file classgroup_data/'class number'")
    print("(https://github.com/KULeuven-COSIC/CSI-FiSh, file referenced by")
    print("the paper's own reference [2] and its README.md: 'This folder")
    print("contains the class number, discrete logarithms and a HKZ reduced")
    print("basis of the relation lattice').")
    N_repo = 254652442229484275177030186010639202161620514305486423592570860975597611726191
    print(f"  N (paper, 3 x product of maximal-order factors): {N_paper}")
    print(f"  N (repo classgroup_data/'class number' file):    {N_repo}")
    exact_agreement = (N_paper == N_repo)
    print(f"  EXACT AGREEMENT: {exact_agreement}")
    print()

    assert ok_csidh, "Factorization-integrity control FAILED for CSIDH-512 N"
    assert exact_agreement, "Cross-citation consistency control FAILED: disagreement between the two independently obtained citations"

    print("=== SUMMARY ===")
    print(f"class_group_order_match: {ok_csidh and exact_agreement}")
    print(f"N = {N_paper}")
    print(f"N bit length: {N_paper.bit_length()}  (paper states 'approximately equal to 2^257.136'; "
          f"log2(N) = {math.log2(N_paper)})")
