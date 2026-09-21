"""Search environment: walk an F_p-isogeny class while choosing a presentation.

State      (curve model E' in the class, presentation spec)
Actions    stay | step along the i-th rational ell-isogeny of E' (ell in primes)
           | set presentation family / m / k / B / c to one of the grid values
Reward     potential-based: Phi(new) - Phi(old) with Phi = score (+ planted bonus)
           so an episode's return is exactly score(final) - score(start).
Episode    max_steps steps from the input curve with the default presentation.

Every rational ell-isogeny used is found by factoring the ell-division
polynomial, its codomain computed by Velu and checked to carry the class order
(a failure raises: it is a bug, never a result), exactly as in
tools/isogeny_dreg_search.py.  Isomorphic models are identified by iso_key so a
state is an (F_p-isomorphism class, presentation) pair and its score is cached.

Controls built into the environment (see analysis/rl-isogeny-search/DESIGN.md):
  permuted=True   the reward handed to the agent is seeded noise, independent of
                  the state; info["true_reward"] still carries the real value.
                  A policy trained here must not beat the random agent.
  planted=True    one reachable (curve, presentation) state, chosen by a seeded
                  random walk, carries a bonus.  A search that cannot find a
                  planted needle is not a search.
"""
from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from tools.isogeny_dreg_search import (
    aut_order,
    f1_support,
    is_singular,
    iso_key,
    j_invariant,
    legendre,
    random_curve_with_other_trace,
    rational_subgroups,
    trace_of,
    velu_from_kernel_polynomial,
    verify_order,
)

from .reward import Measurement, PresentationSpec, RewardMeter, Weights, _seed_from, shape_feasible


@dataclass(frozen=True)
class Curve:
    a: int
    b: int
    j: int
    key: Tuple
    aut: int

    def as_dict(self) -> dict:
        return {"a": self.a, "b": self.b, "j": self.j, "aut": self.aut}


@dataclass(frozen=True)
class GridSpec:
    families: Tuple[str, ...] = ("direct", "digit")
    ms: Tuple[int, ...] = (2, 3)
    ks: Tuple[int, ...] = (1, 2)
    Bs: Tuple[int, ...] = (8,)
    n_c: int = 2                # c values: 0 plus n_c - 1 seeded random nonzero residues

    def as_dict(self) -> dict:
        return {"families": list(self.families), "ms": list(self.ms), "ks": list(self.ks),
                "Bs": list(self.Bs), "n_c": self.n_c}


SMALL_GRID = GridSpec(("direct",), (2,), (1, 2), (8,), 2)
MEDIUM_GRID = GridSpec(("direct", "digit"), (2, 3), (1, 2), (8,), 2)
LARGE_GRID = GridSpec(("direct", "digit"), (2, 3), (1, 2, 3, 4), (4, 8, 16), 3)
CHAINED_GRID = GridSpec(("direct",), (3,), (1, 2), (8,), 1)     # the j = 0 positive control
GRIDS = {"small": SMALL_GRID, "medium": MEDIUM_GRID, "large": LARGE_GRID, "chained": CHAINED_GRID}


