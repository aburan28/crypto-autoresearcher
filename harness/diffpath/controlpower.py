"""CONTROL POWER -- the only new module of EXP-DIFFP-4b165f (TASK-20260824-9a489e).

WHAT THIS MODULE IS.  A measurement instrument pointed at ANOTHER instrument:
the BATCH-f8bf86 novelty adjudicator, which this module imports and NEVER
modifies (IR-2).  It adds the declared key projection and the ablated canonical
form, null family (d) `message_difference_perturbed` with a two-sided known
answer and per-draw component attribution, the generator action profile, the
two-sided known-answer decoy set, and the drivers that run the suite once per
ablation row.

WHAT IT IS NOT.  It is not a repair.  VD-3, VD-4, the {E4}/{E5} zero-image
result, OBJ-3, OBJ-4 and OBJ-10 stand exactly as committed and are MEASURED
here rather than fixed (contract interpretation_limits; batch rules).  It is not
a re-implementation of the adjudicator: every canonical form is built from the
committed `adjudicator.serialize`, the committed `equivalence` generator
actions, and the committed census, and the one place where the committed
`canonical()` body had to be mirrored (its variant list, which that function
does not expose) is checked against `canonical()` itself on every object it
touches -- see `variant_keys` and `VARIANT_MIRROR_CHECK`.

IT SEARCHES NOTHING AND ACQUIRES NOTHING.  No path in this module reads,
parses, extracts or reconstructs `coordination/goals/GOAL-MD5-001/quarantine/**`;
the string does not appear anywhere in this file.  ONE INHERITED BYTE-READ IS
DISCLOSED RATHER THAN GLOSSED: the COMMITTED `census.build_census()` calls
`quarantine_attestation()`, which opens the payload 'rb', hashes it and discards
it without decoding or parsing, so the contract's wording "does not touch it at
all" is not literally achievable while IR-2 forbids editing that module.  See
`_environment_supplement()["quarantine_attestation"]`; no derived quantity of the
payload is computed or reported.  No network call of any kind is made (IR-6).
No search over any difference space, no collision attempt, no cost projection
(IR-5).

REPORT FORM IS A HARD TERM.  Every k >= 1 rejection carries the SET OF
CANONICAL-KEY COMPONENT NAMES that separates the draw from its own source
entry.  A rejection reported without that attribution is not a measurement
(H-3 / IR-10), and no function here emits a single pass/fail summary of the
suite: the deliverable is a per-component DETECTED / NOT DETECTED table for the
OLD suite and for the STRENGTHENED suite, separately.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import random
import signal
import subprocess
import sys
import time

from .compat import ensure as _ensure_compat

COMPAT = _ensure_compat()          # MUST precede the harness.runner import

from harness.runner import RunResult, run_wrapped  # noqa: E402

from . import adjudicator as ADJ                   # noqa: E402
from . import equivalence as EQ                    # noqa: E402
from . import primitives as P                      # noqa: E402
from .census import build_census                   # noqa: E402
from .pathobj import PathObject, bsdr_alternative, bsdr_encode  # noqa: E402

# ---------------------------------------------------------------------------
# frozen contract constants
# ---------------------------------------------------------------------------

EXPERIMENT_ID = "EXP-DIFFP-4b165f"        # IR-7: the LITERAL id, a hard term
EXP_AREA = "DIFFP-4b165f"
TASK_ID = "TASK-20260824-9a489e"
GOAL_ID = "GOAL-DIFFP-84d641"
BATCH_ID = "BATCH-efcae7"
TASK_DIR = ("coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-efcae7/"
            "tasks/TASK-20260824-9a489e")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TASK_ROOT = os.path.join(REPO, TASK_DIR)

# contract inputs.seeds -- EIGHT seeds, IMMUTABLE (IR-3). The first seven are
# EXP-DIFFP-fe894e's, reused byte-identically; the eighth is new in this
# contract and is declared there as a departure.
SEEDS = {
    "equivalence_generator_check": 20260824,
    "planted_path_generation_md5": 84064101,
    "planted_path_generation_sha1": 84064102,
    "null_draw_md5_delta_m": 84064103,
    "null_draw_sha1_dv_in_code": 84064104,
    "null_draw_sha1_dv_unconstrained": 84064105,
    "observation_collision_search": 84064106,
    "null_draw_message_difference_perturbed": 84064107,
}

CEILINGS = {
    "frozen-and-repro": 180,
    "generator-action": 120,
    "null-family-d": 240,
    "ablation-battery-declared-rows": 300,
    "ablation-lattice-and-frozen-recheck": 300,
}

STRICT = frozenset(("E1", "E3", "E4", "E5"))       # the VERIFIED group
PERMISSIVE = frozenset(EQ.ALL_GENERATORS)          # all six DECLARED

K_VALUES = (0, 1, 2, 4, 8, 16)
R_SEEDED = 64                                      # draws per (entry, k >= 1)

# CTL-NULL-D declared bit-index order, stated so a reader can reconstruct a
# draw by inspection: bit position p of the message-difference bit vector is
# bit (p % 32) of word (p // 32), words in their stored order.
BIT_INDEX_ORDER = "p -> (word p//32, bit p%32), words in stored order, LSB first"

# CTL-REPRO pre-registered comparison values, frozen in the contract BEFORE any
# run of this task. 2089 is the CORRECTED value of CORR-20260824-e0088c; if the
# code produces 2094 the correction is wrong and that is a first-class finding
# to be REPORTED, never reconciled.
PRE_REGISTERED = {
    "CTL-PLANT.recall_hits": 96,
    "CTL-PLANT.recall_attempts": 96,
    "CTL-NULL.md5_delta_m.strict_false_positives": 0,
    "CTL-NULL.md5_delta_m.permissive_false_positives": 0,
    "CTL-NULL.sha1_dv_in_code.strict_false_positives": 0,
    "CTL-NULL.sha1_dv_in_code.permissive_false_positives": 0,
    "CTL-NULL.sha1_dv_unconstrained.strict_false_positives": 0,
    "CTL-NULL.sha1_dv_unconstrained.permissive_false_positives": 0,
    "E1.passed": 704, "E1.failed": 0,
    "E2.passed": 2048, "E2.failed": 248,
    "E2.expansion_pass": 2048, "E2.expansion_fail": 0,
    "E2.step_function_pass": 0, "E2.step_function_fail": 248,
    "E3.passed": 128, "E3.failed": 0,
    "E4.passed": 4368, "E4.failed": 0,
    "E4.roundtrip_pass": 4096, "E4.roundtrip_fail": 0,
    "E4.distinct_representation_pass": 256, "E4.distinct_representation_fail": 0,
    "E4.conforming_pair_pass": 16, "E4.conforming_pair_fail": 0,
    "E5.passed": 256, "E5.failed": 0,
    "E6.passed": 17, "E6.failed": 1,
    "E6.step_range_(0, 3).conditions_satisfied": 0,
    "E6.step_range_(0, 0).conditions_satisfied": 2089,
}

# The declared strict key component list (contract
# inputs.key_components_of_the_strict_serialisation). It is stated in the
# contract so the ablation lattice is defined before any run, and it is a HARD
# TERM that the executor DERIVES the list at run time and reports the derived
# list beside this one. A disagreement is a STOP.
DECLARED_KEY_COMPONENTS = ("primitive", "length", "message_difference",
                           "step_delta", "block_index", "in_linearized_code")

VARIANT_MIRROR_CHECK = {"checked": 0, "mismatches": 0, "mismatch_examples": []}


class DeadlineExceeded(Exception):
    pass


class Deadline:
    """An ARMED deadline. Not a promise to be quick -- a signal that fires."""

    def __init__(self, seconds: int, label: str):
        self.seconds = seconds
        self.label = label

    def __enter__(self):
        def _fire(signum, frame):
            raise DeadlineExceeded(
                f"run ceiling {self.seconds}s reached for run '{self.label}'")
        self._old = signal.signal(signal.SIGALRM, _fire)
        signal.setitimer(signal.ITIMER_REAL, self.seconds)
        return self

    def __exit__(self, *exc):
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, self._old)
        return False


# ---------------------------------------------------------------------------
# CTL-FROZEN -- the instrument under measurement is the one that was reviewed
# ---------------------------------------------------------------------------

INSTRUMENT_FILES_NOTE = (
    "The CRITERION set is every committed .py file under harness/diffpath/ plus "
    "harness/__init__.py and harness/runner.py, as the contract names them. "
    "harness/diffpath/controlpower.py is THIS TASK'S OWN NEW MODULE: it did not "
    "exist when the contract was written, it is not part of the reviewed "
    "instrument, and its digest is reported SEPARATELY rather than being folded "
    "into the criterion set. __pycache__ is excluded: it is generated bytecode, "
    "not a committed file.")


def harness_digests() -> dict:
    """sha256 of every file of the instrument under measurement."""
    crit: dict = {}
    new: dict = {}
    root = os.path.dirname(os.path.abspath(__file__))
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in sorted(filenames):
            if not fn.endswith(".py"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, REPO)
            with open(full, "rb") as fh:
                dg = hashlib.sha256(fh.read()).hexdigest()
            (new if fn == "controlpower.py" else crit)[rel] = dg
    for rel in ("harness/__init__.py", "harness/runner.py"):
        with open(os.path.join(REPO, rel), "rb") as fh:
            crit[rel] = hashlib.sha256(fh.read()).hexdigest()
    return {"criterion_set": crit, "this_tasks_new_module": new,
            "criterion_set_files": len(crit), "note": INSTRUMENT_FILES_NOTE}


def compare_digests(pre: dict, post: dict) -> dict:
    a, b = pre["criterion_set"], post["criterion_set"]
    changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    return {
        "files_compared": len(set(a) | set(b)),
        "identical": sorted(k for k in set(a) & set(b) if a[k] == b[k]),
        "identical_count": len(set(a) & set(b)) - len(changed),
        "changed": changed,
        "only_before": sorted(set(a) - set(b)),
        "only_after": sorted(set(b) - set(a)),
        "criterion_met": (not changed and set(a) == set(b)),
        "fraction": (f"{len(set(a) & set(b)) - len(changed)}/"
                     f"{len(set(a) | set(b))}"),
        "new_module_digest_before": pre["this_tasks_new_module"],
        "new_module_digest_after": post["this_tasks_new_module"],
    }


# ---------------------------------------------------------------------------
# the declared key projection and the ablated canonical form
# ---------------------------------------------------------------------------

def project(key: tuple, drop_set) -> tuple:
    """Drop every (name, value) pair whose NAME is in `drop_set`, order kept.

    This is the contract's `ablation_mechanism`: the same committed class over
    the same committed census, with named pairs removed from the serialised key
    by a projection applied at run time. Nothing else changes.
    """
    drop = frozenset(drop_set)
    return tuple(p for p in key if p[0] not in drop)


def variant_keys(obj: PathObject, gens: frozenset) -> list:
    """The serialisations of the orbit variants `canonical()` minimises over.

    MIRRORS the body of the committed `adjudicator.canonical` exactly, because
    that function returns the MINIMUM and does not expose the variant list that
    an inside-minimisation projection has to see. Every call self-checks that
    `min(variant_keys(o, g)) == ADJ.canonical(o, g)`; a mismatch would mean the
    mirror had drifted from the committed source and is counted and reported.
    """
    base = EQ.align_E1(obj) if ("E1" in gens and obj.primitive == "sha1") else obj
    variants = [base]
    if "E3" in gens:
        variants = variants + [EQ.act_E3_negate(v, with_conditions=False)
                               for v in variants]
    if "E2" in gens and obj.primitive == "sha1":
        variants = [EQ.act_E2_rotate(v, b, with_conditions=False)
                    for v in variants for b in range(32)]
    keys = [ADJ.serialize(v, gens) for v in variants]
    VARIANT_MIRROR_CHECK["checked"] += 1
    if min(keys) != ADJ.canonical(obj, gens):
        VARIANT_MIRROR_CHECK["mismatches"] += 1
        if len(VARIANT_MIRROR_CHECK["mismatch_examples"]) < 5:
            VARIANT_MIRROR_CHECK["mismatch_examples"].append(
                {"object": obj.id, "gens": sorted(gens)})
    return keys


def ablated_canonical_inside(keys: list, drop_set) -> tuple:
    """THE CONTRACT'S VALUE: min over the orbit of the PROJECTED serialisation."""
    return min(project(k, drop_set) for k in keys)


