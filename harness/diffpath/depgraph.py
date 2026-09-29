"""THE MEMBERSHIP KEY'S FUNCTIONAL-DEPENDENCY GRAPH -- the only new module of
EXP-DIFFP-04082e (TASK-20260824-68ba87, BATCH-145531).

WHAT THIS MODULE IS.  A measurement instrument pointed at the FUNCTIONAL
STRUCTURE of the committed adjudicator's strict membership key: an ordered-pair
dependency graph with a written derivation and an empirical witness per edge, a
two-sided well-formedness gate, a re-partition of the depth-1 ablation lattice
derived from the graph alone, a fifteen-subset depth-2 classification, the
off-diagonal cells of the family-by-row matrix adjudicated against the honest
instrument and against the REUSED known-false O-E, two degenerate null
instruments through the identical counting rule, and the RC-1 refold BY
RE-SCORING.

WHAT IT IS NOT.  IT IS NOT A REPAIR.  Every committed module under harness/ --
INCLUDING harness/diffpath/controlpower.py -- is a READ-ONLY INPUT (IR-2).
VD-3, VD-4, the {E4}/{E5} zero-image result, OBJ-3, OBJ-4 and OBJ-10 stand
exactly as committed.  The RC-1 fold is a RE-SCORING IN THIS MODULE and the
committed rule's own verdicts are reported UNCHANGED beside it; nothing here
states or implies that the committed rule has been fixed.

IT SEARCHES NOTHING AND ACQUIRES NOTHING.  No path in this module reads,
parses, extracts, fetches or reconstructs the Tier-A quarantine payload; see
QUARANTINE_MECHANISM below, which is a MECHANISM and not an intention.  No
network call of any kind is made (IR-3).  No search over any difference space,
no collision attempt, no cost projection (IR-4).

THE PRODUCER COMPOSES NO VERDICT (IR-8 / H-11).  Every function here emits
tables, partitions, derivations and integers with their populations.  No
function emits a pass, a fraction-as-score or a margin.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import random
import subprocess
import sys
import time

from .compat import ensure as _ensure_compat

COMPAT = _ensure_compat()          # MUST precede the harness.runner import

from harness.runner import RunResult, run_wrapped          # noqa: E402

from . import adjudicator as ADJ                           # noqa: E402
from . import census as CEN                                # noqa: E402
from . import controlpower as CP                           # noqa: E402
from . import equivalence as EQ                            # noqa: E402
from . import primitives as P                              # noqa: E402
from .pathobj import PathObject, bsdr_encode               # noqa: E402

# ---------------------------------------------------------------------------
# frozen contract constants
# ---------------------------------------------------------------------------

EXPERIMENT_ID = "EXP-DIFFP-04082e"        # IR-7: the LITERAL id, a hard term
EXP_AREA = "DIFFP-04082e"
TASK_ID = "TASK-20260824-68ba87"
BATCH_ID = "BATCH-145531"
GOAL_ID = "GOAL-DIFFP-84d641"

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TASK_DIR = ("coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-145531/"
            "tasks/TASK-20260824-68ba87")
TASK_ROOT = os.path.join(REPO, TASK_DIR)

# H-10 / BR-12: RUN LOCATION IS A CONTRACT TERM.  Runs go to
# experiments/EXP-DIFFP-04082e/runs/<RUN-ID>/, which is the ONE glob
# tools/validate_ledger.py registers from.  `out_root=None` gives exactly that.
RUN_OUT_ROOT = None

RT_CONSTRUCTIONS = os.path.join(
    REPO, "coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-efcae7/reviews/"
          "TASK-20260824-e9d21a/constructions")

CEILINGS = {
    "frozen-and-dependency-graph": 60,
    "partition-derived-then-compared": 45,
    "offdiagonal-honest-and-known-false": 105,
    "null-object-counting-controls": 60,
    "rc1-refold-and-frozen-recheck": 60,
}

# The EIGHT declared seeds of EXP-DIFFP-4b165f, inherited BYTE-IDENTICALLY from
# the committed module.  NO NINTH SEED EXISTS OR IS CREATED ANYWHERE HERE: every
# family this module constructs draws from
# SEEDS["null_draw_message_difference_perturbed"], each family instantiating its
# OWN random.Random at that seed and consuming it in a declared order.
SEEDS = dict(CP.SEEDS)

STRICT = CP.STRICT
K_VALUES = CP.K_VALUES
R_COMMITTED = CP.R_SEEDED          # 64, the committed family-(d) draw count
R_NEW_FAMILIES = 8                 # DECLARED HERE, BEFORE ANY RUN

# H-4: carried beside EVERY edge, class, cell and verdict.  NEVER SUMMED.
CENSUS_COMPLETENESS = {
    "readable": 0,
    "quarantined_not_read": 1,
    "acquisition_gap": 8,
    "never_summed": ("these three counts are SEPARATE and are never added "
                     "together; the readable census is ZERO entries and a "
                     "NON-MEMBER verdict against it carries no information "
                     "about the literature at all"),
    "shadow_planted_carried_separately": 16,
}

CONTRACT_KEY_COMPONENTS = ("primitive", "length", "message_difference",
                           "step_delta", "block_index", "in_linearized_code")

# ---------------------------------------------------------------------------
# IR-1 -- THE QUARANTINE FIREWALL, BY MECHANISM
# ---------------------------------------------------------------------------

QUARANTINE_MECHANISM = (
    "IR-1 IS HONOURED BY MECHANISM AND THE MECHANISM IS NAMED. (1) The path "
    "prefix of the Tier-A quarantine directory appears in NO code path of this "
    "module: there is no open() of it, no path join naming it and no string "
    "literal of it, and nothing here parses, extracts, reconstructs or fetches "
    "any part of it. (2) The COMMITTED census builder calls "
    "census.quarantine_attestation(), which opens the payload 'rb' and hashes "
    "it; EXP-DIFFP-04082e IR-1 says this contract 'does not even re-hash the "
    "payload', and IR-2 forbids editing that committed module. This module "
    "therefore REPLACES census.quarantine_attestation IN THIS PROCESS ONLY, "
    "with a stub that opens nothing -- a run-time monkeypatch of an imported "
    "name, writing no committed file. That is the same mechanism "
    "TASK-20260824-e9d21a used. CONSEQUENCE, STATED: no byte of the payload is "
    "read by this task by any route, and the census entry's sha256 field is a "
    "placeholder rather than a hash. Nothing measured here depends on it: only "
    "census.shadow is used and the shadow entries are built from the two "
    "planted seeds. (3) No network call of any kind is made (IR-3). (4) No "
    "census entry is populated from recollection.")

_QUARANTINE_STUB_INSTALLED = {"done": False}


def install_quarantine_firewall() -> dict:
    """Replace the committed attestation with a stub that opens nothing."""
    if not _QUARANTINE_STUB_INSTALLED["done"]:
        CEN.quarantine_attestation = lambda: {
            "path": "<NOT OPENED BY TASK-20260824-68ba87>",
            "bytes_hashed": 0,
            "sha256_recomputed": "0" * 64,
            "sha256_expected": None,
            "match": None,
            "read_mode": "STUBBED -- this task never opened the payload",
            "parsed": False,
            "attestation": "stubbed by TASK-20260824-68ba87 (IR-1)",
        }
        _QUARANTINE_STUB_INSTALLED["done"] = True
    return {"stub_installed": True, "mechanism": QUARANTINE_MECHANISM}


# ---------------------------------------------------------------------------
# CTL-FROZEN-3 -- the criterion set, WITH THIS CONTRACT'S OWN ARTIFACTS OUT
# ---------------------------------------------------------------------------

THIS_CONTRACTS_OWN_ARTIFACTS = ("harness/diffpath/depgraph.py",
                                "tests/test_diffpath_depgraph.py")

FROZEN_CRITERION_NOTE = (
    "THE CRITERION SET EXCLUDES THIS CONTRACT'S OWN REQUIRED NEW ARTIFACTS BY "
    "DEFINITION (EXP-DIFFP-04082e CTL-FROZEN-3, DEC-20260824-c5bb72 PD-5). "
    "harness/diffpath/depgraph.py and tests/test_diffpath_depgraph.py are "
    "REQUIRED ARTIFACTS of this contract; their digests are reported SEPARATELY "
    "before and after, and their being identical to each other is a self-check "
    "and NEVER an identity criterion. Every OTHER .py under harness/diffpath/ "
    "-- INCLUDING controlpower.py, which is now committed -- plus "
    "harness/__init__.py and harness/runner.py IS in the criterion set.")


def digests() -> dict:
    crit: dict = {}
    own: dict = {}
    root = os.path.dirname(os.path.abspath(__file__))
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in sorted(filenames):
            if not fn.endswith(".py"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, REPO).replace(os.sep, "/")
            with open(full, "rb") as fh:
                dg = hashlib.sha256(fh.read()).hexdigest()
            (own if rel in THIS_CONTRACTS_OWN_ARTIFACTS else crit)[rel] = dg
    for rel in ("harness/__init__.py", "harness/runner.py"):
        with open(os.path.join(REPO, rel), "rb") as fh:
            crit[rel] = hashlib.sha256(fh.read()).hexdigest()
    for rel in THIS_CONTRACTS_OWN_ARTIFACTS:
        full = os.path.join(REPO, rel)
        if os.path.exists(full) and rel not in own:
            with open(full, "rb") as fh:
                own[rel] = hashlib.sha256(fh.read()).hexdigest()
    return {"criterion_set": crit,
            "criterion_set_files": len(crit),
            "this_contracts_own_required_artifacts_reported_separately": own,
            "criterion_note": FROZEN_CRITERION_NOTE}


def compare_digests(pre: dict, post: dict) -> dict:
    a, b = pre["criterion_set"], post["criterion_set"]
    changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    return {
        "criterion_files_before": len(a),
        "criterion_files_after": len(b),
        "identical_files": sorted(k for k in set(a) & set(b) if a[k] == b[k]),
        "identical_count": len(set(a) & set(b)) - len(changed),
        "changed_files": changed,
        "only_before": sorted(set(a) - set(b)),
        "only_after": sorted(set(b) - set(a)),
        "criterion_met_identical_before_and_after":
            (not changed and set(a) == set(b)),
        "this_contracts_own_artifacts_before":
            pre["this_contracts_own_required_artifacts_reported_separately"],
        "this_contracts_own_artifacts_after":
            post["this_contracts_own_required_artifacts_reported_separately"],
        "criterion_note": FROZEN_CRITERION_NOTE,
    }


# ---------------------------------------------------------------------------
# IR-13 -- THE STRICT KEY COMPONENT LIST, DERIVED AT RUN TIME
# ---------------------------------------------------------------------------

def derive_components(census) -> dict:
    """The strict key component list, READ OFF THE COMMITTED SERIALISER."""
    per_prim: dict = {}
    for e in census.shadow:
        if e.primitive in per_prim:
            continue
        per_prim[e.primitive] = [p[0] for p in ADJ.serialize(e.obj, STRICT)]
    union: list = []
    for prim in ("md5", "sha1"):
        for name in per_prim.get(prim, []):
            if name not in union:
                union.append(name)
    return {
        "derived_per_primitive": per_prim,
        "derived_union_in_first_appearance_order": union,
        "contract_declared": list(CONTRACT_KEY_COMPONENTS),
        "agrees_with_contract_as_a_set": set(union) == set(CONTRACT_KEY_COMPONENTS),
        "agrees_with_contract_in_order":
            tuple(union) == tuple(CONTRACT_KEY_COMPONENTS),
        "derivation_method": (
            "the names of harness.diffpath.adjudicator.serialize(obj, STRICT) "
            "evaluated on one census entry of each primitive under the "
            "committed STRICT generator set frozenset(('E1','E3','E4','E5')); "
            "NOTHING IS HARD-CODED FROM THE CONTRACT (IR-13)"),
        "per_primitive_difference_that_is_reported_and_not_worked_around": (
            "in_linearized_code IS A KEY COMPONENT ON sha1 ONLY. The committed "
            "serialiser appends it if and only if obj.primitive == 'sha1', so "
            "the MD5 key has FIVE components and the SHA-1 key has SIX. The "
            "contract's six names are the UNION and this module analyses the "
            "union per primitive, reporting on MD5 that in_linearized_code is "
            "NOT A KEY COMPONENT rather than emitting a verdict that reads as "
            "though it were."),
        "census_completeness": CENSUS_COMPLETENESS,
    }


# ---------------------------------------------------------------------------
# CTL-WF -- the two-sided well-formedness gate
# ---------------------------------------------------------------------------

WF_CHECKS = {
    "W1_primitive_is_declared":
        "obj.primitive is one of the two declared primitives md5 | sha1",
    "W2_message_difference_word_count_is_consistent_with_primitive_and_length": (
        "md5: delta_m is present and is EXACTLY 16 words (pathobj.plant_from_pair "
        "sets delta_m from the 16 message words) and dv is absent. sha1: dv is "
        "present and len(dv) == obj.length, because plant_from_pair sets "
        "dv = full_dv[a:b+1] over the closed step range"),
    "W3_in_linearized_code_equals_the_committed_predicate_of_the_dv": (
        "sha1: obj.in_linearized_code == primitives.sha1_in_linearized_code("
        "list(obj.dv)). md5: obj.in_linearized_code is None, because the "
        "committed serialiser never reads it on md5"),
    "W4_step_range_is_well_formed_with_respect_to_the_per_step_arrays": (
        "step_range is a pair of integers with 0 <= a <= b, and "
        "len(step_delta) == len(step_delta_signed) == obj.length, because "
        "plant_from_pair builds exactly one modular difference per step of the "
        "closed range and obj.length is the property b - a + 1"),
    "W5_block_index_lies_in_its_declared_range": (
        "block_index is an integer >= 0. STATED LIMIT: NO COMMITTED MODULE "
        "DECLARES AN UPPER BOUND on block_index -- equivalence.act_E6_reindex "
        "accepts any integer -- so the gate checks integrality and "
        "non-negativity ONLY, and that is the whole of the declared range this "
        "gate can enforce"),
}


def wf_violations(obj) -> list:
    """Return the list of CTL-WF check ids the object VIOLATES."""
    bad: list = []
    if getattr(obj, "primitive", None) not in ("md5", "sha1"):
        return ["W1_primitive_is_declared"]
    if obj.primitive == "md5":
        if obj.delta_m is None or len(obj.delta_m) != 16 or obj.dv is not None:
            bad.append("W2_message_difference_word_count_is_consistent_with_"
                       "primitive_and_length")
        if obj.in_linearized_code is not None:
            bad.append("W3_in_linearized_code_equals_the_committed_predicate_"
                       "of_the_dv")
    else:
        ok_w2 = obj.dv is not None
        try:
            ok_w2 = ok_w2 and len(obj.dv) == obj.length
        except Exception:                                        # noqa: BLE001
            ok_w2 = False
        if not ok_w2:
            bad.append("W2_message_difference_word_count_is_consistent_with_"
                       "primitive_and_length")
        try:
            ok_w3 = (obj.dv is not None
                     and obj.in_linearized_code
                     == P.sha1_in_linearized_code(list(obj.dv)))
        except Exception:                                        # noqa: BLE001
            ok_w3 = False
        if not ok_w3:
            bad.append("W3_in_linearized_code_equals_the_committed_predicate_"
                       "of_the_dv")
    try:
        a, b = obj.step_range
        ok_w4 = (isinstance(a, int) and isinstance(b, int) and 0 <= a <= b
                 and len(obj.step_delta) == obj.length
                 and len(obj.step_delta_signed) == obj.length)
    except Exception:                                            # noqa: BLE001
        ok_w4 = False
    if not ok_w4:
        bad.append("W4_step_range_is_well_formed_with_respect_to_the_per_step_"
                   "arrays")
    if not (isinstance(obj.block_index, int)
            and not isinstance(obj.block_index, bool)
            and obj.block_index >= 0):
        bad.append("W5_block_index_lies_in_its_declared_range")
    return bad


def wf_accepts(obj) -> bool:
    return not wf_violations(obj)


def malformed_null_family_e(obj):
    """The deliberately malformed object CTL-WF must REJECT.

    A SHA-1 entry with in_linearized_code FLIPPED and the dv held fixed. This is
    exactly null family (e) as DEC-20260824-af6d5c P-4 specified it. IT IS BUILT
    HERE ONLY TO BE REJECTED; family (e) IS NOT EXECUTED BY THIS CONTRACT.
    """
    new = PathObject(**{**obj.__dict__})
    new.id = f"{obj.id}~WFMALFORMED"
    new.in_linearized_code = not obj.in_linearized_code
    new.path_data = {"kind": "ctl_wf_deliberately_malformed", "of": obj.id}
    return new


# ---------------------------------------------------------------------------
# the DECLARED OBJECT POPULATION of CTL-DEP
# ---------------------------------------------------------------------------

def family_d_draws(census):
    """(iii) every committed family-(d) draw at the eight declared seeds.

    THE LOOP MIRRORS THE COMMITTED controlpower.family_d_primary EXACTLY --
    census order, then k ascending, then draw index, off ONE random.Random at
    SEEDS['null_draw_message_difference_perturbed'] shared across primitives --
    because that committed function returns counters rather than objects. The
    mirror is SELF-CHECKED by draw counts against the committed
    j8_results.json per-cell integers (8 at k=0 and 520 at each k>=1 per
    primitive); a disagreement is reported, never reconciled.
    """
    rng = random.Random(SEEDS["null_draw_message_difference_perturbed"])
    for e in census.shadow:
        src = e.obj
        nbits = CP.md_bits(src)
        for k in K_VALUES:
            plan = [("deterministic", tuple(range(k)))]
            if k >= 1:
                plan += [("seeded", tuple(sorted(rng.sample(range(nbits), k))))
                         for _ in range(R_COMMITTED)]
            for draw_type, pos in plan:
                obj = CP.perturb_message_difference(
                    src, pos, f"k{k}-{draw_type}-{'.'.join(map(str, pos))}")
                yield e, k, draw_type, obj


def incode_draws(census):
    """(iv) the 520 in-code perturbed SHA-1 objects of the D-SHA1-INCODE arm."""
    rng = random.Random(SEEDS["null_draw_message_difference_perturbed"])
    for e in census.shadow:
        if e.primitive != "sha1":
            continue
        plan = [("deterministic", tuple([1] + [0] * 15))]
        plan += [("seeded", tuple(rng.getrandbits(32) for _ in range(16)))
                 for _ in range(R_COMMITTED)]
        for draw_type, w16 in plan:
            if not any(w16):
                continue
            yield e, draw_type, CP.perturb_by_codeword(e.obj, w16, draw_type)


POPULATION_DECLARATION = (
    "DECLARED BY THE CONTRACT BEFORE IT IS COMPUTED and built here in that "
    "order: (i) the 16 census entries; (ii) every orbit image of every entry "
    "under the STRICT generator set, via the committed "
    "adjudicator.orbit_images; (iii) every committed family-(d) draw at the "
    "eight declared seeds, both the deterministic and the seeded arms; and "
    "(iv) the 520 in-code perturbed SHA-1 objects of the D-SHA1-INCODE "
    "sub-arm. Population sizes are reported as integers PER PRIMITIVE and every "
    "claim of the graph is scoped to them.")


def declared_population(census) -> dict:
    pop = {"md5": [], "sha1": []}
    prov = {"md5": {}, "sha1": {}}

    def add(obj, tag):
        pop[obj.primitive].append(obj)
        prov[obj.primitive][tag] = prov[obj.primitive].get(tag, 0) + 1

    for e in census.shadow:
        add(e.obj, "i_census_entry")
        for img in ADJ.orbit_images(e.obj, STRICT):
            add(img, "ii_strict_orbit_image")
    for e, k, draw_type, obj in family_d_draws(census):
        add(obj, "iii_family_d_draw")
    for e, draw_type, obj in incode_draws(census):
        add(obj, "iv_D_SHA1_INCODE_draw")
    return {"objects": pop, "provenance_counts": prov,
            "population_sizes": {k: len(v) for k, v in pop.items()},
            "declaration": POPULATION_DECLARATION}


# ---------------------------------------------------------------------------
# CTL-DEP -- the edge detector
# ---------------------------------------------------------------------------

def component_value(obj, name):
    """The value of a key component ON AN OBJECT, read the way serialize reads it."""
    if name == "primitive":
        return obj.primitive
    if name == "length":
        return obj.length
    if name == "message_difference":
        return tuple(obj.delta_m or ()) if obj.primitive == "md5" \
            else tuple(obj.dv or ())
    if name == "step_delta":
        return tuple(obj.step_delta)
    if name == "block_index":
        return obj.block_index
    if name == "in_linearized_code":
        return obj.in_linearized_code
    raise KeyError(name)


EDGE_RULE = (
    "THE CONTRACT'S OWN RULE, IMPLEMENTED LITERALLY AND NOT EXTENDED: for the "
    "ordered pair (X, Y), group the declared population by X's VALUE and decide "
    "EDGE if and only if Y is CONSTANT within EVERY group. The flags beside each "
    "verdict -- distinct_X, groups_total, groups_constant, "
    "groups_of_size_ge_2, max_group_size, distinct_Y, LOW_DISTINCT_X and "
    "Y_CONSTANT_ON_POPULATION -- ARE DIAGNOSTICS AND DO NOT CHANGE THE VERDICT. "
    "They are emitted because the same constancy test reports an edge for ANY "
    "pair whose groups are all singletons, and because a pair whose Y takes ONE "
    "value on the population reports an edge that is a property of the "
    "population and not of the key.")


def detect_edge(objs: list, X: str, Y: str) -> dict:
    groups: dict = {}
    for o in objs:
        groups.setdefault(component_value(o, X), set()).add(component_value(o, Y))
    sizes: dict = {}
    for o in objs:
        v = component_value(o, X)
        sizes[v] = sizes.get(v, 0) + 1
    constant = [g for g, ys in groups.items() if len(ys) == 1]
    non_constant = [g for g, ys in groups.items() if len(ys) > 1]
    distinct_y = len({component_value(o, Y) for o in objs})
    verdict = "EDGE" if not non_constant else "NO EDGE"
    out = {
        "X": X, "Y": Y, "verdict": verdict,
        "population_size": len(objs),
        "distinct_X": len(groups),
        "groups_total": len(groups),
        "groups_constant_in_Y": len(constant),
        "groups_non_constant_in_Y": len(non_constant),
        "groups_of_size_ge_2": sum(1 for v in sizes.values() if v >= 2),
        "max_group_size": max(sizes.values()) if sizes else 0,
        "distinct_Y": distinct_y,
        "LOW_DISTINCT_X": len(groups) < 3,
        "Y_CONSTANT_ON_POPULATION": distinct_y <= 1,
        "SINGLETON_GROUPS_ONLY": all(v == 1 for v in sizes.values()) if sizes else None,
        "rule": EDGE_RULE,
    }
    if non_constant:
        g = non_constant[0]
        wit = [o for o in objs if component_value(o, X) == g]
        ys = {}
        for o in wit:
            ys.setdefault(component_value(o, Y), o)
        two = list(ys.items())[:2]
        out["counterexample_certificate"] = {
            "kind": "counterexample_certificate",
            "statement": (f"the ordered pair ({X}, {Y}) is REFUTED on the "
                          f"declared population: two objects share an X value "
                          f"and differ in Y"),
            "shared_X_value": _jsonable(g),
            "objects": [
                {"id": o.id, "provenance": (o.path_data or {}).get("kind", "census_entry"),
                 "X_value": _jsonable(g), "Y_value": _jsonable(y)}
                for y, o in two],
            "verified_by": ("re-reading component_value on both objects, which "
                            "reads the same fields adjudicator.serialize reads"),
        }
    return out


def _jsonable(v):
    if isinstance(v, tuple):
        return [_jsonable(x) for x in v]
    if isinstance(v, (int, float, str, bool)) or v is None:
        return v
    return str(v)


# --- the DERIVATIONS, written from COMMITTED SOURCE (H-1) -------------------

DERIVATIONS = {
    ("step_delta", "length", "md5"): (
        "length IS NOT A STORED FIELD: pathobj.PathObject.length is the PROPERTY "
        "step_range[1] - step_range[0] + 1. pathobj.plant_from_pair builds "
        "step_delta as tuple(P.sub32(trp.q[i], tr.q[i]) for i in range(a, b+1)), "
        "i.e. EXACTLY ONE modular difference per step of the closed range, so "
        "len(step_delta) == length on every object it builds. Every constructor "
        "that reaches this population preserves that: equivalence.act_E1_shift "
        "carries step_delta over and shifts BOTH ends of step_range; "
        "act_E3_negate negates element-wise at constant range; "
        "controlpower.perturb_message_difference and perturb_by_codeword copy "
        "__dict__ and touch neither. THEREFORE the serialised step_delta VALUE "
        "determines length as its own tuple length: length = len(step_delta). "
        "This is a derivation from committed source and not a property of the "
        "census."),
    ("step_delta", "length", "sha1"): None,      # filled below, same text
    ("message_difference", "length", "sha1"): (
        "ON SHA-1 the serialised message_difference is tuple(obj.dv), and "
        "pathobj.plant_from_pair sets obj.dv = full_dv[a:b+1] over the closed "
        "step range, so len(dv) == length. equivalence.act_E1_shift sets "
        "dv = full[a+s : b+s+1] and step_range = (a+s, b+s), preserving both "
        "sides; act_E3_negate leaves dv untouched; "
        "controlpower.perturb_message_difference XORs bits in place and "
        "perturb_by_codeword XORs an 80-word codeword element-wise, neither "
        "changing the word count. THEREFORE the serialised message_difference "
        "VALUE determines length as its own tuple length on SHA-1. IT DOES NOT "
        "HOLD ON MD5, where delta_m is ALWAYS 16 words whatever the length."),
    ("message_difference", "in_linearized_code", "sha1"): (
        "primitives.sha1_in_linearized_code(words) RETURNS "
        "sha1_expand(words[:16], len(words)) == list(words), which is a PURE "
        "FUNCTION OF THE WORD LIST AND OF NOTHING ELSE. Every object of the "
        "declared population that carries the flag has it computed by that "
        "function from its own dv -- plant_from_pair computes it from full_dv, "
        "perturb_message_difference recomputes it as "
        "P.sha1_in_linearized_code(list(d)) after flipping bits, and "
        "perturb_by_codeword does the same -- and CTL-WF check W3 REJECTS any "
        "object whose flag does not equal that predicate of its own dv. "
        "THEREFORE, on the CTL-WF-accepted population, the serialised "
        "message_difference VALUE determines in_linearized_code. TWO SCOPE "
        "LIMITS, STATED IN THE SAME BREATH: (a) plant_from_pair computes the "
        "flag from the FULL 80-word expansion while the serialised value is the "
        "step-range slice, and these coincide only at FULL STEP RANGE, which is "
        "where every planted entry of this census sits; (b) equivalence."
        "act_E1_shift and act_E2_rotate CARRY THE FLAG OVER rather than "
        "recomputing it, so the derivation covers their images only because W3 "
        "is measured on them rather than assumed."),
}
DERIVATIONS[("step_delta", "length", "sha1")] = \
    DERIVATIONS[("step_delta", "length", "md5")]

SCOPE_DERIVATION_PRIMITIVE = (
    "DEGENERATE BY THE ANALYSIS SCOPE AND NOT A PROPERTY OF THE MEMBERSHIP KEY. "
    "The graph is computed PER PRIMITIVE (contract H-4), so `primitive` takes "
    "exactly ONE value on each sub-population and is constant within every "
    "group of every X. This edge is reported because the contract requires all "
    "60 ordered-pair verdicts, and it is labelled a scope artifact so no reader "
    "takes it for a dependency.")


def edge_records(objs: list, prim: str, components: list) -> list:
    out = []
    for X in components:
        for Y in components:
            if X == Y:
                continue
            key_present = {
                "X_is_a_key_component_on_this_primitive":
                    X in ([p[0] for p in ADJ.serialize(objs[0], STRICT)]),
                "Y_is_a_key_component_on_this_primitive":
                    Y in ([p[0] for p in ADJ.serialize(objs[0], STRICT)]),
            }
            rec = detect_edge(objs, X, Y)
            rec["primitive_scope"] = prim
            rec["census_completeness"] = CENSUS_COMPLETENESS
            rec.update(key_present)
            deriv = DERIVATIONS.get((X, Y, prim))
            if deriv is None and Y == "primitive":
                deriv = SCOPE_DERIVATION_PRIMITIVE
                rec["scope_artifact"] = True
            rec["derivation"] = deriv
            if rec["verdict"] == "EDGE":
                if deriv is None:
                    rec["label"] = "empirical_only"
                    rec["label_note"] = (
                        "AN EDGE WITH A WITNESS AND NO DERIVATION FROM COMMITTED "
                        "SOURCE. The words theorem, provable, provably and "
                        "impossible are NOT used for it anywhere in this batch, "
                        "and no partition class of this contract rests on it.")
                elif rec.get("scope_artifact"):
                    rec["label"] = "scope_artifact"
                else:
                    rec["label"] = "derived_and_witnessed"
                if deriv is not None and rec["groups_non_constant_in_Y"]:
                    rec["CONTRADICTION_DERIVATION_WITH_FAILING_WITNESS"] = True
            else:
                rec["label"] = "no_edge"
                if deriv is not None and not rec.get("scope_artifact"):
                    rec["CONTRADICTION_DERIVATION_WITH_FAILING_WITNESS"] = True
                    rec["stop_condition"] = (
                        "CTL-DEP produced an edge with a derivation and a "
                        "FAILING WITNESS. Both are reported and neither is "
                        "chosen (contract stopping_rules).")
            out.append(rec)
    return out


def derived_edge_set(records: list) -> set:
    """The (X, Y) pairs a partition class may rest on: EDGE with a derivation."""
    return {(r["X"], r["Y"]) for r in records
            if r["verdict"] == "EDGE" and r["label"] == "derived_and_witnessed"}


# ---------------------------------------------------------------------------
# CTL-GRAPH-NULL -- the null-object control for the edge detector
# ---------------------------------------------------------------------------

NULL_FORCED_SET_DECLARATION = (
    "DECLARED BEFORE THE NULL POPULATION IS DRAWN AND BEFORE ANY RUN EXECUTES, "
    "AND IT IS A DECLARED DEVIATION FROM THE CONTRACT'S LITERAL KNOWN ANSWER "
    "RATHER THAN A SOFTENING OF IT. The contract requires the detector to "
    "return NO EDGE for EVERY pair on a synthetic independent-coordinate "
    "population 'subject to CTL-WF'. THAT LITERAL ANSWER IS UNREACHABLE BY ANY "
    "IMPLEMENTATION, because CTL-WF -- which the SAME control mandates -- "
    "FORCES some of those very pairs: W4 makes len(step_delta) == length, and "
    "on SHA-1 W2 makes len(dv) == length and W3 makes the flag a function of "
    "the dv. A population that violates them is not CTL-WF-subject; a "
    "population that satisfies them cannot have those coordinates independent. "
    "THIS MODULE THEREFORE REPORTS BOTH: `edges_returned_total`, which is the "
    "contract's literal quantity against its literal known answer of 0, AND "
    "`edges_returned_outside_the_declared_forced_set`, to which the STOP "
    "condition is applied. THE FORCED SET IS ENUMERATED IN ADVANCE and is "
    "exactly: (F1) any ordered pair whose Y takes ONE distinct value on the "
    "null population, which is a degeneracy of the population and not a "
    "dependency; and (F2) (step_delta -> length) on both primitives, "
    "(message_difference -> length) on sha1 and "
    "(message_difference -> in_linearized_code) on sha1, each forced by the "
    "named CTL-WF check. NOTHING ELSE IS EXCUSED. This reading was fixed from "
    "the CONTRACT TEXT AND THE COMMITTED SOURCE before any datum was observed, "
    "so it is not IR-6 in-run repair; it is recorded as a deviation for the "
    "Coordinator to adjudicate.")

NULL_FORCED_PAIRS = {
    "md5": {("step_delta", "length")},
    "sha1": {("step_delta", "length"), ("message_difference", "length"),
             ("message_difference", "in_linearized_code")},
}


def _synthetic_md5(rng, n, md_pool, sd_pools, lengths, blocks):
    out = []
    for i in range(n):
        L = lengths[rng.randrange(len(lengths))]
        dm = md_pool[rng.randrange(len(md_pool))]
        sd = sd_pools[L][rng.randrange(len(sd_pools[L]))]
        bi = blocks[rng.randrange(len(blocks))]
        out.append(PathObject(
            id=f"NULLB-MD5-{i:04d}", primitive="md5", step_range=(0, L - 1),
            provenance="internal", source_ref=TASK_ID, status="readable",
            path_data={"kind": "graph_null_independent_coordinate"},
            delta_m=dm, delta_m_signed=tuple(bsdr_encode(x) for x in dm),
            step_delta=sd,
            step_delta_signed=tuple(bsdr_encode(x) for x in sd),
            block_index=bi))
    return out


def _synthetic_sha1(rng, n, dv_pools, sd_pools, lengths, blocks):
    out = []
    for i in range(n):
        L = lengths[rng.randrange(len(lengths))]
        dv = dv_pools[L][rng.randrange(len(dv_pools[L]))]
        sd = sd_pools[L][rng.randrange(len(sd_pools[L]))]
        bi = blocks[rng.randrange(len(blocks))]
        out.append(PathObject(
            id=f"NULLB-SHA1-{i:04d}", primitive="sha1", step_range=(0, L - 1),
            provenance="internal", source_ref=TASK_ID, status="readable",
            path_data={"kind": "graph_null_independent_coordinate"},
            dv=dv, dv_seed_window=tuple(dv[:16]),
            in_linearized_code=P.sha1_in_linearized_code(list(dv)),
            step_delta=sd,
            step_delta_signed=tuple(bsdr_encode(x) for x in sd),
            block_index=bi))
    return out


def build_null_population(n_per_primitive: int = 400) -> dict:
    """The synthetic INDEPENDENT-COORDINATE population, subject to CTL-WF.

    Declared construction, fixed before any run: four lengths, a pool of five
    message-difference vectors per (primitive, length) -- INDEPENDENT OF LENGTH
    ON MD5, where the word count is always 16 -- a pool of five step_delta
    vectors per length, and four block indices, each coordinate drawn
    INDEPENDENTLY by its own draw from ONE random.Random at the declared seed
    SEEDS['null_draw_message_difference_perturbed'] (NO NINTH SEED). The pools
    are small ON PURPOSE so that the groups are LARGE: a null whose groups are
    all singletons would report an edge for every pair and would demonstrate
    nothing about the detector.
    """
    rng = random.Random(SEEDS["null_draw_message_difference_perturbed"])
    blocks = [0, 1, 2, 3]
    md5_lengths = [4, 6, 8, 10]
    sha1_lengths = [16, 17, 18, 19]
    md_pool = [tuple(rng.getrandbits(32) for _ in range(16)) for _ in range(5)]
    sd_pools = {L: [tuple(rng.getrandbits(32) for _ in range(L))
                    for _ in range(5)]
                for L in set(md5_lengths) | set(sha1_lengths)}
    dv_pools = {}
    for L in sha1_lengths:
        pool = [tuple(P.sha1_expand([rng.getrandbits(32) for _ in range(16)], L))]
        pool += [tuple(rng.getrandbits(32) for _ in range(L)) for _ in range(4)]
        dv_pools[L] = pool
    md5 = _synthetic_md5(rng, n_per_primitive, md_pool, sd_pools, md5_lengths,
                         blocks)
    sha1 = _synthetic_sha1(rng, n_per_primitive, dv_pools, sd_pools,
                           sha1_lengths, blocks)
    kept = {"md5": [o for o in md5 if wf_accepts(o)],
            "sha1": [o for o in sha1 if wf_accepts(o)]}
    rejected = {"md5": len(md5) - len(kept["md5"]),
                "sha1": len(sha1) - len(kept["sha1"])}
    return {"objects": kept, "drawn": {"md5": len(md5), "sha1": len(sha1)},
            "rejected_by_CTL_WF": rejected}


# ---------------------------------------------------------------------------
# the six d_X families
# ---------------------------------------------------------------------------

FAMILY_DECLARATIONS = {
    "d_message_difference": {
        "moves": ["message_difference"],
        "holds_fixed": ["primitive", "length", "step_delta", "block_index"],
        "recomputed_because_derived_from_the_moved_component":
            ["in_linearized_code (sha1)", "delta_m_signed (md5, not in the key)"],
        "declaration_text": (
            "THE COMMITTED FAMILY (d), REUSED AND NOT REBUILT: "
            "controlpower.perturb_message_difference at the committed draw plan "
            "-- k in (0,1,2,4,8,16), the deterministic draw plus 64 seeded draws "
            "per (entry, k>=1) off random.Random(84064107) consumed in census "
            "order then k ascending then draw index. Its own PERTURBATION "
            "DECLARATION is the committed "
            "controlpower.PERTURBATION_DECLARATION and is quoted verbatim in "
            "the result file."),
    },
    "d_step_delta": {
        "moves": ["step_delta"],
        "holds_fixed": ["primitive", "length", "message_difference",
                        "block_index", "in_linearized_code"],
        "recomputed_because_derived_from_the_moved_component":
            ["step_delta_signed (not in the strict key under E4)"],
        "declaration_text": (
            "NEW IN THIS MODULE. Flips k bits of the step_delta word vector, bit "
            "position p mapping to bit p%32 of word p//32 in stored order, and "
            "RECOMPUTES step_delta_signed with pathobj.bsdr_encode so that "
            "bsdr_decode(step_delta_signed[i]) == step_delta[i] and the object "
            "is not internally stale. It moves NOTHING else: the message "
            "difference, the step range, the block index and the flag are "
            "carried over unchanged. Draw plan: k in (0,1,2,4,8,16), the "
            "deterministic draw plus 8 seeded draws per (entry, k>=1)."),
    },
    "d_block_index": {
        "moves": ["block_index"],
        "holds_fixed": ["primitive", "length", "message_difference",
                        "step_delta", "in_linearized_code"],
        "recomputed_because_derived_from_the_moved_component": [],
        "declaration_text": (
            "NEW IN THIS MODULE. Sets block_index to a drawn value in 1..8, "
            "holding every other key component fixed. It is the same movement "
            "equivalence.act_E6_reindex performs, but E6 IS NOT IN THE STRICT "
            "GENERATOR SET, so under STRICT this is a genuine perturbation of a "
            "key component rather than an orbit image."),
    },
    "d_length": {
        "moves": ["length"],
        "holds_fixed": ["primitive", "message_difference", "step_delta",
                        "block_index", "in_linearized_code"],
        "recomputed_because_derived_from_the_moved_component": [],
        "declaration_text": (
            "NEW IN THIS MODULE, AND EXPECTED TO BE REJECTED BY CTL-WF ON EVERY "
            "DRAW RATHER THAN ASSERTED TO BE IMPOSSIBLE. Shortens step_range to "
            "(a, b-1) while holding every other key component fixed. It is "
            "constructed and gated so the outcome is MEASURED."),
    },
    "d_primitive": {
        "moves": ["primitive"],
        "holds_fixed": ["length", "message_difference", "step_delta",
                        "block_index", "in_linearized_code"],
        "recomputed_because_derived_from_the_moved_component": [],
        "declaration_text": (
            "NEW IN THIS MODULE, AND EXPECTED TO BE REJECTED BY CTL-WF ON EVERY "
            "DRAW RATHER THAN ASSERTED TO BE IMPOSSIBLE. Swaps the primitive "
            "label md5 <-> sha1 while holding every other field fixed. It is "
            "constructed and gated so the outcome is MEASURED."),
    },
    "d_in_linearized_code": {
        "moves": ["in_linearized_code"],
        "holds_fixed": ["primitive", "length", "message_difference",
                        "step_delta", "block_index"],
        "recomputed_because_derived_from_the_moved_component": [],
        "declaration_text": (
            "NEW IN THIS MODULE, AND IT IS NULL FAMILY (e) AS "
            "DEC-20260824-af6d5c P-4 SPECIFIED IT. Flips the flag with the dv "
            "held fixed. THIS CONTRACT BUILDS THE GATE AND DOES NOT EXECUTE "
            "FAMILY (e): the draws are constructed ONLY so CTL-WF's rejection is "
            "MEASURED, and family (e) remains an OPEN direction whose revisit "
            "condition is unchanged."),
    },
}


def _perturb_step_delta(obj, positions, tag):
    new = PathObject(**{**obj.__dict__})
    new.id = f"{obj.id}~SD{tag}"
    new.path_data = {"kind": "family_d_step_delta_perturbed", "of": obj.id,
                     "k": len(positions), "flipped_bit_positions": list(positions)}
    d = list(obj.step_delta)
    for p in positions:
        d[p // 32] ^= 1 << (p % 32)
    new.step_delta = tuple(d)
    new.step_delta_signed = tuple(bsdr_encode(x) for x in d)
    return new


def _perturb_block_index(obj, b, tag):
    new = PathObject(**{**obj.__dict__})
    new.id = f"{obj.id}~BI{tag}"
    new.path_data = {"kind": "family_d_block_index_perturbed", "of": obj.id,
                     "block_index": b}
    new.block_index = b
    return new


def _perturb_length(obj, tag):
    new = PathObject(**{**obj.__dict__})
    new.id = f"{obj.id}~LEN{tag}"
    new.path_data = {"kind": "family_d_length_perturbed", "of": obj.id}
    a, b = obj.step_range
    new.step_range = (a, max(a, b - 1))
    return new


def _perturb_primitive(obj, tag):
    new = PathObject(**{**obj.__dict__})
    new.id = f"{obj.id}~PRIM{tag}"
    new.path_data = {"kind": "family_d_primitive_perturbed", "of": obj.id}
    new.primitive = "sha1" if obj.primitive == "md5" else "md5"
    return new


def _perturb_flag(obj, tag):
    new = PathObject(**{**obj.__dict__})
    new.id = f"{obj.id}~FLAG{tag}"
    new.path_data = {"kind": "family_e_in_linearized_code_perturbed",
                     "of": obj.id}
    # ON MD5 THE HONEST VALUE IS None AND THERE IS NOTHING TO FLIP. Setting it
    # to True is the family's declaration honestly ATTEMPTED rather than quietly
    # turned into a no-op: the draw is then offered to CTL-WF, which rejects it
    # because the committed serialiser never reads the flag on md5. A no-op
    # "perturbation" that the gate accepts would report a family as
    # CONSTRUCTIBLE while moving nothing.
    new.in_linearized_code = (True if obj.in_linearized_code is None
                              else not obj.in_linearized_code)
    return new


def build_families(census) -> dict:
    """Every d_X family, EVERY DRAW GATED BY CTL-WF, rejections counted."""
    fams: dict = {}

    def new_fam(name):
        fams[name] = {"declaration": FAMILY_DECLARATIONS[name],
                      "draws": [], "rejected": {"md5": 0, "sha1": 0},
                      "constructed": {"md5": 0, "sha1": 0},
                      "rejection_reasons": {}}

    for name in FAMILY_DECLARATIONS:
        new_fam(name)

    def offer(name, entry, obj, k, draw_type):
        f = fams[name]
        prim = entry.primitive
        f["constructed"][prim] += 1
        bad = wf_violations(obj)
        if bad:
            f["rejected"][prim] += 1
            for b in bad:
                f["rejection_reasons"][b] = f["rejection_reasons"].get(b, 0) + 1
            return
        f["draws"].append({"entry": entry, "obj": obj, "k": k,
                           "draw_type": draw_type, "primitive": prim})

    # --- d_message_difference: THE COMMITTED FAMILY (d), REUSED
    for e, k, draw_type, obj in family_d_draws(census):
        offer("d_message_difference", e, obj, k, draw_type)

    # --- d_step_delta
    rng = random.Random(SEEDS["null_draw_message_difference_perturbed"])
    for e in census.shadow:
        nbits = 32 * len(e.obj.step_delta)
        for k in K_VALUES:
            plan = [("deterministic", tuple(range(k)))]
            if k >= 1:
                plan += [("seeded", tuple(sorted(rng.sample(range(nbits), k))))
                         for _ in range(R_NEW_FAMILIES)]
            for draw_type, pos in plan:
                offer("d_step_delta", e,
                      _perturb_step_delta(e.obj, pos, f"k{k}-{draw_type}"),
                      k, draw_type)

    # --- d_block_index
    rng = random.Random(SEEDS["null_draw_message_difference_perturbed"])
    for e in census.shadow:
        for k in K_VALUES:
            plan = [("deterministic", 0 if k == 0 else k)]
            if k >= 1:
                plan += [("seeded", rng.randrange(1, 9))
                         for _ in range(R_NEW_FAMILIES)]
            for draw_type, b in plan:
                offer("d_block_index", e,
                      _perturb_block_index(e.obj, b, f"k{k}-{draw_type}-{b}"),
                      k, draw_type)

    # --- the three families whose declaration may not be honourable
    for e in census.shadow:
        for k in K_VALUES:
            if k == 0:
                continue
            offer("d_length", e, _perturb_length(e.obj, f"k{k}"), k,
                  "deterministic")
            offer("d_primitive", e, _perturb_primitive(e.obj, f"k{k}"), k,
                  "deterministic")
            offer("d_in_linearized_code", e, _perturb_flag(e.obj, f"k{k}"), k,
                  "deterministic")

    for name, f in fams.items():
        per_prim = {}
        for prim in ("md5", "sha1"):
            kept = sum(1 for d in f["draws"] if d["primitive"] == prim)
            per_prim[prim] = {
                "constructed": f["constructed"][prim],
                "rejected_by_CTL_WF": f["rejected"][prim],
                "accepted": kept,
                "NOT_CONSTRUCTIBLE": (f["constructed"][prim] > 0 and kept == 0),
            }
        f["per_primitive"] = per_prim
        f["NOT_CONSTRUCTIBLE_on_every_primitive"] = all(
            v["NOT_CONSTRUCTIBLE"] for v in per_prim.values())
    return fams


# ---------------------------------------------------------------------------
# instruments: projections over the committed serialisation
# ---------------------------------------------------------------------------

def load_reused_O_E():
    """IR-11: O-E is REUSED from the committed red-team constructions."""
    path = os.path.join(RT_CONSTRUCTIONS, "rt_instruments.py")
    spec = importlib.util.spec_from_file_location("rt_instruments_reused", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rt_instruments_reused"] = mod
    spec.loader.exec_module(mod)
    return mod


def proj_honest(key, prim):
    return key


PROJ_NAMES = {
    "honest": ("THE COMMITTED SERIALISATION, UNMODIFIED -- the identity "
               "projection"),
    "O-E": ("THE KNOWN-FALSE INSTRUMENT, REUSED AND NOT REBUILT (IR-11): "
            "`proj_drop_on_primitive(['message_difference'], 'sha1')` IMPORTED "
            "FROM the committed constructions/rt_instruments.py of "
            "TASK-20260824-e9d21a. It is blind to the SHA-1 message difference "
            "and sighted on the MD5 one, which is why it lies outside "
            "BATCH-efcae7's declared lattice: controlpower.project() cannot "
            "express a per-primitive projection."),
    "always_member": ("A DEGENERATE NULL INSTRUMENT that returns MEMBER for "
                      "every object. It is not a projection; it is a verdict "
                      "function, run through the IDENTICAL counting rule."),
    "always_non_member": ("A DEGENERATE NULL INSTRUMENT that returns "
                          "NON-MEMBER for every object, run through the "
                          "IDENTICAL counting rule. It FAILS CTL-PLANT "
                          "OUTRIGHT and that is reported rather than hidden."),
}


# ---------------------------------------------------------------------------
# CTL-OFFDIAG -- the counting rule and the cell selector
# ---------------------------------------------------------------------------

CELL_RULE = (
    "DECLARED BEFORE ANY CELL IS COMPUTED, AND SHAPED ON THE COMMITTED "
    "family-(d) CLAUSE OF controlpower.DETECTION_RULE. Cell (family d_X, row "
    "deleting Y) is DETECTED for an instrument if and only if AT LEAST ONE "
    "PERTURBED DRAW (k >= 1) of family d_X is a STRICT MEMBER under that "
    "instrument's projection composed with the row's deletion, applied INSIDE "
    "the orbit minimisation over the committed variant list. The k = 0 arm and "
    "CTL-PLANT are reported SEPARATELY per instrument and are NOT folded into "
    "the cell verdict, DELIBERATELY: folding them in would make the degenerate "
    "always_non_member instrument report DETECTED everywhere and would destroy "
    "the counting rule's demonstrated capacity to be large in BOTH directions "
    "(CTL-NULL-OBJ, H-6). DETECTED means THE FAMILY'S OUTCOME CHANGES when the "
    "component is deleted; it is not a claim that the instrument is correct.")

EXCLUSION_REASONS = {
    "diagonal": (
        "CELL (d_X, row deleting X) IS EXCLUDED AND ITS VALUE IS STATED AS A "
        "THEOREM on the general rule TASK-20260824-e9d21a extracted at J13: a "
        "family perturbing exactly the set S while holding every other key "
        "component fixed makes the row deleting S DETECTED BY CONSTRUCTION, "
        "because the perturbed draw and its own source entry then agree on every "
        "retained component. Buying it with compute would pay for an answer "
        "already proved."),
    "forced_by_the_graph": (
        "CELL (d_X, row deleting Y) IS EXCLUDED BECAUSE THE DEPENDENCY GRAPH "
        "FORCES ITS VALUE: a component RETAINED by the row determines Y, so the "
        "row's projection is injective wherever the unablated key is and no "
        "draw's verdict can change. The forcing EDGE, with its derivation, is "
        "carried on the excluded cell."),
    "not_constructible": (
        "CELL EXCLUDED BECAUSE ITS FAMILY IS NOT CONSTRUCTIBLE UNDER CTL-WF: "
        "every draw the family's declaration produces contradicts the object's "
        "own redundant fields and is rejected by the gate. The cell is reported "
        "as NOT CONSTRUCTIBLE and NEVER as a zero, which would be a false "
        "negative wearing an integer."),
}


def select_cells(components: list, families: dict, forced: dict) -> dict:
    """The off-diagonal cell selector, with every exclusion carrying its reason."""
    adjudicated, excluded = [], []
    for fam_name, fam in families.items():
        moved = fam["declaration"]["moves"][0]
        for row in components:
            cell = {"family": fam_name, "row_deletes": row}
            if fam["NOT_CONSTRUCTIBLE_on_every_primitive"]:
                excluded.append({**cell, "exclusion": "not_constructible",
                                 "reason": EXCLUSION_REASONS["not_constructible"],
                                 "per_primitive_gate": fam["per_primitive"],
                                 "value": None})
                continue
            if row == moved:
                excluded.append({**cell, "exclusion": "diagonal",
                                 "reason": EXCLUSION_REASONS["diagonal"],
                                 "stated_value_as_a_theorem": "DETECTED",
                                 "value": None})
                continue
            forcing = forced.get(row)
            if forcing:
                excluded.append({**cell, "exclusion": "forced_by_the_graph",
                                 "reason": EXCLUSION_REASONS["forced_by_the_graph"],
                                 "forcing_edges": forcing,
                                 "stated_value_as_a_theorem": "NOT DETECTED",
                                 "value": None})
                continue
            adjudicated.append(cell)
    return {"adjudicated": adjudicated, "excluded": excluded}


# ---------------------------------------------------------------------------
# the key machinery shared by CTL-OFFDIAG, CTL-NULL-OBJ and CTL-RC1
# ---------------------------------------------------------------------------

def canon_under(keys, prim, proj, drop):
    """min over the committed variant list of the projected, ablated key.

    THE CONTRACT'S ORDER: project INSIDE the orbit minimisation, which
    BATCH-efcae7's Validator established is the same function as deleting the
    pair from the serialiser and minimising.
    """
    drop = frozenset(drop)
    return min(tuple(p for p in proj(k, prim) if p[0] not in drop) for k in keys)


def build_index(entry_keys, proj, drop):
    idx = {}
    for eid, (keys, prim) in entry_keys.items():
        idx.setdefault(canon_under(keys, prim, proj, drop), []).append(eid)
    return idx


def _params(suffix: str, extra: dict | None = None) -> dict:
    out = {
        "experiment_id": EXPERIMENT_ID,          # IR-7, the LITERAL id
        "run_suffix": suffix,
        "code_path_fingerprint": _fingerprint(),
        "armed_deadline_seconds": CEILINGS[suffix],
        "seeds": SEEDS,
        "seed_integrity": ("EXACTLY THE EIGHT SEEDS OF EXP-DIFFP-4b165f, "
                           "inherited byte-identically. NO NINTH SEED EXISTS "
                           "ANYWHERE IN THIS CONTRACT."),
        "network_requests": 0,
    }
    if extra:
        out.update(extra)
    return out


def _fingerprint() -> dict:
    return {
        "canonicalisation_and_membership_functions":
            list(ADJ.CODE_PATH_FINGERPRINT_FUNCTIONS) + [
                "harness.diffpath.controlpower.variant_keys",
                "harness.diffpath.controlpower.project",
                "harness.diffpath.controlpower.perturb_message_difference",
                "harness.diffpath.controlpower.perturb_by_codeword",
                "harness.diffpath.depgraph.detect_edge",
                "harness.diffpath.depgraph.wf_violations",
                "harness.diffpath.depgraph.canon_under",
                "harness.diffpath.depgraph.cell_verdict",
            ],
        "generator_set_in_force": sorted(STRICT),
        "module_sha256": digests(),
    }


CERT_NONE = {"kind": "none", "statement": {
    "why": ("PURE MEASUREMENT RUN. No discrete-log solve and no factor-base "
            "relation is claimed anywhere in EXP-DIFFP-04082e, and no collision, "
            "no differential path, no novelty and no cryptanalytic result of any "
            "kind is claimed. certificate.kind is set to `none` EXPLICITLY, as "
            "docs/claims-and-verification.md requires of a measurement run. The "
            "COUNTEREXAMPLE CERTIFICATES this contract emits are refutation "
            "artifacts carried inside the result files, not solution "
            "certificates.")}}


def cell_verdict(draw_keys, idx, prim_filter=None) -> dict:
    """The counting rule, IDENTICAL for every instrument (CTL-NULL-OBJ)."""
    member = draws = 0
    for prim, k, keys in draw_keys:
        if k < 1:
            continue
        if prim_filter and prim != prim_filter:
            continue
        draws += 1
        if idx(keys, prim):
            member += 1
    return {"verdict": "DETECTED" if member > 0 else "NOT DETECTED",
            "perturbed_draws_k_ge_1": draws,
            "strict_member_draws": member,
            "rule": CELL_RULE,
            "census_completeness": CENSUS_COMPLETENESS}


# ---------------------------------------------------------------------------
# CTL-PART -- the five-class partition, DERIVED FROM THE GRAPH ALONE
# ---------------------------------------------------------------------------

PARTITION_CLASSES = ("PROVABLY_UNDETECTABLE_BY_ANY_FAMILY",
                     "NOT_PROBED_BY_A_DECLARED_FAMILY",
                     "PROBED_AND_GENUINELY_NOT_DETECTED",
                     "ENTAILED_BY_THE_PERTURBING_FAMILYS_OWN_DECLARATION",
                     "CONTINGENT_ON_THE_INSTRUMENT")

ASSIGNING_RULE = (
    "DECLARED BEFORE IT IS RUN AND APPLIED IN THIS PRECEDENCE, USING ONLY (i) "
    "the CTL-DEP graph and (ii) each declared family's OWN perturbation "
    "declaration. NO VERDICT COLUMN OF BATCH-efcae7 IS READ BY THIS FUNCTION. "
    "R1 PROVABLY_UNDETECTABLE_BY_ANY_FAMILY -- some component the row RETAINS "
    "determines the deleted one by an edge that carries a DERIVATION from "
    "committed source (an `empirical_only` edge may not carry this class, H-1), "
    "or the deleted component is not in that primitive's key at all. R2 "
    "ENTAILED_BY_THE_PERTURBING_FAMILYS_OWN_DECLARATION -- a declared family's "
    "own declaration names the deleted component as EXACTLY what it moves while "
    "holding the rest fixed. R3 CONTINGENT_ON_THE_INSTRUMENT -- some declared "
    "draw ISOLATES the component: its canonical key differs from a census "
    "entry's in that component ALONE, so deleting it makes that draw a member "
    "and the verdict turns on which draws the instrument happens to produce. R4 "
    "PROBED_AND_GENUINELY_NOT_DETECTED -- some declared draw differs from ITS "
    "OWN SOURCE census entry in the component but no draw isolates it. R5 "
    "NOT_PROBED_BY_A_DECLARED_FAMILY -- no declared draw differs from its own "
    "source entry in the component and none isolates it. THE OWN-SOURCE "
    "QUANTIFIER IN R4 AND R5 IS DELIBERATE AND IS THE ONE CORR-20260824-c1c8b1 "
    "RECORDS: a fresh null draw of families (a), (b) and (c) has NO source "
    "entry, so it can only speak through R3's isolation test, and the weaker "
    "statement `differs from SOME entry in X` -- which every cross-primitive "
    "comparison satisfies for `primitive` -- is REPORTED as a separate "
    "diagnostic and is NOT used by the rule.")

ISOLATION_QUANTIFIER_NOTE = (
    "QUANTIFIED OVER EXACTLY WHAT THE FUNCTION COMPUTES (H-7, "
    "CORR-20260824-c1c8b1). `isolating_draw_exists(X)` means: THERE EXISTS a "
    "draw D among the declared families and THERE EXISTS a census entry C -- ANY "
    "entry, not necessarily D's own source -- such that the committed "
    "attribution of D's strict canonical key against C's is EXACTLY [X]. "
    "`own_source_differing(X)` is the STRICTLY DIFFERENT statement that a draw "
    "differs from ITS OWN SOURCE entry in X, possibly among other components. "
    "Both are reported; neither is described in the other's words.")


def probing_profile(entry_keys, draw_keys_with_source, components) -> dict:
    """Which components the DECLARED families actually move, two ways."""
    prof = {c: {"isolating_draw_exists": False,
                "isolating_draw_count": 0,
                "isolating_examples": [],
                "own_source_differing": False,
                "own_source_differing_count": 0,
                "any_draw_differing_from_some_entry": False} for c in components}
    ent = {eid: min(k) for eid, (k, p) in entry_keys.items()}
    for rec in draw_keys_with_source:
        dk = min(rec["keys"])
        for eid, ek in ent.items():
            attr = CP.attribution(dk, ek)
            if len(attr) == 1 and attr[0] in prof:
                prof[attr[0]]["isolating_draw_exists"] = True
                prof[attr[0]]["isolating_draw_count"] += 1
                if len(prof[attr[0]]["isolating_examples"]) < 5:
                    prof[attr[0]]["isolating_examples"].append(
                        {"draw": rec["id"], "family": rec["family"],
                         "matched_entry": eid, "own_source": rec["source"],
                         "is_its_own_source": eid == rec["source"]})
            for a in attr:
                if a in prof:
                    prof[a]["any_draw_differing_from_some_entry"] = True
        if rec["source"] is None:
            # A FRESH NULL DRAW OF FAMILIES (a), (b) OR (c) HAS NO SOURCE ENTRY
            # AND CONTRIBUTES NOTHING TO THE OWN-SOURCE STATISTIC. Comparing it
            # against the empty key would report EVERY component as differing,
            # which is the strictly stronger statement CORR-20260824-c1c8b1
            # records the cost of. Such a draw speaks ONLY through R3's
            # isolation test above.
            continue
        own = CP.attribution(dk, ent.get(rec["source"], ()))
        for a in own:
            if a in prof:
                prof[a]["own_source_differing"] = True
                prof[a]["own_source_differing_count"] += 1
    for c in prof:
        prof[c]["quantifier_note"] = ISOLATION_QUANTIFIER_NOTE
    return prof


def derive_partition(components, edges_by_prim, families, probing,
                     key_components_by_prim) -> dict:
    rows = []
    for comp in components:
        per_prim = {}
        for prim in ("md5", "sha1"):
            in_key = comp in key_components_by_prim[prim]
            forcing = [r for r in edges_by_prim[prim]
                       if r["Y"] == comp and r["verdict"] == "EDGE"
                       and r["label"] == "derived_and_witnessed"]
            if not in_key:
                per_prim[prim] = {
                    "class": "PROVABLY_UNDETECTABLE_BY_ANY_FAMILY",
                    "rule_fired": "R1",
                    "because": (f"{comp} IS NOT A COMPONENT OF THE {prim} "
                                f"MEMBERSHIP KEY AT ALL: the committed "
                                f"serialiser never emits it on this primitive, "
                                f"so deleting it is the identity on every "
                                f"{prim} key."),
                    "forcing_edges": []}
            elif forcing:
                per_prim[prim] = {
                    "class": "PROVABLY_UNDETECTABLE_BY_ANY_FAMILY",
                    "rule_fired": "R1",
                    "because": (f"a component the row RETAINS determines "
                                f"{comp} by a derived edge, so the ablated key "
                                f"separates exactly the objects the unablated "
                                f"key separates"),
                    "forcing_edges": [{"X": r["X"], "Y": r["Y"],
                                       "derivation": r["derivation"],
                                       "witness": {
                                           "population_size": r["population_size"],
                                           "distinct_X": r["distinct_X"],
                                           "groups_constant_in_Y":
                                               r["groups_constant_in_Y"],
                                           "groups_total": r["groups_total"]}}
                                      for r in forcing]}
            else:
                fam = [n for n, f in families.items()
                       if f["declaration"]["moves"] == [comp]
                       and not f["NOT_CONSTRUCTIBLE_on_every_primitive"]
                       and n == "d_message_difference"]
                pr = probing[comp]
                if fam:
                    per_prim[prim] = {
                        "class": "ENTAILED_BY_THE_PERTURBING_FAMILYS_OWN_"
                                 "DECLARATION",
                        "rule_fired": "R2",
                        "because": (f"the DECLARED family {fam[0]} states that "
                                    f"it moves EXACTLY {comp} and holds every "
                                    f"other key component fixed, so a draw and "
                                    f"its own source entry agree on every "
                                    f"retained component once {comp} is deleted"),
                        "family_declaration":
                            families[fam[0]]["declaration"]["declaration_text"]}
                elif pr["isolating_draw_exists"]:
                    per_prim[prim] = {
                        "class": "CONTINGENT_ON_THE_INSTRUMENT",
                        "rule_fired": "R3",
                        "because": ("a declared draw ISOLATES this component "
                                    "against some census entry, so the verdict "
                                    "turns on which draws the instrument "
                                    "happens to produce rather than on a "
                                    "declaration or on the graph"),
                        "isolating_draw_count": pr["isolating_draw_count"],
                        "isolating_examples": pr["isolating_examples"],
                        "quantifier_note": ISOLATION_QUANTIFIER_NOTE}
                elif pr["own_source_differing"]:
                    per_prim[prim] = {
                        "class": "PROBED_AND_GENUINELY_NOT_DETECTED",
                        "rule_fired": "R4",
                        "because": ("declared draws differ from THEIR OWN "
                                    "SOURCE census entry in this component but "
                                    "NO draw isolates it, "
                                    "so every such draw is already separated by "
                                    "another retained component")}
                else:
                    per_prim[prim] = {
                        "class": "NOT_PROBED_BY_A_DECLARED_FAMILY",
                        "rule_fired": "R5",
                        "because": ("NO declared draw differs from ITS OWN "
                                    "SOURCE census entry in this component and "
                                    "none isolates it. THIS IS A "
                                    "COVERAGE STATEMENT ABOUT THE DECLARED "
                                    "FAMILIES AND IS NOT EVIDENCE THAT A "
                                    "PROBING FAMILY WOULD FIND NOTHING.")}
        classes = {v["class"] for v in per_prim.values()}
        if classes == {"PROVABLY_UNDETECTABLE_BY_ANY_FAMILY"}:
            row_class = "PROVABLY_UNDETECTABLE_BY_ANY_FAMILY"
        else:
            order = ["CONTINGENT_ON_THE_INSTRUMENT",
                     "ENTAILED_BY_THE_PERTURBING_FAMILYS_OWN_DECLARATION",
                     "PROBED_AND_GENUINELY_NOT_DETECTED",
                     "NOT_PROBED_BY_A_DECLARED_FAMILY",
                     "PROVABLY_UNDETECTABLE_BY_ANY_FAMILY"]
            row_class = next(c for c in order if c in classes)
        rows.append({
            "row_deletes": comp,
            "row_class": row_class,
            "per_primitive": per_prim,
            "combination_rule": (
                "A ROW IS GIVEN THE PROVABLY_UNDETECTABLE CLASS ONLY IF IT HOLDS "
                "ON EVERY PRIMITIVE; otherwise the row takes the strongest "
                "per-primitive class in the order contingent > entailed > probed "
                "and not detected > not probed > provably undetectable, because "
                "the depth-1 lattice row of BATCH-efcae7 deletes the component "
                "on BOTH primitives at once and its verdict is the OR over "
                "them."),
            "census_completeness": CENSUS_COMPLETENESS,
            "assigning_rule": ASSIGNING_RULE})
    counts = {c: sum(1 for r in rows if r["row_class"] == c)
              for c in PARTITION_CLASSES}
    return {"rows": rows, "class_counts_aggregate": counts,
            "rows_total": len(rows)}


# ---------------------------------------------------------------------------
# CTL-DEPTH2
# ---------------------------------------------------------------------------

DEPTH2_RULE = (
    "A SUBSET S OF SIZE TWO BREAKS A DEPENDENCY, ON A GIVEN PRIMITIVE, IF AND "
    "ONLY IF SOME X IN S IS DETERMINED BY AT LEAST ONE DERIVED EDGE AND EVERY "
    "COMPONENT THAT DETERMINES X BY A DERIVED EDGE IS ALSO IN S -- so the "
    "information deleting X alone leaves recoverable is no longer recoverable "
    "once S is deleted. A subset containing a component with no determiner at "
    "all does not thereby break a dependency: deleting that component already "
    "removed information at depth 1.")

DEPTH2_LIMIT = (
    "IT DOES NOT MEASURE THE NON-BREAKING SUBSETS AND A NON-BREAKING SUBSET IS "
    "NOT THEREBY SAFE. Three of them are ALREADY MEASURED to pass the "
    "strengthened suite as blind instruments -- O-C (block_index + length), "
    "O-C-prime (block_index + in_linearized_code) and the depth-3 "
    "O-C-double-prime -- by TASK-20260824-e9d21a. 'DOES NOT BREAK A DEPENDENCY' "
    "NEVER MEANS 'CANNOT HIDE A KNOWN-FALSE INSTRUMENT'.")


def classify_depth2(components, edges_by_prim, key_components_by_prim) -> dict:
    det = {}
    for prim in ("md5", "sha1"):
        d = {c: [] for c in components}
        for r in edges_by_prim[prim]:
            if (r["verdict"] == "EDGE" and r["label"] == "derived_and_witnessed"
                    and r["Y"] in d):
                d[r["Y"]].append(r["X"])
        det[prim] = d
    subsets = []
    for i in range(len(components)):
        for j in range(i + 1, len(components)):
            S = (components[i], components[j])
            per_prim = {}
            for prim in ("md5", "sha1"):
                broken = []
                for X in S:
                    if X not in key_components_by_prim[prim]:
                        continue
                    dets = [y for y in det[prim][X]
                            if y in key_components_by_prim[prim]]
                    if dets and all(y in S for y in dets):
                        broken.append({"component": X, "determiners": dets})
                per_prim[prim] = {
                    "breaks_a_dependency": bool(broken),
                    "broken": broken,
                    "reason": (
                        f"on {prim} the deleted set {list(S)} removes "
                        + (", ".join(f"{b['component']} together with every "
                                     f"derived determiner of it ({b['determiners']})"
                                     for b in broken)
                           if broken else
                           "no component together with all of its derived "
                           "determiners"))}
            subsets.append({
                "subset": list(S),
                "breaks_a_dependency_on_some_primitive":
                    any(v["breaks_a_dependency"] for v in per_prim.values()),
                "per_primitive": per_prim,
                "census_completeness": CENSUS_COMPLETENESS})
    return {"subsets": subsets,
            "subsets_total": len(subsets),
            "breaking_subsets_aggregate":
                sum(1 for s in subsets
                    if s["breaks_a_dependency_on_some_primitive"]),
            "rule": DEPTH2_RULE,
            "what_this_does_not_buy": DEPTH2_LIMIT}


# ---------------------------------------------------------------------------
# artifact writing
# ---------------------------------------------------------------------------

def _write_json(name: str, doc: dict) -> str:
    os.makedirs(TASK_ROOT, exist_ok=True)
    path = os.path.join(TASK_ROOT, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, default=str)
        fh.write("\n")
    return path


def _sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _inference_supplement() -> dict:
    return {
        "requested_policy": "executor-implementation",
        "requested_policy_source":
            "ledger/handoffs/TASK-20260824-68ba87.yaml inference.policy",
        "backend": os.environ.get("AUTORESEARCH_BACKEND")
                   or "anthropic (claude_code runtime)",
        "resolved_model_id": os.environ.get("AUTORESEARCH_RESOLVED_MODEL")
                             or "claude-opus-5",
        "resolved_model_provenance": (
            "self-reported by the answering runtime in its own system context; "
            "NOT probe-verified in this session"),
        "probe_verified": False,
        "reasoning_effort": None,
        "reasoning_effort_note": (
            "the handoff declares inference.reasoning_effort null; the executor "
            "subagent binding carries `medium` per CLAUDE.md's effort table"),
        "fallback_allowed": False,
        "fallback_used": False,
        "degraded_allowed": False,
        "degraded_requirements": None,
        "amazon_bedrock_used": False,
        "shared_runner_discrepancy": (
            "harness/runner.py writes run.inference.requested_policy = "
            "'executor-terra' into every manifest program-wide: it defines "
            "_inference_block() TWICE, at module level, and Python binds the "
            "LAST definition, so the adapter-backed path is dead code. KNOWN, "
            "recorded by BATCH-f8bf86, and OUT OF SCOPE here -- IR-2 forbids "
            "editing harness/runner.py. THE TRUE VALUES ARE THE ONES IN THIS "
            "BLOCK. Infrastructure/provenance defect, never evidence about MD5 "
            "or SHA-1."),
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
            "IR-3, STATED PRECISELY. ZERO network requests left this task by any "
            "route: no curl, wget, git fetch, package-manager invocation or MCP "
            "fetch was issued at any point, and no byte of any source of any "
            "tier was acquired. AMD-20260824-DIFFP-ACQ-1 stands unchanged: Tier "
            "A refused by every route, TIER B BLOCKED PENDING A GOAL-MD5-001 "
            "DECISION -- BLOCKED, NOT CLOSED, with its named unblocking route "
            "intact -- Tier C permitted and not exercised."),
        "quarantine_attestation": QUARANTINE_MECHANISM,
        "tier_a_content_obtained": False,
        "tier_b_content_obtained": False,
        "tier_c_content_obtained": False,
        "environment_compat_shim": COMPAT,
    }


def write_supplement(run_dir: str, suffix: str, extra: dict | None = None) -> str:
    import yaml
    doc = {"manifest_supplement": {
        "run_suffix": suffix,
        "experiment_id": EXPERIMENT_ID,
        "task_id": TASK_ID, "goal_id": GOAL_ID, "batch_id": BATCH_ID,
        "code_path_fingerprint": _fingerprint(),
        "armed_deadline_seconds": CEILINGS[suffix],
        "deadline_mechanism": ("signal.setitimer(ITIMER_REAL) inside the run "
                               "function via harness.diffpath.controlpower."
                               "Deadline, bracketed by harness.runner."
                               "run_wrapped"),
        "seeds": SEEDS,
        "inference": _inference_supplement(),
        "environment": _environment_supplement(),
        "why_this_file_exists": (
            "harness/runner.py is a committed file this contract forbids "
            "editing (IR-2) and its own inference block is both stale and "
            "unable to express this task's true values. code_path_fingerprint "
            "and the armed deadline are ALSO written inside manifest.yaml at "
            "run.inputs.parameters, so the manifest itself does not lack them "
            "(IR-7)."),
    }}
    if extra:
        doc["manifest_supplement"].update(extra)
    path = os.path.join(run_dir, "manifest-supplement.yaml")
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(doc, fh, sort_keys=False, default_flow_style=False)
    return path


# ---------------------------------------------------------------------------
# RUN 1 -- CTL-FROZEN-3 pre, CTL-WF, CTL-DEP, CTL-GRAPH-NULL
# ---------------------------------------------------------------------------

def run_graph(state: dict):
    census = state["census"]
    lines = []

    # --- IR-13
    comp = derive_components(census)
    state["components"] = comp["derived_union_in_first_appearance_order"]
    state["key_components_by_prim"] = comp["derived_per_primitive"]
    if not comp["agrees_with_contract_in_order"]:
        lines.append("IR-13 STOP: derived component list differs from the "
                     "contract's six names")
    lines.append("derived strict key components per primitive: "
                 + json.dumps(comp["derived_per_primitive"]))

    # --- CTL-WF, two-sided
    accept_cases, reject_cases = [], []
    for e in census.shadow:
        for o, tag in [(e.obj, "census_entry")] + [
                (i, "strict_orbit_image") for i in ADJ.orbit_images(e.obj, STRICT)]:
            accept_cases.append((o, tag, e.primitive))
        if e.primitive == "sha1":
            reject_cases.append((malformed_null_family_e(e.obj),
                                 "deliberately_malformed_flag_flipped",
                                 e.primitive))
    acc = {"md5": {"checked": 0, "accepted": 0}, "sha1": {"checked": 0,
                                                          "accepted": 0}}
    acc_fail = []
    for o, tag, prim in accept_cases:
        acc[prim]["checked"] += 1
        v = wf_violations(o)
        if not v:
            acc[prim]["accepted"] += 1
        else:
            acc_fail.append({"object": o.id, "case": tag, "violations": v})
    rej = {"checked": 0, "rejected": 0, "wrongly_accepted": []}
    for o, tag, prim in reject_cases:
        rej["checked"] += 1
        v = wf_violations(o)
        if v:
            rej["rejected"] += 1
        else:
            rej["wrongly_accepted"].append(o.id)
    families = build_families(census)
    state["families"] = families
    wf_doc = {
        "control": "CTL-WF", "status": "COMPLETED",
        "checks": WF_CHECKS,
        "known_answer_two_sided": (
            "THE GATE MUST BOTH ACCEPT AND REJECT. It must ACCEPT all 16 census "
            "entries and all their orbit images under the STRICT generator set, "
            "and it must REJECT a deliberately malformed object -- a SHA-1 entry "
            "with in_linearized_code FLIPPED and the dv held fixed, which is "
            "null family (e) as DEC-20260824-af6d5c P-4 specified it. A GATE "
            "THAT ACCEPTS EVERYTHING IS NOT A GATE."),
        "accept_side_per_primitive": acc,
        "accept_side_failures_reported_in_full": acc_fail,
        "reject_side": rej,
        "gate_is_two_sided_on_this_population": (
            not acc_fail and rej["rejected"] == rej["checked"]
            and rej["checked"] > 0),
        "per_family_per_primitive_rejection_counts": {
            n: f["per_primitive"] for n, f in families.items()},
        "family_declarations": {n: f["declaration"] for n, f in families.items()},
        "census_completeness": CENSUS_COMPLETENESS,
        "family_e_is_not_executed_by_this_contract": (
            "THE d_in_linearized_code DRAWS ARE CONSTRUCTED ONLY SO THE GATE'S "
            "REJECTION IS MEASURED. Null family (e) remains an OPEN direction "
            "with its revisit condition unchanged; this contract builds the gate "
            "DEC-20260824-c5bb72 made its precondition and does not build the "
            "family."),
    }
    _write_json("wellformedness-gate-result.json", wf_doc)
    lines.append(f"CTL-WF accept side: {acc}; reject side: {rej}")

    # --- CTL-DEP
    pop = declared_population(census)
    state["population"] = pop
    edges_by_prim = {}
    for prim in ("md5", "sha1"):
        edges_by_prim[prim] = edge_records(pop["objects"][prim], prim,
                                           state["components"])
    state["edges_by_prim"] = edges_by_prim
    contradictions = [r for prim in edges_by_prim
                      for r in edges_by_prim[prim]
                      if r.get("CONTRADICTION_DERIVATION_WITH_FAILING_WITNESS")]
    dep_doc = {
        "control": "CTL-DEP", "status": "COMPLETED",
        "derived_key_components_IR13": comp,
        "declared_object_population": {
            "declaration": pop["declaration"],
            "population_sizes_per_primitive": pop["population_sizes"],
            "provenance_counts_per_primitive": pop["provenance_counts"]},
        "edge_rule": EDGE_RULE,
        "ordered_pair_verdicts_per_primitive": edges_by_prim,
        "ordered_pairs_decided_aggregate": {
            prim: len(edges_by_prim[prim]) for prim in edges_by_prim},
        "edges_with_a_derivation_and_a_witness": {
            prim: [[r["X"], r["Y"]] for r in edges_by_prim[prim]
                   if r["verdict"] == "EDGE"
                   and r["label"] == "derived_and_witnessed"]
            for prim in edges_by_prim},
        "edges_labelled_empirical_only": {
            prim: [[r["X"], r["Y"]] for r in edges_by_prim[prim]
                   if r["verdict"] == "EDGE" and r["label"] == "empirical_only"]
            for prim in edges_by_prim},
        "edges_labelled_scope_artifact": {
            prim: [[r["X"], r["Y"]] for r in edges_by_prim[prim]
                   if r["verdict"] == "EDGE" and r["label"] == "scope_artifact"]
            for prim in edges_by_prim},
        "counterexample_certificates_reported_in_full": {
            prim: [r["counterexample_certificate"]
                   for r in edges_by_prim[prim] if "counterexample_certificate" in r]
            for prim in edges_by_prim},
        "derivation_with_a_failing_witness_is_a_STOP": contradictions,
        "pre_registered_expectation_P_A": (
            "in_linearized_code = f(message_difference) on SHA-1 objects at full "
            "step range, measured by TASK-20260824-e9d21a on 960 objects with "
            "ZERO exceptions. THAT MEASUREMENT IS AN INPUT AND ITS REPRODUCTION "
            "IS EXPECTED; the DERIVATION is this control's real work and is "
            "carried on the edge itself."),
        "census_completeness": CENSUS_COMPLETENESS,
        "interpretation_limit": (
            "A DEPENDENCY EDGE IS SCOPED TO THE DECLARED OBJECT POPULATION AND "
            "TO THIS CENSUS. Every planted SHA-1 entry is IN THE LINEARIZED "
            "CODE, so an edge that holds because of that is an edge about this "
            "census. AN EDGE IS NOT A THEOREM ABOUT THE ADJUDICATOR IN GENERAL "
            "AND IS NEVER A THEOREM ABOUT SHA-1 OR MD5."),
        "structural_observation_on_O_RT2": {
            "what_is_observed": (
                "primitives.sha1_in_linearized_code(words) RETURNS "
                "sha1_expand(words[:16], len(words)) == list(words). THEREFORE, "
                "ON ANY OBJECT WHOSE FLAG IS TRUE, the whole message-difference "
                "value IS the expansion of its own first 16 words, so the SHA-1 "
                "membership key restricted to IN-CODE objects carries at most "
                "512 bits of message difference plus one flag bit rather than "
                "the 2560 bits its serialised width suggests. THIS IS A "
                "DERIVATION FROM COMMITTED SOURCE, and it is scoped to IN-CODE "
                "objects: on a flag-FALSE object the first 16 words determine "
                "nothing about the rest."),
            "what_is_NOT_concluded": (
                "NOTHING ABOUT WHETHER O-RT2 IS A GOOD OR A KNOWN-FALSE "
                "INSTRUMENT. This module records the structural fact and the "
                "non-injectivity witness below; the judgement belongs to the "
                "Reviewer and the Coordinator (IR-8 / H-11). NO STATEMENT ABOUT "
                "SHA-1's DIFFERENCE SPACE IS MADE OR LICENSED."),
        },
    }
    _write_json("dependency-graph-result.json", dep_doc)
    for prim in edges_by_prim:
        n_edge = sum(1 for r in edges_by_prim[prim] if r["verdict"] == "EDGE")
        lines.append(f"CTL-DEP {prim}: {len(edges_by_prim[prim])} ordered pairs, "
                     f"{n_edge} EDGE verdicts, population "
                     f"{pop['population_sizes'][prim]}")

    # --- CTL-GRAPH-NULL
    nullpop = build_null_population()
    null_records = {}
    for prim in ("md5", "sha1"):
        null_records[prim] = edge_records(nullpop["objects"][prim], prim,
                                          state["components"])
    outside = {}
    for prim in ("md5", "sha1"):
        outside[prim] = [
            [r["X"], r["Y"]] for r in null_records[prim]
            if r["verdict"] == "EDGE"
            and not r["Y_CONSTANT_ON_POPULATION"]
            and (r["X"], r["Y"]) not in NULL_FORCED_PAIRS[prim]]
    md5_flag_pairs = [r for r in edges_by_prim["md5"]
                      if r["Y"] == "in_linearized_code"
                      and r["X"] == "message_difference"]
    null_doc = {
        "control": "CTL-GRAPH-NULL", "status": "COMPLETED",
        "why_it_runs_before_any_edge_is_believed": (
            "docs/inventor-protocol.md requires a null-object control BEFORE "
            "belief. A procedure that reports `Y is constant within every "
            "X-group` will report an edge for ANY pair whenever the population "
            "has few enough distinct X values, or whenever every group is a "
            "singleton."),
        "null_population_A_the_md5_sub_population": {
            "pair": ["message_difference", "in_linearized_code"],
            "verdicts": md5_flag_pairs,
            "the_reason_that_must_be_named": (
                "ON MD5 THE FLAG HAS NO DEFINING FUNCTION OF THE MESSAGE "
                "DIFFERENCE IN THE COMMITTED SOURCE and is not a key component "
                "at all: pathobj.plant_from_pair leaves in_linearized_code None "
                "on every md5 object, so the flag takes ONE CONSTANT VALUE on "
                "the whole md5 sub-population. AN EDGE REPORTED HERE IS A "
                "PROPERTY OF A CONSTANT COLUMN AND NOT A DEPENDENCY, and it is "
                "flagged Y_CONSTANT_ON_POPULATION beside the verdict."),
        },
        "null_population_B_synthetic_independent_coordinates": {
            "construction": build_null_population.__doc__,
            "drawn": nullpop["drawn"],
            "rejected_by_CTL_WF": nullpop["rejected_by_CTL_WF"],
            "population_sizes": {k: len(v) for k, v in nullpop["objects"].items()},
            "verdicts_per_primitive": null_records,
            "edges_returned_total_the_contracts_literal_quantity": {
                prim: sum(1 for r in null_records[prim] if r["verdict"] == "EDGE")
                for prim in null_records},
            "edges_returned_outside_the_declared_forced_set": outside,
            "declared_forced_set": {k: [list(p) for p in v]
                                    for k, v in NULL_FORCED_PAIRS.items()},
            "declared_forced_set_note": NULL_FORCED_SET_DECLARATION,
            "STOP_condition_applied_to":
                "edges_returned_outside_the_declared_forced_set",
            "detector_returned_NO_EDGE_somewhere": {
                prim: sum(1 for r in null_records[prim]
                          if r["verdict"] == "NO EDGE")
                for prim in null_records},
        },
        "census_completeness": CENSUS_COMPLETENESS,
    }
    _write_json("graph-null-control-result.json", null_doc)
    lines.append("CTL-GRAPH-NULL edges outside the declared forced set: "
                 + json.dumps(outside))
    state["graph_null_outside"] = outside

    metrics = {
        "ordered_pairs_decided_md5_aggregate": len(edges_by_prim["md5"]),
        "ordered_pairs_decided_sha1_aggregate": len(edges_by_prim["sha1"]),
        "edges_derived_and_witnessed_md5_aggregate": len(
            dep_doc["edges_with_a_derivation_and_a_witness"]["md5"]),
        "edges_derived_and_witnessed_sha1_aggregate": len(
            dep_doc["edges_with_a_derivation_and_a_witness"]["sha1"]),
        "population_size_md5": pop["population_sizes"]["md5"],
        "population_size_sha1": pop["population_sizes"]["sha1"],
        "graph_null_edges_outside_forced_set_md5_aggregate": len(outside["md5"]),
        "graph_null_edges_outside_forced_set_sha1_aggregate": len(outside["sha1"]),
        "wf_accept_failures_aggregate": len(acc_fail),
        "wf_malformed_rejected_aggregate": rej["rejected"],
    }
    return RunResult(
        run_suffix="frozen-and-dependency-graph", curve_id="n/a-hash-primitive",
        seed=SEEDS["null_draw_message_difference_perturbed"],
        parameters=_params("frozen-and-dependency-graph"),
        metrics=metrics, certificate=CERT_NONE, valid=True,
        stdout="\n".join(lines) + "\n", stderr=""), {
            "wellformedness": wf_doc, "dependency_graph": dep_doc,
            "graph_null": null_doc}


# ---------------------------------------------------------------------------
# RUN 2 -- CTL-PART (derived, THEN compared) and CTL-DEPTH2
# ---------------------------------------------------------------------------

ORDER_DECLARATION = (
    "THE ORDER IS DECLARED PLAINLY AND ITS LIMIT IS STATED IN THE SAME BREATH. "
    "partition-derived.json IS WRITTEN AND CLOSED BY THIS PROCESS BEFORE ANY "
    "BYTE OF BATCH-efcae7's VERDICT COLUMN IS OPENED: the derivation function "
    "reads only the CTL-DEP graph and the declared families' own perturbation "
    "declarations, and the comparison function opens the committed records "
    "afterwards, in the same process, in that order. NO TOOL HERE CAN CHECK "
    "READ ORDER, SO THIS IS CORROBORATION AND NOT PROOF. "
    "ONE DISCLOSURE THAT WEAKENS IT AND IS STATED RATHER THAN OMITTED: the "
    "FROZEN CONTRACT ITSELF, which the producer must read before running "
    "anything, PRINTS THE PRE-REGISTERED TARGET WITH ITS PER-ROW ASSIGNMENT "
    "(CTL-PART `the_pre_registered_target` and preregistered_prediction P-B). "
    "The producer therefore could not be blind to the target, only to "
    "BATCH-efcae7's own DETECTED / NOT DETECTED verdict column, which it did "
    "not open until this file was closed. THAT IS THE HONEST SCOPE OF THE "
    "CLAIM.")


def read_batch_efcae7_column() -> dict:
    """Opened ONLY after partition-derived.json is written and closed."""
    import yaml
    out = {}
    for rel in ("ledger/evidence/EV-DIFFP-b16b01.yaml",
                "ledger/decisions/DEC-20260824-c5bb72.yaml"):
        path = os.path.join(REPO, rel)
        found = {}
        try:
            doc = yaml.safe_load(open(path, encoding="utf-8"))

            def walk(node, trail):
                if isinstance(node, dict):
                    for k, v in node.items():
                        if any(t in str(k).lower() for t in
                               ("per_component", "power_table", "power_profile",
                                "obstruction", "depth_1", "depth1")):
                            found["/".join(trail + [str(k)])] = v
                        else:
                            walk(v, trail + [str(k)])
                elif isinstance(node, list):
                    for i, v in enumerate(node):
                        walk(v, trail + [str(i)])
            walk(doc, [])
        except Exception as exc:                                 # noqa: BLE001
            found["READ_ERROR"] = f"{type(exc).__name__}: {exc}"
        out[rel] = found
    return out


PRE_REGISTERED_PARTITION = {
    "in_linearized_code": "PROVABLY_UNDETECTABLE_BY_ANY_FAMILY",
    "primitive": "NOT_PROBED_BY_A_DECLARED_FAMILY",
    "length": "NOT_PROBED_BY_A_DECLARED_FAMILY",
    "block_index": "NOT_PROBED_BY_A_DECLARED_FAMILY",
    "message_difference": "ENTAILED_BY_THE_PERTURBING_FAMILYS_OWN_DECLARATION",
    "step_delta": "CONTINGENT_ON_THE_INSTRUMENT",
    "_provenance": (
        "QUOTED FROM EXP-DIFFP-04082e CTL-PART `the_pre_registered_target` and "
        "preregistered_prediction P-B, which the contract itself attributes to "
        "DEC-20260824-c5bb72 `per_component_power_table` and EV-DIFFP-b16b01 "
        "`obstruction.value` AND MARKS AS MEASURED BY THAT SESSION AND NOT BY "
        "THE COORDINATOR (BR-6). It is 1 / 3 / 0 / 1 / 1 summing to the six "
        "rows. IT IS NOT RE-MEASURED HERE and it is not this producer's value."),
}


def run_partition(state: dict):
    census = state["census"]
    lines = []
    entry_keys = {e.id: (CP.variant_keys(e.obj, STRICT), e.primitive)
                  for e in census.shadow}
    state["entry_keys"] = entry_keys

    draws = []
    for fam, d in CP.null_draws(census, n=1000).items():
        for o in d["draws"]:
            draws.append({"id": o.id, "family": f"declared_null_family_{fam}",
                          "source": None, "keys": CP.variant_keys(o, STRICT)})
    for e, k, dt, o in family_d_draws(census):
        draws.append({"id": o.id,
                      "family": "declared_null_family_d_message_difference",
                      "source": e.id, "keys": CP.variant_keys(o, STRICT)})
    for e, dt, o in incode_draws(census):
        draws.append({"id": o.id, "family": "declared_sub_arm_D_SHA1_INCODE",
                      "source": e.id, "keys": CP.variant_keys(o, STRICT)})
    for e in census.shadow:
        for img in ADJ.orbit_images(e.obj, STRICT):
            draws.append({"id": img.id, "family": "CTL_PLANT_strict_orbit_image",
                          "source": e.id, "keys": CP.variant_keys(img, STRICT)})
    probing = probing_profile(entry_keys, draws, state["components"])

    derived = derive_partition(state["components"], state["edges_by_prim"],
                               state["families"], probing,
                               state["key_components_by_prim"])
    derived_doc = {
        "control": "CTL-PART", "status": "COMPLETED",
        "written_first": True,
        "order_declaration": ORDER_DECLARATION,
        "assigning_rule": ASSIGNING_RULE,
        "five_classes": list(PARTITION_CLASSES),
        "probing_profile_per_component": probing,
        "declared_draw_populations_aggregate": {
            "families_a_b_c_fresh_null_draws": sum(
                1 for d in draws if d["family"].startswith(
                    "declared_null_family_") and d["source"] is None),
            "family_d_message_difference_draws": sum(
                1 for d in draws
                if d["family"] == "declared_null_family_d_message_difference"),
            "D_SHA1_INCODE_draws": sum(
                1 for d in draws
                if d["family"] == "declared_sub_arm_D_SHA1_INCODE"),
            "CTL_PLANT_strict_orbit_images": sum(
                1 for d in draws
                if d["family"] == "CTL_PLANT_strict_orbit_image")},
        "rows": derived["rows"],
        "class_counts_aggregate": derived["class_counts_aggregate"],
        "rows_total": derived["rows_total"],
        "census_completeness": CENSUS_COMPLETENESS,
        "interpretation_limit": (
            "THE PARTITION IS A STATEMENT ABOUT WHAT THE DECLARED FAMILIES AND "
            "THIS KEY CAN REPORT. `NOT PROBED` IS A COVERAGE STATEMENT ABOUT THE "
            "DECLARED FAMILIES AND IS NOT EVIDENCE THAT A PROBING FAMILY WOULD "
            "FIND NOTHING."),
        "observations_not_used_by_the_assigning_rule": [
            ("THE COMMITTED SERIALISER APPENDS ('in_linearized_code', flag) IF "
             "AND ONLY IF obj.primitive == 'sha1', so on any key that RETAINS "
             "the flag component the primitive is recoverable from the key's "
             "COMPONENT-NAME SET alone. That argument would move the `primitive` "
             "row to PROVABLY_UNDETECTABLE, but it is a statement about the "
             "key's SHAPE and not an ordered-pair dependency between component "
             "VALUES, which is the only object CTL-DEP's formalism decides. IT "
             "IS RECORDED HERE AND DELIBERATELY NOT USED BY THE RULE."),
            ("`length` is determined by `step_delta` on BOTH primitives and "
             "additionally by `message_difference` on sha1. Both edges carry "
             "derivations from committed source. THE CONSEQUENCE FOR THE "
             "PARTITION IS WHATEVER IT IS AND IS NOT ADJUSTED TOWARDS THE "
             "PRE-REGISTERED TARGET."),
        ],
    }
    p_derived = _write_json("partition-derived.json", derived_doc)
    lines.append("partition-derived.json WRITTEN AND CLOSED: "
                 + json.dumps(derived["class_counts_aggregate"]))

    # ---- ONLY NOW is BATCH-efcae7's column opened
    column = read_batch_efcae7_column()
    per_row = []
    agree = 0
    for r in derived["rows"]:
        pre = PRE_REGISTERED_PARTITION.get(r["row_deletes"])
        same = (pre == r["row_class"])
        agree += 1 if same else 0
        per_row.append({
            "row_deletes": r["row_deletes"],
            "class_derived_by_this_contract_from_the_graph_alone": r["row_class"],
            "class_pre_registered_by_BATCH_efcae7": pre,
            "agree": same,
            "disagreement_stated_on_both_sides": None if same else {
                "this_contracts_side": {
                    "class": r["row_class"],
                    "rule_fired": {p: v["rule_fired"]
                                   for p, v in r["per_primitive"].items()},
                    "because": {p: v["because"]
                                for p, v in r["per_primitive"].items()},
                    "forcing_edges": {p: v.get("forcing_edges")
                                      for p, v in r["per_primitive"].items()}},
                "BATCH_efcae7_side": {
                    "class": pre,
                    "provenance": PRE_REGISTERED_PARTITION["_provenance"],
                    "what_this_contract_does_NOT_do": (
                        "IT DOES NOT DECIDE WHICH SIDE IS WRONG. A disagreement "
                        "means either this graph or that reading is wrong, and "
                        "the producer composes no verdict on which (IR-8 / "
                        "H-11).")},
            },
            "primitive_scope": {p: v["class"] for p, v in r["per_primitive"].items()},
            "census_completeness": CENSUS_COMPLETENESS})
    compared_doc = {
        "control": "CTL-PART comparison", "status": "COMPLETED",
        "written_second": True,
        "order_declaration": ORDER_DECLARATION,
        "partition_derived_sha256_at_comparison_time": _sha256_file(p_derived),
        "rows": per_row,
        "rows_agreeing_aggregate": agree,
        "rows_total": len(per_row),
        "class_counts_derived_aggregate": derived["class_counts_aggregate"],
        "class_counts_pre_registered_aggregate": {
            c: sum(1 for k, v in PRE_REGISTERED_PARTITION.items()
                   if k != "_provenance" and v == c)
            for c in PARTITION_CLASSES},
        "BATCH_efcae7_records_opened_after_the_derivation_was_closed": column,
        "both_outcomes_are_results": (
            "REPRODUCING THE PARTITION would mean the profile is computable from "
            "the key's structure and the families' declarations with no charged "
            "adjudication. REFUTING IT means either the graph or BATCH-efcae7's "
            "reading is wrong, and WHICH ONE is determined by the derivation and "
            "not by which record is older. A refutation is written up as fully "
            "as a reproduction and is not softened."),
        "census_completeness": CENSUS_COMPLETENESS,
    }
    _write_json("partition-compared.json", compared_doc)
    lines.append(f"partition-compared.json WRITTEN SECOND: rows agreeing "
                 f"{agree} of {len(per_row)}")

    # ---- CTL-DEPTH2
    d2 = classify_depth2(state["components"], state["edges_by_prim"],
                         state["key_components_by_prim"])
    d2["control"] = "CTL-DEPTH2"
    d2["status"] = "COMPLETED"
    d2["pre_registered_expectation_P_C"] = (
        "EXACTLY ONE dependency-breaking subset, {message_difference, "
        "in_linearized_code}, QUOTED from EV-DIFFP-b16b01 and "
        "DEC-20260824-c5bb72 and MEASURED BY THAT SESSION.")
    d2["census_completeness"] = CENSUS_COMPLETENESS
    _write_json("depth2-classification.json", d2)
    lines.append(f"CTL-DEPTH2: {d2['breaking_subsets_aggregate']} of "
                 f"{d2['subsets_total']} subsets break a dependency")
    state["partition_derived"] = derived
    state["partition_compared"] = compared_doc
    state["depth2"] = d2

    metrics = {
        "rows_classified_aggregate": derived["rows_total"],
        "rows_agreeing_with_BATCH_efcae7_aggregate": agree,
        "depth2_subsets_total_aggregate": d2["subsets_total"],
        "depth2_breaking_subsets_aggregate": d2["breaking_subsets_aggregate"],
        "declared_draws_scanned_aggregate": len(draws),
    }
    return RunResult(
        run_suffix="partition-derived-then-compared",
        curve_id="n/a-hash-primitive",
        seed=SEEDS["null_draw_message_difference_perturbed"],
        parameters=_params("partition-derived-then-compared"),
        metrics=metrics, certificate=CERT_NONE, valid=True,
        stdout="\n".join(lines) + "\n", stderr=""), {
            "partition_derived": derived_doc, "partition_compared": compared_doc,
            "depth2": d2}


# ---------------------------------------------------------------------------
# RUN 3 -- CTL-OFFDIAG
# ---------------------------------------------------------------------------

def forced_rows(components, edges_by_prim, key_components_by_prim) -> dict:
    forced = {}
    for comp in components:
        per_prim = {}
        ok = True
        for prim in ("md5", "sha1"):
            if comp not in key_components_by_prim[prim]:
                per_prim[prim] = [{"X": None, "Y": comp,
                                   "derivation": (f"{comp} IS NOT A COMPONENT "
                                                  f"OF THE {prim} KEY, so "
                                                  f"deleting it is the identity "
                                                  f"on every {prim} key")}]
                continue
            es = [r for r in edges_by_prim[prim]
                  if r["Y"] == comp and r["verdict"] == "EDGE"
                  and r["label"] == "derived_and_witnessed"]
            if not es:
                ok = False
                break
            per_prim[prim] = [{"X": r["X"], "Y": r["Y"],
                               "derivation": r["derivation"],
                               "witness_population_size": r["population_size"],
                               "witness_groups_constant_in_Y":
                                   r["groups_constant_in_Y"],
                               "witness_groups_total": r["groups_total"]}
                              for r in es]
        if ok:
            forced[comp] = per_prim
    return forced


def family_draw_keys(fam) -> list:
    return [(d["primitive"], d["k"], CP.variant_keys(d["obj"], STRICT))
            for d in fam["draws"]]


def run_offdiagonal(state: dict):
    lines = []
    entry_keys = state["entry_keys"]
    families = state["families"]
    forced = forced_rows(state["components"], state["edges_by_prim"],
                         state["key_components_by_prim"])
    sel = select_cells(state["components"], families, forced)
    state["selected_cells"] = sel

    rt = load_reused_O_E()
    o_e_proj = rt.proj_drop_on_primitive(["message_difference"], "sha1")
    instruments = {"honest": proj_honest, "O-E": o_e_proj}

    keys_cache = {}
    for fam_name in {c["family"] for c in sel["adjudicated"]}:
        keys_cache[fam_name] = family_draw_keys(families[fam_name])
        lines.append(f"family {fam_name}: "
                     f"{len(keys_cache[fam_name])} CTL-WF-accepted draws")

    table = []
    differing = []
    for cell in sel["adjudicated"]:
        row = {"family": cell["family"], "row_deletes": cell["row_deletes"],
               "perturbation_declaration":
                   families[cell["family"]]["declaration"]["declaration_text"],
               "per_instrument": {}, "per_primitive": {},
               "census_completeness": CENSUS_COMPLETENESS}
        for iname, proj in instruments.items():
            idx = build_index(entry_keys, proj, (cell["row_deletes"],))

            def look(keys, prim, _idx=idx, _proj=proj,
                     _drop=(cell["row_deletes"],)):
                return canon_under(keys, prim, _proj, _drop) in _idx
            v = cell_verdict(keys_cache[cell["family"]], look)
            v["instrument_declaration"] = PROJ_NAMES[iname]
            row["per_instrument"][iname] = v
            row["per_primitive"][iname] = {
                prim: cell_verdict(keys_cache[cell["family"]], look, prim)
                for prim in ("md5", "sha1")}
        a = row["per_instrument"]["honest"]["verdict"]
        b = row["per_instrument"]["O-E"]["verdict"]
        row["differs_between_honest_and_O_E"] = (a != b)
        if a != b:
            differing.append({"family": cell["family"],
                              "row_deletes": cell["row_deletes"],
                              "honest": a, "O_E": b})
        table.append(row)

    doc = {
        "control": "CTL-OFFDIAG", "status": "COMPLETED",
        "gate": ("RUN 2 COMPLETED AND partition-compared.json WRITTEN. The gate "
                 "is recorded whether or not it fired."),
        "counting_rule": CELL_RULE,
        "the_two_instruments": {k: PROJ_NAMES[k] for k in ("honest", "O-E")},
        "O_E_is_reused_not_rebuilt": (
            "IR-11. The projection object is IMPORTED from the committed file "
            "constructions/rt_instruments.py of TASK-20260824-e9d21a by "
            "importlib and called there; no re-expression of it exists in this "
            "module. Its committed measured integers are re-derived and checked "
            "in CTL-RC1 against constructions/j8_results.json."),
        "per_cell_table": table,
        "cells_adjudicated_aggregate": len(table),
        "excluded_cells_with_every_reason": sel["excluded"],
        "excluded_cells_aggregate_by_reason": {
            r: sum(1 for c in sel["excluded"] if c["exclusion"] == r)
            for r in ("diagonal", "forced_by_the_graph", "not_constructible")},
        "differing_cells_aggregate": len(differing),
        "differing_cells": differing,
        "how_the_count_must_be_read": (
            "THE DIFFERING-CELL COUNT IS AN INTEGER REPORTED BESIDE THE NUMBER "
            "OF CELLS ADJUDICATED, THE EXCLUDED-CELL LIST AND THE PER-CELL "
            "TABLE. IT IS NEVER A FRACTION, A PASS, A SCORE OR A MARGIN (IR-10, "
            "H-5). ZERO DIFFERING CELLS MEANS the power profile over the "
            "ADJUDICATED CELLS is a function of the families' construction and "
            "of the dependency graph and carries NO information about the "
            "instrument; ANY DIFFERING CELL is a place where a verdict is "
            "contingent on the instrument. BOTH ARE RESULTS AND NEITHER IS A "
            "DISAPPOINTMENT. Neither licenses a statement about MD5, SHA-1 or "
            "any difference space."),
        "permissive_mode_is_out_of_scope_and_is_null_never_zero": {
            "permissive_cells": None,
            "why": ("STRICT ONLY, declared at opening (contract "
                    "independent_variables.mode and IR-5). Permissive cells are "
                    "emitted as null and NEVER as 0 (H-8). This is a budget "
                    "decision recorded as one and is NOT evidence that "
                    "permissive mode would behave the same way.")},
        "interpretation_limit": (
            "THE OFF-DIAGONAL MATRIX USES ONE KNOWN-FALSE INSTRUMENT. FOUR "
            "FURTHER SURVIVORS -- O-D, O-C, O-C-prime, O-C-double-prime -- ARE "
            "NOT ADJUDICATED HERE AND REMAIN UNREPLICATED, and three of the six "
            "key components remain deletable SIMULTANEOUSLY without the "
            "committed suite noticing."),
        "census_completeness": CENSUS_COMPLETENESS,
    }
    _write_json("offdiagonal-matrix-result.json", doc)
    state["offdiag"] = doc
    state["offdiag_cells"] = sel["adjudicated"]
    state["offdiag_keys_cache"] = keys_cache
    lines.append(f"CTL-OFFDIAG: {len(table)} cells adjudicated, "
                 f"{len(differing)} differing between honest and O-E, "
                 f"{len(sel['excluded'])} cells excluded")
    metrics = {
        "offdiagonal_cells_adjudicated_aggregate": len(table),
        "differing_cells_honest_versus_O_E_aggregate": len(differing),
        "excluded_cells_aggregate": len(sel["excluded"]),
    }
    metrics.update({f"excluded_{r}_aggregate": v for r, v in
                    doc["excluded_cells_aggregate_by_reason"].items()})
    return RunResult(
        run_suffix="offdiagonal-honest-and-known-false",
        curve_id="n/a-hash-primitive",
        seed=SEEDS["null_draw_message_difference_perturbed"],
        parameters=_params("offdiagonal-honest-and-known-false"),
        metrics=metrics, certificate=CERT_NONE, valid=True,
        stdout="\n".join(lines) + "\n", stderr=""), doc


# ---------------------------------------------------------------------------
# RUN 4 -- CTL-NULL-OBJ
# ---------------------------------------------------------------------------

def run_null_object(state: dict):
    lines = []
    entry_keys = state["entry_keys"]
    cells = state["offdiag_cells"]
    keys_cache = state["offdiag_keys_cache"]

    def honest_look(drop):
        idx = build_index(entry_keys, proj_honest, drop)
        return lambda keys, prim: canon_under(keys, prim, proj_honest,
                                              drop) in idx

    modes = {
        "honest_versus_honest": lambda drop: honest_look(drop),
        "always_member": lambda drop: (lambda keys, prim: True),
        "always_non_member": lambda drop: (lambda keys, prim: False),
    }
    results = {m: {"cells": [], "differing_from_honest_aggregate": 0}
               for m in modes}
    for cell in cells:
        drop = (cell["row_deletes"],)
        hv = cell_verdict(keys_cache[cell["family"]], honest_look(drop))
        for m, mk in modes.items():
            v = cell_verdict(keys_cache[cell["family"]], mk(drop))
            differs = v["verdict"] != hv["verdict"]
            results[m]["differing_from_honest_aggregate"] += 1 if differs else 0
            results[m]["cells"].append({
                "family": cell["family"], "row_deletes": cell["row_deletes"],
                "honest_verdict": hv["verdict"], "mode_verdict": v["verdict"],
                "differs": differs, "strict_member_draws": v["strict_member_draws"],
                "perturbed_draws_k_ge_1": v["perturbed_draws_k_ge_1"],
                "census_completeness": CENSUS_COMPLETENESS})
    honest_not_detected = sum(
        1 for c in results["honest_versus_honest"]["cells"]
        if c["honest_verdict"] == "NOT DETECTED")
    honest_detected = len(cells) - honest_not_detected

    # CTL-PLANT per degenerate instrument, reported SEPARATELY
    plant = {}
    for m in modes:
        hits = att = 0
        for e in state["census"].shadow:
            for o in [e.obj] + list(ADJ.orbit_images(e.obj, STRICT)):
                att += 1
                keys = CP.variant_keys(o, STRICT)
                if m == "always_member":
                    ok = True
                elif m == "always_non_member":
                    ok = False
                else:
                    idx = build_index(entry_keys, proj_honest, ())
                    ok = canon_under(keys, o.primitive, proj_honest, ()) in idx
                hits += 1 if ok else 0
        plant[m] = {"hits": hits, "attempts": att}

    doc = {
        "control": "CTL-NULL-OBJ", "status": "COMPLETED",
        "counting_rule_is_the_identical_code_as_CTL_OFFDIAG": CELL_RULE,
        "cells_adjudicated_aggregate": len(cells),
        "honest_cells_reporting_DETECTED_aggregate": honest_detected,
        "honest_cells_reporting_NOT_DETECTED_aggregate": honest_not_detected,
        "modes": {m: {"instrument_declaration": PROJ_NAMES.get(
            m, "the honest adjudicator against itself"),
            "differing_from_honest_aggregate":
                results[m]["differing_from_honest_aggregate"],
            "cells": results[m]["cells"]} for m in modes},
        "known_answers": {
            "honest_versus_honest": (
                "ZERO differing cells. A nonzero answer would mean the "
                "adjudication is not deterministic at the declared seeds and IS "
                "A STOP."),
            "always_member": (
                "THE MAXIMAL differing-cell count over the adjudicated set: it "
                "differs from the honest instrument on every cell the honest "
                "instrument reports as NOT DETECTED."),
            "always_non_member": (
                "It differs from the honest instrument on every cell the honest "
                "instrument reports as DETECTED, and it FAILS CTL-PLANT "
                "OUTRIGHT, which is reported here rather than hidden by the "
                "counting rule."),
        },
        "predicted_extremes_met": {
            "honest_versus_honest_is_zero":
                results["honest_versus_honest"]["differing_from_honest_aggregate"] == 0,
            "always_member_equals_honest_NOT_DETECTED_count":
                results["always_member"]["differing_from_honest_aggregate"]
                == honest_not_detected,
            "always_non_member_equals_honest_DETECTED_count":
                results["always_non_member"]["differing_from_honest_aggregate"]
                == honest_detected,
        },
        "CTL_PLANT_per_instrument_reported_separately": plant,
        "H_6": ("IF THE TWO DEGENERATE INSTRUMENTS DO NOT PRODUCE THE PREDICTED "
                "EXTREMES, THE COUNTING RULE IS BROKEN, EVERY CTL-OFFDIAG NUMBER "
                "IS UNINTERPRETABLE, AND NO DIFFERING-CELL COUNT MAY BE "
                "REPORTED."),
        "census_completeness": CENSUS_COMPLETENESS,
    }
    _write_json("null-object-control-result.json", doc)
    state["null_object"] = doc
    lines.append("CTL-NULL-OBJ differing-cell counts: "
                 + json.dumps({m: results[m]["differing_from_honest_aggregate"]
                               for m in modes}))
    metrics = {f"differing_cells_{m}_aggregate":
               results[m]["differing_from_honest_aggregate"] for m in modes}
    metrics["honest_cells_NOT_DETECTED_aggregate"] = honest_not_detected
    metrics["honest_cells_DETECTED_aggregate"] = honest_detected
    return RunResult(
        run_suffix="null-object-counting-controls", curve_id="n/a-hash-primitive",
        seed=SEEDS["null_draw_message_difference_perturbed"],
        parameters=_params("null-object-counting-controls"),
        metrics=metrics, certificate=CERT_NONE, valid=True,
        stdout="\n".join(lines) + "\n", stderr=""), doc


# ---------------------------------------------------------------------------
# RUN 5 -- CTL-RC1 (RE-SCORING, NEVER AN EDIT) and CTL-FROZEN-3 post-run
# ---------------------------------------------------------------------------

RC1_RESCORING_NOTE = (
    "RC-1 IS DISCHARGED BY RE-SCORING IN THIS NEW MODULE AND NEVER BY EDITING. "
    "harness/diffpath/controlpower.py IS COMMITTED AND IS NOT EDITED (IR-2). "
    "THE COMMITTED DETECTION RULE'S OWN VERDICTS ARE REPORTED UNCHANGED BESIDE "
    "THE RE-SCORED ONES, AND NO ARTIFACT OF THIS BATCH STATES OR IMPLIES THAT "
    "THE COMMITTED RULE HAS BEEN FIXED. The committed rule computes "
    "`strengthened_detected` from the family-(d) PRIMARY arm only; the re-scored "
    "rule is that same disjunction WITH the D-SHA1-INCODE sub-arm carried in.")

RC1_KNOWN_IN_ADVANCE = (
    "ITS OUTCOME FOR O-E IS KNOWN IN ADVANCE AND IS REPORTED AS A CONFIRMATION "
    "OF A KNOWN OUTCOME, NEVER AS A DISCOVERY. TASK-20260824-e9d21a MEASURED "
    "that O-E returns MEMBER on 520 of 520 in-code objects where the honest "
    "adjudicator returns 0 of 520, so the fold catches O-E WITH CERTAINTY AND "
    "NOT AS A QUESTION. WHAT IS GENUINELY OPEN IS whether the fold touches ANY "
    "OF THE OTHER FOUR SURVIVORS, which are blind to block_index, length and the "
    "flag rather than to the message difference.")


def run_rc1(state: dict):
    lines = []
    census = state["census"]
    rt = load_reused_O_E()
    survivors = [
        ("O-E md-blind on SHA1 ONLY     [plan candidate v]",
         rt.proj_drop_on_primitive(["message_difference"], "sha1")),
        ("O-D block_index-blind", rt.proj_drop(["block_index"])),
        ("O-C d2: block_index+length blind",
         rt.proj_drop(["block_index", "length"])),
        ("O-C' d2: block_index+in_linearized_code blind",
         rt.proj_drop(["block_index", "in_linearized_code"])),
        ("O-C'' d3: block_index+length+in_linearized_code",
         rt.proj_drop(["block_index", "length", "in_linearized_code"])),
    ]
    entry_keys = state["entry_keys"]
    plant_keys = []
    for e in census.shadow:
        for o in [e.obj] + list(ADJ.orbit_images(e.obj, STRICT)):
            plant_keys.append((CP.variant_keys(o, STRICT), o.primitive))
    null_keys = {f: [(CP.variant_keys(o, STRICT), o.primitive)
                     for o in d["draws"]]
                 for f, d in CP.null_draws(census, n=1000).items()}
    d_keys = [(e.primitive, k, CP.variant_keys(o, STRICT))
              for e, k, dt, o in family_d_draws(census)]
    sub_keys = [CP.variant_keys(o, STRICT) for e, dt, o in incode_draws(census)]

    committed = json.load(open(os.path.join(RT_CONSTRUCTIONS,
                                            "j8_results.json"), encoding="utf-8"))
    committed_by_name = {r["name"]: r for r in committed}

    rows, mismatches = [], []
    for name, proj in survivors:
        idx = build_index(entry_keys, proj, ())

        def hit(keys, prim, _idx=idx, _proj=proj):
            return canon_under(keys, prim, _proj, ()) in _idx
        p_hits = sum(1 for keys, prim in plant_keys if hit(keys, prim))
        fp = {f: sum(1 for keys, prim in v if hit(keys, prim))
              for f, v in null_keys.items()}
        fptot = sum(fp.values())
        cells = {}
        for prim, k, keys in d_keys:
            c = cells.setdefault((prim, k), {"draws": 0, "member": 0})
            c["draws"] += 1
            if hit(keys, prim):
                c["member"] += 1
        md5m = sum(c["member"] for (p, k), c in cells.items()
                   if p == "md5" and k >= 1)
        s1m = sum(c["member"] for (p, k), c in cells.items()
                  if p == "sha1" and k >= 1)
        k0m = sum(c["member"] for (p, k), c in cells.items() if k == 0)
        k0d = sum(c["draws"] for (p, k), c in cells.items() if k == 0)
        subm = sum(1 for keys in sub_keys if hit(keys, "sha1"))
        old = (p_hits != len(plant_keys)) or fptot > 0
        committed_rule = (old or md5m + s1m > 0 or k0m != k0d)
        refolded = committed_rule or subm > 0
        ref = committed_by_name.get(name, {})
        checks = {
            "plant": (f"{p_hits}/{len(plant_keys)}", ref.get("plant")),
            "null_fp_total": (fptot, ref.get("null_fp_total")),
            "d_md5_k_ge_1_member": (md5m, ref.get("d_md5_k_ge_1_member")),
            "d_sha1_k_ge_1_member": (s1m, ref.get("d_sha1_k_ge_1_member")),
            "k0": (f"{k0m}/{k0d}", ref.get("k0")),
            "subarm_incode_member": (f"{subm}/{len(sub_keys)}",
                                     ref.get("subarm_incode_member")),
        }
        bad = {k: {"recomputed_here": a, "committed_j8_results": b}
               for k, (a, b) in checks.items() if b is not None and a != b}
        if bad:
            mismatches.append({"instrument": name, "disagreements": bad})
        rows.append({
            "instrument": name,
            "recomputed_integers": {k: a for k, (a, b) in checks.items()},
            "committed_j8_results_integers": {k: b for k, (a, b) in checks.items()},
            "IR_11_agreement": not bad,
            "committed_detection_rule_verdict_UNCHANGED":
                "DETECTED" if committed_rule else "NOT DETECTED",
            "committed_rule_text": CP.DETECTION_RULE,
            "refolded_rule_verdict":
                "CAUGHT" if refolded else "STILL PASSES",
            "refold_changed_this_instrument": refolded and not committed_rule,
            "census_completeness": CENSUS_COMPLETENESS,
        })
        lines.append(f"CTL-RC1 {name}: committed rule "
                     f"{'DETECTED' if committed_rule else 'NOT DETECTED'}, "
                     f"refolded {'CAUGHT' if refolded else 'STILL PASSES'}, "
                     f"subarm {subm}/{len(sub_keys)}")

    post = digests()
    frozen = compare_digests(state["pre_digests"], post)
    frozen_doc = {
        "control": "CTL-FROZEN-3", "status": "COMPLETED",
        "before": state["pre_digests"], "after": post, "comparison": frozen,
        "criterion_note": FROZEN_CRITERION_NOTE,
        "failure_is_a_STOP": (
            "A single changed digest in the criterion set means a committed file "
            "was modified, which violates IR-2 and INVALIDATES THE ENTIRE RUN "
            "SET."),
        "quoted_value_recomputed_rather_than_trusted": (
            "EV-DIFFP-b16b01 records the source digest "
            "953398c4bc92fc1075817987976e9c9582c2756f13eff3f68a357d87355646b7 "
            "for harness/diffpath/controlpower.py. THAT VALUE IS QUOTED FROM A "
            "COMMITTED RECORD AND WAS NOT MEASURED BY THE COORDINATOR (BR-6); "
            "this run RECOMPUTES it."),
        "recomputed_controlpower_digest":
            post["criterion_set"].get("harness/diffpath/controlpower.py"),
        "recomputed_controlpower_digest_matches_the_quoted_value":
            post["criterion_set"].get("harness/diffpath/controlpower.py")
            == "953398c4bc92fc1075817987976e9c9582c2756f13eff3f68a357d87355646b7",
    }
    _write_json("frozen-recheck-result.json", frozen_doc)

    doc = {
        "control": "CTL-RC1", "status": "COMPLETED",
        "rescoring_note": RC1_RESCORING_NOTE,
        "known_in_advance": RC1_KNOWN_IN_ADVANCE,
        "pre_registered_answer_P_D": (
            "The RC-1 refold CATCHES O-E and touches NONE of O-D, O-C, "
            "O-C-prime, O-C-double-prime. QUOTED from red-team-report.yaml J8 "
            "and DEC-20260824-c5bb72 rank 2."),
        "per_instrument": rows,
        "instruments_caught_by_the_refold_aggregate":
            sum(1 for r in rows if r["refolded_rule_verdict"] == "CAUGHT"),
        "instruments_whose_verdict_the_refold_CHANGED_aggregate":
            sum(1 for r in rows if r["refold_changed_this_instrument"]),
        "IR_11_disagreements_are_a_STOP": mismatches,
        "census_completeness": CENSUS_COMPLETENESS,
        "what_RC1_does_not_buy": (
            "THE FOUR OTHER SURVIVORS REMAIN UNREPLICATED -- built once by one "
            "session -- and permissive mode is unmeasured for every one of them "
            "in either direction. Nothing here states that the committed suite "
            "has been repaired."),
    }
    _write_json("rc1-refold-result.json", doc)
    state["rc1"] = doc
    state["frozen"] = frozen_doc
    metrics = {
        "survivors_scored_aggregate": len(rows),
        "instruments_caught_by_the_refold_aggregate":
            doc["instruments_caught_by_the_refold_aggregate"],
        "instruments_whose_verdict_the_refold_changed_aggregate":
            doc["instruments_whose_verdict_the_refold_CHANGED_aggregate"],
        "IR_11_disagreement_count_aggregate": len(mismatches),
        "frozen_criterion_files_identical_aggregate": frozen["identical_count"],
        "frozen_criterion_files_changed_aggregate": len(frozen["changed_files"]),
    }
    return RunResult(
        run_suffix="rc1-refold-and-frozen-recheck", curve_id="n/a-hash-primitive",
        seed=SEEDS["null_draw_message_difference_perturbed"],
        parameters=_params("rc1-refold-and-frozen-recheck"),
        metrics=metrics, certificate=CERT_NONE, valid=True,
        stdout="\n".join(lines) + "\n", stderr=""), {"rc1": doc,
                                                     "frozen": frozen_doc}


# ---------------------------------------------------------------------------
# the driver
# ---------------------------------------------------------------------------

def _charge(suffix: str, fn, command: str) -> str:
    def wrapped() -> RunResult:
        with CP.Deadline(CEILINGS[suffix], suffix):
            return fn()
    return run_wrapped(EXPERIMENT_ID, EXP_AREA, wrapped,
                       status="completed_valid", command=command,
                       out_root=RUN_OUT_ROOT)


def _emit(suffix: str, fn, out: dict) -> dict:
    import yaml
    t0 = time.monotonic()
    command = (f"python3 -m harness.diffpath.depgraph   # run '{suffix}' of "
               f"{EXPERIMENT_ID}, ceiling {CEILINGS[suffix]}s ARMED")
    holder: dict = {}

    def call():
        res, raw = fn()
        holder["raw"] = raw
        return res

    try:
        run_id = _charge(suffix, call, command)
    except CP.DeadlineExceeded as exc:
        rec = {"run_suffix": suffix, "state": "resource_exhaustion",
               "ceiling_seconds": CEILINGS[suffix],
               "wall_seconds": round(time.monotonic() - t0, 3),
               "reason": str(exc),
               "classification": ("resource_exhaustion -- A BUDGET OUTCOME. "
                                  "Never a negative mathematical result, never "
                                  "a finding about the instrument's power in "
                                  "either direction and never a finding about "
                                  "any difference space (AGENTS.md rule 5).")}
        out["runs"].append(rec)
        return rec
    except Exception as exc:                                     # noqa: BLE001
        import traceback
        rec = {"run_suffix": suffix, "state": "implementation_error",
               "ceiling_seconds": CEILINGS[suffix],
               "wall_seconds": round(time.monotonic() - t0, 3),
               "reason": f"{type(exc).__name__}: {exc}",
               "traceback": traceback.format_exc()[-3000:],
               "classification": ("implementation_error -- infrastructure "
                                  "signal, never mathematical evidence.")}
        out["runs"].append(rec)
        return rec

    run_dir = os.path.join(REPO, "experiments", EXPERIMENT_ID, "runs", run_id)
    write_supplement(run_dir, suffix)
    with open(os.path.join(run_dir, "manifest.yaml"), encoding="utf-8") as fh:
        man = yaml.safe_load(fh)["run"]
    rec = {"run_suffix": suffix, "run_id": run_id, "state": "completed_valid",
           "run_dir": os.path.relpath(run_dir, REPO),
           "ceiling_seconds": CEILINGS[suffix],
           "wall_seconds": man["timing"]["wall_seconds"],
           "timing_source": man["timing"].get("timing_source"),
           "ceiling_unspent_seconds":
               round(CEILINGS[suffix] - man["timing"]["wall_seconds"], 3),
           "peak_rss_bytes": man["resources"]["peak_rss_bytes"],
           "experiment_id_in_manifest": man["experiment_id"],
           "experiment_id_in_parameters":
               man["inputs"]["parameters"]["experiment_id"],
           "code_path_fingerprint_in_manifest":
               "code_path_fingerprint" in man["inputs"]["parameters"],
           "armed_deadline_seconds_in_manifest":
               man["inputs"]["parameters"].get("armed_deadline_seconds"),
           "manifest_inference_block_as_written_by_the_shared_wrapper":
               man.get("inference"),
           "metrics": man["result"]["metrics"]}
    out["runs"].append(rec)
    out["raw"][suffix] = holder.get("raw")
    return rec


def _not_run(suffix: str, gate: str, out: dict, artifacts: list) -> None:
    out["runs"].append({
        "run_suffix": suffix, "state": "GATED-NOT-RUN", "gate": gate,
        "ceiling_seconds": CEILINGS[suffix],
        "ceiling_status": ("UNSPENT -- NOT reallocated to any other run. A "
                           "GATED RUN THAT CORRECTLY DOES NOT EXECUTE IS A "
                           "RESULT, NOT A GAP."),
    })
    for name, control in artifacts:
        _write_json(name, {
            "control": control, "status": "GATED-NOT-RUN",
            "gate_that_fired": gate,
            "what_had_been_computed_before_it_fired":
                "nothing of this control; its gate fired before it executed",
            "every_quantity_this_run_would_have_produced": None,
            "why_null_and_never_zero": (
                "AN UNMEASURED CELL, COLUMN OR MODE IS EMITTED AS null AND "
                "NEVER AS INTEGER 0 (H-8), so a machine consumer reading the "
                "JSON alone cannot misread a gated outcome as a measurement."),
            "census_completeness": CENSUS_COMPLETENESS})


def main() -> int:
    os.makedirs(TASK_ROOT, exist_ok=True)
    out: dict = {"experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
                 "batch_id": BATCH_ID, "goal_id": GOAL_ID,
                 "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                              time.gmtime()),
                 "runs": [], "raw": {}}
    firewall = install_quarantine_firewall()
    out["quarantine_firewall"] = firewall
    state: dict = {"pre_digests": digests()}

    state["census"] = CEN.build_census(
        SEEDS["planted_path_generation_md5"],
        SEEDS["planted_path_generation_sha1"],
        scan={"candidates": []})

    r1 = _emit("frozen-and-dependency-graph", lambda: run_graph(state), out)
    if r1["state"] != "completed_valid":
        _not_run("partition-derived-then-compared",
                 "RUN 1 did not complete", out,
                 [("partition-derived.json", "CTL-PART"),
                  ("partition-compared.json", "CTL-PART comparison"),
                  ("depth2-classification.json", "CTL-DEPTH2")])
        _not_run("offdiagonal-honest-and-known-false",
                 "RUN 2 did not complete", out,
                 [("offdiagonal-matrix-result.json", "CTL-OFFDIAG")])
        _not_run("null-object-counting-controls", "RUN 1 did not complete", out,
                 [("null-object-control-result.json", "CTL-NULL-OBJ")])
        _not_run("rc1-refold-and-frozen-recheck", "RUN 3 did not complete", out,
                 [("rc1-refold-result.json", "CTL-RC1"),
                  ("frozen-recheck-result.json", "CTL-FROZEN-3")])
        _finish(out, state)
        return 1

    r2 = _emit("partition-derived-then-compared", lambda: run_partition(state),
               out)
    if r2["state"] != "completed_valid":
        _not_run("offdiagonal-honest-and-known-false",
                 "CTL-PART stopped; this control does not execute and its run "
                 "is reported as GATED-NOT-RUN, which is a declared outcome and "
                 "not a failure and not evidence about anything", out,
                 [("offdiagonal-matrix-result.json", "CTL-OFFDIAG")])
        r3 = {"state": "GATED-NOT-RUN"}
    else:
        r3 = _emit("offdiagonal-honest-and-known-false",
                   lambda: run_offdiagonal(state), out)

    if r3["state"] == "completed_valid":
        _emit("null-object-counting-controls", lambda: run_null_object(state),
              out)
        _emit("rc1-refold-and-frozen-recheck", lambda: run_rc1(state), out)
    else:
        _not_run("null-object-counting-controls",
                 "RUN 3 neither completed nor produced an adjudicated cell set; "
                 "the counting rule has nothing to exercise", out,
                 [("null-object-control-result.json", "CTL-NULL-OBJ")])
        _not_run("rc1-refold-and-frozen-recheck", "RUN 3 did not complete", out,
                 [("rc1-refold-result.json", "CTL-RC1"),
                  ("frozen-recheck-result.json", "CTL-FROZEN-3")])
    _finish(out, state)
    return 0


def _finish(out: dict, state: dict) -> None:
    if "frozen" not in state:
        post = digests()
        frozen = compare_digests(state["pre_digests"], post)
        _write_json("frozen-recheck-result.json", {
            "control": "CTL-FROZEN-3",
            "status": "COMPLETED (post-run recheck taken at the driver's exit "
                      "because run 5 did not execute)",
            "before": state["pre_digests"], "after": post,
            "comparison": frozen, "criterion_note": FROZEN_CRITERION_NOTE,
            "census_completeness": CENSUS_COMPLETENESS})
    index = {"experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
             "run_root": f"experiments/{EXPERIMENT_ID}/runs/",
             "why_this_index_exists": (
                 "BR-7 / BR-8: RUN DIRECTORIES ARE NOT DECLARED IN THE TASK'S "
                 "artifact_paths on purpose, because a completed archive must "
                 "hash every declared artifact and a GATED run correctly has "
                 "none. run-index.json IS declared and CONTENT-BINDS every file "
                 "of every EXECUTED run by sha256."),
             "runs": []}
    for rec in out["runs"]:
        entry = {k: v for k, v in rec.items() if k != "metrics"}
        entry["files"] = None
        if rec.get("run_id"):
            rd = os.path.join(REPO, "experiments", EXPERIMENT_ID, "runs",
                              rec["run_id"])
            files = {}
            for dirpath, _dn, fns in os.walk(rd):
                for fn in sorted(fns):
                    full = os.path.join(dirpath, fn)
                    files[os.path.relpath(full, REPO).replace(os.sep, "/")] = \
                        _sha256_file(full)
            entry["files"] = files
            entry["files_count"] = len(files)
        index["runs"].append(entry)
    _write_json("run-index.json", index)
    out["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _write_json("driver-summary.json", out)


if __name__ == "__main__":
    raise SystemExit(main())
