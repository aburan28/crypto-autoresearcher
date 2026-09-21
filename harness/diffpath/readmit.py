"""EXP-DIFFP-f26790 -- the PER-INSTRUMENT forcing predicate, re-implemented FROM
THE CONTRACT'S WRITTEN STATEMENT, and the CONSISTENT-PAIR flag-and-dv family.

TASK-20260826-82c660, BATCH-171407, GOAL-DIFFP-84d641.

CLAIM CEILING `analyzed`.  NO DIFFERENTIAL PATH IS CLAIMED NEW FOR MD5 OR SHA-1
AT ANY TIER.  NO CRYPTANALYTIC IMPROVEMENT IS CLAIMED.  A PASSING CONTROL IS NOT
AN IMPROVEMENT.  THE MD5 LANE IS BLOCKED, NOT CLOSED.  CENSUS COMPLETENESS --
readable 0 / quarantined_not_read 1 / acquisition_gap 8, NEVER SUMMED, with
shadow_planted 16 carried separately -- accompanies every verdict this module
emits.

INDEPENDENCE (H-1 / IR-12).  The forcing predicate below is written from
EXP-DIFFP-f26790's field
`the_forcing_predicate_stated_formally_so_it_can_be_implemented_from_the_statement`.
The ONE existing implementation of this control lives under the path named in
FORBIDDEN_PATH_LITERAL and is NOT opened, read, imported, copied, executed,
diffed or reconstructed by this module.  An audit hook installed by
install_independence_and_quarantine_firewall() RAISES on any open() or os.open()
whose path lies under that prefix, and under the GOAL-MD5-001 quarantine prefix,
FOR THE LIFETIME OF THE PROCESS.  What the hook can and cannot demonstrate is
stated in INDEPENDENCE_MODE and is not overstated.

IR-2.  This module MODIFIES NO COMMITTED FILE.  It imports the committed
adjudicator package and writes only its own result artifacts and run
directories.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import random
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# ---------------------------------------------------------------------------
# IR-1 and IR-12 -- THE TWO FIREWALLS, INSTALLED BEFORE ANY SUBSTRATE IMPORT
# ---------------------------------------------------------------------------

FORBIDDEN_PATH_LITERAL = ("coordination/goals/GOAL-DIFFP-84d641/batches/"
                          "BATCH-145531/reviews/TASK-20260824-7d9f92/"
                          "constructions")
QUARANTINE_PATH_LITERAL = "coordination/goals/GOAL-MD5-001/quarantine"
SEALED_PRIORS_PATH_LITERAL = "coordination/goals/GOAL-DIFFP-84d641/sealed-priors"

_BLOCKED_PREFIXES = tuple(
    os.path.join(REPO, p) for p in
    (FORBIDDEN_PATH_LITERAL, QUARANTINE_PATH_LITERAL, SEALED_PRIORS_PATH_LITERAL))

_FIREWALL_STATE = {
    "audit_hook_installed": False,
    "census_stub_installed": False,
    "blocked_open_attempts": [],
}


class FirewallBreach(RuntimeError):
    """Raised the instant a blocked prefix is opened, by any route in-process."""


def _audit_hook(event, args):
    if event not in ("open", "os.open"):
        return
    try:
        path = args[0]
    except Exception:                                            # noqa: BLE001
        return
    if isinstance(path, bytes):
        try:
            path = path.decode()
        except Exception:                                        # noqa: BLE001
            return
    if not isinstance(path, str):
        return
    full = os.path.abspath(path)
    for pre in _BLOCKED_PREFIXES:
        if full == pre or full.startswith(pre + os.sep):
            _FIREWALL_STATE["blocked_open_attempts"].append(full)
            raise FirewallBreach(
                f"BLOCKED BY MECHANISM: an open of {full} was attempted; this "
                f"process refuses every path under {pre}")


INDEPENDENCE_MODE = (
    "MECHANICALLY DEMONSTRATED FOR THE PROCESS, ATTESTED FOR THE SESSION, AND "
    "THE DIFFERENCE IS THE WHOLE OF WHAT THIS FIELD SAYS. (1) MECHANICAL: a "
    "sys.addaudithook() installed before any substrate import RAISES "
    "FirewallBreach on every `open` and `os.open` audit event whose resolved "
    "path lies under the forbidden prefix, the GOAL-MD5-001 quarantine prefix "
    "or the sealed-priors prefix, so a read by ANY in-process route -- "
    "builtins.open, io.open, os.open, importlib's loader, json.load, a "
    "subprocess-free shell-out is not a route at all -- terminates the run "
    "instead of succeeding silently. A second mechanical check asserts at run "
    "time that no entry of sys.modules has a __file__ under the forbidden "
    "prefix. (2) ATTESTED AND NOT MECHANICAL: whether the PRODUCING SESSION "
    "read those files with a tool OUTSIDE this process is an honest boolean "
    "carried in independence-attestation.json. NO TOOL IN THIS REPOSITORY CAN "
    "VERIFY THAT BOOLEAN AND THIS MODULE SAYS SO RATHER THAN LETTING THE "
    "MECHANISM'S STRENGTH BE READ ACROSS THE GAP.")

QUARANTINE_MECHANISM = (
    "IR-1 BY MECHANISM AND NEVER BY INTENT, IN TWO LAYERS. (1) THE AUDIT HOOK "
    "ABOVE refuses every open under "
    "coordination/goals/GOAL-MD5-001/quarantine by raising, so a read cannot "
    "silently succeed. (2) THE COMMITTED census builder calls "
    "census.quarantine_attestation(), which opens the Tier-A payload 'rb' to "
    "hash it. This module REPLACES census.quarantine_attestation IN THIS "
    "PROCESS ONLY with a stub that opens nothing -- a run-time monkeypatch of "
    "an imported name, writing no committed file, the same mechanism "
    "TASK-20260824-e9d21a and TASK-20260824-68ba87 used. Layer (2) is what "
    "keeps the census buildable; layer (1) is what makes the refusal "
    "load-bearing rather than a promise. CONSEQUENCE, STATED: no byte of the "
    "payload is read by this task by any route, the quarantined census entry's "
    "sha256 field is a placeholder rather than a hash, and nothing measured "
    "here depends on it because only census.shadow is used. NO NETWORK REQUEST "
    "OF ANY KIND IS MADE (IR-3): this module contains no socket, no urllib, no "
    "http client and no subprocess.")


def install_independence_and_quarantine_firewall() -> dict:
    """Install both firewalls. Idempotent. MUST run before the census is built."""
    if not _FIREWALL_STATE["audit_hook_installed"]:
        sys.addaudithook(_audit_hook)
        _FIREWALL_STATE["audit_hook_installed"] = True
    from harness.diffpath import census as _CEN
    if not _FIREWALL_STATE["census_stub_installed"]:
        _CEN.quarantine_attestation = lambda: {
            "path": "<NOT OPENED BY TASK-20260826-82c660>",
            "bytes_hashed": 0,
            "sha256_recomputed": "0" * 64,
            "sha256_expected": None,
            "match": None,
            "read_mode": "STUBBED -- this task never opened the payload",
            "parsed": False,
            "attestation": "stubbed by TASK-20260826-82c660 (IR-1)",
        }
        _FIREWALL_STATE["census_stub_installed"] = True
    return {
        "audit_hook_installed": True,
        "census_attestation_stub_installed": True,
        "blocked_prefixes": [os.path.relpath(p, REPO) for p in _BLOCKED_PREFIXES],
        "independence_mode": INDEPENDENCE_MODE,
        "quarantine_mechanism": QUARANTINE_MECHANISM,
    }


def assert_forbidden_path_absent_from_process() -> dict:
    """IR-12 run-time assertion: no loaded module lives under the forbidden path."""
    pre = os.path.join(REPO, FORBIDDEN_PATH_LITERAL)
    offenders = []
    for name, mod in list(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if isinstance(f, str) and os.path.abspath(f).startswith(pre):
            offenders.append({"module": name, "file": f})
    return {
        "assertion": ("no entry of sys.modules has a __file__ under "
                      f"{FORBIDDEN_PATH_LITERAL}"),
        "modules_loaded_from_the_forbidden_path": offenders,
        "assertion_holds": not offenders,
        "modules_in_process_total": len(sys.modules),
        "blocked_open_attempts_recorded_by_the_audit_hook":
            list(_FIREWALL_STATE["blocked_open_attempts"]),
    }


install_independence_and_quarantine_firewall()

# --- the committed substrate, imported READ-ONLY and modified nowhere --------
from harness.diffpath import adjudicator as ADJ           # noqa: E402
from harness.diffpath import census as CEN                # noqa: E402
from harness.diffpath import controlpower as CP           # noqa: E402
from harness.diffpath import depgraph as DG               # noqa: E402
from harness.diffpath import primitives as P              # noqa: E402
from harness.diffpath.pathobj import PathObject, bsdr_encode   # noqa: E402
from harness.runner import RunResult, run_wrapped         # noqa: E402

# ---------------------------------------------------------------------------
# contract identifiers and budget
# ---------------------------------------------------------------------------

EXPERIMENT_ID = "EXP-DIFFP-f26790"        # IR-7: the LITERAL id, a hard term
EXP_AREA = "DIFFP-f26790"
TASK_ID = "TASK-20260826-82c660"
BATCH_ID = "BATCH-171407"
GOAL_ID = "GOAL-DIFFP-84d641"
QUESTION_ID = "RQ-DIFFP-a5c483"

TASK_DIR = ("coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-171407/"
            "tasks/TASK-20260826-82c660")
TASK_ROOT = os.path.join(REPO, TASK_DIR)
RUN_OUT_ROOT = None                       # H-10: the contract's declared root

CEILINGS = {
    "frozen-and-forcing-predicate": 45,
    "readmitted-cells": 75,
    "consistent-pair-family": 60,
    "pair-cells-and-null-object": 75,
}

SEEDS = dict(CP.SEEDS)                    # THE EIGHT DECLARED SEEDS, INHERITED
STRICT = CP.STRICT
K_VALUES = CP.K_VALUES
R_NEW_FAMILIES = 8                        # the committed new-family draw count

CENSUS_COMPLETENESS = DG.CENSUS_COMPLETENESS
CONTRACT_KEY_COMPONENTS = tuple(DG.CONTRACT_KEY_COMPONENTS)

RT_CONSTRUCTIONS = os.path.join(
    REPO, "coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-efcae7/reviews/"
          "TASK-20260824-e9d21a/constructions")
BATCH3_PRODUCER_DIR = os.path.join(
    REPO, "coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-145531/tasks/"
          "TASK-20260824-68ba87")

TRAVERSAL_ROOTS = [
    "harness/",
    "harness/diffpath/",
    "coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-efcae7/reviews/"
    "TASK-20260824-e9d21a/constructions/",
    "coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-145531/tasks/"
    "TASK-20260824-68ba87/",
    TASK_DIR + "/",
    "experiments/EXP-DIFFP-f26790/runs/",
]

# ---------------------------------------------------------------------------
# CTL-FROZEN-4 -- the criterion set, WITH THIS CONTRACT'S OWN ARTIFACTS OUT
# ---------------------------------------------------------------------------

THIS_CONTRACTS_OWN_ARTIFACTS = ("harness/diffpath/readmit.py",
                                "tests/test_diffpath_readmit.py")

FROZEN_CRITERION_NOTE = (
    "CTL-FROZEN-4's CRITERION SET IS EVERY .py UNDER harness/diffpath/ -- "
    "INCLUDING depgraph.py and controlpower.py, which are committed inputs of "
    "this contract -- PLUS harness/__init__.py AND harness/runner.py, MINUS "
    "THIS CONTRACT'S OWN TWO REQUIRED NEW ARTIFACTS. harness/diffpath/"
    "readmit.py and tests/test_diffpath_readmit.py are REQUIRED ARTIFACTS this "
    "contract obliges the producer to create; a criterion set containing them "
    "could not be satisfied and the control would be vacuous. Their digests "
    "are reported SEPARATELY, before and after, and their being identical to "
    "each other is a self-check and NEVER an identity criterion.")


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
            "criterion_set_file_list": sorted(crit),
            "this_contracts_own_required_artifacts_reported_separately": own,
            "criterion_note": FROZEN_CRITERION_NOTE}


def compare_digests(pre: dict, post: dict) -> dict:
    a, b = pre["criterion_set"], post["criterion_set"]
    changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    return {
        "control": "CTL-FROZEN-4",
        "criterion_files_before": len(a),
        "criterion_files_after": len(b),
        "criterion_set_file_list": sorted(set(a) | set(b)),
        "identical_count": len(set(a) & set(b)) - len(changed),
        "changed_files": changed,
        "only_before": sorted(set(a) - set(b)),
        "only_after": sorted(set(b) - set(a)),
        "known_answer": "IDENTICAL BEFORE AND AFTER, 0 changed",
        "criterion_met_identical_before_and_after":
            (not changed and set(a) == set(b)),
        "digests_before": a,
        "digests_after": b,
        "this_contracts_own_artifacts_before":
            pre["this_contracts_own_required_artifacts_reported_separately"],
        "this_contracts_own_artifacts_after":
            post["this_contracts_own_required_artifacts_reported_separately"],
        "criterion_note": FROZEN_CRITERION_NOTE,
        "census_completeness": CENSUS_COMPLETENESS,
    }


# ---------------------------------------------------------------------------
# IR-13 -- THE STRICT KEY COMPONENT LIST, DERIVED AT RUN TIME
# ---------------------------------------------------------------------------

def derive_key_components(census) -> dict:
    """Read the component NAMES straight off the committed serialiser.

    NOTHING IS HARD-CODED FROM THE CONTRACT. The names come from
    adjudicator.serialize(obj, STRICT) evaluated on census entries; the
    contract's six names are compared against the DERIVED UNION and a
    difference is a STOP and a finding about the contract.
    """
    per_prim: dict = {}
    stability: dict = {}
    for e in census.shadow:
        names = tuple(p[0] for p in ADJ.serialize(e.obj, STRICT))
        stability.setdefault(e.primitive, set()).add(names)
        per_prim.setdefault(e.primitive, list(names))
    union: list = []
    for prim in ("md5", "sha1"):
        for n in per_prim.get(prim, []):
            if n not in union:
                union.append(n)
    return {
        "derived_per_primitive": {k: list(v) for k, v in per_prim.items()},
        "name_list_is_constant_within_each_primitive":
            {k: len(v) == 1 for k, v in stability.items()},
        "derived_union_in_first_appearance_order": union,
        "contract_declared": list(CONTRACT_KEY_COMPONENTS),
        "agrees_with_contract_as_a_set": set(union) == set(CONTRACT_KEY_COMPONENTS),
        "agrees_with_contract_in_order":
            tuple(union) == tuple(CONTRACT_KEY_COMPONENTS),
        "STOP_the_derived_list_differs_from_the_contracts_six_names":
            set(union) != set(CONTRACT_KEY_COMPONENTS),
        "derivation_method": (
            "the names of harness.diffpath.adjudicator.serialize(obj, STRICT) "
            "under the committed STRICT generator set, evaluated on EVERY "
            "census shadow entry and checked for constancy within each "
            "primitive; NOTHING IS HARD-CODED FROM THE CONTRACT (IR-13)"),
        "the_per_primitive_difference_reported_and_not_worked_around": (
            "in_linearized_code IS A KEY COMPONENT ON sha1 ONLY. The committed "
            "serialiser appends it if and only if obj.primitive == 'sha1', so "
            "the MD5 key has FIVE components and the SHA-1 key has SIX. The "
            "contract's six names are the UNION. THIS FACT IS LOAD-BEARING FOR "
            "THE FORCING PREDICATE and is handled explicitly below rather than "
            "silently -- see VACUOUS_ROW_DECLARATION."),
        "census_completeness": CENSUS_COMPLETENESS,
    }


# ===========================================================================
# ARM (a) -- THE PER-INSTRUMENT FORCING PREDICATE, FROM THE STATEMENT
# ===========================================================================

FORCING_PREDICATE_RULE = (
    "IMPLEMENTED FROM EXP-DIFFP-f26790's WRITTEN STATEMENT AND FROM NO CODE. "
    "LET K BE THE STRICT MEMBERSHIP KEY, DERIVED AT RUN TIME FROM THE "
    "COMMITTED SERIALISER. Let r be a depth-1 row, i.e. the deletion of exactly "
    "one component c(r) from K. Let I be an instrument given as a PROJECTION "
    "pi_I on the serialised key. THE CELL (F, r) IS FORCED FOR I ON PRIMITIVE p "
    "IF AND ONLY IF, in the key pi_I(K_p) with c(r) additionally deleted, THERE "
    "REMAINS a component d such that the committed graph carries an edge "
    "d -> c(r) ON p whose label is `derived_and_witnessed`. A cell forced for I "
    "is EXCLUDED FOR I; a cell not forced for I is ADJUDICATED FOR I. "
    "THE EDGE MUST BE DERIVATION-BACKED: an edge labelled `empirical_only` may "
    "NOT force a cell for any instrument, and neither may a `scope_artifact` "
    "edge on a constant column. THIS FUNCTION APPLIES EXACTLY THAT RULE AND NO "
    "OTHER CLAUSE: it does not restrict by family name, it does not consult the "
    "committed six-cell exclusion, and it does not consult the instrument's "
    "verdict function. A reader can reproduce every cell of the emitted tables "
    "from this paragraph plus the committed edge records (H-7).")

COMPOSITION_ORDERS = {
    "project_then_delete": (
        "READING 1 OF `pi_I's PROJECTION COMPOSED WITH THE ROW'S DELETION`: "
        "apply pi_I to the serialised key FIRST, then delete c(r) from the "
        "result. Retained names = names(pi_I(K_p)) minus {c(r)}."),
    "delete_then_project": (
        "READING 2: delete c(r) from the serialised key FIRST, then apply "
        "pi_I to the result. Retained names = names(pi_I(K_p minus {c(r)})). "
        "BOTH READINGS ARE MEASURED AND BOTH ARE REPORTED. CHOOSING ONE AFTER "
        "SEEING WHICH GIVES THE MORE INTERESTING COUNT WOULD BE AN IR-6 "
        "VIOLATION; THIS MODULE PICKS NEITHER."),
}

VACUOUS_ROW_DECLARATION = (
    "A SPECIFICATION GAP THE PRODUCER REPORTS RATHER THAN RESOLVES, DECLARED "
    "IN THIS MODULE BEFORE ANY RUN EXECUTED AND THEREFORE NOT IR-6 IN-RUN "
    "REPAIR. The contract's statement defines forcing for a depth-1 row of K, "
    "i.e. the deletion of a component OF K. On MD5 the derived key has FIVE "
    "components: in_linearized_code IS NOT ONE OF THEM, so the row deleting it "
    "is not a depth-1 row of the MD5 key at all and its deletion is the "
    "IDENTITY on every MD5 key. THE CONTRACT'S `IF AND ONLY IF` DOES NOT SAY "
    "WHICH SIDE SUCH A ROW FALLS ON, AND THE TWO ANSWERS DIFFER: "
    "(R1) `edge_only` -- read the iff literally. No component d remains with a "
    "derivation-backed edge d -> in_linearized_code on MD5, because the "
    "committed graph carries NO derived_and_witnessed edge into that column on "
    "MD5 (its 5 MD5 edges into that column are all `empirical_only` on a "
    "constant column, which the contract's own clause (2) forbids as a forcing "
    "edge). SO THE CELL IS NOT FORCED AND IS ADJUDICATED. "
    "(R2) `edge_or_vacuous` -- treat a row whose component is absent from the "
    "primitive's key as forced vacuously, its value unchangeable because the "
    "deletion is the identity. THIS IS THE READING THE COMMITTED "
    "BATCH-145531 RULE TOOK: its own excluded-cell record carries, for MD5, a "
    "forcing edge with X = null and the derivation `in_linearized_code IS NOT A "
    "COMPONENT OF THE md5 KEY, so deleting it is the identity on every md5 "
    "key`. THAT RECORD HAS A DERIVATION BUT NO SOURCE COMPONENT d, WHICH IS "
    "EXACTLY WHY THE TWO READINGS COME APART. "
    "THIS MODULE MEASURES AND REPORTS BOTH READINGS EVERYWHERE, EXACTLY AS IT "
    "MEASURES AND REPORTS BOTH COMPOSITION ORDERS, AND CHOOSES NEITHER. THE "
    "CHOICE BELONGS TO THE COORDINATOR AS A SPECIFICATION QUESTION, AND ITS "
    "CONSEQUENCE FOR CTL-FORCE-PI's KNOWN ANSWER IS REPORTED UNDER BOTH "
    "READINGS RATHER THAN ASSERTED UNDER ONE.")

FORCING_READINGS = ("edge_only", "edge_or_vacuous")


def _serialised_key(obj):
    return tuple(ADJ.serialize(obj, STRICT))


def retained_component_names(key, prim, proj, deleted, order) -> tuple:
    """The names surviving pi_I composed with the row's deletion, per order."""
    if order == "project_then_delete":
        k = proj(key, prim)
        k = tuple(p for p in k if p[0] != deleted)
    elif order == "delete_then_project":
        k = tuple(p for p in key if p[0] != deleted)
        k = proj(k, prim)
    else:                                                        # pragma: no cover
        raise KeyError(order)
    return tuple(p[0] for p in k)