def ablated_canonical_outside(keys: list, drop_set) -> tuple:
    """The other order: project the minimum. Reported for comparison (IR-8)."""
    return project(min(keys), drop_set)


def key_components(key: tuple) -> list:
    return [p[0] for p in key]


def attribution(draw_key: tuple, source_key: tuple) -> list:
    """H-3: the canonical-key component names that COULD have decided a rejection.

    The set of component names on which the draw's canonical form differs from
    that of its own source census entry -- including names present in one key
    and absent from the other.
    """
    a = dict(draw_key)
    b = dict(source_key)
    names = set(a) | set(b)
    return sorted(n for n in names if a.get(n, _MISSING) != b.get(n, _MISSING))


_MISSING = object()


class Row:
    """One ablation row: a drop-set, its indices, and its accumulated counts."""

    def __init__(self, row_id, drop_set, label, group, pre_registered=None):
        self.row_id = row_id
        self.drop_set = tuple(drop_set)
        self.label = label
        self.group = group
        self.pre_registered = pre_registered or {}
        self.index: dict = {"strict": {}, "permissive": {}}
        self.plant_hits = 0
        self.plant_attempts = 0
        self.plant_misses: list = []
        self.null: dict = {}
        self.nulld: dict = {}
        self.nulld_member_examples: list = []

    def build_index(self, entry_keys: dict) -> None:
        for mode in ("strict", "permissive"):
            idx: dict = {}
            for eid, keys in entry_keys[mode].items():
                idx.setdefault(ablated_canonical_inside(keys, self.drop_set),
                               []).append(eid)
            self.index[mode] = idx

    def lookup(self, keys: list, mode: str):
        hit = self.index[mode].get(ablated_canonical_inside(keys, self.drop_set))
        return hit[0] if hit else None

    def record(self) -> dict:
        old_detected = (self.plant_hits != self.plant_attempts
                        or sum(f["strict_false_positives"]
                               for f in self.null.values()) > 0)
        d_member_k_ge_1 = sum(c["strict_member"] for key, c in self.nulld.items()
                              if c["k"] >= 1)
        d_k0_member = sum(c["strict_member"] for key, c in self.nulld.items()
                          if c["k"] == 0)
        d_k0_draws = sum(c["draws"] for key, c in self.nulld.items()
                         if c["k"] == 0)
        strengthened_detected = (old_detected or d_member_k_ge_1 > 0
                                 or d_k0_member != d_k0_draws)
        return {
            "row": self.row_id,
            "group": self.group,
            "label": self.label,
            "drop_set": list(self.drop_set),
            "CTL_PLANT": {"hits": self.plant_hits,
                          "attempts": self.plant_attempts,
                          "fraction": f"{self.plant_hits}/{self.plant_attempts}",
                          "misses_sample": self.plant_misses[:5]},
            "CTL_NULL_per_family": self.null,
            "CTL_NULL_strict_false_positives_total":
                sum(f["strict_false_positives"] for f in self.null.values()),
            "CTL_NULL_permissive_false_positives_total":
                sum(f["permissive_false_positives"] for f in self.null.values()),
            "CTL_NULL_D_per_cell": self.nulld,
            "CTL_NULL_D_strict_member_k_ge_1": d_member_k_ge_1,
            "CTL_NULL_D_k0_member_fraction": f"{d_k0_member}/{d_k0_draws}",
            "CTL_NULL_D_k_ge_1_member_examples": self.nulld_member_examples[:10],
            "detected_by_OLD_suite": "DETECTED" if old_detected else "NOT DETECTED",
            "detected_by_STRENGTHENED_suite":
                "DETECTED" if strengthened_detected else "NOT DETECTED",
            "detection_rule": DETECTION_RULE,
            "pre_registered": self.pre_registered or None,
            "strict_and_permissive_never_merged": (
                "strict and permissive counts are separate fields and are never "
                "summed, averaged or merged (IR-4); this row's counts are stated "
                "beside its drop_set, which is the other half of IR-4"),
        }


DETECTION_RULE = (
    "DECLARED BEFORE THE RUNS, and read off the contract's own pre-registered "
    "group-1 values (row 3 is pre-registered DETECTED with 6 strict false "
    "positives; row 1, the honest row, with 0). A row is DETECTED BY THE OLD "
    "SUITE iff CTL-PLANT recall is not its full attempt count OR any strict-mode "
    "false positive occurs in CTL-NULL families (a),(b),(c). It is DETECTED BY "
    "THE STRENGTHENED SUITE iff that holds OR CTL-NULL-D's primary arm yields a "
    "strict MEMBER at some k >= 1 OR its k = 0 arm is not fully MEMBER. "
    "DETECTED means the SUITE'S OUTCOME CHANGES when the component is deleted; "
    "it is not a claim that the instrument is correct.")


# ---------------------------------------------------------------------------
# CTL-NULL-D -- null family (d), `message_difference_perturbed`
# ---------------------------------------------------------------------------

PERTURBATION_DECLARATION = {
    "target": ("the MESSAGE DIFFERENCE only: `delta_m` (16 words) for md5, `dv` "
               "(80 words over the object's step_range) for sha1"),
    "held_fixed": ("step_delta, step_delta_signed, block_index, step_range, "
                   "conditions, cv/m/mp, primitive, length AND -- for sha1 -- "
                   "dv_seed_window, which is a SEPARATE FIELD of the path object "
                   "and not the message difference"),
    "recomputed_because_derived_from_the_perturbed_component": (
        "md5: delta_m_signed, the signed-digit representation OF delta_m (not in "
        "the membership key). sha1: in_linearized_code, which is a PREDICATE OF "
        "THE DV and is honestly recomputed by P.sha1_in_linearized_code rather "
        "than carried over -- the contract's own pre-registered prediction turns "
        "on that recomputation. Leaving either stale would make the object "
        "internally inconsistent; both choices are declared here rather than "
        "made silently."),
    "bit_index_order": BIT_INDEX_ORDER,
    "deterministic_draw": "positions = the k lowest bit indices, i.e. range(k)",
    "seeded_draws": (f"R = {R_SEEDED} per (entry, k >= 1); positions = "
                     "sorted(rng.sample(range(nbits), k)) from a "
                     "random.Random(84064107) instantiated once per arm and "
                     "consumed in declared order: entries in census order, then "
                     "k ascending, then draw index"),
}


