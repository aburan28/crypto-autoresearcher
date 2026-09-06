"""Tests for harness/rl_isogeny (TESTS of an instrument, not runs, not evidence).

Expected values are pre-registered closed forms (the structural first fall
B + 2k of the direct presentation, analysis/isogeny-dreg-search/DESIGN.md),
independent brute-force evaluations, or planted constructions whose answer is
forced.  No expected value was adjusted to fit an observation.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness.rl_isogeny import (  # noqa: E402
    MEDIUM_GRID,
    SMALL_GRID,
    GridSpec,
    IsogenyPDPEnv,
    PresentationSpec,
    RandomAgent,
    TabularQAgent,
    build_presentation,
    compare,
    evaluate,
    exhaustive_oracle,
    fibre_poly_general,
    run_episode,
    summarize,
    train,
    yield_log2_trials,
)
from tools.isogeny_dreg_search import (  # noqa: E402
    iso_key,
    peval,
    random_point,
    s3_coeffs,
    trace_exact,
)

P = 1009
A, B_ = 3, 5


def _s3_eval(a, b, p, x1, x2, x3):
    return sum(c * pow(x1, e1, p) * pow(x2, e2, p) * pow(x3, e3, p)
               for (e1, e2, e3), c in s3_coeffs(a, b, p).items()) % p


def test_fibre_poly_general_matches_direct_evaluation():
    rng = random.Random(1)
    for k, c in [(1, 0), (2, 0), (3, 5), (4, 17), (2, 900)]:
        x1, xR = rng.randrange(P), rng.randrange(P)
        f = fibre_poly_general(A, B_, P, k, c, x1, xR)
        assert len(f) - 1 == 2 * k
        for _ in range(20):
            u = rng.randrange(P)
            X = (pow(u, k, P) + c * u) % P
            assert peval(f, u, P) == _s3_eval(A, B_, P, x1, X, xR)


def test_direct_presentation_first_fall_is_B_plus_2k_pre_registered():
    env = IsogenyPDPEnv(P, A, B_, seed=3, grid=GridSpec(("direct",), (2,), (1, 2), (6, 8), 1),
                        max_steps=4)
    env.reset()
    for spec in env.spec_list():
        m = env.measure(env.start, spec)
        assert m.feasible
        assert m.d_ff_real == spec.B + 2 * spec.k
        assert m.d_ff_null == spec.B + 2 * spec.k
        assert m.excess_fall == 0 and m.deficit_excess == 0


def test_chained_presentation_builds_two_curve_generators_and_three_memberships():
    spec = PresentationSpec("direct", 3, 1, 0, 6)
    built = build_presentation(P, s3_coeffs(A, B_, P), 7, spec)
    assert built.n_system == 2 and len(built.polys) == 5
    assert built.ring.n_free == 4          # u1, u2, u3, w
    assert built.degrees[:2] == [4, 4] and built.degrees[2:] == [6, 6, 6]
    digit = PresentationSpec("digit", 2, 1, 0, 8)
    bd = build_presentation(P, s3_coeffs(A, B_, P), 7, digit)
    assert bd.ring.n_sq == 6 and bd.ring.n_free == 0 and bd.n_system == 1 and len(bd.polys) == 1


def test_yield_term_is_the_conservation_mean():
    import math
    N = 1000
    assert yield_log2_trials(PresentationSpec("direct", 2, 1, 0, 8), N) == pytest.approx(math.log2(2 * N / 64))
    assert yield_log2_trials(PresentationSpec("direct", 3, 1, 0, 8), N) == pytest.approx(math.log2(6 * N / 512))
    assert yield_log2_trials(PresentationSpec("direct", 3, 1, 0, 64), N) == 0.0   # clipped at one trial


def test_isogeny_steps_stay_in_the_trace_class_and_are_order_checked():
    env = IsogenyPDPEnv(P, A, B_, seed=5, grid=SMALL_GRID, max_steps=10)
    env.reset()
    labels = env.action_labels()
    seen = {env.curve.key}
    moves = 0
    rng = random.Random(0)
    while not env.done:
        mask = env.action_mask()
        iso = [i for i in range(1, env.n_iso + 1) if mask[i]]
        action = rng.choice(iso) if iso else 0
        env.step(action)
        if action:
            moves += 1
            assert labels[action].startswith("iso(")
        assert trace_exact(env.curve.a, env.curve.b, P) == env.trace
        assert env.curve.key == iso_key(env.curve.a, env.curve.b, P)
        seen.add(env.curve.key)
    assert moves == env.iso_moves
    assert env.order_checks > 0
    for ell in env.primes:
        assert len(env.neighbours(env.start, ell)) <= ell + 1


def test_reward_is_potential_based_and_deterministic():
    def run(seed):
        env = IsogenyPDPEnv(P, A, B_, seed=11, grid=MEDIUM_GRID, max_steps=8)
        rec = run_episode(env, RandomAgent(seed))
        return env, rec
    env1, r1 = run(4)
    env2, r2 = run(4)
    assert r1["trajectory"] == r2["trajectory"]
    assert r1["final_score"] == r2["final_score"]
    assert r1["true_return"] == pytest.approx(r1["final_score"] - r1["start_score"])
    assert r1["best_score"] >= max(r1["final_score"], r1["start_score"])


def test_presentation_actions_change_spec_and_invalid_actions_raise():
    env = IsogenyPDPEnv(P, A, B_, seed=2, grid=MEDIUM_GRID, max_steps=6)
    env.reset()
    labels = env.action_labels()
    mask = env.action_mask()
    a_digit = labels.index("family=digit")
    assert mask[a_digit]
    env.step(a_digit)
    assert env.spec.family == "digit"
    a_m3 = labels.index("m=3")
    env.step(a_m3)
    assert env.spec.m == 3 and env.spec.chained
    with pytest.raises(ValueError):
        env.step(env.n_actions + 5)
    bad = [i for i, ok in enumerate(env.action_mask()) if not ok]
    if bad:
        with pytest.raises(ValueError):
            env.step(bad[0])


def test_permuted_mode_hands_out_noise_but_keeps_the_true_reward():
    env = IsogenyPDPEnv(P, A, B_, seed=6, grid=SMALL_GRID, max_steps=6, permuted=True)
    env.reset()
    diffs = 0
    tot = 0.0
    while not env.done:
        _, r, _, info = env.step(0)
        tot += info["true_reward"]
        diffs += int(r != info["true_reward"])
    assert diffs == env.max_steps                 # stay never changes the score, noise does
    assert tot == pytest.approx(0.0)


def test_planted_needle_is_found_by_tabular_q_and_rarely_by_random():
    env = IsogenyPDPEnv(P, A, B_, seed=21, grid=SMALL_GRID, max_steps=6, planted=True, plant_depth=1)
    env.reset()
    assert env.planted_target is not None
    agent = TabularQAgent(env.n_actions, seed=1, eps_episodes=30)
    recs = train(env, agent, 60)
    ev = evaluate(env, agent, 3)
    assert all(r["planted_hit"] for r in ev)
    assert ev[0]["final_score"] > ev[0]["start_score"] + env.weights.planted_bonus - 1.0
    rnd = train(env, RandomAgent(9), 60)
    c = compare(recs, rnd)
    assert c["agent_planted_hit_rate"] > c["random_planted_hit_rate"]
    s = summarize(recs)
    assert s["planted_hit_rate"] > 0.5


def test_oracle_certifies_the_class_and_agrees_with_the_env_meter():
    env = IsogenyPDPEnv(P, A, B_, seed=8, grid=SMALL_GRID, max_steps=4)
    env.reset()
    orc = exhaustive_oracle(env)
    assert orc["certified"] is True
    assert orc["class_size"] >= 1 and orc["n_states"] == orc["class_size"] * len(env.specs)
    start_rows = [r for r in orc["rows"] if r["j"] == env.start.j and r["spec"] == env.spec.label()]
    assert start_rows and start_rows[0]["score"] == pytest.approx(env.measure(env.start, env.spec).score)
    assert orc["best"]["score"] == max(r["score"] for r in orc["rows"])
    for stats in orc["per_spec"].values():
        assert stats["n"] == orc["class_size"]


def test_ppo_smoke_respects_masks_and_updates():
    torch = pytest.importorskip("torch")
    from harness.rl_isogeny import PPOAgent
    env = IsogenyPDPEnv(P, A, B_, seed=13, grid=SMALL_GRID, max_steps=5)
    env.reset()
    agent = PPOAgent(env.obs_dim, env.n_actions, seed=0, update_every=2, minibatch=8)
    recs = train(env, agent, 4)
    assert agent.updates >= 1
    assert len(recs) == 4
    ev = evaluate(env, agent, 1)
    assert ev[0]["steps"] == 5


# --------------------------------------------------------------------------
# leading-form certificate (harness/rl_isogeny/leading_forms.py)
# --------------------------------------------------------------------------

from harness.rl_isogeny.leading_forms import certify, leading_forms  # noqa: E402


def test_leading_forms_of_direct_presentation_are_the_closed_form_and_curve_free():
    spec = PresentationSpec("direct", 2, 2, 0, 8)
    rng = random.Random(3)
    seen = set()
    for _ in range(4):
        while True:
            a, b = rng.randrange(1, P), rng.randrange(1, P)
            if (4 * a ** 3 + 27 * b * b) % P:
                break
        built = build_presentation(P, s3_coeffs(a, b, P), rng.randrange(P), spec)
        lf = leading_forms(built)
        seen.add(tuple(lf))
        ring = built.ring
        # LF(S_3(u1^2, u2^2, x_R)) = u1^4 u2^4 ; LF(f_V(u_i)) = u_i^8
        assert lf[0] == (((0, (4, 4)), 1),)
        assert lf[1] == (((0, (8, 0)), 1),) and lf[2] == (((0, (0, 8)), 1),)
        assert ring.degree(built.polys[0]) == 8
    assert len(seen) == 1


def test_certificate_holds_on_toy_and_large_primes_and_predicts_the_measured_first_fall():
    for spec in (PresentationSpec("direct", 2, 1, 0, 6), PresentationSpec("direct", 3, 1, 0, 6),
                 PresentationSpec("digit", 2, 1, 0, 8)):
        cert = certify(spec, primes=(P, 281474976710597), curves_per_prime=2, seed=1)
        assert cert.holds, cert.as_dict()
        for pc in cert.per_prime:
            assert pc.leading_forms_identical
            assert pc.consistent and pc.predicted_first_fall is not None
            if spec.family == "direct" and spec.m == 2:
                assert pc.predicted_first_fall == spec.B + 2 * spec.k