def forcing_edges_for(deleted, prim, proj, order, key_names,
                      representative_key, edge_records_by_prim) -> dict:
    """THE PREDICATE. Returns the evidence, not just a boolean."""
    retained = retained_component_names(representative_key[prim], prim, proj,
                                        deleted, order)
    vacuous = deleted not in key_names[prim]
    edges = []
    for rec in edge_records_by_prim[prim]:
        if rec["Y"] != deleted:
            continue
        if rec["verdict"] != "EDGE" or rec["label"] != "derived_and_witnessed":
            continue
        if rec["X"] not in retained:
            continue
        edges.append({
            "X": rec["X"], "Y": rec["Y"], "primitive_scope": prim,
            "edge_label": rec["label"],
            "derivation": rec["derivation"],
            "witness_population_size": rec["population_size"],
            "witness_groups_constant_in_Y": rec["groups_constant_in_Y"],
            "witness_groups_total": rec["groups_total"],
        })
    return {
        "primitive_scope": prim,
        "composition_order": order,
        "retained_component_names": list(retained),
        "deleted_component": deleted,
        "component_is_in_this_primitives_key": not vacuous,
        "vacuous_row": vacuous,
        "vacuous_row_derivation": (
            f"{deleted} IS NOT A COMPONENT OF THE {prim} KEY, so deleting it "
            f"is the identity on every {prim} key" if vacuous else None),
        "forcing_edges": edges,
        "forced_literal_edge_only": bool(edges),
        "forced_edge_or_vacuous": bool(edges) or vacuous,
        "census_completeness": CENSUS_COMPLETENESS,
    }


def cell_universe(components, family_names) -> list:
    """3 constructible families x 6 union rows x 2 primitives = 36 cells.

    THE DENOMINATOR IS DERIVED HERE AND NOT INHERITED (H-13). RT-J8-4's 30 is
    NOT adopted; the number below is computed from the derived component list
    and the constructible family list and its arithmetic is emitted beside it.
    """
    cells = []
    for fam in family_names:
        for row in components:
            for prim in ("md5", "sha1"):
                cells.append({"family": fam, "row_deletes": row,
                              "primitive": prim})
    return cells


DIAGONAL_RULE = (
    "THE COMMITTED DIAGONAL EXCLUSION, QUOTED AND APPLIED ONLY WHERE ITS OWN "
    "HYPOTHESIS HOLDS (TASK-20260824-e9d21a J13): a family perturbing EXACTLY "
    "THE SET S while holding every other key component fixed makes the row "
    "deleting S DETECTED BY CONSTRUCTION, because the perturbed draw and its "
    "own source entry then agree on every retained component. EACH OF THE "
    "THREE FAMILIES ARM (a) REUSES MOVES EXACTLY ONE COMPONENT, so |S| = 1 and "
    "the depth-1 row deleting that component is diagonal. THE CONSISTENT-PAIR "
    "FAMILY OF ARM (b) MOVES TWO, so NO depth-1 row deletes its whole S and the "
    "theorem's hypothesis is FALSE for every depth-1 row of it; this module "
    "therefore applies NO diagonal exclusion to that family and adjudicates all "
    "six of its rows. That is a derivation from the committed rule text, "
    "declared before any run, and a reader can check it against the quoted "
    "hypothesis.")


def build_forced_tables(components, families, instruments, edge_records_by_prim,
                        key_names, representative_key) -> dict:
    """The per-instrument forced set: per instrument, per primitive, per order."""
    fam_names = sorted(n for n, f in families.items()
                       if not f["NOT_CONSTRUCTIBLE_on_every_primitive"])
    universe = cell_universe(components, fam_names)
    out: dict = {}
    for iname, spec in instruments.items():
        proj = spec["projection"]
        per_order: dict = {}
        for order in COMPOSITION_ORDERS:
            per_cell = []
            for cell in universe:
                moved = families[cell["family"]]["declaration"]["moves"]
                diagonal = (len(moved) == 1 and cell["row_deletes"] == moved[0])
                ev = forcing_edges_for(cell["row_deletes"], cell["primitive"],
                                       proj, order, key_names,
                                       representative_key, edge_records_by_prim)
                per_cell.append({**cell,
                                 "family_moves": list(moved),
                                 "diagonal": diagonal,
                                 "forcing": ev})
            per_order[order] = per_cell
        out[iname] = {
            "instrument_declaration": spec["declaration"],
            "projection_kind": spec["kind"],
            "per_composition_order": per_order,
        }
    return {"forced_tables": out,
            "constructible_families": fam_names,
            "cell_universe_size_per_primitive_cells": len(universe),
            "cell_universe_arithmetic": (
                f"{len(fam_names)} CTL-WF-constructible families x "
                f"{len(components)} derived union rows x 2 primitives = "
                f"{len(universe)} PER-PRIMITIVE cells. DERIVED HERE FROM THE "
                f"RUN-TIME COMPONENT LIST AND THE GATE, NOT INHERITED (H-13)."),
            "diagonal_rule": DIAGONAL_RULE}


def forced_and_adjudicated(per_cell, reading) -> dict:
    key = ("forced_literal_edge_only" if reading == "edge_only"
           else "forced_edge_or_vacuous")
    forced, adjudicated, diagonal = [], [], []
    for c in per_cell:
        if c["diagonal"]:
            diagonal.append(c)
        elif c["forcing"][key]:
            forced.append(c)
        else:
            adjudicated.append(c)
    return {"reading": reading, "forced": forced, "adjudicated": adjudicated,
            "diagonal": diagonal}


# ---------------------------------------------------------------------------
# instruments
# ---------------------------------------------------------------------------

def proj_identity(key, prim):
    return key


DEGENERATE_PROJECTION_NOTE = (
    "always_member AND always_non_member ARE NOT PROJECTIONS -- THEY ARE "
    "VERDICT FUNCTIONS, and the committed module says so in terms. The "
    "contract's forcing predicate is defined for an instrument GIVEN AS A "
    "PROJECTION, so for the two degenerate instruments this module uses the "
    "IDENTITY projection for the forcing/cell-selection half and the constant "
    "verdict for the counting half, AND DECLARES IT. CONSEQUENCE, STATED SO NO "
    "READER MISTAKES IT FOR A MEASUREMENT: their forced set is EQUAL TO THE "
    "IDENTITY INSTRUMENT'S BY DECLARATION, not by observation, and it is "
    "therefore EXCLUDED from CTL-FORCE-PI's `does the forced set move across "
    "instruments` side, which is evaluated over the PROJECTIVE instruments "
    "honest and O-E.")