def perturb_message_difference(obj: PathObject, positions, tag: str) -> PathObject:
    new = PathObject(**{**obj.__dict__})
    new.id = f"{obj.id}~D{tag}"
    new.path_data = {"kind": "family_d_message_difference_perturbed",
                     "of": obj.id, "k": len(positions),
                     "flipped_bit_positions": list(positions)}
    if obj.primitive == "md5":
        d = list(obj.delta_m)
        for p in positions:
            d[p // 32] ^= 1 << (p % 32)
        new.delta_m = tuple(d)
        new.delta_m_signed = tuple(bsdr_encode(x) for x in d)
    else:
        d = list(obj.dv)
        for p in positions:
            d[p // 32] ^= 1 << (p % 32)
        new.dv = tuple(d)
        new.in_linearized_code = P.sha1_in_linearized_code(list(d))
    return new


def perturb_by_codeword(obj: PathObject, w16, tag: str) -> PathObject:
    """D-SHA1-INCODE: add a nonzero codeword of the linearized expansion code.

    The SHA-1 message expansion is GF(2)-linear, so dv XOR expand(w16) is again
    a codeword and the honestly recomputed `in_linearized_code` stays True. That
    is the point: it isolates the message difference from the FLAG.
    """
    cw = P.sha1_expand(list(w16), 80)
    d = [(x ^ y) & P.MASK32 for x, y in zip(obj.dv, cw)]
    new = PathObject(**{**obj.__dict__})
    new.id = f"{obj.id}~DINCODE{tag}"
    weight = sum(bin(x).count("1") for x in cw)
    new.path_data = {"kind": "family_d_in_code_perturbed", "of": obj.id,
                     "codeword_hamming_weight": weight}
    new.dv = tuple(d)
    new.in_linearized_code = P.sha1_in_linearized_code(list(d))
    return new


def md_bits(obj: PathObject) -> int:
    return 32 * len(obj.delta_m if obj.primitive == "md5" else obj.dv)


# ---------------------------------------------------------------------------
# fast declared membership path (committed functions, no re-implementation)
# ---------------------------------------------------------------------------

class FastAdj:
    """Membership by the COMMITTED canonical form against the COMMITTED index.

    `Adjudicator.adjudicate` computes BOTH modes plus the closest-entry loop on
    every call; a permissive sha1 canonical form costs ~22 ms because E2 puts 64
    variants in the orbit, so calling it where only the strict verdict is needed
    would have spent the run ceiling on arithmetic the contract does not ask
    for. This wrapper uses `ADJ.canonical` and the committed Adjudicator's own
    index dicts, so a verdict here is the same verdict by construction. The
    equality is CHECKED against `adjudicate()` on a declared sample rather than
    asserted (see `fidelity_check`).
    """

    def __init__(self, adj: ADJ.Adjudicator):
        self.adj = adj

    def verdict(self, obj: PathObject, mode: str) -> tuple:
        gens = self.adj.strict if mode == "strict" else self.adj.permissive
        key = ADJ.canonical(obj, gens)
        hit = self.adj._index[mode].get(key)
        return ("MEMBER" if hit else "NON-MEMBER", hit[0] if hit else None, key)

    def closest(self, obj: PathObject) -> dict:
        v = ADJ.diff_vector(obj)
        best_id, best_d = None, None
        for e in self.adj.census.plantable_entries():
            d = ADJ.hamming_distance(v, ADJ.diff_vector(e.obj))
            if d is None:
                continue
            if best_d is None or d < best_d:
                best_id, best_d = e.id, d
        return {"closest_entry": best_id, "closest_distance": best_d}


def fidelity_check(adj: ADJ.Adjudicator, fast: FastAdj, objs: list) -> dict:
    """The fast path must agree with the committed `adjudicate()`, and is checked."""
    n = agree = 0
    disagreements = []
    for o in objs:
        a = adj.adjudicate(o)
        s, _, _ = fast.verdict(o, "strict")
        p, _, _ = fast.verdict(o, "permissive")
        n += 1
        if (s, p) == (a.strict_verdict, a.permissive_verdict):
            agree += 1
        else:
            disagreements.append({"object": o.id, "fast": [s, p],
                                  "committed": [a.strict_verdict,
                                                a.permissive_verdict]})
    return {"objects": n, "agree": agree, "fraction": f"{agree}/{n}",
            "disagreements": disagreements,
            "what_it_checks": ("that the fast strict/permissive membership path "
                               "used for the high-count arms returns exactly "
                               "what the committed Adjudicator.adjudicate "
                               "returns on the same objects")}


# ---------------------------------------------------------------------------
# CTL-NULL draw regeneration (the SAME draws, from the SAME seeds)
# ---------------------------------------------------------------------------

def null_draws(census, n: int = 1000) -> dict:
    """Regenerate CTL-NULL's declared draws, in the committed draw order.

    The loop structure and the RNG consumption order are those of the committed
    `adjudicator.ctl_null`, and the draws are built by the committed
    `_null_draw_md5` / `_null_draw_sha1`. Regenerating them once and reusing the
    OBJECTS across ablation rows is an efficiency and not a protocol change: the
    draws are defined by their seeds, and every row sees the identical sequence.
    Draw-sequence fidelity is evidenced by the candidate ids, which embed RNG
    output -- they are reported so a reviewer can compare them with the
    committed run's own recorded ids.
    """
    md5_weights = [sum(bin(d).count("1") for d in e.obj.delta_m)
                   for e in census.shadow if e.primitive == "md5"]
    out = {}
    for fam, seed in (("md5_delta_m", SEEDS["null_draw_md5_delta_m"]),
                      ("sha1_dv_in_code", SEEDS["null_draw_sha1_dv_in_code"]),
                      ("sha1_dv_unconstrained",
                       SEEDS["null_draw_sha1_dv_unconstrained"])):
        rng = random.Random(seed)
        draws = []
        for _ in range(n):
            if fam == "md5_delta_m":
                draws.append(ADJ._null_draw_md5(rng, rng.choice(md5_weights)))
            else:
                draws.append(ADJ._null_draw_sha1(rng, fam == "sha1_dv_in_code"))
        out[fam] = {"seed": seed, "draws": draws}
    return out


# ---------------------------------------------------------------------------
# CTL-TWOSIDED -- the two-sided known-answer decoy set
# ---------------------------------------------------------------------------

def twosided_objects(census) -> dict:
    """T1..T5, each with the answer the contract pre-registered for BOTH sides."""
    sha1_entries = [e for e in census.shadow if e.primitive == "sha1"]
    md5_entries = [e for e in census.shadow if e.primitive == "md5"]
    s0 = sha1_entries[0].obj
    m0 = md5_entries[0].obj

    t1 = [EQ.act_E2_rotate(s0, b) for b in (1, 7, 16, 31)]
    t2 = [EQ.act_E6_reindex(m0, 3), EQ.act_E6_reindex(s0, 3)]

    t3 = PathObject(**{**m0.__dict__})
    t3.id = f"{m0.id}~T3altsigned"
    t3.step_delta_signed = tuple(bsdr_alternative(d) for d in m0.step_delta)
    t3.delta_m_signed = tuple(bsdr_alternative(d) for d in m0.delta_m)
    t3.path_data = {"kind": "T3_alternative_signed_representation", "of": m0.id}

    t4 = PathObject(**{**s0.__dict__})
    t4.id = f"{s0.id}~T4sha0"
    t4.dv = tuple(P.sha0_expand(list(s0.dv_seed_window), 80))
    t4.in_linearized_code = P.sha1_in_linearized_code(list(t4.dv))
    t4.path_data = {"kind": "T4_sha0_codeword_presented_as_sha1_dv", "of": s0.id}
    t4f = PathObject(**{**t4.__dict__})
    t4f.id = f"{s0.id}~T4sha0-flagforced"
    t4f.in_linearized_code = True

    t5 = [e.obj for e in census.shadow]
    return {"T1": t1, "T2": t2, "T3": t3, "T4": t4, "T4_flag_forced": t4f,
            "T5": t5,
            "T3_signed_representation_changed_but_step_delta_equal":
                (t3.step_delta == m0.step_delta),
            "T4_in_linearized_code_recomputed": t4.in_linearized_code}


TWOSIDED_PREREGISTERED = {
    "T1": "strict NON-MEMBER on all four AND permissive MEMBER on all four",
    "T2": "strict NON-MEMBER and permissive MEMBER, on both primitives",
    "T3": ("MEMBER with E4 in the strict group, NON-MEMBER with E4 removed "
           "from it"),
    "T4": ("NON-MEMBER in both modes, and STILL NON-MEMBER at the same distance "
           "with in_linearized_code forced True (over-determined)"),
    "T5": "MEMBER, all 16, in strict mode",
}


# ---------------------------------------------------------------------------
# manifests, environment and the run wrapper
# ---------------------------------------------------------------------------

def _fingerprint(gens_in_force, drop_sets=None) -> dict:
    return {
        "canonicalisation_and_membership_functions":
            list(ADJ.CODE_PATH_FINGERPRINT_FUNCTIONS) + [
                "harness.diffpath.controlpower.project",
                "harness.diffpath.controlpower.variant_keys",
                "harness.diffpath.controlpower.ablated_canonical_inside",
                "harness.diffpath.controlpower.ablated_canonical_outside",
                "harness.diffpath.controlpower.attribution",
                "harness.diffpath.controlpower.perturb_message_difference",
                "harness.diffpath.controlpower.perturb_by_codeword",
                "harness.diffpath.controlpower.FastAdj.verdict",
            ],
        "generator_set_in_force": sorted(gens_in_force),
        "drop_sets_in_force": [list(d) for d in (drop_sets or [])],
        "module_sha256": harness_digests(),
    }


def _inference_supplement() -> dict:
    """The TRUE inference block for this task (AGENTS.md artifact policy)."""
    return {
        "requested_policy": "executor-implementation",
        "requested_policy_source":
            "ledger/handoffs/TASK-20260824-9a489e.yaml inference.policy",
        "backend": os.environ.get("AUTORESEARCH_BACKEND")
                   or "anthropic (claude_code runtime)",
        "resolved_model_id": os.environ.get("AUTORESEARCH_RESOLVED_MODEL")
                             or "claude-opus-5",
        "resolved_model_provenance": (
            "self-reported by the answering runtime in its own system context; "
            "NOT probe-verified in this session"),
        "probe_verified": False,
        "reasoning_effort": None,
        "reasoning_effort_note": ("handoff declares inference.reasoning_effort "
                                  "null; the executor subagent binding carries "
                                  "`medium` per CLAUDE.md"),
        "fallback_allowed": False,
        "fallback_used": False,
        "degraded_allowed": False,
        "degraded_requirements": None,
        "amazon_bedrock_used": False,
        "shared_runner_discrepancy": (
            "harness/runner.py writes run.inference.requested_policy = "
            "'executor-terra' into every manifest program-wide: it defines "
            "_inference_block() TWICE (module-level defs at lines 183 and 695) "
            "and Python binds the LAST definition, so the adapter-backed path is "
            "dead code. KNOWN, recorded by BATCH-f8bf86, and OUT OF SCOPE for "
            "this task -- IR-2 forbids editing harness/runner.py. The true "
            "values are the ones in this block. Infrastructure/provenance "
            "defect, never evidence about MD5 or SHA-1."),
    }


def _environment_supplement() -> dict:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                                     capture_output=True, text=True).stdout.strip(),
        "git_dirty_tracked": bool(subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"], cwd=REPO,
            capture_output=True, text=True).stdout.strip()),
        "network_requests_made_by_this_task": 0,
        "network_attestation": (
            "IR-6, stated precisely. ZERO network requests left this task by any "
            "route: no curl, wget, git fetch, package-manager invocation or MCP "
            "fetch was issued at any point, and no byte of any source of any "
            "tier was acquired. This task holds run_commands and deliberately "
            "not web_search; fetching through the shell would route around a "
            "declared role boundary."),
        "quarantine_attestation": (
            "IR-1, BY MECHANISM RATHER THAN BY INTENT, AND WITH ITS ONE "
            "INHERITED BYTE-READ DISCLOSED RATHER THAN GLOSSED. "
            "MECHANISM: the prefix coordination/goals/GOAL-MD5-001/quarantine/ "
            "appears in NO code path of harness/diffpath/controlpower.py -- the "
            "module contains no open() of it, no path join naming it and no "
            "string literal of it, and it neither parses, extracts, "
            "reconstructs nor fetches any part of it. No census entry was "
            "populated from recollection (IR-11). No network call of any kind "
            "was made (IR-6). "
            "DISCLOSED INHERITANCE: the contract states that this batch 'does "
            "not re-hash the payload: it does not touch it at all'. The "
            "COMMITTED census builder, harness/diffpath/census.py "
            "build_census(), calls quarantine_attestation() unconditionally, "
            "which opens the payload 'rb', hashes the bytes and discards them "
            "-- no decode, no parse, no field inspection. IR-2 forbids editing "
            "that committed module and the census is a required input, so that "
            "whole-file byte hash is re-entered once per census build. It is "
            "the same authorised whole-file sha256 CTL-QUAR performed in "
            "BATCH-f8bf86, it stays strictly inside IR-1's permitted operation, "
            "and NO DERIVED QUANTITY OF THE PAYLOAD -- not its byte count, not "
            "any field -- is computed or reported by this task. Recorded here "
            "as a protocol deviation from the contract's 'does not touch it at "
            "all' wording rather than repaired, because repairing it would mean "
            "editing a committed module."),
        "tier_a_content_obtained": False,
        "tier_b_content_obtained": False,
        "tier_c_content_obtained": False,
        "environment_compat_shim": COMPAT,
    }


def write_supplement(run_dir: str, suffix: str, gens, drop_sets=None,
                     extra: dict | None = None) -> str:
    import yaml
    doc = {"manifest_supplement": {
        "run_suffix": suffix,
        "experiment_id": EXPERIMENT_ID,
        "task_id": TASK_ID, "goal_id": GOAL_ID, "batch_id": BATCH_ID,
        "code_path_fingerprint": _fingerprint(gens, drop_sets),
        "armed_deadline_seconds": CEILINGS[suffix],
        "deadline_mechanism": ("signal.setitimer(ITIMER_REAL) inside the run "
                               "function, bracketed by "
                               "harness.runner.run_wrapped"),
        "seeds": SEEDS,
        "inference": _inference_supplement(),
        "environment": _environment_supplement(),
        "why_this_file_exists": (
            "harness/runner.py is a committed file this contract forbids "
            "editing (IR-2) and it cannot express code_path_fingerprint or this "
            "task's true inference block. code_path_fingerprint is ALSO written "
            "inside manifest.yaml at run.inputs.parameters, so the manifest "
            "itself does not lack it (IR-7)."),
    }}
    if extra:
        doc["manifest_supplement"].update(extra)
    path = os.path.join(run_dir, "manifest-supplement.yaml")
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(doc, fh, sort_keys=False, default_flow_style=False)
    return path


def _params(suffix: str, gens, drop_sets=None) -> dict:
    return {
        "experiment_id": EXPERIMENT_ID,          # IR-7, the LITERAL id
        "run_suffix": suffix,
        "code_path_fingerprint": _fingerprint(gens, drop_sets),
        "armed_deadline_seconds": CEILINGS[suffix],
        "seeds": SEEDS,
        "network_requests": 0,
    }