class IsogenyPDPEnv:
    NEIGHBOUR_CLASSES = 4     # count in {0}, {1}, {2}, {>= 3}

    def __init__(self, p: int, a: int, b: int, *, seed: int = 0,
                 primes: Sequence[int] = (2, 3, 5, 7), grid: Optional[GridSpec] = None,
                 max_steps: int = 24, n_null: int = 2, null_kind: str = "other_trace",
                 weights: Optional[Weights] = None, permuted: bool = False,
                 planted: bool = False, plant_depth: int = 3, identity_bits: int = 8,
                 exact_trace_limit: int = 1 << 17, coverage_samples: int = 16,
                 max_rows: int = 40000, max_cols: int = 40000, start_spec: Optional[str] = None):
        a %= p
        b %= p
        if is_singular(a, b, p):
            raise ValueError("singular input curve")
        self.p, self.a0, self.b0 = p, a, b
        self.seed = seed
        self.rng = random.Random(_seed_from(seed, "env"))
        self.noise_rng = random.Random(_seed_from(seed, "noise"))
        self.primes = tuple(primes)
        self.grid = grid or MEDIUM_GRID
        self.max_steps = max_steps
        self.permuted = permuted
        self.planted = planted
        self.plant_depth = plant_depth
        self.identity_bits = identity_bits
        self.exact_trace_limit = exact_trace_limit
        self.weights = weights or Weights()

        t = trace_of(a, b, p, self.rng, exact_trace_limit)
        if t % p == 0:
            raise ValueError("supersingular input curve: out of scope")
        self.trace = t
        self.N = p + 1 - t
        self.D = t * t - 4 * p
        self.null_curves: List[Tuple[int, int]] = []
        for _ in range(n_null if null_kind == "other_trace" else 0):
            na, nb, _nt = random_curve_with_other_trace(p, t, self.rng, exact_trace_limit)
            self.null_curves.append((na, nb))
        self.cs: List[int] = [0] + [self.rng.randrange(1, p) for _ in range(max(0, self.grid.n_c - 1))]

        # presentation grid, feasibility by shape only
        self.specs: Dict[Tuple[int, int, int, int, int], PresentationSpec] = {}
        self.infeasible: List[str] = []
        for fi, fam in enumerate(self.grid.families):
            for mi, m in enumerate(self.grid.ms):
                for ki, k in enumerate(self.grid.ks):
                    for Bi, B in enumerate(self.grid.Bs):
                        for ci, c in enumerate(self.cs):
                            if fam == "digit" and (B & (B - 1)):
                                continue
                            spec = PresentationSpec(fam, m, k, c, B)
                            if shape_feasible(p, spec, max_rows, max_cols):
                                self.specs[(fi, mi, ki, Bi, ci)] = spec
                            else:
                                self.infeasible.append(spec.label())
        if not self.specs:
            raise ValueError("no feasible presentation in the grid")
        self.default_idx = (0, 0, 0, 0, 0)
        if self.default_idx not in self.specs:
            self.default_idx = min(self.specs)

        self.active_primes = tuple(ell for ell in self.primes if self._has_rational_isogenies(ell))
        self.iso_slots: List[Tuple[int, int]] = [(ell, i) for ell in self.primes for i in range(ell + 1)]
        self.n_iso = len(self.iso_slots)
        g = self.grid
        self.pres_groups = [len(g.families), len(g.ms), len(g.ks), len(g.Bs), len(self.cs)]
        self.n_actions = 1 + self.n_iso + sum(self.pres_groups)

        self.meter = RewardMeter(p, self.N, self.null_curves, seed=seed, null_kind=null_kind,
                                 weights=self.weights, max_rows=max_rows, max_cols=max_cols,
                                 coverage_samples=coverage_samples)
        self._curves: Dict[Tuple, Curve] = {}
        self._nbrs: Dict[Tuple[Tuple, int], List[Curve]] = {}
        self.start = self._curve_for(a, b)
        if start_spec in ("worst", "best"):
            scored = [(self.measure(self.start, s).score, k) for k, s in sorted(self.specs.items())]
            self.default_idx = (min(scored) if start_spec == "worst" else max(scored))[1]
        elif start_spec is not None:
            matches = [k for k, s in self.specs.items() if s.label() == start_spec]
            if not matches:
                raise ValueError(f"start_spec {start_spec!r} is not in the grid: "
                                 f"{[s.label() for s in self.specs.values()]}")
            self.default_idx = matches[0]
        self.planted_target: Optional[Tuple[Tuple, Tuple]] = None
        self.order_checks = 0
        self._episode = 0
        self.curve = self.start
        self.spec_idx = self.default_idx
        self.steps = 0
        self.done = True

    # -- class structure -----------------------------------------------------
    def _has_rational_isogenies(self, ell: int) -> bool:
        p, D = self.p, self.D
        if ell == p or (D % ell == 0):
            return ell != p
        return legendre(D, ell) == 1 if ell != 2 else (D % 8 == 1)

    def _curve_for(self, a: int, b: int) -> Curve:
        key = iso_key(a, b, self.p)
        c = self._curves.get(key)
        if c is None:
            c = Curve(a % self.p, b % self.p, j_invariant(a, b, self.p), key, aut_order(a, b, self.p))
            self._curves[key] = c
        return c

    def neighbours(self, curve: Curve, ell: int) -> List[Curve]:
        ck = (curve.key, ell)
        if ck in self._nbrs:
            return self._nbrs[ck]
        out: List[Curve] = []
        if ell in self.active_primes:
            for h in rational_subgroups(curve.a, curve.b, self.p, ell, self.rng):
                a2, b2 = velu_from_kernel_polynomial(curve.a, curve.b, self.p, h)
                if is_singular(a2, b2, self.p):
                    raise RuntimeError("Velu produced a singular curve")
                if not verify_order(a2, b2, self.p, self.N, self.rng):
                    raise RuntimeError(f"codomain of {ell}-isogeny does not have order {self.N}")
                self.order_checks += 1
                out.append(self._curve_for(a2, b2))
        self._nbrs[ck] = out
        return out

    # -- presentation grid ---------------------------------------------------
    @property
    def spec(self) -> PresentationSpec:
        return self.specs[self.spec_idx]

    def spec_list(self) -> List[PresentationSpec]:
        return [self.specs[k] for k in sorted(self.specs)]

    def _pres_action_target(self, action: int) -> Optional[Tuple[int, int, int, int, int]]:
        """Spec index tuple that a presentation action would select, or None."""
        a = action - 1 - self.n_iso
        if a < 0:
            return None
        idx = list(self.spec_idx)
        for group, size in enumerate(self.pres_groups):
            if a < size:
                idx[group] = a
                return tuple(idx)  # type: ignore[return-value]
            a -= size
        return None

    def action_labels(self) -> List[str]:
        labels = ["stay"] + [f"iso(ell={ell},#{i})" for ell, i in self.iso_slots]
        g = self.grid
        labels += [f"family={f}" for f in g.families] + [f"m={m}" for m in g.ms]
        labels += [f"k={k}" for k in g.ks] + [f"B={B}" for B in g.Bs]
        labels += [f"c={'0' if i == 0 else f'c{i}'}" for i in range(len(self.cs))]
        return labels

    # -- masks / observations -------------------------------------------------
    def action_mask(self) -> List[bool]:
        mask = [True]
        for ell, i in self.iso_slots:
            mask.append(ell in self.active_primes and i < len(self.neighbours(self.curve, ell)))
        for a in range(1 + self.n_iso, self.n_actions):
            tgt = self._pres_action_target(a)
            mask.append(tgt is not None and tgt in self.specs)
        return mask

    def _identity(self, key: Tuple) -> List[float]:
        if self.identity_bits <= 0:
            return []
        h = hashlib.sha256(f"id:{self.seed}:{key}".encode()).digest()
        bits = []
        for i in range(self.identity_bits):
            bits.append(1.0 if (h[i // 8] >> (i % 8)) & 1 else -1.0)
        return bits

    def _neighbour_class(self, curve: Curve, ell: int) -> int:
        n = len(self.neighbours(curve, ell)) if ell in self.active_primes else 0
        return min(n, 3)

    def discrete_key(self) -> Tuple:
        c = self.curve
        return (tuple(self._neighbour_class(c, ell) for ell in self.primes),
                (legendre(c.a, self.p), legendre(c.b, self.p)), self.spec_idx,
                tuple(int(x > 0) for x in self._identity(c.key)))

    def observation(self) -> List[float]:
        c = self.curve
        p = self.p
        feats: List[float] = []
        for ell in self.primes:
            cls = self._neighbour_class(c, ell)
            feats += [1.0 if cls == i else 0.0 for i in range(self.NEIGHBOUR_CLASSES)]
        feats += [1.0 if legendre(c.a, p) == 1 else 0.0, 1.0 if legendre(c.b, p) == 1 else 0.0,
                  1.0 if c.a == 0 else 0.0, 1.0 if c.b == 0 else 0.0]
        feats.append(f1_support(c.a, c.b, p) / 13.0)
        feats += [self.iso_moves / self.max_steps, (self.max_steps - self.steps) / self.max_steps]
        for group, size in enumerate(self.pres_groups):
            feats += [1.0 if self.spec_idx[group] == i else 0.0 for i in range(size)]
        if self.permuted:
            # the permuted control hands the agent no trace of the true score at all
            feats += [0.0, 0.0, 0.0, 0.0]
        else:
            sc = (self.score - self.start_score) / 4.0
            bs = (self.best_score - self.start_score) / 4.0
            feats += [max(-2.0, min(2.0, sc)), max(-2.0, min(2.0, bs)),
                      max(-2.0, min(2.0, (self.score - self.best_score) / 4.0))]
            feats.append(self.measurement.coverage)
        feats += self._identity(c.key)
        return feats

    @property
    def obs_dim(self) -> int:
        return (len(self.primes) * self.NEIGHBOUR_CLASSES + 4 + 1 + 2 + sum(self.pres_groups)
                + 3 + 1 + max(0, self.identity_bits))

    # -- scoring -------------------------------------------------------------
    def measure(self, curve: Curve, spec: PresentationSpec) -> Measurement:
        return self.meter.measure(curve.a, curve.b, curve.j, curve.key, spec)

    def _phi(self, curve: Curve, spec: PresentationSpec) -> Tuple[float, bool]:
        meas = self.measure(curve, spec)
        hit = self.planted_target is not None and (curve.key, spec.key) == self.planted_target
        return meas.score + (self.weights.planted_bonus if hit else 0.0), hit

    def state_key(self) -> Tuple[Tuple, Tuple]:
        return (self.curve.key, self.spec.key)

    # -- episode -------------------------------------------------------------
    def _plant(self) -> None:
        prng = random.Random(_seed_from(self.seed, "plant"))
        curve = self.start
        for _ in range(self.plant_depth):
            options = [(ell, n) for ell in self.active_primes for n in self.neighbours(curve, ell)]
            if not options:
                break
            curve = prng.choice(options)[1]
        specs = [s for k, s in sorted(self.specs.items()) if k != self.default_idx] or list(self.specs.values())
        spec = prng.choice(specs)
        self.planted_target = (curve.key, spec.key)
        self.planted_curve = curve
        self.planted_spec = spec

    def reset(self) -> List[float]:
        if self.planted and self.planted_target is None:
            self._plant()
        self.curve = self.start
        self.spec_idx = self.default_idx
        self.steps = 0
        self.iso_moves = 0
        self.done = False
        self._episode += 1
        self.measurement = self.measure(self.curve, self.spec)
        phi, hit = self._phi(self.curve, self.spec)
        self.score = phi
        self.start_score = phi
        self.best_score = phi
        self.best_state = self._state_record(hit)
        self.planted_hit = hit
        return self.observation()

    def _state_record(self, hit: bool) -> dict:
        m = self.measurement
        return {"curve": self.curve.as_dict(), "spec": self.spec.label(), "score": m.score,
                "excess_fall": m.excess_fall, "d_ff_real": m.d_ff_real, "d_ff_null": m.d_ff_null,
                "log2_nnz": m.log2_nnz, "coverage": m.coverage, "planted_hit": hit}

    def step(self, action: int) -> Tuple[List[float], float, bool, dict]:
        if self.done:
            raise RuntimeError("episode is over; call reset()")
        mask = self.action_mask()
        if not (0 <= action < self.n_actions) or not mask[action]:
            raise ValueError(f"invalid action {action}")
        old_phi = self.score
        moved = "stay"
        if 1 <= action <= self.n_iso:
            ell, i = self.iso_slots[action - 1]
            self.curve = self.neighbours(self.curve, ell)[i]
            self.iso_moves += 1
            moved = f"iso(ell={ell},#{i})"
        elif action > self.n_iso:
            tgt = self._pres_action_target(action)
            assert tgt is not None
            self.spec_idx = tgt
            moved = self.spec.label()
        self.measurement = self.measure(self.curve, self.spec)
        phi, hit = self._phi(self.curve, self.spec)
        self.score = phi
        true_reward = phi - old_phi
        if hit:
            self.planted_hit = True
        if phi > self.best_score:
            self.best_score = phi
            self.best_state = self._state_record(hit)
        self.steps += 1
        self.done = self.steps >= self.max_steps
        reward = self.noise_rng.gauss(0.0, 1.0) if self.permuted else true_reward
        info = {"true_reward": true_reward, "score": phi, "planted_hit": hit, "action": moved,
                "curve": self.curve.as_dict(), "spec": self.spec.label(),
                "measurement": self.measurement}
        return self.observation(), reward, self.done, info

    def summary(self) -> dict:
        return {
            "p": self.p, "a": self.a0, "b": self.b0, "trace": self.trace, "order": self.N,
            "discriminant": self.D, "primes": list(self.primes), "active_primes": list(self.active_primes),
            "grid": self.grid.as_dict(), "c_values": self.cs, "n_specs": len(self.specs),
            "specs": [s.label() for s in self.spec_list()], "infeasible_specs": self.infeasible,
            "n_actions": self.n_actions, "obs_dim": self.obs_dim, "max_steps": self.max_steps,
            "null_kind": self.meter.null_kind, "null_curves": self.null_curves,
            "weights": self.weights.as_dict(), "permuted": self.permuted, "planted": self.planted,
            "planted_target": (None if self.planted_target is None else
                               {"curve": self.planted_curve.as_dict(), "spec": self.planted_spec.label()}),
            "identity_bits": self.identity_bits,
            "start_spec": self.specs[self.default_idx].label(),
        }
