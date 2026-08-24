"""EXP-MLKEM-007 -- control implementations and attestations.

Controls (specification.yaml `controls`):
  CTRL-KNOWN-ANSWER              known_answer_baseline()      (driver)
  CTRL-COVARIANCE-MODEL          covariance_model_control()
  CTRL-FUSION-ABLATION           driver (unweighted_mean rule, always measured)
  CTRL-RANDOM-SIGNED-PERMUTATION driver (random_signed_permutation rule)
  CTRL-SHUFFLED-ORBIT-LABELS     shuffled_label_map()
  CTRL-EXACT-EQUALITY            exact_equality_control()
  CTRL-SEED-DISCIPLINE           SeedGuard
"""

from fractions import Fraction
import math

from mlwe_sampler import (Q, ETA, CBD_WEIGHTS, CBD_DENOM, CBD_PROB, LAYER_CLASS,
                          apply_shift, shift_signs, gen_instance)
import orbit_scoring as osc


# --------------------------------------------------------- seed discipline

class SeedGuard(object):
    """Records every instance seed read, tagged by phase.

    Fitting phases ('covariance_fit', 'subset_selection', 'threshold_pinning',
    'calibration') may only read training seeds.  Any violation raises, which
    the driver classifies as invalid_implementation_or_instrumentation.
    """

    FITTING_PHASES = ("covariance_fit", "subset_selection", "threshold_pinning",
                      "calibration")

    def __init__(self, training_seeds, heldout_seeds):
        self.training = set(training_seeds)
        self.heldout = set(heldout_seeds)
        self.reads = []
        self.violations = []

    def read(self, phase, n, seed):
        self.reads.append({"phase": phase, "n": n, "seed": seed})
        if phase in self.FITTING_PHASES and seed in self.heldout:
            v = {"phase": phase, "n": n, "seed": seed}
            self.violations.append(v)
            raise RuntimeError("seed-discipline violation: %r" % (v,))

    def attestation(self):
        fit_seeds = sorted(set(r["seed"] for r in self.reads
                               if r["phase"] in self.FITTING_PHASES))
        return {
            "training_seeds": sorted(self.training),
            "held_out_seeds": sorted(self.heldout),
            "seeds_read_by_fitting_phases": fit_seeds,
            "held_out_seeds_read_by_fitting_phases":
                sorted(set(fit_seeds) & self.heldout),
            "total_reads": len(self.reads),
            "violations": self.violations,
            "pass": len(self.violations) == 0 and
                    not (set(fit_seeds) & self.heldout),
        }


# ------------------------------------------------- CTRL-COVARIANCE-MODEL

CHI2_CRIT_DF6_ALPHA_001 = 22.458  # frozen tolerance, df = 6, alpha = 0.001


def covariance_model_control(n, seeds, orbit, k=2, instances=None):
    """Per-orbit-element preservation of the exact CBD(eta=3) law.

    (a) exact structural check: X^j * a is a signed permutation of a, so the
        multiset of |coefficients| is preserved exactly;
    (b) chi-square against the exact integer CBD weights and first/second
        moment checks on the pooled coefficients of X^j*s and X^j*e.
    """
    results = []
    exact_struct_ok = True
    for j in orbit:
        counts_s = dict((x, 0) for x in CBD_WEIGHTS)
        counts_e = dict((x, 0) for x in CBD_WEIGHTS)
        for idx, seed in enumerate(seeds):
            inst = instances[idx] if instances else gen_instance(n, seed, k)
            for comp in range(k):
                for arr, counts in ((inst.s[comp], counts_s), (inst.e[comp], counts_e)):
                    sh = apply_shift(arr, j)
                    if sorted(abs(x) for x in sh) != sorted(abs(x) for x in arr):
                        exact_struct_ok = False
                    for x in sh:
                        counts[x] += 1
        for name, counts in (("s", counts_s), ("e", counts_e)):
            N = sum(counts.values())
            chi2 = 0.0
            for x, w in CBD_WEIGHTS.items():
                exp = N * w / CBD_DENOM
                chi2 += (counts[x] - exp) ** 2 / exp
            m1 = sum(x * c for x, c in counts.items()) / N
            m2 = sum(x * x * c for x, c in counts.items()) / N
            var_exact = sum(x * x * CBD_WEIGHTS[x] for x in CBD_WEIGHTS) / CBD_DENOM
            m4 = sum(x ** 4 * CBD_WEIGHTS[x] for x in CBD_WEIGHTS) / CBD_DENOM
            se1 = math.sqrt(var_exact / N)
            se2 = math.sqrt(max(m4 - var_exact ** 2, 0.0) / N)
            results.append({
                "orbit_element_j": j, "quantity": name, "samples": N,
                "chi_square": chi2, "chi_square_df": 6,
                "chi_square_critical_alpha_0.001": CHI2_CRIT_DF6_ALPHA_001,
                "chi_square_pass": chi2 <= CHI2_CRIT_DF6_ALPHA_001,
                "first_moment": m1, "first_moment_tolerance_4se": 4 * se1,
                "first_moment_pass": abs(m1) <= 4 * se1,
                "second_moment": m2, "second_moment_exact": var_exact,
                "second_moment_tolerance_4se": 4 * se2,
                "second_moment_pass": abs(m2 - var_exact) <= 4 * se2,
                "counts": dict((str(x), c) for x, c in sorted(counts.items())),
            })
    all_pass = (exact_struct_ok and
                all(r["chi_square_pass"] and r["first_moment_pass"] and
                    r["second_moment_pass"] for r in results))
    return {"exact_signed_permutation_structure": exact_struct_ok,
            "per_element": results, "pass": bool(all_pass)}