CERT_NONE = {"kind": "none", "statement": {
    "why": ("PURE MEASUREMENT RUN. No discrete-log solve and no factor-base "
            "relation is claimed anywhere in EXP-DIFFP-4b165f, and no collision, "
            "no differential path and no cryptanalytic result of any kind is "
            "claimed. certificate.kind is set to `none` EXPLICITLY, as "
            "docs/claims-and-verification.md requires of a measurement run.")}}


# ---------------------------------------------------------------------------
# RUN 1 -- CTL-FROZEN (pre-run digests) and CTL-REPRO
# ---------------------------------------------------------------------------

def run_frozen_and_repro(state: dict):
    pre = harness_digests()
    state["pre_digests"] = pre

    verdicts = EQ.run_all_checks(SEEDS["equivalence_generator_check"])
    measured: dict = {}
    for gid, v in verdicts.items():
        measured[f"{gid}.passed"] = v.passed
        measured[f"{gid}.failed"] = v.failed
        for k, val in (v.extra or {}).items():
            if isinstance(val, int):
                measured[f"{gid}.{k}"] = val
    for rng_key, d in (verdicts["E6"].extra or {}).get("per_step_range", {}).items():
        measured[f"E6.step_range_{rng_key}.conditions_satisfied"] = \
            d["conditions_satisfied"]

    census = build_census(SEEDS["planted_path_generation_md5"],
                         SEEDS["planted_path_generation_sha1"], 8)
    state["census"] = census
    adj = ADJ.Adjudicator(census, STRICT)
    state["adj"] = adj
    plant = ADJ.ctl_plant(adj, census)
    null = ADJ.ctl_null(adj, census, SEEDS, n=1000)
    measured["CTL-PLANT.recall_hits"] = plant["recall_hits"]
    measured["CTL-PLANT.recall_attempts"] = plant["recall_attempts"]
    for fam, d in null["families"].items():
        measured[f"CTL-NULL.{fam}.strict_false_positives"] = \
            d["strict_false_positives"]
        measured[f"CTL-NULL.{fam}.permissive_false_positives"] = \
            d["permissive_false_positives"]

    table = []
    agree = 0
    for key, expected in PRE_REGISTERED.items():
        got = measured.get(key, "NOT MEASURED")
        ok = (got == expected)
        agree += ok
        table.append({"quantity": key, "pre_registered": expected,
                      "measured": got, "exact_agreement": ok})
    disagreements = [r for r in table if not r["exact_agreement"]]

    # the run-time-derived strict key component list, beside the declared one
    derived: list = []
    for e in census.shadow:
        for name in key_components(ADJ.serialize(e.obj, STRICT)):
            if name not in derived:
                derived.append(name)
    derived_matches = sorted(derived) == sorted(DECLARED_KEY_COMPONENTS)

    e6_00 = measured.get("E6.step_range_(0, 0).conditions_satisfied")
    lines = [
        f"CTL-FROZEN pre-run digests over {pre['criterion_set_files']} "
        f"criterion-set files",
        f"CTL-REPRO exact agreement {agree}/{len(PRE_REGISTERED)}",
        f"CTL-REPRO E6 step_range (0,0) conditions_satisfied = {e6_00} "
        f"(pre-registered 2089, the CORRECTED value of CORR-20260824-e0088c; "
        f"execution-report.yaml of BATCH-f8bf86 states 2094)",
        f"derived strict key components = {derived} (declared match: "
        f"{derived_matches})",
    ] + [f"CTL-REPRO DISAGREEMENT: {r['quantity']} pre-registered "
         f"{r['pre_registered']} measured {r['measured']}" for r in disagreements]

    raw = {
        "CTL_FROZEN_pre_run": pre,
        "CTL_REPRO": {
            "comparison_table": table,
            "exact_agreement_fraction": f"{agree}/{len(PRE_REGISTERED)}",
            "disagreements": disagreements,
            "E6_step_range_0_0_conditions_satisfied": e6_00,
            "E6_2089_vs_2094": (
                "The contract PRE-REGISTERED 2089, the corrected value of "
                "CORR-20260824-e0088c, and this is that correction's first "
                f"confirmation under a charged run. MEASURED: {e6_00}. "
                "Reported, not reconciled."),
            "CTL_PLANT_full_record": plant,
            "CTL_NULL_full_record": null,
            "provenance_of_the_pre_registered_values": (
                "quoted in the frozen contract from EV-DIFFP-b878aa O-1/O-2, "
                "validation-report joint_J1 and CORR-20260824-e0088c; measured "
                "by TASK-20260824-c6625a, TASK-20260824-3bd362 and "
                "TASK-20260824-c40847, not by this task and not by the "
                "Coordinator"),
        },
        "key_components": {
            "declared_in_contract": list(DECLARED_KEY_COMPONENTS),
            "derived_at_run_time": derived,
            "agree": derived_matches,
            "hard_term": ("the contract requires the component list to be "
                          "DERIVED at run time and reported beside the declared "
                          "one; a disagreement is a STOP and an infrastructure "
                          "finding"),
        },
        "census_counts": census.counts(),
    }
    metrics = {
        "ctl_repro_agreements": agree,
        "ctl_repro_values": len(PRE_REGISTERED),
        "ctl_repro_exact": agree == len(PRE_REGISTERED),
        "ctl_plant_hits": plant["recall_hits"],
        "ctl_plant_attempts": plant["recall_attempts"],
        "ctl_null_strict_false_positives_total": null["strict_false_positive_total"],
        "ctl_null_permissive_false_positives_total":
            null["permissive_false_positive_total"],
        "e6_step_range_0_0_conditions_satisfied": e6_00,
        "key_component_list_agrees_with_contract": derived_matches,
        "frozen_pre_run_files": pre["criterion_set_files"],
    }
    return RunResult(
        run_suffix="frozen-and-repro", curve_id="n/a-hash-primitive",
        seed=SEEDS["equivalence_generator_check"],
        parameters=_params("frozen-and-repro", STRICT),
        metrics=metrics, certificate=CERT_NONE, valid=True,
        stdout="\n".join(lines) + "\n", stderr="", raw=raw), raw


# ---------------------------------------------------------------------------
# RUN 2 -- CTL-GEN-ACT and CTL-TWOSIDED
# ---------------------------------------------------------------------------

GEN_SUBSETS = [("E1", ("E1",)), ("E2", ("E2",)), ("E3", ("E3",)),
               ("E4", ("E4",)), ("E5", ("E5",)), ("E6", ("E6",)),
               ("{E4,E5}", ("E4", "E5")),
               ("{E1,E3,E4,E5}", ("E1", "E3", "E4", "E5"))]


def _verdicts_over(adjA, adjB, objs, mode):
    fa, fb = FastAdj(adjA), FastAdj(adjB)
    changed = []
    for o in objs:
        va = fa.verdict(o, mode)[0]
        vb = fb.verdict(o, mode)[0]
        if va != vb:
            changed.append({"object": o.id, "with_generator": va,
                            "without_generator": vb})
    return {"objects": len(objs), "verdicts_changed": len(changed),
            "changed_sample": changed[:8]}


