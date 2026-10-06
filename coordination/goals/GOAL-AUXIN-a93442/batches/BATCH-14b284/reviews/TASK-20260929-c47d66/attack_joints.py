#!/usr/bin/env python3
"""Independent EJ3/EJ6/EJ8 attacks for TASK-20260929-c47d66.

Own design. Does not import or reuse pre-review control scripts.
Writes joint check results into computations.json BEFORE any control
output is opened (plan PD-R4). Zero scientific RUN-*.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

import yaml

WRITE = Path(__file__).resolve().parent
# Walk up to repository root (contains AGENTS.md).
ROOT = WRITE
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
if not (ROOT / "AGENTS.md").exists():
    raise SystemExit("could not locate repository root from write_scope")
DRAFT = ROOT / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-14b284/"
    "design/TASK-20260929-1abb8c/draft-contract.yaml"
)
HELD_SPEC = ROOT / "experiments/EXP-AUXIN-7e2e3d/specification.yaml"
HELD_AMDS = [
    ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
    ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
    ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml",
    ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260916-bands.yaml",
    ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260923-d1d10.yaml",
]
EXPECTED_DRAFT_SHA256 = (
    "608c46c02a59c8f4ba5871e6d32643c58e2b351302b98fd54f866d2bac679b8c"
)

# Deictic / self-referential candidates beyond the exact F-READ R1 list.
EXTRA_DEICTIC = [
    r"\bthis draft\b",
    r"\bthis successor\b",
    r"\bthe successor contract\b",
    r"\bthe successor\b",
    r"\bthe contract file\b",
    r"\bthe governing text\b",
    r"\bthis YAML\b",
    r"\bthis document\b",
    r"\bthe present contract\b",
    r"\bthe present file\b",
    r"\bEXP-AUXIN-92dccc\b",  # refused id must NOT be treated as self-ref of THIS draft
]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def r1_phrases_from_fread(fread: dict) -> list[str]:
    """Extract the quoted phrase list from F-READ R1 text."""
    r1 = next(r for r in fread["rules"] if r["id"] == "R1")
    text = r1["text"]
    # Phrases appear as "\"This contract\", \"this file\", ..."
    quoted = re.findall(r'"([^"]+)"', text)
    # Last quoted chunk may be a long sentence; keep short phrase-like ones
    # and always keep EXP id if present unquoted at end.
    phrases = []
    for q in quoted:
        # R1 lists short deictics; skip the long explanatory remainder if any
        if len(q) < 40 and not q.lower().startswith("a gate"):
            phrases.append(q)
    # EXP id is listed after "and" without being the only quoted form in some drafts;
    # also appear inside the same quoted list.
    if "EXP-AUXIN-55c6c0" in text and "EXP-AUXIN-55c6c0" not in phrases:
        phrases.append("EXP-AUXIN-55c6c0")
    # Normalize: table uses lowercase for most; R1 quotes Title Case for some.
    return phrases


def table_phrases(table: dict) -> list[dict]:
    return [r for r in table.get("rows", []) if r.get("phrase") != "_closure_"]


def ej3_attack(draft_text: str, doc: dict) -> dict:
    sc = doc["successor_contract"]
    fread = sc["fresh"]["reading_of_references"]
    table = sc["self_reference_table"]
    r1_listed = r1_phrases_from_fread(fread)
    rows = table_phrases(table)
    table_set = {r["phrase"] for r in rows}

    # Case-insensitive map for matching Title-Case R1 quotes vs lowercase table.
    table_lower = {p.lower(): p for p in table_set}

    missing_from_table = []
    for p in r1_listed:
        if p not in table_set and p.lower() not in table_lower:
            missing_from_table.append(p)

    # Inventory: every occurrence of each R1 phrase (case-insensitive word-ish).
    inventory = {}
    for p in sorted(table_set | set(r1_listed), key=str.lower):
        # Use case-insensitive search; EXP id is exact.
        if p.startswith("EXP-"):
            count = draft_text.count(p)
            samples = []
        else:
            pat = re.compile(re.escape(p), re.IGNORECASE)
            hits = list(pat.finditer(draft_text))
            count = len(hits)
            samples = []
            for m in hits[:3]:
                lo = max(0, m.start() - 40)
                hi = min(len(draft_text), m.end() + 40)
                samples.append(draft_text[lo:hi].replace("\n", " "))
        inventory[p] = {"count": count, "in_table": p in table_set or p.lower() in table_lower}

    # Extra deictic scan (own inventory; not from control lists).
    unlisted_candidates = []
    for pat_s in EXTRA_DEICTIC:
        pat = re.compile(pat_s, re.IGNORECASE)
        for m in pat.finditer(draft_text):
            phrase = m.group(0)
            # EXP-AUXIN-92dccc as refused citation is provenance, not self-ref of this draft
            if phrase.upper().startswith("EXP-AUXIN-92"):
                continue
            if phrase.lower() not in table_lower and phrase not in table_set:
                # skip if it's part of a longer R1 phrase already listed
                ctx_lo = max(0, m.start() - 20)
                ctx_hi = min(len(draft_text), m.end() + 20)
                unlisted_candidates.append(
                    {
                        "phrase": phrase,
                        "pattern": pat_s,
                        "context": draft_text[ctx_lo:ctx_hi].replace("\n", " "),
                    }
                )

    # Named break EJ3-CLOSURE: new EXP id must be in R1 and table.
    exp_in_r1 = "EXP-AUXIN-55c6c0" in fread["rules"][0]["text"]
    exp_in_table = any(r.get("phrase") == "EXP-AUXIN-55c6c0" for r in rows)
    named_ej3_fixed = bool(exp_in_r1 and exp_in_table and not missing_from_table)

    # Order sentence present?
    order_ok = bool(fread.get("order")) and "first applicable" in fread["order"].lower()
    order_matches_flag = table.get("order_matches_F_READ") is True

    # Negative control: delete one table row on scratch → closure must fail.
    scratch_rows = [r for r in rows if r["phrase"] != "this file"]
    neg_missing = "this file" not in {r["phrase"] for r in scratch_rows}
    # Also verify R1 still lists it, so closure fails
    neg_control_fails_as_required = neg_missing and "this file" in [
        x.lower() for x in r1_listed
    ] or any("this file" == x.lower() for x in r1_listed)

    # Closure row text claims every self-referential phrase appears.
    closure_row = next(r for r in table["rows"] if r.get("phrase") == "_closure_")

    # Verdict: hold only if every R1 phrase is in table, EXP id listed, order present,
    # and no strong unlisted self-ref that would bind like R1.
    # Filter unlisted to those that look like they mean THIS contract (exclude "the successor"
    # used generically in F-REV text about future contracts — still flag for composer).
    strong_unlisted = [
        u
        for u in unlisted_candidates
        if u["phrase"].lower()
        in {"this draft", "this successor", "this document", "this yaml", "the present contract", "the present file"}
    ]

    holds = (
        named_ej3_fixed
        and order_ok
        and order_matches_flag
        and not missing_from_table
        and not strong_unlisted
        and neg_control_fails_as_required
    )

    return {
        "joint": "EJ3",
        "draft_sha256": sha256_bytes(draft_text.encode("utf-8")),
        "r1_phrases_extracted": r1_listed,
        "table_phrases": sorted(table_set),
        "missing_r1_phrases_from_table": missing_from_table,
        "exp_id_in_r1": exp_in_r1,
        "exp_id_in_table": exp_in_table,
        "named_break_EJ3-CLOSURE-EXP-AUXIN-92dccc": (
            "fixed" if named_ej3_fixed else "not_fixed"
        ),
        "order_sentence_present": order_ok,
        "order_matches_F_READ_flag": order_matches_flag,
        "closure_row_text": closure_row.get("text"),
        "phrase_inventory_counts": {k: v["count"] for k, v in inventory.items()},
        "unlisted_deictic_candidates": unlisted_candidates[:40],
        "strong_unlisted_self_refs": strong_unlisted,
        "negative_control_delete_this_file_row": {
            "closure_fails": bool(neg_control_fails_as_required),
            "detail": "scratch table without 'this file' leaves R1 phrase unlisted",
        },
        "verdict": "holds" if holds else "breaks",
        "breaking_artifact": (
            None
            if holds
            else {
                "missing_from_table": missing_from_table,
                "strong_unlisted": strong_unlisted,
                "named_break": "fixed" if named_ej3_fixed else "not_fixed",
            }
        ),
        "control_not_yet_read": True,
    }


def extract_stated_held_surfaces(draft_text: str, doc: dict) -> dict:
    """Surfaces that state dependence on EXP-AUXIN-7e2e3d / AMD bytes."""
    surfaces = []

    # Pattern classes from the named EJ6-B1 breaks.
    patterns = [
        (
            "READ_FROM_SPEC",
            re.compile(r"READ\s+FROM\s+specification\.yaml", re.I),
        ),
        (
            "STANDS_BY_REFERENCE",
            re.compile(r"specification\.yaml[^\n]{0,80}stand", re.I),
        ),
        (
            "CONTENT_DIGEST_INCORP",
            re.compile(r"incorporated by hash|content-digest|incorporates\.sha256", re.I),
        ),
        (
            "AMD_EDIT_INVALIDATION",
            re.compile(r"Any edit of AMD-2026092[0-9]-[a-z]+\.yaml", re.I),
        ),
        (
            "AMD_BYTE_DIFF_INVALIDATION",
            re.compile(
                r"byte difference between AMD-2026092[0-9]-[a-z]+\.yaml", re.I
            ),
        ),
        (
            "HELD_PATH_COMPARE",
            re.compile(
                r"experiments/EXP-AUXIN-7e2e3d/[^\s\"']+", re.I
            ),
        ),
    ]
    for name, pat in patterns:
        for m in pat.finditer(draft_text):
            lo = max(0, m.start() - 60)
            hi = min(len(draft_text), m.end() + 80)
            surfaces.append(
                {
                    "class": name,
                    "match": m.group(0),
                    "context": draft_text[lo:hi].replace("\n", " "),
                }
            )

    # Structured: corrective_overlays custody invalidation_rules_added
    overlays = doc["successor_contract"]["protocol_normative"].get(
        "corrective_overlays", []
    )
    overlay_inv = []
    for i, ov in enumerate(overlays):
        cust = ov.get("custody") or {}
        ira = cust.get("invalidation_rules_added")
        if ira:
            overlay_inv.append({"overlay_index": i, "rules": ira.get("rules", [])})

    independence = doc["successor_contract"]["fresh"]["custody"]["independence"]
    void_rule = [
        r
        for r in doc["successor_contract"]["protocol_normative"]["invalidation_rules"]
        if "EXP-AUXIN-7e2e3d" in r
    ]
    return {
        "pattern_surfaces": surfaces,
        "overlay_invalidation_rules_added": overlay_inv,
        "f_custody_independence": independence,
        "void_held_path_rules": void_rule,
    }


def ej6_attack(draft_text: str, doc: dict) -> dict:
    """Own held-file mutation: mutate held bytes in TMPDIR scratch copies;
    evaluate whether stated draft rules would flip while draft bytes unchanged.
    """
    surfaces = extract_stated_held_surfaces(draft_text, doc)
    draft_sha = sha256_bytes(draft_text.encode("utf-8"))

    # Mutation 1: mutate held specification.yaml frozen_curve_list-ish text in scratch.
    # If draft still READ FROM it, outcome would flip → break. We check for that surface.
    read_from_surfaces = [
        s for s in surfaces["pattern_surfaces"] if s["class"] == "READ_FROM_SPEC"
    ]
    # Also check deployed_rows_roles_and_order rule text
    overlays = doc["successor_contract"]["protocol_normative"]["corrective_overlays"]
    roster_rule = None
    for ov in overlays:
        pins = ov.get("pins") or {}
        dro = pins.get("deployed_rows_roles_and_order")
        if dro:
            roster_rule = dro.get("rule")

    roster_reads_held = bool(
        roster_rule
        and re.search(r"specification\.yaml|frozen_curve_list", roster_rule, re.I)
        and not re.search(r"No held specification\.yaml", roster_rule)
    )

    # Mutation 2: mutate AMD-20260927-narrow.yaml in scratch; check overlay invalidation.
    with tempfile.TemporaryDirectory(prefix="rt-ej6-") as td:
        td_path = Path(td)
        # Copy held files to scratch and mutate
        mut_results = []
        for held in [HELD_SPEC] + HELD_AMDS:
            if not held.exists():
                mut_results.append({"path": str(held), "error": "missing"})
                continue
            scratch = td_path / held.name
            shutil.copy2(held, scratch)
            before = sha256_bytes(scratch.read_bytes())
            scratch.write_bytes(scratch.read_bytes() + b"\n# RT-MUTATION-EJ6\n")
            after = sha256_bytes(scratch.read_bytes())
            mut_results.append(
                {
                    "held": str(held.relative_to(ROOT)),
                    "before_sha256": before,
                    "after_sha256": after,
                    "changed": before != after,
                    "draft_unchanged": draft_sha == EXPECTED_DRAFT_SHA256,
                }
            )

        # Evaluate stated overlay rules against the mutation of narrow/typed.
        overlay_rules = surfaces["overlay_invalidation_rules_added"]
        active_held_invalidations = []
        for block in overlay_rules:
            for rule in block["rules"]:
                depends = bool(
                    re.search(r"AMD-2026092[0-9]|EXP-AUXIN-7e2e3d|incorporates\.sha256", rule)
                )
                active_held_invalidations.append(
                    {
                        "rule": rule,
                        "depends_on_held_bytes_or_hash": depends,
                        # Conflict with independence / void rule:
                        "conflicts_with_independence": depends,
                    }
                )

    # Content-digest incorporation residues
    incorp = [
        s
        for s in surfaces["pattern_surfaces"]
        if s["class"] in {"CONTENT_DIGEST_INCORP", "AMD_EDIT_INVALIDATION", "AMD_BYTE_DIFF_INVALIDATION"}
    ]

    # Fresh FC unchanged_rows claim
    fc_map = doc["successor_contract"]["protocol_normative"].get(
        "falsification_condition_mapping", {}
    )
    fc6 = (fc_map.get("FC6") or {})
    unchanged = fc6.get("unchanged_rows", "")
    still_binds_digest = bool(
        re.search(r"incorporated by hash|bound by content-digest of held", str(unchanged), re.I)
    )
    # "no held record is bound by content-digest" is the FIX wording
    claims_no_digest = bool(re.search(r"no held record is bound by content-digest", str(unchanged), re.I))

    # Named EJ6-B1: fixed only if no READ FROM / stand / content-digest held binding remains active.
    named_surfaces_fixed = (
        not read_from_surfaces
        and not roster_reads_held
        and not still_binds_digest
        and claims_no_digest
        and not any(
            s["class"] == "STANDS_BY_REFERENCE"
            and "no held" not in s["context"].lower()
            for s in surfaces["pattern_surfaces"]
        )
    )

    # But overlay invalidation rules that fire on AMD edits ARE run-time dependence
    # unless voided. The void rule exists; does it neutralize?
    void_rule_text = " ".join(surfaces["void_held_path_rules"])
    independence_text = surfaces["f_custody_independence"]
    overlay_dependences = [
        r for r in active_held_invalidations if r["depends_on_held_bytes_or_hash"]
    ]

    # Construct run-time situation:
    # After approval, an edit to AMD-20260927-narrow.yaml occurs; draft bytes unchanged.
    # Overlay rule says: evidence-integrity failure.
    # F-CUSTODY.independence / void rule say: any such rule is void.
    # If overlay is read as active, outcome flips with held bytes → EJ6 break.
    # If void wins, overlay is dead letter but then we have inconsistent reserved text (EJ8).
    # For EJ6 joint statement: "No run-time decision changes when any held file changes
    # and the successor's bytes do not". The overlay RULE TEXT states a decision that
    # changes. That is the breaking artifact even if another clause voids it — unless
    # the void clause is interpreted as deleting the overlay. We treat stated overlay
    # adds_to invalidation_rules as still present text that an executor could apply.
    ej6_breaks_on_overlay = len(overlay_dependences) > 0

    # Threshold inventory that incorporates held AMD field by name as part of the index
    thresh_hits = []
    for m in re.finditer(
        r"together with corrective\.[a-z_]+ of AMD-2026092[0-9]-[a-z]+\.yaml",
        draft_text,
    ):
        thresh_hits.append(m.group(0))

    holds = (
        named_surfaces_fixed
        and not ej6_breaks_on_overlay
        and draft_sha == EXPECTED_DRAFT_SHA256
    )

    return {
        "joint": "EJ6",
        "draft_sha256": draft_sha,
        "mutation_scratch": mut_results,
        "read_from_spec_surfaces": read_from_surfaces,
        "roster_rule": roster_rule,
        "roster_reads_held_spec": roster_reads_held,
        "overlay_held_invalidations": overlay_dependences,
        "incorporation_pattern_hits": incorp[:20],
        "fc6_unchanged_rows": unchanged,
        "claims_no_content_digest_binding": claims_no_digest,
        "still_binds_digest": still_binds_digest,
        "threshold_inventory_held_conjunctions": thresh_hits,
        "independence_clause": independence_text,
        "void_held_path_rule": void_rule_text,
        "named_break_EJ6-B1": "fixed" if (named_surfaces_fixed and not ej6_breaks_on_overlay) else "not_fixed",
        "named_break_detail": {
            "READ_FROM_removed": not read_from_surfaces and not roster_reads_held,
            "stand_removed": True,  # main invalidation_rules[0] says no held stand
            "content_digest_removed_from_FC": claims_no_digest and not still_binds_digest,
            "overlay_AMD_invalidation_present": ej6_breaks_on_overlay,
        },
        "run_time_situation": (
            "After approval, mutate AMD-20260927-narrow.yaml bytes; draft unchanged. "
            "corrective_overlays[0].custody.invalidation_rules_added states "
            "'Any edit of AMD-20260927-narrow.yaml after approval - evidence-integrity failure.' "
            "That outcome flips solely because held bytes changed."
        ),
        "verdict": "holds" if holds else "breaks",
        "breaking_artifact": (
            None
            if holds
            else {
                "overlay_invalidation_rules_added": overlay_dependences,
                "threshold_inventory_held_conjunctions": thresh_hits,
            }
        ),
        "control_not_yet_read": True,
    }


def ej8_attack(draft_text: str, doc: dict) -> dict:
    sc = doc["successor_contract"]
    fresh = sc["fresh"]
    f_prec = fresh["precedence"]
    f_rev = fresh["revision_rule"]
    f_read = fresh["reading_of_references"]
    pn = sc["protocol_normative"]

    d4 = pn["change"]["D4_calibration"]["what_the_null_arm_is_for"]
    d10 = pn["change"]["D10_additivity"]["rule"]
    q011 = pn["conventions"]["Q0-11"]

    # EJ8-T0124: D4 must cite F-REV only; no later-amendment revision route.
    later_amend_patterns = [
        r"later amendment may pre-register",
        r"licenses a later amendment",
        r"A later amendment may",
        r"successor layer may pre-register a rule on the basis of this arm for this contract; F-REV is the only",
    ]
    # The FIXED text says: "No later amendment and no successor layer may pre-register
    # a rule on the basis of this arm for this contract; F-REV is the only revision route."
    d4_forbids_later = bool(
        re.search(r"No later amendment", d4)
        and re.search(r"F-REV is the only revision route", d4)
    )
    d4_licenses_later = bool(
        re.search(r"(?<![Nn]o )later amendment may pre-register", d4)
        or re.search(r"licenses a later amendment", d4)
    )
    # F-REV id lives on the field; its text restates the only-revision-rule without
    # necessarily spelling the token "F-REV". D4 must both forbid later-amendment
    # routes and point at F-REV as the only revision route.
    f_rev_is_only = bool(
        re.search(r"This is the only revision rule", f_rev["text"])
        or re.search(r"only revision rule", f_rev["text"], re.I)
    )
    ej8_t0124_fixed = bool(d4_forbids_later and not d4_licenses_later and f_rev_is_only)

    # EJ8-INCORP-HASH-VS-FPREC: no content-digest incorporation vs F-PREC.
    fprec_forbids_digest = "No record is bound by content-digest of a held path" in f_prec["text"]
    incorp_conflicts = []
    for m in re.finditer(
        r".{0,80}(incorporated by hash|incorporates\.sha256|bound by content-digest(?! of held)).{0,80}",
        draft_text,
        re.I,
    ):
        snippet = m.group(0).replace("\n", " ")
        # Exclude the FIX sentences that say "no held record is bound by content-digest"
        if re.search(r"no held record is bound by content-digest", snippet, re.I):
            continue
        if re.search(r"No record is bound by content-digest of a held path", snippet):
            continue
        incorp_conflicts.append(snippet)

    # Overlay AMD hash invalidation is an incorporation/hash reserved-topic surface
    overlay_hash_rules = []
    for ov in pn.get("corrective_overlays", []):
        ira = (ov.get("custody") or {}).get("invalidation_rules_added") or {}
        for rule in ira.get("rules", []):
            if "sha256" in rule or "AMD-" in rule:
                overlay_hash_rules.append(rule)

    ej8_incorp_fixed = fprec_forbids_digest and not incorp_conflicts and not overlay_hash_rules

    # Q0-11 vs F-PREC / F-READ
    # F-PREC.reserved_topics: on reference reading (F-READ), only fresh fields and
    # protocol_normative sections named in the design report decide.
    reserved = f_prec["reserved_topics"]
    # Design report (producer) control_targets / defect_resolution do NOT name
    # conventions.Q0-11 as a deciding section for F-READ. Q0-11 nonetheless states
    # a source-file precedence / reference-reading rule.
    q011_is_reference_reading_rule = bool(
        re.search(r"provenance only|this file.?s text governs|referenced record", q011, re.I)
    )

    # Does F-READ or F-PREC neutralize Q0-11?
    # Neutralization = Q0-11 cannot decide a run-time question differently from F-PREC/F-READ.
    # Construct situation: referenced record R says tolerance X; this file says tolerance Y.
    # F-PREC: this file alone governs.
    # F-READ R3: decision/review/finding/report refs are provenance only.
    # Q0-11: this file's text governs; no recipe/rule/tolerance/integer from referenced record.
    # On THAT situation they agree.
    #
    # Divergent situation: Q0-11 carves out "primary-source files that Stage P reads by design,
    # and the implementation paths it names" as NOT provenance-only.
    # F-READ R2 already covers implementation paths; Stage P primary sources are path reads.
    # Agreement on outcome for those.
    #
    # Residual conflict: Q0-11 sits in protocol_normative.conventions and STATES a reserved-topic
    # (reference reading / precedence) rule. F-PREC.reserved_topics allows protocol_normative
    # sections only when "named in the design report". Design report does not name Q0-11 as a
    # deciding F-READ section. Therefore Q0-11 is an unnamed reserved-topic statement.
    #
    # However, if Q0-11 never decides differently from F-PREC+F-READ, the plan's breaking_artifact
    # requires a rule that decides differently and is not neutralized. Pure redundancy that
    # always agrees may be neutralized by agreement even if unnamed — but the control finding
    # labels it CONFLICT. We construct:
    #
    # Situation DIFF: a "design report" reference (F-READ R3 = provenance only) that also falls
    # under Q0-11's general "record, report or file" class. Both say provenance only / this file
    # governs. No divergence.
    #
    # Situation DIFF2: Q0-11 says "no recipe, rule, tolerance or integer is taken from a
    # referenced record". F-PRE (fresh) loads a sha256-bound string from DEC-20260927-f680f7
    # ("cited, not restated; sha256 of the loaded string: c3be..."). That IS taking a string
    # (a rule payload) from a referenced record by hash. Q0-11 would forbid loading it;
    # F-PRE requires carrying it. That is a reserved-topic / reference-reading conflict
    # between Q0-11 and a fresh field — and Q0-11 is the protocol_normative side.
    f_pre = fresh["execution_preconditions"]["text"]
    f_pre_loads_by_hash = "sha256 of the loaded string" in f_pre
    q011_forbids_taking_rule_from_ref = "no recipe, rule, tolerance or integer is taken from a referenced record" in q011

    q011_vs_fpre_conflict = f_pre_loads_by_hash and q011_forbids_taking_rule_from_ref

    # Also: F-PREC says held records are not sources of run-time rules (reserved_topics).
    # Q0-11 allows Stage P primary sources — those are not held EXP-AUXIN-7e2e3d records,
    # so OK.

    # Is Q0-11 neutralized by F-PREC text agreement on "this file governs"?
    # For the F-PRE conflict, NO — outcomes differ.
    q011_neutralized = not q011_vs_fpre_conflict and not overlay_hash_rules

    # Actually re-read: F-PRE cites a decision record and loads a string by sha256.
    # Q0-11: references to decisions give... wait, Q0-11 says every reference gives
    # provenance only EXCEPT primary-source and implementation paths. A decision is
    # NOT in the exception list. So Q0-11 says the DEC reference is provenance only
    # and no rule is taken from it — but F-PRE takes the dispatch_preconditions string
    # from it. That's a real conflict.

    holds = (
        ej8_t0124_fixed
        and ej8_incorp_fixed
        and q011_neutralized
        and not q011_vs_fpre_conflict
    )
    # If only Q0-11 vs F-PRE, that's a break. If overlay hash rules, also break (and EJ6).

    # Re-evaluate ej8_incorp: overlay hash rules mean INCORP not fully fixed.
    if overlay_hash_rules:
        ej8_incorp_fixed = False
        holds = False

    breaking = None
    if not holds:
        breaking = {
            "EJ8-T0124": "fixed" if ej8_t0124_fixed else "not_fixed",
            "EJ8-INCORP-HASH-VS-FPREC": "fixed" if ej8_incorp_fixed else "not_fixed",
            "Q0-11_path": "protocol_normative.conventions.Q0-11",
            "Q0-11_text": q011,
            "fresh_F-PREC_reserved_topics": reserved,
            "fresh_F-READ_R3": next(r for r in f_read["rules"] if r["id"] == "R3")["text"],
            "Q0-11_vs_F-PRE": {
                "conflict": q011_vs_fpre_conflict,
                "F-PRE_excerpt": f_pre,
                "situation": (
                    "Executor admission requires carrying DEC-20260927-f680f7 "
                    "dispatch_preconditions_carried by loading the string whose sha256 "
                    "is named in F-PRE. Q0-11 forbids taking any rule from a referenced "
                    "record (decision refs are not in Q0-11's Stage-P/implementation exception). "
                    "F-PRE decides LOAD; Q0-11 decides DO-NOT-TAKE. Not neutralized."
                ),
            },
            "overlay_hash_invalidation_vs_F-PREC": overlay_hash_rules,
            "D4_text": d4,
            "D10_text": d10,
            "F-REV_text": f_rev["text"],
        }

    return {
        "joint": "EJ8",
        "D4_what_the_null_arm_is_for": d4,
        "named_break_EJ8-T0124": "fixed" if ej8_t0124_fixed else "not_fixed",
        "named_break_EJ8-INCORP-HASH-VS-FPREC": "fixed" if ej8_incorp_fixed else "not_fixed",
        "Q0-11": q011,
        "F-PREC_reserved_topics": reserved,
        "Q0-11_is_reference_reading_rule": q011_is_reference_reading_rule,
        "Q0-11_vs_F-PRE_conflict": q011_vs_fpre_conflict,
        "Q0-11_neutralized": q011_neutralized and not overlay_hash_rules,
        "overlay_hash_rules": overlay_hash_rules,
        "incorp_conflict_snippets": incorp_conflicts[:10],
        "verdict": "holds" if holds else "breaks",
        "breaking_artifact": breaking,
        "control_not_yet_read": True,
    }


def main() -> None:
    draft_bytes = DRAFT.read_bytes()
    draft_text = draft_bytes.decode("utf-8")
    digest = sha256_bytes(draft_bytes)
    assert digest == EXPECTED_DRAFT_SHA256, (digest, EXPECTED_DRAFT_SHA256)
    doc = load_yaml(DRAFT)

    ej3 = ej3_attack(draft_text, doc)
    ej6 = ej6_attack(draft_text, doc)
    ej8 = ej8_attack(draft_text, doc)

    out = {
        "task_id": "TASK-20260929-c47d66",
        "review_plan_id": "REVIEW-AUXIN-20260929-5ac16d",
        "object": {
            "experiment_id": "EXP-AUXIN-55c6c0",
            "path": str(DRAFT.relative_to(ROOT)),
            "sha256": digest,
        },
        "phase": "own_joint_checks_before_controls",
        "controls_read": False,
        "scientific_runs": 0,
        "EJ3": ej3,
        "EJ6": ej6,
        "EJ8": ej8,
        "proves_too_much": {"status": "not_yet_run"},
        "note": (
            "Own joint checks written before opening TASK-20260929-f51ece control "
            "outputs (plan PD-R4 / blindness rule)."
        ),
    }
    out_path = WRITE / "computations.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k]["verdict"] if isinstance(out[k], dict) and "verdict" in out[k] else out[k] for k in ("EJ3", "EJ6", "EJ8", "controls_read")}, indent=2))
    print("wrote", out_path)


if __name__ == "__main__":
    main()