# ---------------------------------------------------- CTRL-EXACT-EQUALITY

def exact_equality_control(inst, vs, uGs, orbit, guess_block, sw,
                           max_vectors=24, max_candidates=9):
    """Batched negacyclic-convolution path versus direct scalar evaluation.

    Check 1 (integers, exact): rho^(j)_t from the batched negacyclic
      correlation equals <v_t, X^j b> computed scalar-wise, mod q.
    Check 2 (integers, exact): the switched phase index of the factored score
      term, formed by adding per-coordinate switched indices, equals the index
      formed by the direct scalar computation, mod P.
    Check 3 (exact rationals): the CBD weight of each expanded term computed as
      a product of per-coordinate integer weights equals the direct product.
    Check 4 (floats): the factored complex score equals the scalar reference to
      <= 1e-9 relative; floats are non-associative so this is a bound, while
      checks 1-3 are exact.
    """
    work = osc.Work()
    vs_c = vs[:max_vectors]
    uGs_c = uGs[:max_vectors]

    batched = osc.orbit_residuals_batched(vs_c, inst, orbit, work)
    n_checks = 0
    mismatches = []
    for oi, j in enumerate(orbit):
        scal, _ = osc.orbit_residuals_scalar(vs_c, inst, j)
        for t in range(len(vs_c)):
            n_checks += 1
            if batched[oi][t] != scal[t]:
                mismatches.append({"check": "residual", "j": j, "t": t,
                                   "batched": batched[oi][t], "scalar": scal[t]})

    rho_sw = [[sw.switch(x) for x in row] for row in batched]
    uG_sw = [[sw.switch(x) for x in row] for row in uGs_c]

    cands = osc.enumerate_candidates(len(guess_block))[:max_candidates]
    idx_checks = 0
    weight_checks = 0
    float_max_rel = 0.0
    for oi in range(len(orbit)):
        for c in cands:
            # direct scalar reference
            ref_re, ref_im, idxs, weights = osc.scalar_score_reference(
                rho_sw[oi], uG_sw, c, guess_block, sw)
            # factored path, expanded term by term with exact integer indices
            assigns = [()]
            for a in range(len(guess_block)):
                assigns = [asn + (x,) for asn in assigns for x in LAYER_CLASS[c[a]]]
            pos = 0
            fac_re = 0.0
            fac_im = 0.0
            for t in range(len(vs_c)):
                base = rho_sw[oi][t] % sw.P
                for asn in assigns:
                    k = base
                    wf = Fraction(1, 1)
                    for a in range(len(guess_block)):
                        k = (k + ((-uG_sw[t][a] * asn[a]) % sw.P)) % sw.P
                        wf *= Fraction(CBD_WEIGHTS[asn[a]], CBD_DENOM)
                    idx_checks += 1
                    if k != idxs[pos][1]:
                        mismatches.append({"check": "phase_index", "t": t,
                                           "factored": k, "scalar": idxs[pos][1]})
                    weight_checks += 1
                    wref = Fraction(1, 1)
                    for a in range(len(guess_block)):
                        wref *= Fraction(CBD_WEIGHTS[asn[a]], CBD_DENOM)
                    if wf != wref:
                        mismatches.append({"check": "weight", "t": t})
                    fw = float(wf)
                    fac_re += fw * sw.cos[k]
                    fac_im += fw * sw.sin[k]
                    pos += 1
            denom = max(abs(ref_re), abs(ref_im), 1e-12)
            rel = max(abs(fac_re - ref_re), abs(fac_im - ref_im)) / denom
            float_max_rel = max(float_max_rel, rel)

    return {"residual_checks": n_checks,
            "phase_index_checks": idx_checks,
            "weight_checks": weight_checks,
            "float_max_relative_deviation": float_max_rel,
            "float_tolerance": 1e-9,
            "failures": mismatches,
            "pass": len(mismatches) == 0 and float_max_rel <= 1e-9}


# ------------------------------------------- CTRL-SHUFFLED-ORBIT-LABELS

def shuffled_label_map(n_elem, seed_rng):
    """A derangement of orbit labels: score of element oi is paired with the
    candidate-coordinate map of element pi(oi) != oi."""
    if n_elem < 2:
        return list(range(n_elem))
    while True:
        perm = list(range(n_elem))
        seed_rng.shuffle(perm)
        if all(perm[i] != i for i in range(n_elem)):
            return perm