def run_generator_action(state: dict):
    census = state["census"]
    adj = state["adj"]
    two = twosided_objects(census)

    # the declared verdict-change object set
    sample_null = []
    for fam, d in null_draws(census, n=20).items():
        sample_null += d["draws"]
    objs = [e.obj for e in census.shadow]
    for e in census.shadow:
        objs += ADJ.orbit_images(e.obj, STRICT)
    objs += two["T1"] + two["T2"] + [two["T3"], two["T4"], two["T4_flag_forced"]]
    objs += sample_null
    state["gen_act_object_count"] = len(objs)

    profile = {}
    for label, gset in GEN_SUBSETS:
        G = frozenset(gset)
        images = {}
        for e in census.shadow:
            try:
                images[e.id] = len(ADJ.orbit_images(e.obj, G))
            except Exception as exc:                       # noqa: BLE001
                images[e.id] = f"ERROR {type(exc).__name__}: {exc}"
        per_prim = {}
        for prim in ("md5", "sha1"):
            vals = [images[e.id] for e in census.shadow if e.primitive == prim]
            per_prim[prim] = {"per_object": vals,
                              "total": sum(v for v in vals if isinstance(v, int))}

        with_g, without_g = STRICT | G, STRICT - G
        comp_changes = {}
        for prim in ("md5", "sha1"):
            e = [x for x in census.shadow if x.primitive == prim][0]
            ka = dict(ADJ.serialize(e.obj, with_g))
            kb = dict(ADJ.serialize(e.obj, without_g))
            names = set(ka) | set(kb)
            comp_changes[prim] = {
                "components_with_generator": key_components(
                    ADJ.serialize(e.obj, with_g)),
                "components_without_generator": key_components(
                    ADJ.serialize(e.obj, without_g)),
                "component_names_that_change": sorted(
                    n for n in names
                    if ka.get(n, _MISSING) is not kb.get(n, _MISSING)
                    and ka.get(n, _MISSING) != kb.get(n, _MISSING)),
                "serialised_key_differs": ADJ.serialize(e.obj, with_g)
                                          != ADJ.serialize(e.obj, without_g),
            }

        strict_cmp = _verdicts_over(
            ADJ.Adjudicator(census, with_g), ADJ.Adjudicator(census, without_g),
            objs, "strict")
        perm_cmp = _verdicts_over(
            ADJ.Adjudicator(census, STRICT, PERMISSIVE),
            ADJ.Adjudicator(census, STRICT, PERMISSIVE - G),
            objs, "permissive")

        profile[label] = {
            "generator_set": sorted(gset),
            "a_orbit_images_emitted": {"per_entry": images, "per_primitive": per_prim},
            "b_key_components_changed": comp_changes,
            "c_verdict_changes": {"strict_mode": strict_cmp,
                                  "permissive_mode": perm_cmp},
            "reported_separately_note": (
                "(a) orbit ACTION, (b) key effect and (c) verdict effect are "
                "three separate measurements and are reported separately: a "
                "generator can emit no orbit image and still change the key, or "
                "do neither and still be VERIFIED. VERIFICATION STATUS IS NOT "
                "MEASURED HERE and is not implied by any of these numbers."),
        }

    # --- CTL-TWOSIDED
    fast = FastAdj(adj)
    e4_removed = ADJ.Adjudicator(census, STRICT - {"E4"})
    ts = {}
    t1 = [{"object": o.id, "strict": fast.verdict(o, "strict")[0],
           "permissive": fast.verdict(o, "permissive")[0]} for o in two["T1"]]
    ts["T1"] = {"pre_registered": TWOSIDED_PREREGISTERED["T1"], "objects": t1,
                "met": all(r["strict"] == "NON-MEMBER"
                           and r["permissive"] == "MEMBER" for r in t1)}
    t2 = [{"object": o.id, "primitive": o.primitive,
           "strict": fast.verdict(o, "strict")[0],
           "permissive": fast.verdict(o, "permissive")[0]} for o in two["T2"]]
    ts["T2"] = {"pre_registered": TWOSIDED_PREREGISTERED["T2"], "objects": t2,
                "met": all(r["strict"] == "NON-MEMBER"
                           and r["permissive"] == "MEMBER" for r in t2)}
    t3o = two["T3"]
    t3_with = fast.verdict(t3o, "strict")[0]
    t3_without = FastAdj(e4_removed).verdict(t3o, "strict")[0]
    ts["T3"] = {"pre_registered": TWOSIDED_PREREGISTERED["T3"],
                "object": t3o.id,
                "with_E4_in_strict_group": t3_with,
                "with_E4_removed_from_strict_group": t3_without,
                "step_delta_unchanged_by_construction":
                    two["T3_signed_representation_changed_but_step_delta_equal"],
                "met": t3_with == "MEMBER" and t3_without == "NON-MEMBER"}
    t4o, t4f = two["T4"], two["T4_flag_forced"]
    t4rec = {
        "pre_registered": TWOSIDED_PREREGISTERED["T4"],
        "object": t4o.id,
        "in_linearized_code_recomputed": two["T4_in_linearized_code_recomputed"],
        "strict": fast.verdict(t4o, "strict")[0],
        "permissive": fast.verdict(t4o, "permissive")[0],
        "closest": fast.closest(t4o),
        "flag_forced_true": {"strict": fast.verdict(t4f, "strict")[0],
                             "permissive": fast.verdict(t4f, "permissive")[0],
                             "closest": fast.closest(t4f)},
    }
    t4rec["met"] = (t4rec["strict"] == "NON-MEMBER"
                    and t4rec["permissive"] == "NON-MEMBER"
                    and t4rec["flag_forced_true"]["strict"] == "NON-MEMBER"
                    and t4rec["flag_forced_true"]["permissive"] == "NON-MEMBER"
                    and t4rec["closest"]["closest_distance"]
                    == t4rec["flag_forced_true"]["closest"]["closest_distance"])
    t4rec["distance_is_a_diagnostic"] = (
        "closest_distance is a REPORTED DIAGNOSTIC, not a decision variable and "
        "not a margin (EV-DIFFP-b878aa O-9: an object at distance 0 adjudicates "
        "NON-MEMBER and one at distance 1277 adjudicates MEMBER under "
        "permissive).")
    ts["T4"] = t4rec
    t5 = [{"object": o.id, "strict": fast.verdict(o, "strict")[0]}
          for o in two["T5"]]
    ts["T5"] = {"pre_registered": TWOSIDED_PREREGISTERED["T5"],
                "member_fraction":
                    f"{sum(1 for r in t5 if r['strict'] == 'MEMBER')}/{len(t5)}",
                "objects": t5,
                "met": all(r["strict"] == "MEMBER" for r in t5)}
    ts["fidelity_check_of_the_fast_membership_path"] = fidelity_check(
        adj, fast, two["T1"] + two["T2"] + [t3o, t4o] + two["T5"][:4])

    lines = [f"CTL-GEN-ACT profiled {len(GEN_SUBSETS)} generator sets over "
             f"{len(objs)} objects"]
    for label, rec in profile.items():
        lines.append(
            f"  {label}: images md5={rec['a_orbit_images_emitted']['per_primitive']['md5']['total']} "
            f"sha1={rec['a_orbit_images_emitted']['per_primitive']['sha1']['total']}, "
            f"strict verdict changes="
            f"{rec['c_verdict_changes']['strict_mode']['verdicts_changed']}, "
            f"permissive verdict changes="
            f"{rec['c_verdict_changes']['permissive_mode']['verdicts_changed']}")
    for tid in ("T1", "T2", "T3", "T4", "T5"):
        lines.append(f"  CTL-TWOSIDED {tid}: pre-registered answer met="
                     f"{ts[tid]['met']}")

    raw = {"CTL_GEN_ACT": profile, "CTL_TWOSIDED": ts,
           "verdict_change_object_set": {
               "count": len(objs),
               "composition": ("the 16 planted entries, their orbit images under "
                               "the strict set, the CTL-TWOSIDED decoys, and a "
                               "DECLARED SAMPLE of 20 null draws per family (60) "
                               "regenerated from the declared family seeds")}}
    metrics = {"generator_sets_profiled": len(GEN_SUBSETS),
               "objects_in_verdict_change_set": len(objs),
               **{f"twosided_{t}_met": ts[t]["met"]
                  for t in ("T1", "T2", "T3", "T4", "T5")},
               **{f"images_{label}_sha1": profile[label]
                  ["a_orbit_images_emitted"]["per_primitive"]["sha1"]["total"]
                  for label, _ in GEN_SUBSETS},
               **{f"images_{label}_md5": profile[label]
                  ["a_orbit_images_emitted"]["per_primitive"]["md5"]["total"]
                  for label, _ in GEN_SUBSETS}}
    return RunResult(
        run_suffix="generator-action", curve_id="n/a-hash-primitive",
        seed=SEEDS["equivalence_generator_check"],
        parameters=_params("generator-action", STRICT),
        metrics=metrics, certificate=CERT_NONE, valid=True,
        stdout="\n".join(lines) + "\n", stderr="", raw=raw), raw


# ---------------------------------------------------------------------------
# RUN 3 -- CTL-NULL-D, null family (d), against the HONEST adjudicator only
# ---------------------------------------------------------------------------

def _cell(store: dict, key: str, k: int, arm: str, draw_type: str,
          primitive: str) -> dict:
    return store.setdefault(key, {
        "primitive": primitive, "k": k, "arm": arm, "draw_type": draw_type,
        "draws": 0, "strict_member": 0, "strict_non_member": 0,
        "permissive_member": 0, "permissive_non_member": 0,
        "attribution_distribution": {}, "attribution_note": (
            "H-3: for every k >= 1 rejection, the SET of canonical-key component "
            "names on which the draw's canonical form differs from that of its "
            "OWN source census entry -- the components that COULD have decided "
            "it. A control whose rejections are decided by a component other "
            "than the one it perturbs has NO POWER over the component it was "
            "built for."),
        "closest_non_matching_draw": None,
    })


def _note_attr(cell: dict, attr: list) -> None:
    key = "+".join(attr) if attr else "(none: canonical forms identical)"
    cell["attribution_distribution"][key] = \
        cell["attribution_distribution"].get(key, 0) + 1


def _note_closest(cell: dict, obj, fast, k: int) -> None:
    if k == 0:
        return
    c = fast.closest(obj)
    if c["closest_distance"] is None:
        return
    cur = cell["closest_non_matching_draw"]
    if cur is None or c["closest_distance"] < cur["closest_distance"]:
        cell["closest_non_matching_draw"] = {
            "candidate": obj.id, **c,
            "distance_units": ("bits of the concatenated message-difference and "
                               "per-step modular-difference vector"),
            "LABEL": ("A REPORTED DIAGNOSTIC, NOT A DECISION VARIABLE AND NOT A "
                      "MARGIN. EV-DIFFP-b878aa O-9 measured that this distance "
                      "neither bounds nor tracks the verdict in either "
                      "direction."),
        }


def family_d_primary(census, fast, strict_keys: dict, both_modes=True,
                     rows=None, entry_keys=None):
    """The primary arm. `rows` is None for run 3 and the row list in the battery."""
    store: dict = {}
    rng = random.Random(SEEDS["null_draw_message_difference_perturbed"])
    members: list = []
    for e in census.shadow:
        src = e.obj
        nbits = md_bits(src)
        src_key = strict_keys.get(e.id)      # None on the battery path
        for k in K_VALUES:
            plan = [("deterministic", tuple(range(k)))]
            if k >= 1:
                plan += [("seeded", tuple(sorted(rng.sample(range(nbits), k))))
                         for _ in range(R_SEEDED)]
            for draw_type, pos in plan:
                obj = perturb_message_difference(
                    src, pos, f"k{k}-{draw_type}-{'.'.join(map(str, pos))}")
                if rows is not None:
                    keys = variant_keys(obj, STRICT)
                    for row in rows:
                        c = _cell(row.nulld,
                                  f"{e.primitive}|k={k}|{draw_type}", k,
                                  "primary", draw_type, e.primitive)
                        c["draws"] += 1
                        hit = row.lookup(keys, "strict")
                        if hit:
                            c["strict_member"] += 1
                            if k >= 1 and len(row.nulld_member_examples) < 10:
                                row.nulld_member_examples.append(
                                    {"candidate": obj.id, "source_entry": e.id,
                                     "k": k, "flipped_bit_positions": list(pos),
                                     "matched_entry": hit})
                        else:
                            c["strict_non_member"] += 1
                            if k >= 1:
                                _note_attr(c, attribution(
                                    ablated_canonical_inside(keys, row.drop_set),
                                    ablated_canonical_inside(
                                        entry_keys["strict"][e.id],
                                        row.drop_set)))
                    continue
                c = _cell(store, f"{e.primitive}|k={k}|{draw_type}", k,
                          "primary", draw_type, e.primitive)
                c["draws"] += 1
                sv, sm, skey = fast.verdict(obj, "strict")
                if sv == "MEMBER":
                    c["strict_member"] += 1
                else:
                    c["strict_non_member"] += 1
                    if k >= 1:
                        _note_attr(c, attribution(skey, src_key))
                if both_modes:
                    pv, pm, _ = fast.verdict(obj, "permissive")
                    if pv == "MEMBER":
                        c["permissive_member"] += 1
                    else:
                        c["permissive_non_member"] += 1
                else:
                    pv, pm = "NOT MEASURED", None
                _note_closest(c, obj, fast, k)
                if k >= 1 and sv == "MEMBER":
                    members.append({
                        "candidate": obj.id, "source_entry": e.id, "k": k,
                        "draw_type": draw_type, "flipped_bit_positions": list(pos),
                        "strict_matched_entry": sm,
                        "permissive_verdict": pv, "permissive_matched_entry": pm,
                        "draw_canonical_form": [list(map(str, p)) for p in skey],
                        "source_canonical_form": [list(map(str, p))
                                                  for p in src_key],
                        "component_attribution": attribution(skey, src_key),
                        "why_it_is_reported_in_full": (
                            "contract stopping_rules: a k >= 1 MEMBER on the "
                            "honest adjudicator is a COUNTEREXAMPLE OBJECT and a "
                            "required artifact. It is reported and the run "
                            "CONTINUES; no perturbation rule is changed after "
                            "seeing it."),
                    })
    return store, members