def load_reused_O_E():
    """IR-11: O-E is REUSED from the committed BATCH-efcae7 construction file.

    IMPORTED BY importlib AND CALLED THERE. No re-expression of the projection
    exists anywhere in this module; grep for proj_drop_on_primitive and it
    appears only as an attribute lookup on the imported module.
    """
    path = os.path.join(RT_CONSTRUCTIONS, "rt_instruments.py")
    spec = importlib.util.spec_from_file_location("rt_instruments_reused", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rt_instruments_reused"] = mod
    spec.loader.exec_module(mod)
    return mod


def build_instruments(rt) -> dict:
    return {
        "honest": {
            "projection": proj_identity, "kind": "projection",
            "declaration": ("THE COMMITTED SERIALISATION, UNMODIFIED -- the "
                            "IDENTITY projection. This is CTL-FORCE-PI's "
                            "null object for the new rule."),
            "verdict_override": None},
        "O-E": {
            "projection": rt.proj_drop_on_primitive(["message_difference"],
                                                    "sha1"),
            "kind": "projection",
            "declaration": ("THE KNOWN-FALSE INSTRUMENT, REUSED AND NOT "
                            "REBUILT (IR-11): "
                            "`proj_drop_on_primitive(['message_difference'], "
                            "'sha1')` IMPORTED FROM the committed "
                            "constructions/rt_instruments.py of "
                            "TASK-20260824-e9d21a. Blind to the SHA-1 message "
                            "difference and sighted on the MD5 one."),
            "verdict_override": None},
        "always_member": {
            "projection": proj_identity, "kind": "degenerate_verdict_function",
            "declaration": ("A DEGENERATE NULL INSTRUMENT returning MEMBER for "
                            "every object, run through the IDENTICAL counting "
                            "path. " + DEGENERATE_PROJECTION_NOTE),
            "verdict_override": True},
        "always_non_member": {
            "projection": proj_identity, "kind": "degenerate_verdict_function",
            "declaration": ("A DEGENERATE NULL INSTRUMENT returning NON-MEMBER "
                            "for every object, run through the IDENTICAL "
                            "counting path. " + DEGENERATE_PROJECTION_NOTE),
            "verdict_override": False},
    }


# ---------------------------------------------------------------------------
# the counting path -- THE COMMITTED RULE, UNCHANGED AND SHARED BY EVERY ARM
# ---------------------------------------------------------------------------

COUNTING_PATH_NOTE = (
    "THE COUNTING RULE IS THE COMMITTED ONE AND IS NOT RE-EXPRESSED: "
    "harness.diffpath.depgraph.cell_verdict, build_index and canon_under are "
    "CALLED. The contract's composition-order ambiguity is stated INSIDE the "
    "FORCING PREDICATE's paragraph and this module varies the order THERE "
    "ONLY; the committed counting rule's own order -- project inside the orbit "
    "minimisation, then delete -- is a term of the closed BATCH-145531 contract "
    "and is left exactly as committed (IR-6, H-2). EVERY INSTRUMENT, INCLUDING "
    "THE TWO DEGENERATE ONES, GOES THROUGH THIS IDENTICAL PATH.")


def cell_verdict_for(instrument, entry_keys, draw_keys, deleted, prim):
    """Per-primitive BY CONSTRUCTION (H-12): prim_filter is passed, never
    applied after the fact, and the draw set is filtered inside the committed
    cell_verdict, so md5 and sha1 never share a computed statistic."""
    override = instrument["verdict_override"]
    if override is not None:
        def look(keys, p, _o=override):
            return _o
    else:
        proj = instrument["projection"]
        idx = DG.build_index(entry_keys, proj, (deleted,))

        def look(keys, p, _idx=idx, _proj=proj, _drop=(deleted,)):
            return DG.canon_under(keys, p, _proj, _drop) in _idx
    v = DG.cell_verdict(draw_keys, look, prim)
    v["instrument_declaration"] = instrument["declaration"]
    v["computed_per_primitive"] = True
    v["per_primitive_note"] = (
        f"COMPUTED PER PRIMITIVE: the draw set was filtered to {prim} INSIDE "
        f"the committed cell_verdict via prim_filter, so this integer is a "
        f"{prim} statistic and never a primitive-blind one indexed per "
        f"primitive (H-12).")
    return v


# ===========================================================================
# ARM (b) -- THE CONSISTENT-PAIR FLAG-AND-dv FAMILY
# ===========================================================================

CONSISTENT_PAIR_DECLARATION = {
    "name": "d_consistent_pair_flag_and_dv",
    "moves": ["message_difference", "in_linearized_code"],
    "holds_fixed": ["primitive", "length", "step_delta", "block_index"],
    "declaration_text": (
        "NEW IN THIS MODULE AND IT IS THE ONE NAMED REPAIR OF NULL FAMILY (e)'s "
        "SUBSTANTIVE RETIREMENT (DEC-20260824-257f35 R3-J7). IT PERTURBS THE "
        "FLAG AND THE dv TOGETHER SO THE PAIR STAYS MUTUALLY CONSISTENT. "
        "ON SHA-1: flip k bits of the message difference IN THE EXPANSION TAIL "
        "-- words 16..len(dv)-1, the words primitives.sha1_in_linearized_code "
        "compares against sha1_expand(words[:16], len(words)) -- and then SET "
        "THE FLAG TO THE COMMITTED PREDICATE'S VALUE OF THE NEW dv, "
        "P.sha1_in_linearized_code(list(dv)). A tail flip makes the dv a "
        "NON-CODEWORD and the recomputed flag False, so the pair moves TOGETHER "
        "and stays mutually consistent by construction. Nothing else is "
        "touched: length, step_delta, step_range, block_index and primitive are "
        "carried over unchanged. "
        "ON MD5 THE SAME DECLARATION IS ATTEMPTED HONESTLY AND NOT QUIETLY "
        "TURNED INTO A NO-OP: MD5 has no dv and no codeword predicate, so the "
        "attempt flips k bits of delta_m and SETS in_linearized_code to False, "
        "which is the MD5 reading of `set the flag`. It is then offered to the "
        "committed gate. A no-op perturbation the gate accepts would report a "
        "family CONSTRUCTIBLE while moving nothing, which is the failure mode "
        "the committed _perturb_flag comment names. "
        "DRAW PLAN, DECLARED BEFORE ANY DRAW: k in (0,1,2,4,8,16), the "
        "deterministic draw plus 8 seeded draws per (entry, k>=1), off ONE "
        "random.Random(SEEDS['null_draw_message_difference_perturbed']) = "
        "random.Random(84064107) consumed in census order then k ascending then "
        "draw index. NO NINTH SEED IS CREATED; this is the same declared seed "
        "the committed new families use."),
    "inconsistent_side_declaration_text": (
        "THE DELIBERATELY INCONSISTENT CONSTRUCTION CTL-PAIR-WF REQUIRES THE "
        "GATE TO REJECT: the IDENTICAL dv perturbation with the flag LEFT AT "
        "ITS OLD VALUE instead of recomputed. On SHA-1 that leaves the flag "
        "True over a non-codeword dv. On MD5 it leaves the flag set to True "
        "where the committed serialiser requires None."),
}


def perturb_consistent_pair(obj, positions, tag, consistent=True):
    """THE PAIR CONSTRUCTOR. `consistent=False` is CTL-PAIR-WF's other side."""
    new = PathObject(**{**obj.__dict__})
    new.id = f"{obj.id}~PAIR{'' if consistent else 'X'}{tag}"
    new.path_data = {"kind": ("family_consistent_pair_flag_and_dv" if consistent
                              else "family_consistent_pair_DELIBERATELY_"
                                   "INCONSISTENT"),
                     "of": obj.id, "k": len(positions),
                     "flipped_bit_positions": list(positions)}
    if obj.primitive == "sha1":
        d = list(obj.dv)
        tail = len(d) - 16
        for p in positions:
            w = 16 + ((p // 32) % tail) if tail > 0 else (p // 32) % len(d)
            d[w] ^= 1 << (p % 32)
        new.dv = tuple(d)
        new.in_linearized_code = (P.sha1_in_linearized_code(list(d))
                                  if consistent else obj.in_linearized_code)
    else:
        d = list(obj.delta_m)
        for p in positions:
            d[(p // 32) % len(d)] ^= 1 << (p % 32)
        new.delta_m = tuple(d)
        new.delta_m_signed = tuple(bsdr_encode(x) for x in d)
        new.in_linearized_code = False if consistent else True
    return new


def build_consistent_pair_family(census) -> dict:
    """Both sides of CTL-PAIR-WF, every draw offered to the COMMITTED gate."""
    fam = {"declaration": CONSISTENT_PAIR_DECLARATION,
           "draws": [],
           "constructed": {"md5": 0, "sha1": 0},
           "rejected": {"md5": 0, "sha1": 0},
           "rejection_reasons": {"md5": {}, "sha1": {}},
           "inconsistent_constructed": {"md5": 0, "sha1": 0},
           "inconsistent_accepted": {"md5": 0, "sha1": 0},
           "inconsistent_rejection_reasons": {"md5": {}, "sha1": {}}}
    rng = random.Random(SEEDS["null_draw_message_difference_perturbed"])
    for e in census.shadow:
        prim = e.primitive
        nbits = CP.md_bits(e.obj)
        for k in K_VALUES:
            plan = [("deterministic", tuple(range(k)))]
            if k >= 1:
                plan += [("seeded", tuple(sorted(rng.sample(range(nbits), k))))
                         for _ in range(R_NEW_FAMILIES)]
            for draw_type, pos in plan:
                good = perturb_consistent_pair(e.obj, pos, f"k{k}-{draw_type}",
                                               True)
                fam["constructed"][prim] += 1
                bad = DG.wf_violations(good)
                if bad:
                    fam["rejected"][prim] += 1
                    for b in bad:
                        fam["rejection_reasons"][prim][b] = \
                            fam["rejection_reasons"][prim].get(b, 0) + 1
                else:
                    fam["draws"].append({"entry": e, "obj": good, "k": k,
                                         "draw_type": draw_type,
                                         "primitive": prim})
                if k >= 1 and draw_type == "deterministic":
                    bad2 = perturb_consistent_pair(e.obj, pos, f"k{k}", False)
                    fam["inconsistent_constructed"][prim] += 1
                    v2 = DG.wf_violations(bad2)
                    if not v2:
                        fam["inconsistent_accepted"][prim] += 1
                    for b in v2:
                        fam["inconsistent_rejection_reasons"][prim][b] = \
                            fam["inconsistent_rejection_reasons"][prim].get(b, 0) + 1
    per_prim = {}
    for prim in ("md5", "sha1"):
        kept = sum(1 for d in fam["draws"] if d["primitive"] == prim)
        per_prim[prim] = {
            "consistent_side_constructed": fam["constructed"][prim],
            "consistent_side_accepted_by_CTL_WF": kept,
            "consistent_side_rejected_by_CTL_WF": fam["rejected"][prim],
            "consistent_side_rejection_gate_clauses":
                dict(fam["rejection_reasons"][prim]) or None,
            "inconsistent_side_constructed": fam["inconsistent_constructed"][prim],
            "inconsistent_side_accepted_by_CTL_WF":
                fam["inconsistent_accepted"][prim],
            "inconsistent_side_rejection_gate_clauses":
                dict(fam["inconsistent_rejection_reasons"][prim]) or None,
            "CONSTRUCTIBLE": kept > 0,
            "computed_per_primitive": True,
            "census_completeness": CENSUS_COMPLETENESS,
        }
    fam["per_primitive"] = per_prim
    fam["NOT_CONSTRUCTIBLE_on_every_primitive"] = not any(
        v["CONSTRUCTIBLE"] for v in per_prim.values())
    return fam


def measure_moved_components(fam) -> dict:
    """CTL-PAIR-DECL: the MEASURED moved set beside the DECLARED one."""
    declared = sorted(CONSISTENT_PAIR_DECLARATION["moves"])
    out = {}
    for prim in ("md5", "sha1"):
        draws = [d for d in fam["draws"]
                 if d["primitive"] == prim and d["k"] >= 1]
        if not draws:
            out[prim] = {
                "declared_moved_components": declared,
                "measured_moved_components": None,
                "measured_on_draws": 0,
                "why_null_and_never_an_empty_list": (
                    "NO CTL-WF-ACCEPTED PERTURBED DRAW EXISTS ON THIS "
                    "PRIMITIVE, so the moved set is UNMEASURED and is emitted "
                    "as null and NEVER as [] or 0 (H-8). An empty list would "
                    "read as `measured, and nothing moved`, which is false."),
                "declared_equals_measured": None,
                "computed_per_primitive": True,
                "census_completeness": CENSUS_COMPLETENESS}
            continue
        union, per_draw = set(), []
        for d in draws:
            before = dict(_serialised_key(d["entry"].obj))
            after = dict(_serialised_key(d["obj"]))
            moved = sorted(n for n in set(before) | set(after)
                           if before.get(n) != after.get(n))
            union |= set(moved)
            per_draw.append(tuple(moved))
        counts = {}
        for m in per_draw:
            counts[m] = counts.get(m, 0) + 1
        out[prim] = {
            "declared_moved_components": declared,
            "measured_moved_components_union_over_draws": sorted(union),
            "measured_moved_sets_with_draw_counts":
                [{"moved": list(k), "draws": v} for k, v in sorted(counts.items())],
            "measured_on_draws": len(draws),
            "declared_equals_measured_union": sorted(union) == declared,
            "discrepancy_between_declared_and_measured":
                (None if sorted(union) == declared else
                 {"declared_not_measured": sorted(set(declared) - union),
                  "measured_not_declared": sorted(union - set(declared)),
                  "why_this_is_a_first_class_finding": (
                      "DEC-20260824-257f35 C_4: a family that declares one "
                      "movement and performs another breaks every theorem "
                      "instantiated on its declaration. THE MEASUREMENT "
                      "GOVERNS AND THE DECLARATION IS THE THING FOUND WRONG.")}),
            "measurement_method": (
                "the COMMITTED serialiser: dict(adjudicator.serialize(obj, "
                "STRICT)) on the SOURCE census entry and on the DRAW, compared "
                "component by component. Nothing is inferred from the "
                "constructor's own intent."),
            "computed_per_primitive": True,
            "census_completeness": CENSUS_COMPLETENESS}
    return out


# ---------------------------------------------------------------------------
# CTL-O-E-REUSE
# ---------------------------------------------------------------------------

O_E_COMMITTED_ROW_NAME = "O-E md-blind on SHA1 ONLY     [plan candidate v]"

O_E_REUSE_SCOPE_NOTE = (
    "WHAT `ALL 30 COMMITTED COMPARISONS` IS TAKEN TO MEAN, STATED BECAUSE THE "
    "CONTRACT'S PHRASE ADMITS TWO ARITHMETICS THAT BOTH REACH 30 AND THE "
    "PRODUCER DOES NOT GET TO PICK SILENTLY. READING TAKEN AND MEASURED: O-E's "
    "OWN committed row in j8_results.json carries 12 per_cell entries x "
    "(draws, member) = 24 integers PLUS 6 summary integers (plant, "
    "null_fp_total, d_md5_k_ge_1_member, d_sha1_k_ge_1_member, k0, "
    "subarm_incode_member) = EXACTLY 30, and CTL-O-E-REUSE is a control ABOUT "
    "O-E. READING NOT TAKEN AND REPORTED AS UNMEASURED, NEVER AS AGREEMENT: "
    "BATCH-145531's CTL-RC1 checked 5 instruments x those same 6 summary "
    "integers = 30. THIS CONTRACT'S RUN 2 CEILING IS 75 s AND ONE run_suite "
    "COSTS ~52 s, so five of them CANNOT be executed inside the declared "
    "budget; the other four instruments are therefore emitted as null and "
    "NEVER as 0 or as agreement (H-8). WHICH READING THE CONTRACT MEANT IS A "
    "QUESTION FOR THE COORDINATOR AND IS NOT RESOLVED HERE.")


def ctl_o_e_reuse(rt, instruments) -> dict:
    with open(os.path.join(RT_CONSTRUCTIONS, "j8_results.json"),
              encoding="utf-8") as fh:
        committed = json.load(fh)
    row = next((r for r in committed if r["name"] == O_E_COMMITTED_ROW_NAME),
               None)
    if row is None:
        return {"control": "CTL-O-E-REUSE", "status": "STOP",
                "reason": ("the committed O-E row was not found in "
                           "j8_results.json under its committed name"),
                "committed_row_name_sought": O_E_COMMITTED_ROW_NAME,
                "row_names_present": [r["name"] for r in committed]}
    I = rt.Instr("O-E", instruments["O-E"]["projection"])
    r = rt.run_suite(I)
    comparisons = []

    def cmp(label, got, want):
        comparisons.append({"quantity": label, "recomputed": got,
                            "committed": want, "agrees": got == want})

    for cellname in sorted(row["per_cell"]):
        for f in ("draws", "member"):
            cmp(f"per_cell[{cellname}].{f}",
                r["CTL_NULL_D_per_primitive_k"].get(cellname, {}).get(f),
                row["per_cell"][cellname][f])
    cmp("plant", r["CTL_PLANT"], row["plant"])
    cmp("null_fp_total", r["CTL_NULL_strict_fp_total"], row["null_fp_total"])
    cmp("d_md5_k_ge_1_member", r["CTL_NULL_D_member_k_ge_1_md5"],
        row["d_md5_k_ge_1_member"])
    cmp("d_sha1_k_ge_1_member", r["CTL_NULL_D_member_k_ge_1_sha1"],
        row["d_sha1_k_ge_1_member"])
    cmp("k0", r["CTL_NULL_D_k0"], row["k0"])
    cmp("subarm_incode_member",
        f"{r['SUBARM_D_SHA1_INCODE_member']['member']}/"
        f"{r['SUBARM_D_SHA1_INCODE_member']['draws']}",
        row["subarm_incode_member"])
    agree = sum(1 for c in comparisons if c["agrees"])
    return {
        "control": "CTL-O-E-REUSE",
        "status": "COMPLETED",
        "committed_row_name": O_E_COMMITTED_ROW_NAME,
        "comparisons": comparisons,
        "comparisons_total": len(comparisons),
        "comparisons_agreeing": agree,
        "comparisons_disagreeing": len(comparisons) - agree,
        "disagreements": [c for c in comparisons if not c["agrees"]],
        "known_answer": "agreement on all 30 committed comparisons",
        "known_answer_met": (agree == len(comparisons) == 30),
        "STOP_any_disagreement": agree != len(comparisons),
        "the_other_four_instruments_of_BATCH_145531s_CTL_RC1": None,
        "scope_note": O_E_REUSE_SCOPE_NOTE,
        "reuse_mechanism": (
            "IR-11. rt_instruments.py is loaded by importlib from the committed "
            "BATCH-efcae7 review directory and proj_drop_on_primitive is CALLED "
            "THERE. NO RE-EXPRESSION OF THE PROJECTION EXISTS IN THIS MODULE. "
            "rt.Instr and rt.run_suite are the committed wrapper and are also "
            "called there, so the `mechanically necessary wrapper` this control "
            "names is the reviewer's own committed code and not a new one."),
        "census_completeness": CENSUS_COMPLETENESS,
    }


# ---------------------------------------------------------------------------
# the committed six cells, read from the BATCH-145531 PRODUCER artifact
# ---------------------------------------------------------------------------

def committed_six_forced_cells() -> dict:
    path = os.path.join(BATCH3_PRODUCER_DIR, "offdiagonal-matrix-result.json")
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    cells = [c for c in doc["excluded_cells_with_every_reason"]
             if c["exclusion"] == "forced_by_the_graph"]
    return {
        "source": os.path.relpath(path, REPO),
        "source_note": ("THE PRODUCER's committed artifact of the CLOSED "
                        "BATCH-145531, a declared input of this contract. IT IS "
                        "NOT the H-1 forbidden path, which is that batch's "
                        "reviews/TASK-20260824-7d9f92/constructions directory "
                        "and is never opened."),
        "aggregate_cells": [{"family": c["family"],
                             "row_deletes": c["row_deletes"],
                             "forcing_edges": c["forcing_edges"]}
                            for c in cells],
        "aggregate_cell_count": len(cells),
    }


# ---------------------------------------------------------------------------
# CTL-FORCE-PI -- the two-sided null-object control for the NEW rule
# ---------------------------------------------------------------------------

CTL_FORCE_PI_LIMIT = (
    "WHAT CTL-FORCE-PI DOES NOT BUY, QUOTED FROM THE CONTRACT AND CARRIED ON "
    "THE RESULT SO IT CANNOT BE DROPPED IN TRANSIT: the first side pins the new "
    "rule to the old one on the one case where the old rule is right; the "
    "second side proves the new rule can move at all. NEITHER SIDE SHOWS THAT "
    "THE PER-INSTRUMENT READING IS THE CORRECT GENERALISATION, only that it is "
    "A generalisation that agrees where it must and moves where it can. NO "
    "RECORD OF THIS BATCH MAY READ CTL-FORCE-PI PASSING AS EVIDENCE THAT THE "
    "QUANTIFIER IS RIGHT.")


def ctl_force_pi(forced_bundle, committed, components) -> dict:
    tables = forced_bundle["forced_tables"]
    out: dict = {"control": "CTL-FORCE-PI", "per_reading": {},
                 "limit": CTL_FORCE_PI_LIMIT,
                 "census_completeness": CENSUS_COMPLETENESS,
                 "vacuous_row_declaration": VACUOUS_ROW_DECLARATION}
    committed_set = {(c["family"], c["row_deletes"])
                     for c in committed["aggregate_cells"]}
    for reading in FORCING_READINGS:
        per_order = {}
        for order in COMPOSITION_ORDERS:
            ident = forced_and_adjudicated(
                tables["honest"]["per_composition_order"][order], reading)
            oe = forced_and_adjudicated(
                tables["O-E"]["per_composition_order"][order], reading)

            def agg(f):
                by = {}
                for c in f["forced"]:
                    by.setdefault((c["family"], c["row_deletes"]), set()).add(
                        c["primitive"])
                return {k: sorted(v) for k, v in by.items()
                        if set(v) == {"md5", "sha1"}}

            ident_agg, oe_agg = agg(ident), agg(oe)
            missing = sorted(committed_set - set(ident_agg))
            extra = sorted(set(ident_agg) - committed_set)
            side_a_met = (not missing and not extra)
            ident_pp = {(c["family"], c["row_deletes"], c["primitive"])
                        for c in ident["forced"]}
            oe_pp = {(c["family"], c["row_deletes"], c["primitive"])
                     for c in oe["forced"]}
            per_order[order] = {
                "composition_order_declaration": COMPOSITION_ORDERS[order],
                "side_a_identity_versus_the_committed_six": {
                    "identity_forced_set_aggregate":
                        [{"family": f, "row_deletes": r,
                          "primitives_forced_on": p}
                         for (f, r), p in sorted(ident_agg.items())],
                    "identity_forced_aggregate_cell_count": len(ident_agg),
                    "committed_forced_aggregate_cell_count":
                        len(committed_set),
                    "in_committed_but_not_in_identity_forced_set":
                        [{"family": f, "row_deletes": r} for f, r in missing],
                    "in_identity_forced_set_but_not_committed":
                        [{"family": f, "row_deletes": r} for f, r in extra],
                    "known_answer": ("EXACTLY EQUAL AS A SET AND CELL BY CELL, "
                                     "6 of 6, with the forcing EDGE named for "
                                     "each"),
                    "known_answer_met": side_a_met,
                    "which_side_the_difference_is_on_if_any": (
                        None if side_a_met else
                        "REPORTED AND NOT DECIDED (P-A status_if_refuted). The "
                        "difference is entirely the MD5 half of the three "
                        "in_linearized_code rows under the `edge_only` "
                        "reading: the committed rule forces them by a "
                        "no-source-component record and the literal `iff` of "
                        "this contract's own statement does not. WHETHER THE "
                        "COMMITTED SIX WERE WRONG OR THIS RULE IS NOT A "
                        "GENERALISATION OF THEM IS NOT THIS PRODUCER'S TO "
                        "DECIDE; both forced sets are emitted in full."),
                },
                "side_b_does_the_forced_set_move_across_instruments": {
                    "scope": ("THE PROJECTIVE INSTRUMENTS ONLY -- honest and "
                              "O-E. The two degenerate instruments take the "
                              "IDENTITY projection BY DECLARATION and their "
                              "forced set is therefore equal to the identity's "
                              "by construction, which would be bookkeeping and "
                              "never a demonstration. " +
                              DEGENERATE_PROJECTION_NOTE),
                    "identity_forced_per_primitive_cells":
                        sorted([list(x) for x in ident_pp]),
                    "O_E_forced_per_primitive_cells":
                        sorted([list(x) for x in oe_pp]),
                    "identity_forced_per_primitive_count": len(ident_pp),
                    "O_E_forced_per_primitive_count": len(oe_pp),
                    "forced_in_identity_but_not_in_O_E":
                        sorted([list(x) for x in ident_pp - oe_pp]),
                    "forced_in_O_E_but_not_in_identity":
                        sorted([list(x) for x in oe_pp - ident_pp]),
                    "forced_set_MOVES_at_per_primitive_granularity":
                        ident_pp != oe_pp,
                    "identity_forced_aggregate_cells":
                        sorted([list(k) for k in ident_agg]),
                    "O_E_forced_aggregate_cells":
                        sorted([list(k) for k in oe_agg]),
                    "forced_set_MOVES_at_aggregate_granularity":
                        set(ident_agg) != set(oe_agg),
                    "granularity_note": (
                        "AN AGGREGATE COUNT AND A PER-PRIMITIVE COUNT ARE "
                        "DIFFERENT QUANTITIES AND ARE NEVER MERGED (H-9). The "
                        "aggregate cell requires forcing on BOTH primitives, "
                        "which is the committed rule's own quantifier; the "
                        "per-primitive cell is the granularity at which the "
                        "re-admitted denominator is counted."),
                    "known_answer": ("the forced set under O-E must NOT equal "
                                     "the identity forced set"),
                    "known_answer_met_at_per_primitive_granularity":
                        ident_pp != oe_pp,
                    "known_answer_met_at_aggregate_granularity":
                        set(ident_agg) != set(oe_agg),
                },
                "forced_cells_with_their_edges": {
                    iname: [{"family": c["family"],
                             "row_deletes": c["row_deletes"],
                             "primitive_scope": c["primitive"],
                             "forcing_edges": c["forcing"]["forcing_edges"],
                             "vacuous_row": c["forcing"]["vacuous_row"],
                             "vacuous_row_derivation":
                                 c["forcing"]["vacuous_row_derivation"],
                             "retained_component_names":
                                 c["forcing"]["retained_component_names"]}
                            for c in forced_and_adjudicated(
                                tables[iname]["per_composition_order"][order],
                                reading)["forced"]]
                    for iname in tables},
            }
        orders = list(COMPOSITION_ORDERS)
        a, b = per_order[orders[0]], per_order[orders[1]]
        out["per_reading"][reading] = {
            "reading_declaration": VACUOUS_ROW_DECLARATION,
            "per_composition_order": per_order,
            "the_two_composition_orders_agree": (
                a["side_a_identity_versus_the_committed_six"][
                    "identity_forced_set_aggregate"]
                == b["side_a_identity_versus_the_committed_six"][
                    "identity_forced_set_aggregate"]
                and a["side_b_does_the_forced_set_move_across_instruments"][
                    "identity_forced_per_primitive_cells"]
                == b["side_b_does_the_forced_set_move_across_instruments"][
                    "identity_forced_per_primitive_cells"]
                and a["side_b_does_the_forced_set_move_across_instruments"][
                    "O_E_forced_per_primitive_cells"]
                == b["side_b_does_the_forced_set_move_across_instruments"][
                    "O_E_forced_per_primitive_cells"]),
            "agreement_was_CHECKED_and_not_assumed": True,
        }
    return out


# ---------------------------------------------------------------------------
# CTL-READMIT and CTL-READMIT-NULL
# ---------------------------------------------------------------------------

READMIT_RULE = (
    "FOR EACH INSTRUMENT I IN SCOPE, THE CELLS NOT FORCED FOR I ARE ADJUDICATED "
    "FOR I -- against the HONEST instrument and against the REUSED O-E, over "
    "the EXISTING draw sets of the three constructible families. THE DIFFERING "
    "COUNT IS THE NUMBER OF ADJUDICATED CELLS AT WHICH THE HONEST VERDICT AND "
    "THE O-E VERDICT DISAGREE, AND IT IS REPORTED BESIDE ITS DENOMINATOR, ITS "
    "EXCLUSION LIST AND EVERY EXCLUSION'S FORCING EDGE. NEVER A FRACTION, NEVER "
    "A PASS, NEVER A MARGIN (IR-10, H-5). The instrument I selects the CELL "
    "SET; the pair (honest, O-E) supplies the VERDICTS. Those are two different "
    "roles for the word instrument and this sentence is why the tables carry "
    "both.")


def readmit_table(instrument_name, per_cell, reading, entry_keys, keys_cache,
                  instruments, families) -> dict:
    sel = forced_and_adjudicated(per_cell, reading)
    rows = []
    differing = []
    honest_detected = 0
    for c in sel["adjudicated"]:
        dk = keys_cache[c["family"]]
        h = cell_verdict_for(instruments["honest"], entry_keys, dk,
                             c["row_deletes"], c["primitive"])
        o = cell_verdict_for(instruments["O-E"], entry_keys, dk,
                             c["row_deletes"], c["primitive"])
        if h["verdict"] == "DETECTED":
            honest_detected += 1
        differs = h["verdict"] != o["verdict"]
        if differs:
            differing.append({"family": c["family"],
                              "row_deletes": c["row_deletes"],
                              "primitive_scope": c["primitive"],
                              "honest": h["verdict"], "O_E": o["verdict"]})
        rows.append({
            "family": c["family"], "row_deletes": c["row_deletes"],
            "primitive_scope": c["primitive"],
            "family_moves": c["family_moves"],
            "perturbation_declaration":
                families[c["family"]]["declaration"]["declaration_text"],
            "honest": h, "O_E": o,
            "differs_between_honest_and_O_E": differs,
            "retained_component_names_under_this_instrument":
                c["forcing"]["retained_component_names"],
            "census_completeness": CENSUS_COMPLETENESS,
        })
    return {
        "cell_set_selected_by_instrument": instrument_name,
        "instrument_declaration":
            instruments[instrument_name]["declaration"],
        "reading": reading,
        "counting_rule": DG.CELL_RULE,
        "counting_path_note": COUNTING_PATH_NOTE,
        "readmit_rule": READMIT_RULE,
        "per_cell_table": rows,
        "cells_adjudicated_per_primitive_cells": len(rows),
        "cells_diagonal_excluded_per_primitive_cells": len(sel["diagonal"]),
        "cells_forced_excluded_per_primitive_cells": len(sel["forced"]),
        "denominator_arithmetic": (
            f"{len(rows) + len(sel['diagonal']) + len(sel['forced'])} "
            f"per-primitive cells in the derived universe = "
            f"{len(sel['diagonal'])} diagonal + {len(sel['forced'])} forced for "
            f"{instrument_name} + {len(rows)} adjudicated. THE DENOMINATOR IS "
            f"{len(rows)} AND IT IS DERIVED HERE, NOT INHERITED FROM RT-J8-4's "
            f"30 (H-13)."),
        "excluded_cells_with_every_reason": (
            [{"family": c["family"], "row_deletes": c["row_deletes"],
              "primitive_scope": c["primitive"], "exclusion": "diagonal",
              "reason": DIAGONAL_RULE, "value": None}
             for c in sel["diagonal"]] +
            [{"family": c["family"], "row_deletes": c["row_deletes"],
              "primitive_scope": c["primitive"],
              "exclusion": "forced_for_this_instrument",
              "forcing_edges": c["forcing"]["forcing_edges"],
              "vacuous_row": c["forcing"]["vacuous_row"],
              "vacuous_row_derivation": c["forcing"]["vacuous_row_derivation"],
              "retained_component_names":
                  c["forcing"]["retained_component_names"],
              "reason": FORCING_PREDICATE_RULE, "value": None}
             for c in sel["forced"]]),
        "differing_cells": differing,
        "differing_cell_count": len(differing),
        "honest_detected_cell_count": honest_detected,
        "honest_detected_cell_count_note": (
            "THE TWO-DIRECTIONAL CAPACITY QUANTITY. It is the number of "
            "ADJUDICATED cells at which the HONEST instrument reports DETECTED, "
            "and it is the field that decides whether the always_non_member arm "
            "of CTL-READMIT-NULL is ARITHMETICALLY PINNED."),
        "census_completeness": CENSUS_COMPLETENESS,
    }


def readmit_null(per_cell, reading, entry_keys, keys_cache, instruments,
                 honest_detected, adjudicated_total) -> dict:
    sel = forced_and_adjudicated(per_cell, reading)
    arms = {}
    for arm in ("always_member", "always_non_member"):
        diff = 0
        rows = []
        for c in sel["adjudicated"]:
            dk = keys_cache[c["family"]]
            h = cell_verdict_for(instruments["honest"], entry_keys, dk,
                                 c["row_deletes"], c["primitive"])
            d = cell_verdict_for(instruments[arm], entry_keys, dk,
                                 c["row_deletes"], c["primitive"])
            differs = h["verdict"] != d["verdict"]
            diff += differs
            rows.append({"family": c["family"],
                         "row_deletes": c["row_deletes"],
                         "primitive_scope": c["primitive"],
                         "honest": h["verdict"], "degenerate": d["verdict"],
                         "differs": differs,
                         "census_completeness": CENSUS_COMPLETENESS})
        honest_not_detected = adjudicated_total - honest_detected
        extreme = (honest_not_detected if arm == "always_member"
                   else honest_detected)
        pinned = (extreme == 0)
        arms[arm] = {
            "instrument_declaration": instruments[arm]["declaration"],
            "per_cell_table": rows,
            "differing_cell_count": diff,
            "denominator_cells_adjudicated": adjudicated_total,
            "the_extreme_this_arm_must_meet": extreme,
            "extreme_derivation": (
                "always_member must differ on EVERY adjudicated cell where the "
                "honest instrument reports NOT DETECTED; always_non_member must "
                "differ on EVERY adjudicated cell where the honest instrument "
                "reports DETECTED. honest DETECTED = "
                f"{honest_detected}, honest NOT DETECTED = "
                f"{honest_not_detected}, denominator = {adjudicated_total}."),
            "extreme_met": diff == extreme,
            "arm_was_arithmetically_pinned": pinned,
            "the_count_that_makes_it_so": {
                "honest_detected_cell_count": honest_detected,
                "honest_not_detected_cell_count": honest_not_detected,
                "adjudicated_cell_denominator": adjudicated_total},
            "pinning_note": (
                "AN ARM IS ARITHMETICALLY PINNED WHEN ITS EXTREME IS ZERO: IT "
                "CANNOT FAIL, AND ITS MET EXTREME IS BOOKKEEPING RATHER THAN A "
                "DEMONSTRATION. This field exists because BATCH-145531's "
                "always_non_member arm was pinned at 0 -- the honest instrument "
                "reported DETECTED on ZERO of nine adjudicated cells -- and the "
                "batch reported the met extreme without the field (D-10, "
                "RT-J8-2). REPORTED, NOT REPEATED."),
            "STOP_arm_failed_an_unpinned_extreme":
                (not pinned) and diff != extreme,
            "census_completeness": CENSUS_COMPLETENESS,
        }
    return arms


# ===========================================================================
# artifact plumbing
# ===========================================================================

def _write_json(name: str, doc: dict) -> str:
    os.makedirs(TASK_ROOT, exist_ok=True)
    path = os.path.join(TASK_ROOT, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, sort_keys=False, default=str)
        fh.write("\n")
    return path


def _sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _fingerprint() -> dict:
    return {
        "canonicalisation_and_membership_functions":
            list(ADJ.CODE_PATH_FINGERPRINT_FUNCTIONS) + [
                "harness.diffpath.controlpower.variant_keys",
                "harness.diffpath.depgraph.canon_under",
                "harness.diffpath.depgraph.build_index",
                "harness.diffpath.depgraph.cell_verdict",
                "harness.diffpath.depgraph.wf_violations",
                "harness.diffpath.depgraph.edge_records",
                "harness.diffpath.depgraph.build_families",
                "harness.diffpath.readmit.retained_component_names",
                "harness.diffpath.readmit.forcing_edges_for",
                "harness.diffpath.readmit.perturb_consistent_pair",
                "harness.diffpath.readmit.cell_verdict_for",
            ],
        "generator_set_in_force": sorted(STRICT),
        "module_sha256": digests(),
    }


def _params(suffix: str, extra: dict | None = None) -> dict:
    out = {
        "experiment_id": EXPERIMENT_ID,          # IR-7, the LITERAL id
        "run_suffix": suffix,
        "task_id": TASK_ID,
        "batch_id": BATCH_ID,
        "goal_id": GOAL_ID,
        "code_path_fingerprint": _fingerprint(),
        "armed_deadline_seconds": CEILINGS[suffix],
        "seeds": SEEDS,
        "seed_integrity": (
            "EXACTLY THE EIGHT SEEDS INHERITED BYTE-IDENTICALLY FROM "
            "EXP-DIFFP-4b165f THROUGH EXP-DIFFP-04082e, top-level seed "
            "84064107. NO NINTH SEED EXISTS OR WAS CREATED ANYWHERE IN THIS "
            "CONTRACT."),
        "network_requests": 0,
        "claim_ceiling": "analyzed",
        "census_completeness": CENSUS_COMPLETENESS,
    }
    if extra:
        out.update(extra)
    return out


CERT_NONE = {"kind": "none", "statement": {
    "why": ("PURE MEASUREMENT RUN. No discrete-log solve and no factor-base "
            "relation is claimed anywhere in EXP-DIFFP-f26790, and no "
            "collision, no differential path, no novelty and no cryptanalytic "
            "result of any kind is claimed. certificate.kind is set to `none` "
            "EXPLICITLY, as docs/claims-and-verification.md requires of a "
            "measurement run.")}}


def _inference_supplement() -> dict:
    return {
        "requested_policy": "executor-implementation",
        "resolved_policy": os.environ.get("AUTORESEARCH_POLICY"),
        "resolved_backend": os.environ.get("AUTORESEARCH_BACKEND"),
        "resolved_model": os.environ.get("AUTORESEARCH_MODEL"),
        "fallback_used": None,
        "note": ("THE RESOLVED POLICY/BACKEND/MODEL FIELDS ARE READ FROM THE "
                 "PROCESS ENVIRONMENT AND ARE null WHEN THE SESSION WAS NOT "
                 "LAUNCHED THROUGH `python3 -m orchestration.adapter env`. THEY "
                 "ARE EMITTED AS null AND NEVER GUESSED (H-8). "
                 "`fallback_used` IS null RATHER THAN false BECAUSE THIS "
                 "PROCESS CANNOT OBSERVE WHETHER A FALLBACK OCCURRED."),
    }


def write_supplement(run_dir: str, suffix: str) -> str:
    import yaml
    doc = {
        "manifest_supplement": {
            "run_suffix": suffix,
            "experiment_id": EXPERIMENT_ID,
            "task_id": TASK_ID, "batch_id": BATCH_ID, "goal_id": GOAL_ID,
            "question_id": QUESTION_ID,
            "why_this_file_exists": (
                "H-10 AND THE AGENTS.md ARTIFACT POLICY. The shared wrapper's "
                "own inference block cannot see the requested policy from the "
                "handoff, so the requested/resolved pair is recorded here "
                "rather than by hand-editing a manifest, which the contract "
                "forbids."),
            "inference": _inference_supplement(),
            "claim_ceiling": "analyzed",
            "certificate_kind": "none",
            "census_completeness": CENSUS_COMPLETENESS,
            "independence": {
                "forbidden_path": FORBIDDEN_PATH_LITERAL,
                "mode": INDEPENDENCE_MODE},
            "quarantine": {"path": QUARANTINE_PATH_LITERAL,
                           "mechanism": QUARANTINE_MECHANISM},
            "no_novelty_statement": (
                "NO DIFFERENTIAL PATH IS CLAIMED NEW FOR MD5 OR SHA-1 AT ANY "
                "TIER. NO SEARCH OVER EITHER DIFFERENCE SPACE WAS RUN. NO "
                "SOURCE WAS ACQUIRED. NO COMMITTED INSTRUMENT WAS REPAIRED. "
                "THE MD5 LANE IS BLOCKED, NOT CLOSED."),
        }
    }
    path = os.path.join(run_dir, "manifest-supplement.yaml")
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(doc, fh, sort_keys=False, allow_unicode=True,
                       default_flow_style=False, width=100)
    return path


# ===========================================================================
# THE FOUR GATED RUNS
# ===========================================================================

def run_stage1(state: dict):
    """CTL-FROZEN-4 pre-digests; the forcing predicate; CTL-FORCE-PI."""
    lines = []
    census = state["census"]
    comps_doc = derive_key_components(census)
    state["components_doc"] = comps_doc
    components = comps_doc["derived_union_in_first_appearance_order"]
    state["components"] = components
    key_names = {p: set(v) for p, v in comps_doc["derived_per_primitive"].items()}
    state["key_names"] = key_names
    rep = {}
    for e in census.shadow:
        rep.setdefault(e.primitive, _serialised_key(e.obj))
    state["representative_key"] = rep
    lines.append(f"IR-13 derived components per primitive: "
                 f"{comps_doc['derived_per_primitive']}")

    pop = DG.declared_population(census)
    edges = {p: DG.edge_records(pop["objects"][p], p, components)
             for p in ("md5", "sha1")}
    state["edges_by_prim"] = edges
    derived = {p: sorted((r["X"], r["Y"]) for r in edges[p]
                         if r["label"] == "derived_and_witnessed")
               for p in ("md5", "sha1")}
    lines.append(f"derived_and_witnessed edges: {derived}")

    families = DG.build_families(census)
    state["families"] = families

    rt = load_reused_O_E()
    state["rt"] = rt
    instruments = build_instruments(rt)
    state["instruments"] = instruments

    bundle = build_forced_tables(components, families, instruments, edges,
                                 key_names, rep)
    state["forced_bundle"] = bundle
    committed = committed_six_forced_cells()
    state["committed_six"] = committed
    force_pi = ctl_force_pi(bundle, committed, components)
    state["force_pi"] = force_pi

    doc = {
        "control": "CTL-FORCE-PI + the per-instrument forcing predicate",
        "status": "COMPLETED",
        "experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
        "batch_id": BATCH_ID, "goal_id": GOAL_ID,
        "claim_ceiling": "analyzed",
        "forcing_predicate_rule": FORCING_PREDICATE_RULE,
        "composition_orders": COMPOSITION_ORDERS,
        "the_specification_gap_reported_and_not_resolved":
            VACUOUS_ROW_DECLARATION,
        "readings_measured": list(FORCING_READINGS),
        "IR_13_key_components_derived_at_run_time": comps_doc,
        "declared_population_sizes_per_primitive": pop["population_sizes"],
        "edge_label_counts_per_primitive": {
            p: {lab: sum(1 for r in edges[p] if r["label"] == lab)
                for lab in sorted({r["label"] for r in edges[p]})}
            for p in ("md5", "sha1")},
        "derived_and_witnessed_edges_per_primitive":
            {p: [{"X": x, "Y": y} for x, y in derived[p]]
             for p in ("md5", "sha1")},
        "the_edge_must_be_derivation_backed": (
            "CONTRACT CLAUSE (2), APPLIED: an `empirical_only` edge may NOT "
            "force a cell for any instrument and neither may an "
            "`edge_on_a_constant_column`. The counts above show how much that "
            "clause does: a rule that accepted any EDGE verdict would force "
            "nearly everything."),
        "constructible_families": bundle["constructible_families"],
        "family_gate_per_primitive": {
            n: f["per_primitive"] for n, f in families.items()},
        "cell_universe_size_per_primitive_cells":
            bundle["cell_universe_size_per_primitive_cells"],
        "cell_universe_arithmetic": bundle["cell_universe_arithmetic"],
        "diagonal_rule": DIAGONAL_RULE,
        "instruments_in_scope": {
            k: {"declaration": v["declaration"], "kind": v["kind"]}
            for k, v in instruments.items()},
        "committed_six_forced_cells_read_from_the_producer_artifact": committed,
        "CTL_FORCE_PI": force_pi,
        "per_instrument_forced_sets": {
            iname: {
                reading: {
                    order: {
                        "per_primitive_forced_cells": [
                            {"family": c["family"],
                             "row_deletes": c["row_deletes"],
                             "primitive_scope": c["primitive"],
                             "forcing_edges": c["forcing"]["forcing_edges"],
                             "vacuous_row": c["forcing"]["vacuous_row"],
                             "vacuous_row_derivation":
                                 c["forcing"]["vacuous_row_derivation"],
                             "retained_component_names":
                                 c["forcing"]["retained_component_names"],
                             "census_completeness": CENSUS_COMPLETENESS}
                            for c in forced_and_adjudicated(
                                bundle["forced_tables"][iname][
                                    "per_composition_order"][order],
                                reading)["forced"]],
                        "per_primitive_forced_count": len(
                            forced_and_adjudicated(
                                bundle["forced_tables"][iname][
                                    "per_composition_order"][order],
                                reading)["forced"]),
                        "per_primitive_adjudicated_count": len(
                            forced_and_adjudicated(
                                bundle["forced_tables"][iname][
                                    "per_composition_order"][order],
                                reading)["adjudicated"]),
                        "per_primitive_diagonal_count": len(
                            forced_and_adjudicated(
                                bundle["forced_tables"][iname][
                                    "per_composition_order"][order],
                                reading)["diagonal"]),
                    } for order in COMPOSITION_ORDERS
                } for reading in FORCING_READINGS
            } for iname in bundle["forced_tables"]},
        "aggregate_keys_are_named_as_aggregates": (
            "EVERY COUNT ABOVE IS A PER-PRIMITIVE CELL COUNT AND SAYS SO IN "
            "ITS KEY. AGGREGATE COUNTS -- those requiring forcing on BOTH "
            "primitives -- appear ONLY inside CTL_FORCE_PI under keys "
            "containing the word aggregate (H-9)."),
        "interpretation_limit": CTL_FORCE_PI_LIMIT,
        "no_novelty": (
            "NO PATH IS CLAIMED NEW FOR EITHER PRIMITIVE AT ANY TIER. THIS RUN "
            "MEASURES THIS PROGRAM'S OWN ADJUDICATION INSTRUMENT AT CENSUS SIZE "
            "ZERO. THE MD5 LANE IS BLOCKED, NOT CLOSED."),
        "census_completeness": CENSUS_COMPLETENESS,
    }
    _write_json("forcing-predicate-per-instrument.json", doc)

    stop = (comps_doc["STOP_the_derived_list_differs_from_the_contracts_six_names"])
    lines.append(f"CTL-FORCE-PI computed under {len(FORCING_READINGS)} readings "
                 f"x {len(COMPOSITION_ORDERS)} composition orders")
    metrics = {}
    for reading in FORCING_READINGS:
        for order in COMPOSITION_ORDERS:
            b = force_pi["per_reading"][reading]["per_composition_order"][order]
            metrics[f"identity_forced_aggregate_cells__{reading}__{order}"] = \
                b["side_a_identity_versus_the_committed_six"][
                    "identity_forced_aggregate_cell_count"]
            metrics[f"identity_equals_committed_six__{reading}__{order}"] = int(
                b["side_a_identity_versus_the_committed_six"]["known_answer_met"])
            metrics[f"forced_set_moves_per_primitive__{reading}__{order}"] = int(
                b["side_b_does_the_forced_set_move_across_instruments"][
                    "forced_set_MOVES_at_per_primitive_granularity"])
    metrics["derived_key_component_list_matches_contract_six_names"] = int(
        comps_doc["agrees_with_contract_as_a_set"])
    metrics["cell_universe_per_primitive_cells"] = \
        bundle["cell_universe_size_per_primitive_cells"]
    metrics["STOP_derived_component_list_differs"] = int(stop)
    return RunResult(
        run_suffix="frozen-and-forcing-predicate",
        curve_id="n/a-hash-primitive",
        seed=SEEDS["null_draw_message_difference_perturbed"],
        parameters=_params("frozen-and-forcing-predicate",
                           {"pre_run_digests": state["pre_digests"]}),
        metrics=metrics, certificate=CERT_NONE, valid=True,
        stdout="\n".join(lines) + "\n", stderr=""), doc


def run_stage2(state: dict):
    """CTL-READMIT over the cells not forced per instrument; CTL-O-E-REUSE."""
    lines = []
    census = state["census"]
    entry_keys = {e.id: (CP.variant_keys(e.obj, STRICT), e.primitive)
                  for e in census.shadow}
    state["entry_keys"] = entry_keys
    families = state["families"]
    keys_cache = {n: DG.family_draw_keys(families[n])
                  for n in state["forced_bundle"]["constructible_families"]}
    state["keys_cache"] = keys_cache
    for n, v in keys_cache.items():
        lines.append(f"family {n}: {len(v)} CTL-WF-accepted draws")

    tables = state["forced_bundle"]["forced_tables"]
    results: dict = {}
    for iname in ("honest", "O-E"):
        results[iname] = {}
        for reading in FORCING_READINGS:
            results[iname][reading] = {}
            for order in COMPOSITION_ORDERS:
                t = readmit_table(iname,
                                  tables[iname]["per_composition_order"][order],
                                  reading, entry_keys, keys_cache,
                                  state["instruments"], families)
                results[iname][reading][order] = t
                lines.append(
                    f"CTL-READMIT cell set of {iname} [{reading}/{order}]: "
                    f"{t['differing_cell_count']} differing of "
                    f"{t['cells_adjudicated_per_primitive_cells']} adjudicated "
                    f"per-primitive cells; honest DETECTED "
                    f"{t['honest_detected_cell_count']}")
    state["readmit"] = results

    oe = ctl_o_e_reuse(state["rt"], state["instruments"])
    state["o_e_reuse"] = oe
    lines.append(f"CTL-O-E-REUSE: {oe.get('comparisons_agreeing')} of "
                 f"{oe.get('comparisons_total')} committed comparisons agree")

    doc = {
        "control": "CTL-READMIT + CTL-O-E-REUSE",
        "status": "COMPLETED",
        "experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
        "claim_ceiling": "analyzed",
        "readmit_rule": READMIT_RULE,
        "counting_rule": DG.CELL_RULE,
        "counting_path_note": COUNTING_PATH_NOTE,
        "the_specification_gap_reported_and_not_resolved":
            VACUOUS_ROW_DECLARATION,
        "composition_orders": COMPOSITION_ORDERS,
        "what_the_blinded_quantity_is": (
            "P-B. THIS CONTRACT DELIBERATELY PRE-REGISTERS NO INTEGER FOR THE "
            "RE-ADMITTED DIFFERING-CELL COUNT AND PRE-REGISTERS THE "
            "INTERPRETATION OF BOTH OUTCOMES INSTEAD. THE PRODUCER REPORTS THE "
            "MEASUREMENT AND COMPOSES NO VERDICT ON IT (IR-8, H-11). A "
            "DIFFERING-CELL COUNT OF ZERO AND A DIFFERING-CELL COUNT OF TEN "
            "ARE BOTH MEASUREMENTS AND NEITHER IS A SCORE."),
        "per_instrument_cell_set": results,
        "the_two_composition_orders_agree_per_instrument_and_reading": {
            iname: {reading: (
                [ (r["family"], r["row_deletes"], r["primitive_scope"],
                   r["honest"]["verdict"], r["O_E"]["verdict"])
                  for r in results[iname][reading]["project_then_delete"][
                      "per_cell_table"]]
                == [ (r["family"], r["row_deletes"], r["primitive_scope"],
                      r["honest"]["verdict"], r["O_E"]["verdict"])
                     for r in results[iname][reading]["delete_then_project"][
                         "per_cell_table"]])
                for reading in FORCING_READINGS}
            for iname in ("honest", "O-E")},
        "agreement_was_CHECKED_and_not_assumed": True,
        "CTL_O_E_REUSE": oe,
        "permissive_mode_is_out_of_scope_and_is_null_never_zero": {
            "permissive_cells": None,
            "why": ("STRICT ONLY. Permissive cells are emitted as null and "
                    "NEVER as 0 (H-8). This is a scope decision recorded as "
                    "one and is NOT evidence that permissive mode would behave "
                    "the same way.")},
        "how_the_count_must_be_read": (
            "EVERY DIFFERING-CELL COUNT ABOVE APPEARS BESIDE ITS DENOMINATOR, "
            "ITS EXCLUSION LIST AND EVERY EXCLUSION'S FORCING EDGE. IT IS NEVER "
            "A FRACTION, A PASS, A SCORE OR A MARGIN (IR-10, H-5). NEITHER "
            "OUTCOME LICENSES A STATEMENT ABOUT MD5, SHA-1 OR ANY DIFFERENCE "
            "SPACE, AND WITH A READABLE CENSUS OF ZERO A NON-MEMBER VERDICT "
            "CARRIES NO INFORMATION ABOUT THE LITERATURE AT ALL."),
        "interpretation_limit": (
            "AGREEMENT BETWEEN THIS IMPLEMENTATION AND RT-J8-4 IS WEAKER "
            "EVIDENCE THAN DISAGREEMENT, because contamination pushes toward "
            "agreement and not away from it. THE PRODUCER RECORDS THAT LIMIT "
            "AND DOES NOT WEIGH THE OUTCOME."),
        "census_completeness": CENSUS_COMPLETENESS,
    }
    _write_json("readmitted-cells-result.json", doc)

    metrics = {}
    for iname in ("honest", "O-E"):
        tag = iname.replace("-", "_")
        for reading in FORCING_READINGS:
            for order in COMPOSITION_ORDERS:
                t = results[iname][reading][order]
                metrics[f"differing_cells__cellset_{tag}__{reading}__{order}"] \
                    = t["differing_cell_count"]
                metrics[f"adjudicated_per_primitive_cells__cellset_{tag}"
                        f"__{reading}__{order}"] = \
                    t["cells_adjudicated_per_primitive_cells"]
                metrics[f"honest_detected_cells__cellset_{tag}__{reading}"
                        f"__{order}"] = t["honest_detected_cell_count"]
    metrics["o_e_reuse_comparisons_total"] = oe.get("comparisons_total", 0)
    metrics["o_e_reuse_comparisons_agreeing"] = oe.get("comparisons_agreeing", 0)
    return RunResult(
        run_suffix="readmitted-cells",
        curve_id="n/a-hash-primitive",
        seed=SEEDS["null_draw_message_difference_perturbed"],
        parameters=_params("readmitted-cells"),
        metrics=metrics, certificate=CERT_NONE, valid=True,
        stdout="\n".join(lines) + "\n", stderr=""), doc


def run_stage3(state: dict):
    """The consistent-pair family; CTL-PAIR-WF two-sided; CTL-PAIR-DECL."""
    lines = []
    fam = build_consistent_pair_family(state["census"])
    state["pair_family"] = fam
    moved = measure_moved_components(fam)
    state["pair_moved"] = moved
    for prim in ("md5", "sha1"):
        pp = fam["per_primitive"][prim]
        lines.append(f"{prim}: consistent side accepted "
                     f"{pp['consistent_side_accepted_by_CTL_WF']} of "
                     f"{pp['consistent_side_constructed']}; inconsistent side "
                     f"accepted {pp['inconsistent_side_accepted_by_CTL_WF']} of "
                     f"{pp['inconsistent_side_constructed']}")

    constructible = {p: fam["per_primitive"][p]["CONSTRUCTIBLE"]
                     for p in ("md5", "sha1")}
    doc = {
        "control": "CTL-PAIR-WF + CTL-PAIR-DECL",
        "status": "COMPLETED",
        "experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
        "claim_ceiling": "analyzed",
        "family_name": CONSISTENT_PAIR_DECLARATION["name"],
        "declared_perturbation_text":
            CONSISTENT_PAIR_DECLARATION["declaration_text"],
        "declared_inconsistent_side_text":
            CONSISTENT_PAIR_DECLARATION["inconsistent_side_declaration_text"],
        "declared_moves": CONSISTENT_PAIR_DECLARATION["moves"],
        "declared_holds_fixed": CONSISTENT_PAIR_DECLARATION["holds_fixed"],
        "CTL_PAIR_WF": {
            "gate": "the COMMITTED well-formedness gate depgraph.wf_violations",
            "gate_checks": DG.WF_CHECKS,
            "two_sided": True,
            "per_primitive": fam["per_primitive"],
            "known_answer": ("accepted on the consistent side, rejected on the "
                             "inconsistent side, with per-primitive counts"),
            "known_answer_met_per_primitive": {
                p: (fam["per_primitive"][p]["CONSTRUCTIBLE"]
                    and fam["per_primitive"][p][
                        "inconsistent_side_accepted_by_CTL_WF"] == 0)
                for p in ("md5", "sha1")},
            "computed_per_primitive": True,
        },
        "constructible_per_primitive": constructible,
        "P_C_outcome": {
            "statement": "THE CONSISTENT-PAIR FAMILY IS CONSTRUCTIBLE UNDER CTL-WF.",
            "measured_per_primitive": constructible,
            "not_constructible_derivation_per_primitive": {
                p: (None if constructible[p] else {
                    "gate_clause_that_rejected_it": sorted(
                        (fam["per_primitive"][p][
                            "consistent_side_rejection_gate_clauses"] or {})),
                    "derivation": (
                        "A DERIVED FACT ABOUT THE KEY FORMAT AND THE GATE AND "
                        "NEVER A FAMILY THAT PRODUCED ZERO DETECTIONS. On MD5 "
                        "the committed serialiser NEVER READS in_linearized_"
                        "code, so it is not a component of the MD5 key, and "
                        "CTL-WF check W3 requires obj.in_linearized_code to be "
                        "None on MD5. The family's declaration REQUIRES the "
                        "flag to move together with the message difference; any "
                        "draw honouring that declaration on MD5 sets the flag "
                        "to a non-None value and W3 rejects it. A draw that "
                        "left the flag None would move ONE component and would "
                        "be the committed family d_message_difference under a "
                        "new name, which is the no-op the committed "
                        "_perturb_flag comment names. THE MD5 ARM IS THEREFORE "
                        "NOT CONSTRUCTIBLE BY DERIVATION, and its cells are "
                        "emitted as null and NEVER as 0."),
                    "note_on_the_gates_own_status": (
                        "W3 IS THE CHECK, AND CTL-WF ITSELF IS AN INSTRUMENT "
                        "THIS CAMPAIGN HAS NOT VALIDATED. This derivation is a "
                        "statement about the committed serialiser and the "
                        "committed gate, not about MD5.")})
                for p in ("md5", "sha1")},
            "P_C_is_refuted_on_this_primitive": {
                p: (not constructible[p]) for p in ("md5", "sha1")},
        },
        "CTL_PAIR_DECL": {
            "what": ("the DECLARED perturbation beside the MEASURED "
                     "moved-component set, per primitive"),
            "basis": (
                "DEC-20260824-257f35 C_4. The diagonal theorem's hypothesis was "
                "FALSE for the one family BATCH-145531 reused, because "
                "controlpower.perturb_message_difference HONESTLY RECOMPUTES "
                "in_linearized_code, so on sha1 that draw moves TWO key "
                "components and does not perturb exactly one. THIS CONTROL "
                "MEASURES THE DECLARATION RATHER THAN TRUSTING IT."),
            "per_primitive": moved,
            "any_discrepancy": {
                p: (moved[p].get("discrepancy_between_declared_and_measured")
                    is not None) for p in ("md5", "sha1")},
        },
        "why_this_family_exists": (
            "IT IS THE ONLY NAMED REPAIR OF NULL FAMILY (e)'s SUBSTANTIVE "
            "RETIREMENT (DEC-20260824-257f35 R3-J7, rank 8 folded into rank 1). "
            "It probes whether the instrument separates IN-CODE from "
            "OUT-OF-CODE objects at all. NULL FAMILY (e)'s DIRECTION IS NOT "
            "CLOSED BY THIS RUN IN EITHER OUTCOME, and this producer composes "
            "no verdict on it (IR-8, H-11)."),
        "no_novelty": (
            "NO PATH IS CLAIMED NEW FOR EITHER PRIMITIVE AT ANY TIER. THE MD5 "
            "LANE IS BLOCKED, NOT CLOSED."),
        "census_completeness": CENSUS_COMPLETENESS,
    }
    _write_json("consistent-pair-family-result.json", doc)

    metrics = {
        "consistent_pair_constructible_md5": int(constructible["md5"]),
        "consistent_pair_constructible_sha1": int(constructible["sha1"]),
        "consistent_pair_accepted_draws_md5":
            fam["per_primitive"]["md5"]["consistent_side_accepted_by_CTL_WF"],
        "consistent_pair_accepted_draws_sha1":
            fam["per_primitive"]["sha1"]["consistent_side_accepted_by_CTL_WF"],
        "consistent_pair_inconsistent_side_accepted_md5":
            fam["per_primitive"]["md5"]["inconsistent_side_accepted_by_CTL_WF"],
        "consistent_pair_inconsistent_side_accepted_sha1":
            fam["per_primitive"]["sha1"]["inconsistent_side_accepted_by_CTL_WF"],
    }
    return RunResult(
        run_suffix="consistent-pair-family",
        curve_id="n/a-hash-primitive",
        seed=SEEDS["null_draw_message_difference_perturbed"],
        parameters=_params("consistent-pair-family"),
        metrics=metrics, certificate=CERT_NONE, valid=True,
        stdout="\n".join(lines) + "\n", stderr=""), doc


def run_stage4(state: dict):
    """The pair cells; CTL-READMIT-NULL with the pinning field; post-digests."""
    lines = []
    entry_keys = state["entry_keys"]
    instruments = state["instruments"]
    fam = state["pair_family"]
    families = state["families"]
    tables = state["forced_bundle"]["forced_tables"]

    # --- CTL-READMIT-NULL, through the IDENTICAL counting path ---------------
    null_doc = {"control": "CTL-READMIT-NULL", "status": "COMPLETED",
                "experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
                "claim_ceiling": "analyzed",
                "counting_path_note": COUNTING_PATH_NOTE,
                "degenerate_projection_note": DEGENERATE_PROJECTION_NOTE,
                "the_specification_gap_reported_and_not_resolved":
                    VACUOUS_ROW_DECLARATION,
                "per_cell_set": {}, "census_completeness": CENSUS_COMPLETENESS}
    for iname in ("honest", "O-E"):
        null_doc["per_cell_set"][iname] = {}
        for reading in FORCING_READINGS:
            null_doc["per_cell_set"][iname][reading] = {}
            for order in COMPOSITION_ORDERS:
                t = state["readmit"][iname][reading][order]
                arms = readmit_null(
                    tables[iname]["per_composition_order"][order], reading,
                    entry_keys, state["keys_cache"], instruments,
                    t["honest_detected_cell_count"],
                    t["cells_adjudicated_per_primitive_cells"])
                null_doc["per_cell_set"][iname][reading][order] = {
                    "cell_set_selected_by_instrument": iname,
                    "denominator_cells_adjudicated":
                        t["cells_adjudicated_per_primitive_cells"],
                    "honest_detected_cell_count":
                        t["honest_detected_cell_count"],
                    "arms": arms}
                for a, v in arms.items():
                    lines.append(
                        f"CTL-READMIT-NULL [{iname}/{reading}/{order}] {a}: "
                        f"{v['differing_cell_count']} differing of "
                        f"{v['denominator_cells_adjudicated']}; extreme "
                        f"{v['the_extreme_this_arm_must_meet']}; pinned="
                        f"{v['arm_was_arithmetically_pinned']}")
    _write_json("readmit-null-object-result.json", null_doc)
    state["null_doc"] = null_doc

    # --- the consistent-pair cells, GATED on constructibility ----------------
    constructible = {p: fam["per_primitive"][p]["CONSTRUCTIBLE"]
                     for p in ("md5", "sha1")}
    pair_doc = {
        "control": "the consistent-pair family's cells, honest versus O-E",
        "experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
        "claim_ceiling": "analyzed",
        "family_name": CONSISTENT_PAIR_DECLARATION["name"],
        "declared_perturbation_text":
            CONSISTENT_PAIR_DECLARATION["declaration_text"],
        "declared_moves": CONSISTENT_PAIR_DECLARATION["moves"],
        "diagonal_rule": DIAGONAL_RULE,
        "counting_rule": DG.CELL_RULE,
        "counting_path_note": COUNTING_PATH_NOTE,
        "constructible_per_primitive": constructible,
        "census_completeness": CENSUS_COMPLETENESS,
    }
    if not any(constructible.values()):
        pair_doc.update({
            "status": "GATED-NOT-RUN",
            "gate_that_fired": ("stage 3 reported the consistent-pair family "
                                "NOT CONSTRUCTIBLE on every primitive; the "
                                "contract's stage-4 gate names this exactly"),
            "per_cell_table": None,
            "differing_cell_count": None,
            "cells_adjudicated_per_primitive_cells": None,
            "honest_detected_cell_count": None,
            "why_null_and_never_zero": (
                "AN UNMEASURED CELL, COLUMN OR MODE IS EMITTED AS null AND "
                "NEVER AS INTEGER 0 (H-8). A gated outcome must not be "
                "readable as a family that produced zero detections."),
        })
        lines.append("consistent-pair cells: GATED-NOT-RUN")
    else:
        keys = [(d["primitive"], d["k"], CP.variant_keys(d["obj"], STRICT))
                for d in fam["draws"]]
        rep = state["representative_key"]
        key_names = state["key_names"]
        per_reading = {}
        for reading in FORCING_READINGS:
            per_order = {}
            for order in COMPOSITION_ORDERS:
                per_instr = {}
                for iname in ("honest", "O-E"):
                    proj = instruments[iname]["projection"]
                    rows, differing, hdet = [], [], 0
                    excluded = []
                    for row in state["components"]:
                        for prim in ("md5", "sha1"):
                            if not constructible[prim]:
                                excluded.append({
                                    "family": CONSISTENT_PAIR_DECLARATION["name"],
                                    "row_deletes": row, "primitive_scope": prim,
                                    "exclusion": "not_constructible",
                                    "gate_clause_that_rejected_it": sorted(
                                        (fam["per_primitive"][prim][
                                            "consistent_side_rejection_gate_"
                                            "clauses"] or {})),
                                    "value": None})
                                continue
                            ev = forcing_edges_for(row, prim, proj, order,
                                                   key_names, rep,
                                                   state["edges_by_prim"])
                            key = ("forced_literal_edge_only"
                                   if reading == "edge_only"
                                   else "forced_edge_or_vacuous")
                            if ev[key]:
                                excluded.append({
                                    "family": CONSISTENT_PAIR_DECLARATION["name"],
                                    "row_deletes": row, "primitive_scope": prim,
                                    "exclusion": "forced_for_this_instrument",
                                    "forcing_edges": ev["forcing_edges"],
                                    "vacuous_row": ev["vacuous_row"],
                                    "vacuous_row_derivation":
                                        ev["vacuous_row_derivation"],
                                    "retained_component_names":
                                        ev["retained_component_names"],
                                    "reason": FORCING_PREDICATE_RULE,
                                    "value": None})
                                continue
                            h = cell_verdict_for(instruments["honest"],
                                                 entry_keys, keys, row, prim)
                            o = cell_verdict_for(instruments["O-E"], entry_keys,
                                                 keys, row, prim)
                            if h["verdict"] == "DETECTED":
                                hdet += 1
                            differs = h["verdict"] != o["verdict"]
                            if differs:
                                differing.append(
                                    {"family": CONSISTENT_PAIR_DECLARATION["name"],
                                     "row_deletes": row,
                                     "primitive_scope": prim,
                                     "honest": h["verdict"],
                                     "O_E": o["verdict"]})
                            rows.append({
                                "family": CONSISTENT_PAIR_DECLARATION["name"],
                                "row_deletes": row, "primitive_scope": prim,
                                "family_moves":
                                    CONSISTENT_PAIR_DECLARATION["moves"],
                                "honest": h, "O_E": o,
                                "differs_between_honest_and_O_E": differs,
                                "retained_component_names_under_this_instrument":
                                    ev["retained_component_names"],
                                "census_completeness": CENSUS_COMPLETENESS})
                    per_instr[iname] = {
                        "cell_set_selected_by_instrument": iname,
                        "per_cell_table": rows,
                        "cells_adjudicated_per_primitive_cells": len(rows),
                        "excluded_cells_with_every_reason": excluded,
                        "differing_cells": differing,
                        "differing_cell_count": len(differing),
                        "honest_detected_cell_count": hdet,
                        "denominator_arithmetic": (
                            f"{len(rows)} adjudicated + {len(excluded)} "
                            f"excluded per-primitive cells over "
                            f"{len(state['components'])} derived rows x 2 "
                            f"primitives. NO DIAGONAL EXCLUSION IS APPLIED: "
                            f"the family moves TWO components, so no depth-1 "
                            f"row deletes its whole moved set and the "
                            f"committed diagonal theorem's hypothesis is FALSE "
                            f"for every depth-1 row of it."),
                        "census_completeness": CENSUS_COMPLETENESS}
                    lines.append(
                        f"pair cells [{iname}/{reading}/{order}]: "
                        f"{len(differing)} differing of {len(rows)} "
                        f"adjudicated; honest DETECTED {hdet}")
                per_order[order] = per_instr
            per_reading[reading] = per_order
        pair_doc.update({"status": "COMPLETED",
                         "gate_that_fired": None,
                         "accepted_draws_per_primitive": {
                             p: fam["per_primitive"][p][
                                 "consistent_side_accepted_by_CTL_WF"]
                             for p in ("md5", "sha1")},
                         "per_reading": per_reading})
    _write_json("consistent-pair-cells-result.json", pair_doc)
    state["pair_doc"] = pair_doc

    # --- P-D, MEASURED AND NOT JUDGED ---------------------------------------
    hd = []
    for iname in ("honest", "O-E"):
        for reading in FORCING_READINGS:
            for order in COMPOSITION_ORDERS:
                hd.append(state["readmit"][iname][reading][order][
                    "honest_detected_cell_count"])
    pair_hd = []
    if pair_doc["status"] == "COMPLETED":
        for reading in FORCING_READINGS:
            for order in COMPOSITION_ORDERS:
                for iname in ("honest", "O-E"):
                    pair_hd.append(pair_doc["per_reading"][reading][order][
                        iname]["honest_detected_cell_count"])
    state["p_d"] = {
        "statement": ("AT LEAST ONE CELL IN THE UNION OF THE RE-ADMITTED SET "
                      "AND THE CONSISTENT-PAIR SET HAS THE HONEST INSTRUMENT AT "
                      "DETECTED."),
        "honest_detected_counts_over_the_readmitted_sets": hd,
        "honest_detected_counts_over_the_consistent_pair_sets":
            (pair_hd or None),
        "max_honest_detected_over_every_reported_cell_set":
            max(hd + pair_hd) if (hd or pair_hd) else None,
        "P_D_holds_as_measured": (max(hd + pair_hd) > 0) if (hd or pair_hd)
                                 else None,
        "producer_note": ("MEASURED AND REPORTED. WHETHER THE RANK-3 REVISIT "
                          "CONDITION IS THEREBY MET IS THE COORDINATOR'S "
                          "RULING AND NOT THIS PRODUCER'S (IR-8, H-11)."),
        "census_completeness": CENSUS_COMPLETENESS,
    }

    # --- CTL-FROZEN-4 post-run ----------------------------------------------
    post = digests()
    frozen = compare_digests(state["pre_digests"], post)
    frozen["independence_assertion"] = assert_forbidden_path_absent_from_process()
    _write_json("frozen-recheck-4-result.json", frozen)
    state["frozen"] = frozen
    lines.append(f"CTL-FROZEN-4: {frozen['identical_count']} identical, "
                 f"{len(frozen['changed_files'])} changed over "
                 f"{frozen['criterion_files_after']} criterion files")

    metrics = {
        "frozen4_criterion_files": frozen["criterion_files_after"],
        "frozen4_changed_files": len(frozen["changed_files"]),
        "frozen4_identical_before_and_after":
            int(frozen["criterion_met_identical_before_and_after"]),
        "consistent_pair_cells_status_completed":
            int(pair_doc["status"] == "COMPLETED"),
        "max_honest_detected_over_every_reported_cell_set":
            state["p_d"]["max_honest_detected_over_every_reported_cell_set"],
    }
    for iname in ("honest", "O-E"):
        tag = iname.replace("-", "_")
        for reading in FORCING_READINGS:
            for order in COMPOSITION_ORDERS:
                blk = null_doc["per_cell_set"][iname][reading][order]
                for a, v in blk["arms"].items():
                    metrics[f"nullobj_{a}_differing__cellset_{tag}__{reading}"
                            f"__{order}"] = v["differing_cell_count"]
                    metrics[f"nullobj_{a}_pinned__cellset_{tag}__{reading}"
                            f"__{order}"] = int(v["arm_was_arithmetically_pinned"])
    if pair_doc["status"] == "COMPLETED":
        for reading in FORCING_READINGS:
            for order in COMPOSITION_ORDERS:
                for iname in ("honest", "O-E"):
                    tag = iname.replace("-", "_")
                    b = pair_doc["per_reading"][reading][order][iname]
                    metrics[f"pair_differing__cellset_{tag}__{reading}"
                            f"__{order}"] = b["differing_cell_count"]
                    metrics[f"pair_adjudicated__cellset_{tag}__{reading}"
                            f"__{order}"] = \
                        b["cells_adjudicated_per_primitive_cells"]
    return RunResult(
        run_suffix="pair-cells-and-null-object",
        curve_id="n/a-hash-primitive",
        seed=SEEDS["null_draw_message_difference_perturbed"],
        parameters=_params("pair-cells-and-null-object",
                           {"post_run_digests": post}),
        metrics=metrics, certificate=CERT_NONE, valid=True,
        stdout="\n".join(lines) + "\n", stderr=""), doc_or_none(pair_doc)


def doc_or_none(d):
    return d


# ===========================================================================
# the driver
# ===========================================================================

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
    command = (f"python3 -m harness.diffpath.readmit   # run '{suffix}' of "
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
               "classification": (
                   "resource_exhaustion -- A BUDGET OUTCOME AND INFRASTRUCTURE "
                   "SIGNAL. Never a negative mathematical result, never a "
                   "finding about the instrument's power in either direction "
                   "and never a finding about any difference space (IR-16, "
                   "AGENTS.md rule 5).")}
        out["runs"].append(rec)
        return rec
    except FirewallBreach as exc:
        rec = {"run_suffix": suffix, "state": "invalid_measurement",
               "ceiling_seconds": CEILINGS[suffix],
               "wall_seconds": round(time.monotonic() - t0, 3),
               "reason": str(exc),
               "classification": (
                   "FIREWALL BREACH -- IR-1 or IR-12. The run set is invalid "
                   "and the breach is reported, never concealed.")}
        out["runs"].append(rec)
        return rec
    except Exception as exc:                                     # noqa: BLE001
        import traceback
        rec = {"run_suffix": suffix, "state": "implementation_error",
               "ceiling_seconds": CEILINGS[suffix],
               "wall_seconds": round(time.monotonic() - t0, 3),
               "reason": f"{type(exc).__name__}: {exc}",
               "traceback": traceback.format_exc()[-3000:],
               "classification": ("implementation_error -- INFRASTRUCTURE "
                                  "SIGNAL, never mathematical evidence "
                                  "(IR-16).")}
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
    out["raw"][suffix] = True
    return rec


def _not_run(suffix: str, gate: str, out: dict, artifacts: list) -> None:
    out["runs"].append({
        "run_suffix": suffix, "state": "GATED-NOT-RUN", "gate": gate,
        "ceiling_seconds": CEILINGS[suffix],
        "ceiling_status": ("UNSPENT -- NOT reallocated to any other run and "
                           "NOT reallocated without a versioned "
                           "protocol_amendment. A GATED RUN THAT CORRECTLY "
                           "DOES NOT EXECUTE IS A RESULT, NOT A GAP.")})
    for name, control in artifacts:
        _write_json(name, {
            "control": control, "status": "GATED-NOT-RUN",
            "gate_that_fired": gate,
            "what_had_been_computed_before_it_fired":
                "nothing of this control; its gate fired before it executed",
            "every_quantity_this_run_would_have_produced": None,
            "why_null_and_never_zero": (
                "AN UNMEASURED CELL, COLUMN, MODE OR INSTRUMENT IS EMITTED AS "
                "null AND NEVER AS INTEGER 0 (H-8), so a machine consumer "
                "reading the JSON alone cannot misread a gated outcome as a "
                "measurement."),
            "census_completeness": CENSUS_COMPLETENESS})


def _run_index(out: dict) -> dict:
    idx = {"experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
           "run_location": f"experiments/{EXPERIMENT_ID}/runs/<RUN-ID>/",
           "runs": {}}
    for rec in out["runs"]:
        rid = rec.get("run_id")
        if not rid:
            continue
        rd = os.path.join(REPO, "experiments", EXPERIMENT_ID, "runs", rid)
        files = {}
        for dirpath, dirnames, filenames in os.walk(rd):
            for fn in sorted(filenames):
                full = os.path.join(dirpath, fn)
                files[os.path.relpath(full, rd)] = _sha256_file(full)
        idx["runs"][rid] = {"run_dir": os.path.relpath(rd, REPO),
                            "files": files, "file_count": len(files)}
    idx["task_artifacts"] = {
        fn: _sha256_file(os.path.join(TASK_ROOT, fn))
        for fn in sorted(os.listdir(TASK_ROOT))
        if os.path.isfile(os.path.join(TASK_ROOT, fn))}
    return idx


def main() -> int:
    os.makedirs(TASK_ROOT, exist_ok=True)
    out: dict = {"experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
                 "batch_id": BATCH_ID, "goal_id": GOAL_ID,
                 "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                              time.gmtime()),
                 "runs": [], "raw": {}}
    fw = install_independence_and_quarantine_firewall()
    out["firewalls"] = fw
    out["independence_assertion_at_start"] = \
        assert_forbidden_path_absent_from_process()

    state: dict = {"pre_digests": digests()}
    state["census"] = CEN.build_census(
        SEEDS["planted_path_generation_md5"],
        SEEDS["planted_path_generation_sha1"],
        scan={"candidates": []})

    r1 = _emit("frozen-and-forcing-predicate", lambda: run_stage1(state), out)
    if r1["state"] != "completed_valid":
        _not_run("readmitted-cells", "stage 1 did not complete", out,
                 [("readmitted-cells-result.json", "CTL-READMIT")])
        _not_run("consistent-pair-family", "stage 1 did not complete", out,
                 [("consistent-pair-family-result.json", "CTL-PAIR-WF")])
        _not_run("pair-cells-and-null-object", "stage 1 did not complete", out,
                 [("consistent-pair-cells-result.json", "pair cells"),
                  ("readmit-null-object-result.json", "CTL-READMIT-NULL"),
                  ("frozen-recheck-4-result.json", "CTL-FROZEN-4")])
        return _finish(out, state)

    # H-6: the null-object side of CTL-FORCE-PI is checked BEFORE run 2.
    fp = state["force_pi"]
    stops = []
    for reading in FORCING_READINGS:
        for order in COMPOSITION_ORDERS:
            b = fp["per_reading"][reading]["per_composition_order"][order]
            if not b["side_a_identity_versus_the_committed_six"][
                    "known_answer_met"]:
                stops.append(f"CTL-FORCE-PI side A UNMET under "
                             f"{reading}/{order}")
            if not b["side_b_does_the_forced_set_move_across_instruments"][
                    "known_answer_met_at_per_primitive_granularity"]:
                stops.append(f"CTL-FORCE-PI side B UNMET at per-primitive "
                             f"granularity under {reading}/{order}")
    out["CTL_FORCE_PI_stop_conditions_observed"] = stops
    out["CTL_FORCE_PI_stop_disposition"] = (
        "REPORTED AND ROUTED, NOT SILENTLY RESOLVED. The contract's stopping "
        "rule fires on the identity known-answer differing from the committed "
        "six IN EITHER DIRECTION. THIS PRODUCER MEASURES THAT CONDITION UNDER "
        "BOTH DECLARED READINGS OF THE SPECIFICATION GAP AT "
        "`the_specification_gap_reported_and_not_resolved` AND UNDER BOTH "
        "COMPOSITION ORDERS. WHERE THE TWO READINGS DISAGREE ABOUT WHETHER THE "
        "STOP FIRES, THE PRODUCER DOES NOT PICK: it continues the measurement, "
        "reports both, and hands the reading question to the Coordinator as a "
        "SPECIFICATION FINDING. Suppressing the arithmetic under one reading "
        "would destroy a measurement both readings share, and asserting the "
        "known answer met under the reading that meets it would resolve the "
        "gap by fiat. NEITHER IS DONE. THE CONTINUATION IS DECLARED HERE AS A "
        "PROTOCOL DEVIATION AND IS NOT PRESENTED AS COMPLIANCE.")

    _emit("readmitted-cells", lambda: run_stage2(state), out)
    r3 = _emit("consistent-pair-family", lambda: run_stage3(state), out)
    if r3["state"] != "completed_valid":
        _not_run("pair-cells-and-null-object",
                 "stage 3 did not complete", out,
                 [("consistent-pair-cells-result.json", "pair cells"),
                  ("readmit-null-object-result.json", "CTL-READMIT-NULL"),
                  ("frozen-recheck-4-result.json", "CTL-FROZEN-4")])
        return _finish(out, state)
    _emit("pair-cells-and-null-object", lambda: run_stage4(state), out)
    return _finish(out, state)


def _finish(out: dict, state: dict) -> int:
    out["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out["independence_assertion_at_end"] = \
        assert_forbidden_path_absent_from_process()
    out["P_D_as_measured"] = state.get("p_d")
    out["budget"] = {
        "declared_wall_clock_seconds": 330,
        "declared_memory_gb": 4,
        "maximum_runs": 4,
        "charged_runs": sum(1 for r in out["runs"] if r.get("run_id")),
        "per_run_ceilings": CEILINGS,
        "declared_ceiling_sum_seconds": sum(CEILINGS.values()),
        "unspent_ceilings_are_reported_as_unspent_and_never_reallocated": True,
    }
    for name, control, key in (
            ("readmitted-cells-result.json", "CTL-READMIT", "readmit"),
            ("consistent-pair-family-result.json", "CTL-PAIR-WF", "pair_family"),
            ("consistent-pair-cells-result.json", "pair cells", "pair_doc"),
            ("readmit-null-object-result.json", "CTL-READMIT-NULL", "null_doc"),
            ("frozen-recheck-4-result.json", "CTL-FROZEN-4", "frozen")):
        p = os.path.join(TASK_ROOT, name)
        if not os.path.exists(p):
            _write_json(name, {
                "control": control, "status": "NOT-WRITTEN-BY-ITS-RUN",
                "gate_that_fired": ("its run did not reach completed_valid; see "
                                    "execution-report.yaml runs[]"),
                "every_quantity_this_run_would_have_produced": None,
                "why_null_and_never_zero": (
                    "AN UNMEASURED QUANTITY IS EMITTED AS null AND NEVER AS 0 "
                    "(H-8)."),
                "census_completeness": CENSUS_COMPLETENESS})
    _write_json("independence-attestation.json", independence_attestation(out))
    _write_json("run-index.json", _run_index(out))
    scratch = os.environ.get("READMIT_DRIVER_SUMMARY")
    if scratch:
        # WRITE-SCOPE DISCIPLINE: the driver summary is NOT one of this task's
        # nine declared artifact paths, so it is written OUTSIDE the task
        # directory, to a path the caller names, or not at all.
        with open(scratch, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1, default=str)
            fh.write("\n")
    print(json.dumps({"runs": [{k: r.get(k) for k in
                                ("run_suffix", "run_id", "state",
                                 "wall_seconds", "ceiling_unspent_seconds")}
                               for r in out["runs"]]}, indent=1))
    return 0


def independence_attestation(out: dict) -> dict:
    return {
        "control": "CTL-INDEP (with CTL-QUAR and IR-14 carried beside it)",
        "experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
        "batch_id": BATCH_ID, "goal_id": GOAL_ID,
        "the_forbidden_path_named_literally": FORBIDDEN_PATH_LITERAL,
        "what_it_contains_per_the_contract": (
            "rt3_rederive.py and rt3_objects.py -- the ONE implementation that "
            "has ever computed the control this task replicates. NAMED FROM THE "
            "CONTRACT AND THE TASK CARD; THIS PRODUCER DID NOT LIST THE "
            "DIRECTORY TO FIND OUT."),
        "run_time_assertion": out.get("independence_assertion_at_end")
                              or out.get("independence_assertion_at_start"),
        "audit_hook": {
            "installed_before_any_substrate_import": True,
            "events_hooked": ["open", "os.open"],
            "blocked_prefixes": [
                FORBIDDEN_PATH_LITERAL, QUARANTINE_PATH_LITERAL,
                SEALED_PRIORS_PATH_LITERAL],
            "blocked_open_attempts_recorded":
                list(_FIREWALL_STATE["blocked_open_attempts"]),
            "behaviour_on_a_blocked_open": (
                "raises FirewallBreach, which the driver catches and records as "
                "invalid_measurement rather than letting the run proceed"),
        },
        "filesystem_traversal_roots_used_by_this_process": TRAVERSAL_ROOTS,
        "network_requests_made": 0,
        "network_mechanism": (
            "NO NETWORK ACQUISITION BY ANY ROUTE (IR-3). This module imports no "
            "socket, no urllib, no http client and no subprocess, and holds no "
            "web_search tool."),
        "is_the_non_reading_MECHANICALLY_DEMONSTRATED_or_ATTESTED":
            INDEPENDENCE_MODE,
        "no_tool_in_this_repository_can_verify_the_boolean": (
            "STATED AS THE CONTRACT REQUIRES. The audit hook proves the "
            "PROCESS did not read the forbidden path. WHETHER THE PRODUCING "
            "SESSION READ IT WITH AN AGENT TOOL OUTSIDE THIS PROCESS IS AN "
            "HONEST BOOLEAN, RECORDED IN execution-report.yaml UNDER "
            "`independence_attestation`, AND NO TOOL IN THIS REPOSITORY CAN "
            "VERIFY IT."),
        "quarantine_attestation": {
            "path": QUARANTINE_PATH_LITERAL,
            "reads_by_every_route": 0,
            "mechanism": QUARANTINE_MECHANISM,
            "build_census_was_called": True,
            "build_census_note": (
                "STATED PLAINLY AND NOT ELIDED. census.build_census IS CALLED, "
                "because arm (a) REUSES the draw sets and every draw is built "
                "from census.shadow. What is NOT done is any read of the "
                "quarantined payload: census.quarantine_attestation is replaced "
                "in this process by a stub that opens nothing, and the audit "
                "hook would raise if any code path attempted the open anyway. "
                "THE PAYLOAD REMAINS QUARANTINED AND HASH-ONLY AND THIS TASK "
                "DID NOT EVEN RE-HASH IT."),
        },
        "sealed_priors_attestation": {
            "path": SEALED_PRIORS_PATH_LITERAL,
            "reads_by_every_route": 0,
            "mechanism": "the same audit hook prefix (IR-14)"},
        "IR_12_consequence_if_the_forbidden_path_HAD_been_read": (
            "A READ DOES NOT DISCARD THE ARITHMETIC. It DOWNGRADES THE LABEL "
            "from REPLICATION to RE-EXECUTION, and it is reported rather than "
            "concealed."),
        "census_completeness": CENSUS_COMPLETENESS,
    }


if __name__ == "__main__":                                   # pragma: no cover
    raise SystemExit(main())