def run_null_family_d(state: dict):
    census, adj = state["census"], state["adj"]
    fast = FastAdj(adj)
    strict_keys = {e.id: ADJ.canonical(e.obj, STRICT) for e in census.shadow}

    primary, members = family_d_primary(census, fast, strict_keys)

    # --- D-SHA1-INCODE
    incode: dict = {}
    rng = random.Random(SEEDS["null_draw_message_difference_perturbed"])
    weights: list = []
    for e in census.shadow:
        if e.primitive != "sha1":
            continue
        plan = [("deterministic", tuple([1] + [0] * 15))]
        plan += [("seeded", tuple(rng.getrandbits(32) for _ in range(16)))
                 for _ in range(R_SEEDED)]
        for draw_type, w16 in plan:
            if not any(w16):
                continue
            obj = perturb_by_codeword(e.obj, w16, f"{draw_type}")
            c = _cell(incode, f"sha1|in_code|{draw_type}", 1, "D-SHA1-INCODE",
                      draw_type, "sha1")
            c["draws"] += 1
            weights.append(obj.path_data["codeword_hamming_weight"])
            c.setdefault("in_linearized_code_true", 0)
            c["in_linearized_code_true"] += 1 if obj.in_linearized_code else 0
            sv, sm, skey = fast.verdict(obj, "strict")
            if sv == "MEMBER":
                c["strict_member"] += 1
            else:
                c["strict_non_member"] += 1
                _note_attr(c, attribution(skey, strict_keys[e.id]))
            pv, _, _ = fast.verdict(obj, "permissive")
            c["permissive_member" if pv == "MEMBER"
              else "permissive_non_member"] += 1
            _note_closest(c, obj, fast, 1)

    # --- D-VD3-PROFILE (strict mode only, reported SEPARATELY, never counted
    #     into family (d)'s pass/fail)
    vd3: dict = {}
    rng = random.Random(SEEDS["null_draw_message_difference_perturbed"])
    for e in census.shadow:
        if e.primitive != "sha1":
            continue
        for s in EQ.E1_SHIFTS:
            img = EQ.act_E1_shift(e.obj, s)
            nbits = md_bits(img)
            for k in K_VALUES:
                plan = [("deterministic", tuple(range(k)))]
                if k >= 1:
                    plan += [("seeded",
                              tuple(sorted(rng.sample(range(nbits), k))))
                             for _ in range(R_SEEDED)]
                for draw_type, pos in plan:
                    obj = perturb_message_difference(img, pos, f"vd3s{s}k{k}")
                    c = _cell(vd3, f"sha1|shift={s}|k={k}|{draw_type}", k,
                              "D-VD3-PROFILE", draw_type, "sha1")
                    c["draws"] += 1
                    sv, _, skey = fast.verdict(obj, "strict")
                    if sv == "MEMBER":
                        c["strict_member"] += 1
                    else:
                        c["strict_non_member"] += 1
                        if k >= 1:
                            _note_attr(c, attribution(skey, strict_keys[e.id]))

    def _fold(store, keyfn):
        out: dict = {}
        for cell in store.values():
            kk = keyfn(cell)
            r = out.setdefault(kk, {"draws": 0, "strict_member": 0,
                                    "permissive_member": 0,
                                    "attribution_distribution": {}})
            r["draws"] += cell["draws"]
            r["strict_member"] += cell["strict_member"]
            r["permissive_member"] += cell["permissive_member"]
            for a, n in cell["attribution_distribution"].items():
                r["attribution_distribution"][a] = \
                    r["attribution_distribution"].get(a, 0) + n
        for r in out.values():
            r["strict_non_member_fraction"] = \
                f"{r['draws'] - r['strict_member']}/{r['draws']}"
            r["permissive_non_member_fraction"] = \
                f"{r['draws'] - r['permissive_member']}/{r['draws']}"
        return out

    k0 = {kk: c for kk, c in primary.items() if c["k"] == 0}
    k0_member = sum(c["strict_member"] for c in k0.values())
    k0_draws = sum(c["draws"] for c in k0.values())

    lines = [
        f"CTL-NULL-D k=0 arm (KNOWN ANSWER MEMBER): {k0_member}/{k0_draws} "
        f"strict MEMBER",
        f"CTL-NULL-D primary k>=1 strict MEMBER verdicts: {len(members)}",
    ]
    for kk, r in sorted(_fold(primary, lambda c: f"{c['primitive']}|k={c['k']}").items()):
        lines.append(f"  primary {kk}: strict NON-MEMBER "
                     f"{r['strict_non_member_fraction']}, permissive NON-MEMBER "
                     f"{r['permissive_non_member_fraction']}, attribution "
                     f"{r['attribution_distribution']}")
    for kk, r in sorted(_fold(incode, lambda c: c["draw_type"]).items()):
        lines.append(f"  D-SHA1-INCODE {kk}: strict NON-MEMBER "
                     f"{r['strict_non_member_fraction']}, attribution "
                     f"{r['attribution_distribution']}")
    for kk, r in sorted(_fold(vd3, lambda c: f"k={c['k']}").items()):
        lines.append(f"  D-VD3-PROFILE {kk}: strict NON-MEMBER "
                     f"{r['strict_non_member_fraction']} (REPORTED SEPARATELY; "
                     f"NEVER counted into family (d)'s pass/fail)")

    raw = {
        "CTL_NULL_D": {
            "perturbation_declaration": PERTURBATION_DECLARATION,
            "primary_arm": {
                "per_cell": primary,
                "folded_per_primitive_and_k": _fold(
                    primary, lambda c: f"{c['primitive']}|k={c['k']}"),
                "folded_per_primitive_k_and_draw_type": _fold(
                    primary,
                    lambda c: f"{c['primitive']}|k={c['k']}|{c['draw_type']}"),
                "k0_arm": {"known_answer": "MEMBER",
                           "strict_member_fraction": f"{k0_member}/{k0_draws}",
                           "per_cell": k0,
                           "note": ("the k = 0 arm is constructed through the "
                                    "IDENTICAL perturbation code path with an "
                                    "empty flip set and is ADJUDICATED, not "
                                    "assumed")},
                "k_ge_1_MEMBER_verdicts_in_full": members,
            },
            "sub_arm_D_SHA1_INCODE": {
                "per_cell": incode,
                "folded": _fold(incode, lambda c: c["draw_type"]),
                "codeword_hamming_weight": {
                    "n": len(weights),
                    "min": min(weights) if weights else None,
                    "max": max(weights) if weights else None,
                    "mean": (sum(weights) / len(weights)) if weights else None},
                "construction": ("dv XOR sha1_expand(w16, 80): the SHA-1 "
                                 "expansion is GF(2)-linear, so the perturbed DV "
                                 "is again a codeword and the HONESTLY "
                                 "RECOMPUTED in_linearized_code stays True. This "
                                 "is what isolates the message difference from "
                                 "the FLAG."),
            },
            "sub_arm_D_VD3_PROFILE": {
                "per_cell": vd3,
                "folded_per_k": _fold(vd3, lambda c: f"k={c['k']}"),
                "folded_per_shift": _fold(vd3, lambda c: c["arm"] + "|" + str(
                    c["primitive"])),
                "what_it_is": ("a MEASUREMENT OF A KNOWN DEFECT (VD-3), not a "
                               "repair and not a known-correct answer. It is "
                               "REPORTED SEPARATELY and is NEVER counted into "
                               "family (d)'s pass/fail."),
                "pre_registered_expectation": (
                    "MEMBER, i.e. the perturbation is ERASED, because "
                    "EQ.align_E1 discards the declared dv and recomputes it from "
                    "dv_seed_window whenever step_start > 0"),
            },
            "fidelity_check_of_the_fast_membership_path": fidelity_check(
                adj, fast, [perturb_message_difference(e.obj, (0,), "fid")
                            for e in census.shadow]),
        },
        "variant_mirror_check": dict(VARIANT_MIRROR_CHECK),
    }
    metrics = {
        "k0_strict_member": k0_member, "k0_draws": k0_draws,
        "k_ge_1_strict_member_verdicts": len(members),
        "primary_draws": sum(c["draws"] for c in primary.values()),
        "incode_draws": sum(c["draws"] for c in incode.values()),
        "vd3_draws": sum(c["draws"] for c in vd3.values()),
        "vd3_strict_member": sum(c["strict_member"] for c in vd3.values()),
        "incode_strict_member": sum(c["strict_member"] for c in incode.values()),
    }
    return RunResult(
        run_suffix="null-family-d", curve_id="n/a-hash-primitive",
        seed=SEEDS["null_draw_message_difference_perturbed"],
        parameters=_params("null-family-d", STRICT),
        metrics=metrics, certificate=CERT_NONE, valid=True,
        stdout="\n".join(lines) + "\n", stderr="", raw=raw), raw


# ---------------------------------------------------------------------------
# RUNS 4 and 5 -- CTL-ABL, the ablation battery
# ---------------------------------------------------------------------------

GROUP1_ROWS = [
    (1, (), "HONEST (unmodified)",
     {"CTL_PLANT": "96/96", "CTL_NULL_strict_of_3000": 0, "detected": "n/a"}),
    (2, ("message_difference",), "message_difference deleted",
     {"CTL_PLANT": "96/96", "CTL_NULL_strict_of_3000": 0, "detected": "NO"}),
    (3, ("step_delta",), "step_delta deleted",
     {"CTL_PLANT": "96/96", "CTL_NULL_strict_of_3000": 6, "detected": "YES"}),
    (4, ("in_linearized_code",), "in_linearized_code deleted",
     {"CTL_PLANT": "96/96", "CTL_NULL_strict_of_3000": 0, "detected": "NO"}),
    (5, ("message_difference", "in_linearized_code"), "both deleted",
     {"CTL_PLANT": "96/96", "CTL_NULL_strict_of_3000": 0, "detected": "NO"}),
    (6, ("message_difference", "step_delta", "block_index", "in_linearized_code"),
     "everything except primitive and length",
     {"CTL_PLANT": "96/96", "CTL_NULL_strict_of_3000": 3000, "detected": "YES"}),
]


def _battery(state: dict, rows: list, suffix: str):
    census, adj = state["census"], state["adj"]
    entry_keys = {"strict": {}, "permissive": {}}
    for e in census.shadow:
        entry_keys["strict"][e.id] = variant_keys(e.obj, STRICT)
        entry_keys["permissive"][e.id] = variant_keys(e.obj, PERMISSIVE)
    for row in rows:
        row.build_index(entry_keys)

    # --- CTL-PLANT, over the identical 96 attempts (strict mode, as committed)
    for e in census.shadow:
        cases = [("planted", e.obj)] + [
            ((img.path_data or {}).get("kind", "image"), img)
            for img in ADJ.orbit_images(e.obj, STRICT)]
        for cls, o in cases:
            keys = variant_keys(o, STRICT)
            for row in rows:
                row.plant_attempts += 1
                if row.lookup(keys, "strict"):
                    row.plant_hits += 1
                elif len(row.plant_misses) < 20:
                    row.plant_misses.append({"planted_entry": e.id,
                                             "case": cls, "candidate": o.id})

    # --- CTL-NULL, the 3000 declared draws in three families, both modes
    for fam, d in null_draws(census, n=1000).items():
        for row in rows:
            row.null[fam] = {"draws": 0, "seed": d["seed"],
                             "strict_false_positives": 0,
                             "permissive_false_positives": 0,
                             "false_positive_examples": []}
        for obj in d["draws"]:
            ks = variant_keys(obj, STRICT)
            kp = variant_keys(obj, PERMISSIVE)
            for row in rows:
                r = row.null[fam]
                r["draws"] += 1
                hs, hp = row.lookup(ks, "strict"), row.lookup(kp, "permissive")
                if hs:
                    r["strict_false_positives"] += 1
                    if len(r["false_positive_examples"]) < 5:
                        r["false_positive_examples"].append(
                            {"candidate": obj.id, "mode": "strict",
                             "matched": hs})
                if hp:
                    r["permissive_false_positives"] += 1
                    if len(r["false_positive_examples"]) < 10:
                        r["false_positive_examples"].append(
                            {"candidate": obj.id, "mode": "permissive",
                             "matched": hp})

    # --- CTL-NULL-D primary arm, STRICT MODE ONLY (declared scope, see note)
    family_d_primary(census, None, {}, both_modes=False, rows=rows,
                     entry_keys=entry_keys)

    records = [row.record() for row in rows]
    lines = [f"CTL-ABL {suffix}: {len(rows)} rows"]
    for r in records:
        lines.append(
            f"  row {r['row']} drop_set={r['drop_set']}: CTL-PLANT "
            f"{r['CTL_PLANT']['fraction']}, CTL-NULL strict FP "
            f"{r['CTL_NULL_strict_false_positives_total']}/3000, permissive FP "
            f"{r['CTL_NULL_permissive_false_positives_total']}/3000, "
            f"CTL-NULL-D k>=1 strict MEMBER "
            f"{r['CTL_NULL_D_strict_member_k_ge_1']}, OLD "
            f"{r['detected_by_OLD_suite']}, STRENGTHENED "
            f"{r['detected_by_STRENGTHENED_suite']}")
    return records, lines


def run_battery_group1(state: dict):
    rows = [Row(rid, ds, label, "group 1 -- the replication of EV-DIFFP-b878aa "
                "O-7's six declared rows", pre)
            for rid, ds, label, pre in GROUP1_ROWS]
    records, lines = _battery(state, rows, "group 1")
    for rec in records:
        pre = rec["pre_registered"] or {}
        rec["pre_registered_beside_measured"] = {
            "pre_registered_CTL_PLANT": pre.get("CTL_PLANT"),
            "measured_CTL_PLANT": rec["CTL_PLANT"]["fraction"],
            "CTL_PLANT_agrees": pre.get("CTL_PLANT") == rec["CTL_PLANT"]["fraction"],
            "pre_registered_CTL_NULL_strict_of_3000":
                pre.get("CTL_NULL_strict_of_3000"),
            "measured_CTL_NULL_strict_of_3000":
                rec["CTL_NULL_strict_false_positives_total"],
            "CTL_NULL_agrees": (pre.get("CTL_NULL_strict_of_3000")
                                == rec["CTL_NULL_strict_false_positives_total"]),
            "pre_registered_detected_by_OLD_suite": pre.get("detected"),
            "measured_detected_by_OLD_suite": rec["detected_by_OLD_suite"],
        }
    state["group1"] = records

    # inside- vs outside-minimisation projection comparison, six declared rows
    census = state["census"]
    cmp_rows = []
    for rid, ds, label, _pre in GROUP1_ROWS:
        diff = same = 0
        examples = []
        for e in census.shadow:
            for mode, gens in (("strict", STRICT), ("permissive", PERMISSIVE)):
                keys = variant_keys(e.obj, gens)
                a = ablated_canonical_inside(keys, ds)
                b = ablated_canonical_outside(keys, ds)
                if a == b:
                    same += 1
                else:
                    diff += 1
                    if len(examples) < 3:
                        examples.append({"object": e.id, "mode": mode})
        cmp_rows.append({"row": rid, "drop_set": list(ds), "identical": same,
                         "different": diff, "examples": examples})
    state["projection_comparison"] = cmp_rows

    lines.append("inside- vs outside-minimisation projection: "
                 + ", ".join(f"row {c['row']} same={c['identical']} "
                             f"diff={c['different']}" for c in cmp_rows))
    raw = {"CTL_ABL_group_1": records,
           "inside_vs_outside_minimisation": {
               "rows": cmp_rows,
               "which_is_the_contract_value": (
                   "THE INSIDE-MINIMISATION FORM, min(project(serialize(v,gens))) "
                   "over the identical variant list, which is exactly what an "
                   "edit to serialize() would have produced. A difference is a "
                   "reportable finding about the canonicaliser, not a defect to "
                   "be tuned away (contract ablation_mechanism)."),
           },
           "variant_mirror_check": dict(VARIANT_MIRROR_CHECK),
           "family_d_in_the_battery_is_strict_only": (
               "DECLARED SCOPE, NOT A MERGE. In the battery CTL-NULL-D's primary "
               "arm is adjudicated in STRICT MODE ONLY, because the DETECTED "
               "verdict is read from strict-mode outcomes and the permissive "
               "family-(d) counts are measured in full in run 3 "
               "(null-family-d). Strict and permissive remain SEPARATE FIELDS "
               "and are never merged (IR-4); the permissive column of the "
               "battery's family-(d) cells is reported as NOT MEASURED rather "
               "than as zero.")}
    metrics = {f"row{r['row']}_plant_hits": r["CTL_PLANT"]["hits"] for r in records}
    metrics.update({f"row{r['row']}_null_strict_fp":
                    r["CTL_NULL_strict_false_positives_total"] for r in records})
    metrics.update({f"row{r['row']}_nulld_member_k_ge_1":
                    r["CTL_NULL_D_strict_member_k_ge_1"] for r in records})
    metrics["group1_rows"] = len(records)
    return RunResult(
        run_suffix="ablation-battery-declared-rows", curve_id="n/a-hash-primitive",
        seed=SEEDS["null_draw_md5_delta_m"],
        parameters=_params("ablation-battery-declared-rows", STRICT,
                           [r.drop_set for r in rows]),
        metrics=metrics, certificate=CERT_NONE, valid=True,
        stdout="\n".join(lines) + "\n", stderr="", raw=raw), raw


def run_battery_group2(state: dict):
    derived = state["derived_components"]
    rows = [Row(100 + i, (name,), f"{name} deleted (depth-1 lattice)",
                "group 2 -- the COMPLETE depth-1 single-deletion lattice, "
                "reported SEPARATELY and NEVER merged into group 1's fraction")
            for i, name in enumerate(derived, start=1)]
    records, lines = _battery(state, rows, "group 2 (complete depth-1 lattice)")
    state["group2"] = records
    post = harness_digests()
    frozen = compare_digests(state["pre_digests"], post)
    state["post_digests"] = post
    state["frozen_comparison"] = frozen
    lines.append(f"CTL-FROZEN post-run re-verification: {frozen['fraction']} "
                 f"identical, criterion_met={frozen['criterion_met']}, "
                 f"changed={frozen['changed']}")
    raw = {"CTL_ABL_group_2": records,
           "lattice_definition": {
               "components": list(derived),
               "exhaustive_at_depth": 1,
               "what_it_still_does_not_cover": (
                   "DEPTH >= 2 subsets beyond group 1's two declared "
                   "multi-deletions, and VARIATION ACROSS SEED SETS. Both remain "
                   "unmeasured. Exhaustiveness is claimed at depth 1 and nowhere "
                   "else."),
           },
           "CTL_FROZEN_post_run": post,
           "CTL_FROZEN_comparison": frozen,
           "variant_mirror_check": dict(VARIANT_MIRROR_CHECK)}
    metrics = {f"{r['drop_set'][0]}_null_strict_fp":
               r["CTL_NULL_strict_false_positives_total"] for r in records}
    metrics.update({f"{r['drop_set'][0]}_plant_hits": r["CTL_PLANT"]["hits"]
                    for r in records})
    metrics.update({f"{r['drop_set'][0]}_nulld_member_k_ge_1":
                    r["CTL_NULL_D_strict_member_k_ge_1"] for r in records})
    metrics["group2_rows"] = len(records)
    metrics["ctl_frozen_criterion_met"] = frozen["criterion_met"]
    metrics["ctl_frozen_identical_files"] = frozen["identical_count"]
    return RunResult(
        run_suffix="ablation-lattice-and-frozen-recheck",
        curve_id="n/a-hash-primitive", seed=SEEDS["null_draw_md5_delta_m"],
        parameters=_params("ablation-lattice-and-frozen-recheck", STRICT,
                           [r.drop_set for r in rows]),
        metrics=metrics, certificate=CERT_NONE, valid=True,
        stdout="\n".join(lines) + "\n", stderr="", raw=raw), raw


# ---------------------------------------------------------------------------
# the per-component power table -- THE HEADLINE, AND IT IS A TABLE
# ---------------------------------------------------------------------------

def power_table(group_records: list, group_name: str, isolating: dict) -> dict:
    rows = []
    for r in group_records:
        comps = r["drop_set"]
        rows.append({
            "drop_set": comps,
            "row": r["row"],
            "label": r["label"],
            "OLD_suite": r["detected_by_OLD_suite"],
            "STRENGTHENED_suite": r["detected_by_STRENGTHENED_suite"],
            "read_from": {
                "CTL_PLANT": r["CTL_PLANT"]["fraction"],
                "CTL_NULL_strict_false_positives_of_3000":
                    r["CTL_NULL_strict_false_positives_total"],
                "CTL_NULL_permissive_false_positives_of_3000":
                    r["CTL_NULL_permissive_false_positives_total"],
                "CTL_NULL_D_strict_member_k_ge_1":
                    r["CTL_NULL_D_strict_member_k_ge_1"],
                "CTL_NULL_D_k0_member_fraction": r["CTL_NULL_D_k0_member_fraction"],
            },
            "isolating_draw_exists_in_a_declared_family":
                (isolating.get(comps[0]) if len(comps) == 1 else "n/a (multi-deletion row)"),
        })
    return {
        "group": group_name,
        "rows": rows,
        "reporting_rule": (
            "IR-10. This table, not a fraction and not a pass, is the "
            "deliverable. Reporting 'the null passed' or any single pass/fail "
            "summary of the suite in place of it is a contract violation. Where "
            "a component is NOT probed by any declared family, that is said BY "
            "NAME in `isolating_draw_exists_in_a_declared_family` rather than "
            "reported as NOT DETECTED as though the suite had looked."),
        "scope": (
            "at the eight declared seeds, against the declared families, over a "
            "16-entry SYNTHETIC SHADOW census (8 md5, 8 sha1) in which EVERY "
            "PLANTED MD5 ENTRY CARRIES A WEIGHT-1 MESSAGE DIFFERENCE THAT NO "
            "REAL MD5 COLLISION CHARACTERISTIC HAS. The readable census has ZERO "
            "entries. Depth >= 2 subsets and a second seed set are UNMEASURED."),
    }


def isolating_components(nulld_raw: dict) -> dict:
    """Which components a declared family ISOLATES, measured rather than assumed.

    A component X is isolated iff some declared draw's canonical form differs
    from that of its own source census entry in X ALONE. Family (d) is the only
    declared family whose draws are constructed FROM a census entry, so for
    families (a), (b) and (c) no isolating draw exists by construction -- their
    draws are freshly generated and have no source entry to differ from in one
    component.
    """
    out: dict = {}
    for name in DECLARED_KEY_COMPONENTS:
        out[name] = ("NO -- no declared family produces a draw differing from a "
                     "census entry in this component alone")
    prim = nulld_raw["CTL_NULL_D"]["primary_arm"]["per_cell"]
    incode = nulld_raw["CTL_NULL_D"]["sub_arm_D_SHA1_INCODE"]["per_cell"]
    for store in (prim, incode):
        for cell in store.values():
            for attr, n in cell["attribution_distribution"].items():
                if "+" not in attr and attr in DECLARED_KEY_COMPONENTS:
                    out[attr] = (f"YES -- family (d) draws whose canonical form "
                                 f"differs from their source entry in "
                                 f"`{attr}` ALONE were observed")
    return out


# ---------------------------------------------------------------------------
# the driver
# ---------------------------------------------------------------------------

def _charge(suffix: str, fn, command: str) -> str:
    def wrapped() -> RunResult:
        with Deadline(CEILINGS[suffix], suffix):
            return fn()
    return run_wrapped(EXPERIMENT_ID, EXP_AREA, wrapped,
                       status="completed_valid", command=command,
                       out_root=TASK_ROOT)


def _emit(suffix: str, fn, gens, out: dict, drop_sets=None) -> dict:
    import yaml
    t0 = time.monotonic()
    command = (f"python3 -m harness.diffpath.controlpower   # run '{suffix}' of "
               f"{EXPERIMENT_ID}, ceiling {CEILINGS[suffix]}s ARMED")
    holder: dict = {}

    def call():
        res, raw = fn()
        holder["raw"] = raw
        return res

    try:
        run_id = _charge(suffix, call, command)
    except DeadlineExceeded as exc:
        rec = {"run_suffix": suffix, "state": "resource_exhaustion",
               "ceiling_seconds": CEILINGS[suffix],
               "wall_seconds": round(time.monotonic() - t0, 3),
               "reason": str(exc),
               "classification": ("resource_exhaustion -- A BUDGET OUTCOME. "
                                  "Never a negative mathematical result, never a "
                                  "finding about the null's power and never a "
                                  "finding about any difference space "
                                  "(AGENTS.md rule 5).")}
        out["runs"].append(rec)
        return rec
    except Exception as exc:                                  # noqa: BLE001
        import traceback
        rec = {"run_suffix": suffix, "state": "implementation_error",
               "ceiling_seconds": CEILINGS[suffix],
               "wall_seconds": round(time.monotonic() - t0, 3),
               "reason": f"{type(exc).__name__}: {exc}",
               "traceback": traceback.format_exc()[-2000:],
               "classification": ("implementation_error -- infrastructure "
                                  "signal, never mathematical evidence.")}
        out["runs"].append(rec)
        return rec

    run_dir = os.path.join(TASK_ROOT, "runs", run_id)
    write_supplement(run_dir, suffix, gens, drop_sets)
    with open(os.path.join(run_dir, "manifest.yaml"), encoding="utf-8") as fh:
        man = yaml.safe_load(fh)["run"]
    rec = {"run_suffix": suffix, "run_id": run_id, "state": "completed_valid",
           "run_dir": os.path.relpath(run_dir, REPO),
           "ceiling_seconds": CEILINGS[suffix],
           "wall_seconds": man["timing"]["wall_seconds"],
           "timing_source": man["timing"].get("timing_source"),
           "peak_rss_bytes": man["resources"]["peak_rss_bytes"],
           "experiment_id_in_manifest": man["experiment_id"],
           "experiment_id_in_parameters":
               man["inputs"]["parameters"]["experiment_id"],
           "code_path_fingerprint_in_manifest":
               "code_path_fingerprint" in man["inputs"]["parameters"],
           "armed_deadline_seconds_in_manifest":
               man["inputs"]["parameters"].get("armed_deadline_seconds"),
           "metrics": man["result"]["metrics"]}
    out["runs"].append(rec)
    out["raw"][suffix] = holder.get("raw")
    return rec


def _not_run(suffix: str, gate: str, out: dict) -> None:
    out["runs"].append({
        "run_suffix": suffix, "state": "not_run", "gate": gate,
        "ceiling_seconds": CEILINGS[suffix],
        "ceiling_status": ("UNSPENT -- NOT reallocated to any other run. A gated "
                           "run that correctly does not execute is a RESULT, not "
                           "a gap."),
    })


def main() -> int:
    os.makedirs(TASK_ROOT, exist_ok=True)
    out: dict = {"experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
                 "batch_id": BATCH_ID, "goal_id": GOAL_ID,
                 "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                 "runs": [], "raw": {}}
    state: dict = {}

    r1 = _emit("frozen-and-repro", lambda: run_frozen_and_repro(state),
               STRICT, out)
    repro_ok = (r1["state"] == "completed_valid"
                and r1["metrics"].get("ctl_repro_exact") is True)
    key_ok = (r1["state"] == "completed_valid"
              and r1["metrics"].get("key_component_list_agrees_with_contract"))
    state["derived_components"] = (
        out["raw"].get("frozen-and-repro", {}).get("key_components", {})
        .get("derived_at_run_time", []))

    if not repro_ok:
        gate = ("run 1 CTL-REPRO did not agree exactly on every pre-registered "
                "value; the contract STOPS after run 1 and does not measure "
                "control power against an instrument that is not the one that "
                "was reviewed. This is INFRASTRUCTURE SIGNAL, not a mathematical "
                "finding.")
        for s in ("generator-action", "null-family-d",
                  "ablation-battery-declared-rows",
                  "ablation-lattice-and-frozen-recheck"):
            _not_run(s, gate, out)
        _finish(out, state)
        return 1

    _emit("generator-action", lambda: run_generator_action(state), STRICT, out)

    r3 = _emit("null-family-d", lambda: run_null_family_d(state), STRICT, out)

    if r3["state"] != "completed_valid":
        _not_run("ablation-battery-declared-rows",
                 "run 3 did not complete; run 4's gate requires runs 1 and 3 "
                 "completed", out)
        _not_run("ablation-lattice-and-frozen-recheck", "run 4 did not run", out)
        _finish(out, state)
        return 1

    r4 = _emit("ablation-battery-declared-rows",
               lambda: run_battery_group1(state), STRICT, out,
               [r[1] for r in GROUP1_ROWS])

    if r4["state"] != "completed_valid" or not key_ok:
        _not_run("ablation-lattice-and-frozen-recheck",
                 ("run 4 did not complete" if r4["state"] != "completed_valid"
                  else "the run-time-derived key component list disagreed with "
                       "the contract's declared one"), out)
    else:
        _emit("ablation-lattice-and-frozen-recheck",
              lambda: run_battery_group2(state), STRICT, out,
              [(c,) for c in state["derived_components"]])
    _finish(out, state)
    return 0


def _sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _finish(out: dict, state: dict) -> None:
    raw = out["raw"]

    # CTL-FROZEN post-run: run 5 does it; if run 5 did not execute it is done
    # here as run 4's teardown, because it is NOT OPTIONAL.
    if "frozen_comparison" not in state and "pre_digests" in state:
        post = harness_digests()
        state["post_digests"] = post
        state["frozen_comparison"] = compare_digests(state["pre_digests"], post)
        state["frozen_comparison"]["executed_as"] = (
            "run 4 teardown, because run 5 did not execute; the contract makes "
            "the post-run re-verification non-optional")

    if "frozen-and-repro" in raw:
        doc = {
            "experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
            "CTL_REPRO": raw["frozen-and-repro"]["CTL_REPRO"],
            "key_components": raw["frozen-and-repro"]["key_components"],
            "census_counts": raw["frozen-and-repro"]["census_counts"],
            "census_counts_note": (
                "readable / quarantined_not_read / acquisition_gap are THREE "
                "SEPARATE POPULATIONS and are NEVER SUMMED; shadow_planted is "
                "carried separately and is NEVER a readable census entry."),
            "CTL_FROZEN": {
                "pre_run": state.get("pre_digests"),
                "post_run": state.get("post_digests"),
                "comparison": state.get("frozen_comparison"),
                "what_it_measures": (
                    "that this batch did not modify the object it was measuring "
                    "(IR-2). It makes 'we did not repair the instrument' a "
                    "MEASUREMENT rather than an attestation."),
            },
        }
        _write_json("repro-and-frozen-result.json", doc)

    if "generator-action" in raw:
        g = raw["generator-action"]
        _write_json("generator-action-profile.json", {
            "experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
            "CTL_GEN_ACT": g["CTL_GEN_ACT"],
            "verdict_change_object_set": g["verdict_change_object_set"],
            "CTL_TWOSIDED": g["CTL_TWOSIDED"],
            "action_is_not_verification": (
                "CTL-GEN-ACT measures ACTION, not VERIFICATION STATUS. E1..E6's "
                "VERIFIED/EXCLUDED verdicts stand exactly as EXP-DIFFP-fe894e "
                "froze them and are reproduced by CTL-REPRO; nothing here "
                "re-decides one. 'VERIFIED' and 'does observable work' are "
                "different properties and are reported as different fields."),
        })

    if "null-family-d" in raw:
        d = raw["null-family-d"]
        _write_json("null-family-d-result.json", {
            "experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
            **d,
            "scope": (
                "16-entry SYNTHETIC shadow census (8 md5, 8 sha1) at seeds "
                "84064101/84064102, readable census ZERO entries, every planted "
                "MD5 entry carrying a WEIGHT-1 message difference that no real "
                "MD5 collision characteristic has. Nothing here transfers to a "
                "published characteristic."),
        })

    if "group1" in state or "group2" in state:
        isolating = isolating_components(raw["null-family-d"]) \
            if "null-family-d" in raw else {}
        doc = {
            "experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
            "ablation_mechanism": {
                "definition": (
                    "the SAME committed Adjudicator serialisation over the SAME "
                    "committed census, with named (name, value) pairs dropped by "
                    "a declared projection applied INSIDE the orbit "
                    "minimisation: min(project(serialize(v, gens))) over the "
                    "identical variant list. NO COMMITTED MODULE IS EDITED."),
                "run_time_derived_key_components": state.get("derived_components"),
                "declared_key_components": list(DECLARED_KEY_COMPONENTS),
            },
            "group_1_the_replication": state.get("group1"),
            "group_1_power_table": (power_table(state["group1"], "group 1 -- the "
                                    "six declared rows of EV-DIFFP-b878aa O-7",
                                    isolating) if "group1" in state else None),
            "group_2_the_complete_depth_1_lattice": state.get("group2"),
            "group_2_power_table": (power_table(state["group2"], "group 2 -- the "
                                    "complete depth-1 single-deletion lattice",
                                    isolating) if "group2" in state else None),
            "groups_are_never_merged": (
                "GROUP 1 IS THE REPLICATION and GROUP 2 IS AN EXTENSION. Group "
                "2 is NEVER merged into group 1's '2 of 5' fraction, which is a "
                "POINT ESTIMATE OVER A HAND-CHOSEN FIVE-ELEMENT SAMPLE and whose "
                "scope must stay visible."),
            "isolating_draw_per_component": isolating,
            "inside_vs_outside_minimisation":
                state.get("projection_comparison"),
            "detection_rule": DETECTION_RULE,
            "interpretation_limit": (
                "A control suite that detects more ablations is a BETTER "
                "INSTRUMENT and is NOT a result about MD5 or SHA-1. Nothing here "
                "bears on either primitive's difference space, on any published "
                "characteristic, or on novelty. NO PATH IS CLAIMED NEW."),
        }
        _write_json("ablation-battery-result.json", doc)

    # --- run-index.json: a sha256 for EVERY FILE OF EVERY EXECUTED RUN
    index = {k: v for k, v in out.items() if k != "raw"}
    files: dict = {}
    for rec in out["runs"]:
        if rec.get("state") != "completed_valid":
            continue
        rd = os.path.join(REPO, rec["run_dir"])
        for dirpath, _dirnames, filenames in os.walk(rd):
            for fn in sorted(filenames):
                full = os.path.join(dirpath, fn)
                files[os.path.relpath(full, REPO)] = _sha256_file(full)
    index["run_files_sha256"] = files
    index["run_files_note"] = (
        "RUN DIRECTORIES ARE DELIBERATELY NOT DECLARED AS QUEUE artifact_paths: "
        "a completed archive's path_sha256 must cover every declared source "
        "artifact, so declaring the files of a GATED run would make the snapshot "
        "unable to complete whenever that run correctly does not execute. This "
        "file IS in the binding set and carries a sha256 for EVERY FILE OF EVERY "
        "EXECUTED RUN, which is how the runs are content-bound (batch rule BR-7).")
    index["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    index["variant_mirror_check"] = dict(VARIANT_MIRROR_CHECK)
    _write_json("run-index.json", index)


def _write_json(name: str, doc: dict) -> None:
    with open(os.path.join(TASK_ROOT, name), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, sort_keys=True, default=str)


if __name__ == "__main__":
    raise SystemExit(main())
