#!/usr/bin/env python3
"""Assemble research_goals_20260723.md and registry.yaml from the 10 cluster drafts."""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path("/Volumes/Volume/crypto-autoresearcher")
DRAFTS = ROOT / "coordination/goals30/drafts"

# (cluster_no, cluster_name, draft_filename)
CLUSTERS = [
    (1, "BASELINE", "cluster_01_baseline_G30-001..003.md"),
    (2, "GROEBNER", "cluster_02_groebner_G30-004..006.md"),
    (3, "MONODROMY", "cluster_03_monodromy_G30-007..009.md"),
    (4, "FACTORBASE", "cluster_04_factorbase_G30-010..012.md"),
    (5, "RELATIONS", "cluster_05_relations_G30-013..015.md"),
    (6, "LINALG", "cluster_06_linalg_G30-016..018.md"),
    (7, "TRANSFER", "cluster_07_transfer_G30-019..021.md"),
    (8, "BARRIERS", "cluster_08_barriers_G30-022..024.md"),
    (9, "HARNESS", "cluster_09_harness_G30-025..027.md"),
    (10, "GOVERNANCE", "cluster_10_governance_G30-028..030.md"),
]

# Curated goal metadata parsed from the drafts (hard dependencies only; soft/optional
# edges are recorded in notes, not in the DAG).
GOALS = [
    dict(id="G30-001", title="Fully-charged group-op-equivalent cost standard for algebraic attack stages",
         cluster="01 BASELINE", type="infrastructure", claim_tier="infrastructure", deps=[], draft=1),
    dict(id="G30-002", title="Corrigan-Gibbs–Kogan S·T² preprocessing/advice accounting gate",
         cluster="01 BASELINE", type="governance", claim_tier="infrastructure", deps=["G30-001"], draft=1),
    dict(id="G30-003", title="Toy-to-crypto extrapolation and claim-tier-elevation protocol",
         cluster="01 BASELINE", type="governance", claim_tier="infrastructure", deps=["G30-001"], draft=1),
    dict(id="G30-004", title="Commission a true degree-of-regularity backend (F4/F5 via Sage/GBLA) into harness/",
         cluster="02 GROEBNER", type="infrastructure", claim_tier="infrastructure", deps=["G30-025"], draft=2),
    dict(id="G30-005", title="Execute and close EXP-DREG-003 — confirmatory D6-at-n=12 cell for the dreg-linear-law diagnosis",
         cluster="02 GROEBNER", type="measurement", claim_tier="toy", deps=["G30-004"], draft=2),
    dict(id="G30-006", title="Prime-field Semaev first-fall / solving-degree growth census, m ∈ {2,3,4}, 8–20-bit ladder (KN-OPEN-002)",
         cluster="02 GROEBNER", type="measurement", claim_tier="toy", deps=["G30-004", "G30-005", "G30-026"], draft=2),
    dict(id="G30-007", title="Chebotarev census of the m-th Semaev summation cover at toy scale",
         cluster="03 MONODROMY", type="measurement", claim_tier="toy", deps=[], draft=3),
    dict(id="G30-008", title="Imprimitive-monodromy resolvent test of the summation cover",
         cluster="03 MONODROMY", type="attack-probe", claim_tier="toy", deps=["G30-001"], draft=3),
    dict(id="G30-009", title="Wreath-monodromy barrier theorem — prove or refute quasirandom relation rates (D2)",
         cluster="03 MONODROMY", type="barrier", claim_tier="toy", deps=["G30-007"], draft=3),
    dict(id="G30-010", title="Execute the H-FB3-001 structured factor-base geometry battery (EXP-FB3-001)",
         cluster="04 FACTORBASE", type="measurement", claim_tier="toy", deps=[], draft=4),
    dict(id="G30-011", title="Representation census — Edwards / Jacobi-intersection / Hessian vs short Weierstrass at matched instances",
         cluster="04 FACTORBASE", type="measurement", claim_tier="toy", deps=["G30-026"], draft=4),
    dict(id="G30-012", title="Exceptional-curve sieve — Chebotarev/monodromy and S-unit predicates with fresh-curve held-out controls",
         cluster="04 FACTORBASE", type="attack-probe", claim_tier="toy", deps=["G30-007", "G30-008"], draft=4),
    dict(id="G30-013", title="PO-transfer-007 probe — label-conditioned smoothness on cyclic covers X_d: z^d = h(P), fully charged",
         cluster="05 RELATIONS", type="attack-probe", claim_tier="toy", deps=["G30-001"], draft=5),
    dict(id="G30-014", title="B1 AG-code enumerator calculus — exact relation-count law validated against brute force at toy scale",
         cluster="05 RELATIONS", type="measurement", claim_tier="toy", deps=[], draft=5),
    dict(id="G30-015", title="Split-Jacobian projected smoothness — a genus-2 correspondence relation engine that never factors through x-line Semaev",
         cluster="05 RELATIONS", type="attack-probe", claim_tier="toy", deps=["G30-001"], draft=5),
    dict(id="G30-016", title="Calibrated sparse/structured linear-algebra benchmark module over F_p",
         cluster="06 LINALG", type="infrastructure", claim_tier="infrastructure", deps=["G30-001"], draft=6),
    dict(id="G30-017", title="Designed relation supports → low-displacement-rank matrices, net of relation-probability penalty",
         cluster="06 LINALG", type="attack-probe", claim_tier="toy", deps=["G30-016"], draft=6),
    dict(id="G30-018", title="Origin of the 14/16 rank saturation — search for source constructions touching free columns [6,7]/[6,16] pre-insertion",
         cluster="06 LINALG", type="barrier", claim_tier="toy", deps=[], draft=6),
    dict(id="G30-019", title="ISOWALK-C1 — non-backtracking isogeny-walk collision exponent vs birthday",
         cluster="07 TRANSFER", type="measurement", claim_tier="toy", deps=[], draft=7),
    dict(id="G30-020", title="A2 boundary theorem — exact characterization of toy no-transfer and the minimal structure permitting cross-curve advice",
         cluster="07 TRANSFER", type="barrier", claim_tier="toy", deps=["G30-019", "G30-001"], draft=7),
    dict(id="G30-021", title="PO96 residual-label probe — one DLP-free compressed-label construction with fully charged Lift/Apply/Return",
         cluster="07 TRANSFER", type="attack-probe", claim_tier="toy", deps=["G30-001"], draft=7),
    dict(id="G30-022", title="D1 quasirandomness barrier — anomalous factor base implies GAP structure in log space",
         cluster="08 BARRIERS", type="barrier", claim_tier="toy", deps=["G30-025", "G30-010"], draft=8),
    dict(id="G30-023", title="D3 Massey/cd(F_p)=1 barrier — obstruction certificate and geometric-class Frobenius-descent loophole probe",
         cluster="08 BARRIERS", type="barrier", claim_tier="toy", deps=["G30-025", "G30-022"], draft=8),
    dict(id="G30-024", title="RITT-B3 functional indecomposability of the iteration map f_m beyond PH-trivial divisors",
         cluster="08 BARRIERS", type="barrier", claim_tier="toy", deps=[], draft=8),
    dict(id="G30-025", title="Parameterized EXP registration and Sage environment capture",
         cluster="09 HARNESS", type="infrastructure", claim_tier="infrastructure", deps=[], draft=9),
    dict(id="G30-026", title="Semaev m=3/m=4 decomposition measurement and certified 40–64-bit instance ladder",
         cluster="09 HARNESS", type="measurement", claim_tier="toy", deps=["G30-025"], draft=9),
    dict(id="G30-027", title="Replication protocol, independent-verifier promotion path, and CI validator hardening",
         cluster="09 HARNESS", type="governance", claim_tier="infrastructure", deps=["G30-025"], draft=9),
    dict(id="G30-028", title="NoveltyGate — mandatory literature screening before any \"novel\" label",
         cluster="10 GOVERNANCE", type="governance", claim_tier="infrastructure", deps=[], draft=10),
    dict(id="G30-029", title="ClaimTier Ladder — explicit toy→medium→crypto-relevant escalation gates with alphaXiv-style decomposition",
         cluster="10 GOVERNANCE", type="governance", claim_tier="infrastructure", deps=["G30-003", "G30-030"], draft=10),
    dict(id="G30-030", title="PreMortem Gate — standing falsification-route review before any expansion capacity",
         cluster="10 GOVERNANCE", type="governance", claim_tier="infrastructure", deps=[], draft=10),
]

DRAFT_FILES = {c[0]: c[2] for c in CLUSTERS}


def extract_goal_bodies():
    """Return concatenated goal bodies (from first '## G30-' onward) per draft file,
    stripping per-file header notes (filename-deviation notes, drafter/theme/source
    preambles). Revision-note lines inside goal bodies are preserved."""
    bodies = []
    for cno, _name, fname in CLUSTERS:
        text = (DRAFTS / fname).read_text(encoding="utf-8")
        m = re.search(r"^## G30-", text, flags=re.M)
        if not m:
            sys.exit(f"FATAL: no goal heading found in {fname}")
        body = text[m.start():].rstrip() + "\n"
        n = len(re.findall(r"^## G30-", body, flags=re.M))
        if n != 3:
            sys.exit(f"FATAL: expected 3 goal headings in {fname}, found {n}")
        bodies.append(body)
    return bodies


def check_acyclic():
    deps = {g["id"]: list(g["deps"]) for g in GOALS}
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {k: WHITE for k in deps}

    def visit(u):
        color[u] = GRAY
        for v in deps[u]:
            if color[v] == GRAY:
                sys.exit(f"FATAL: dependency cycle at {u} -> {v}")
            if color[v] == WHITE:
                visit(v)
        color[u] = BLACK

    for k in deps:
        if color[k] == WHITE:
            visit(k)


def build_master(bodies):
    out = []
    out.append("# Research Goals 2026-07-23 — 30-Goal Program Toward Cryptographically Relevant Prime-Field ECDLP Breaks\n")
    out.append("**Date anchor:** 2026-07-23\n")
    out.append("**Status:** Planning record. Every goal is toy-tier or infrastructure; nothing here is a performance claim or crypto-scale evidence. All cost comparisons are void until G30-001's GOE cost ruler exists.\n")

    out.append("\n## 1. Program thesis\n")
    out.append(
        "\nThe long-term ambition, inherited from GOAL-ECDLP-001, is an end-to-end prime-field ECDLP attack whose fully charged cost falls below the Pollard rho / Shoup generic boundary — not a partial stage win, but a certified break. The portfolio logic of these 30 goals is deliberately defensive: roughly a third of the program (G30-001/002/003, G30-016, G30-025/027, G30-028/029/030, plus measurement scaffolding) is cost-ruler, metrology, and governance plumbing, because the closed record — 761+ negative results across seven failure families — shows that partial wins die from uncharged costs (preprocessing, linear algebra, descent, memory, amortization omitted from the ledger) and from selector fragility (frozen selectors collapsing on fresh-window controls). Attack probes (G30-008/012/013/015/017/021) are therefore paired with barrier theorems (G30-009/018/020/022/023/024) so that failure is never wasted: every killed direction produces a closure certificate, a scoped KN-FIND entry, and dedup evidence against re-proposal, while any genuine positive is routed through mandatory independent review before it can move the campaign.\n")

    out.append("\n## 2. Goal index\n")
    out.append("\n| ID | Title | Cluster | Type | Claim tier | Dependencies |")
    out.append("|---|---|---|---|---|---|")
    for g in GOALS:
        deps = ", ".join(g["deps"]) if g["deps"] else "—"
        out.append(f"| {g['id']} | {g['title']} | {g['cluster']} | {g['type']} | {g['claim_tier']} | {deps} |")

    out.append("\n## 3. Execution order\n")
    out.append(
        "\nFirst wave (per the coherence review), strictly sequenced by the dependency DAG:\n"
        "\n1. **G30-025** — parameterized EXP registry + Sage env capture; four other goals consume its registration API, so nothing scales until it lands."
        "\n2. **G30-001** — the GOE cost ruler; no \"× rho\" figure is admissible anywhere in the program before this exists."
        "\n3. **G30-016** — the sparse/structured LA benchmark substrate that applies G30-001's calibration constants; gates G30-017 and all LA-bearing attack claims."
        "\n4. **G30-004** — the true d_reg (F4/F5) backend, which requires G30-025's env capture; gates the entire Gröbner metrology line (G30-005/006)."
        "\n5. **G30-027** — replication protocol and independent-verifier promotion path; must harden CI over the G30-025/026 modules before any claim scales."
        "\n6. **G30-026** — measure_sm_decomposition (m=3,4) plus the certified 40–64-bit instance ladder; gates G30-006 and G30-011."
        "\n\nSecond wave: **G30-002 / G30-003 / G30-007** — the CGK preprocessing gate and the extrapolation protocol build directly on G30-001's ruler, and the Chebotarev census is dependency-free and seeds the whole monodromy cluster (G30-008/009/012)."
        "\n\nFocus discipline: the repo admits at most **3 concurrent experiments** (GOAL-ECDLP-001 budget discipline); the wave above is a priority queue, not a parallel dispatch — slots are filled only as dependencies clear.\n")

    out.append("\n## 4. Explicit deferrals\n")
    out.append(
        "\nThe following are recorded as Coordinator-level deferral decisions, not oversights:\n"
        "\n- **(a) CLM-ECDLP-BLIND-DESCENT** — campaign-critical, status not_attempted, and no G30 goal staffs it. **Deferred** until at least one attack probe survives G30-001 full-cost gating; staffing a descent claim before a charged sub-rho candidate exists would repeat the PO67 partial-win pattern."
        "\n- **(b) CLM-ECDLP-SUBRHO-END-TO-END integration owner** — **deferred** on the same grounds: end-to-end integration is only meaningful once a component clears the GOE full-cost gate, so no integration owner is assigned in this program round."
        "\n- **(c) Round-2 directions B2 (function-field xedni), B3 (Coppersmith small-root lattices), C1 (Buium arithmetic δ-characters), C3 (Heegner/Drinfeld special-cycle heights)** — unstaffed and **deferred** pending theory formalization; MODHECKE-B1 / ZILBERPINK-C2-class directions need theory-agent work to produce falsifiable statements before any experimental goal can be drafted for them.\n")

    out.append("\n## 5. The 30 goals\n")
    out.append(
        "\nFull goal texts, concatenated in cluster order (G30-001..G30-030) from the reviewed draft files in `coordination/goals30/drafts/`. Per-file drafting-process header notes (filename-deviation notes, drafter/source preambles) are stripped; each goal's template and its 2026-07-23 review revision notes are preserved verbatim.\n")
    for body in bodies:
        out.append("\n---\n")
        out.append("\n" + body)

    out.append("\n---\n\n## 6. Review record\n")
    out.append(
        "\nDrafting was executed by 10 parallel cluster agents (one per cluster, 2026-07-23), each reading the three cartography files (closed / active / harness) plus the live ledgers. Review applied three lenses — **overlap** (no two goals commissioning the same capability), **testability** (every goal carries quantified predictions, controls, falsification criteria, and stopping rules), and **coherence** (dependency DAG, single-owner rules, tier discipline). Outcome: 26 goals PASS on first review; 4 FIX findings were issued and resolved, touching G30-008, G30-013, G30-015, G30-022, and G30-023 (each fix is recorded as a \"Revision note (2026-07-23 review)\" line retained in Section 5). Single-owner rules enforced: **G30-001** is the sole owner of the GOE end-to-end cost ruler (all other goals consume it as a hard dependency, never co-commission); **G30-025** is the sole owner of the EXP runner registry and Sage environment capture; **G30-026** is the sole owner of measure_sm_decomposition for m=3,4. The monodromy census was merged into cluster 03 with **G30-012** rescoped as a pure consumer of G30-007/G30-008 outputs (no census or resolvent engine of its own). Tier protocols are chained: **G30-029**'s toy→medium rung invokes **G30-003**'s quantitative extrapolation rule rather than defining a competing one. The hard-dependency DAG was verified acyclic.\n")

    return "\n".join(out).rstrip() + "\n"


def build_registry():
    return {
        "metadata": {
            "created": "2026-07-23",
            "parent_goal": "GOAL-ECDLP-001",
            "total_goals": 30,
            "status": ("Planning record. Every goal is toy-tier or infrastructure; nothing here is a "
                       "performance claim or crypto-scale evidence. All cost comparisons are void until "
                       "G30-001's GOE cost ruler exists."),
            "master_document": "research_goals_20260723.md",
            "drafts_directory": "coordination/goals30/drafts/",
        },
        "goals": [
            {
                "id": g["id"],
                "title": g["title"],
                "cluster": g["cluster"],
                "type": g["type"],
                "claim_tier": g["claim_tier"],
                "dependencies": g["deps"],
                "draft_file": f"coordination/goals30/drafts/{DRAFT_FILES[g['draft']]}",
            }
            for g in GOALS
        ],
        "deferrals": [
            {
                "item": "CLM-ECDLP-BLIND-DESCENT",
                "kind": "campaign-critical claim",
                "status": "not_attempted",
                "decision": "deferred",
                "reason": ("No G30 goal staffs it; deferred until at least one attack probe survives "
                           "G30-001 full-cost gating, to avoid repeating the PO67 partial-win pattern."),
            },
            {
                "item": "CLM-ECDLP-SUBRHO-END-TO-END integration owner",
                "kind": "campaign-critical claim",
                "status": "not_attempted",
                "decision": "deferred",
                "reason": ("Deferred on the same grounds as CLM-ECDLP-BLIND-DESCENT: end-to-end integration "
                           "is only meaningful once a component clears the GOE full-cost gate."),
            },
            {
                "item": "Round-2 direction B2 — function-field xedni (rank-1 elliptic surface, MW-lattice linear algebra)",
                "kind": "research direction",
                "status": "unstaffed",
                "decision": "deferred",
                "reason": "Pending theory formalization; needs theory-agent work before an experimental goal can be drafted.",
            },
            {
                "item": "Round-2 direction B3 — Coppersmith small-root lattices for windowed relation finding",
                "kind": "research direction",
                "status": "unstaffed",
                "decision": "deferred",
                "reason": "Pending theory formalization; needs theory-agent work before an experimental goal can be drafted.",
            },
            {
                "item": "Round-2 direction C1 — Buium arithmetic δ-characters (Manin-kernel channel)",
                "kind": "research direction",
                "status": "unstaffed",
                "decision": "deferred",
                "reason": "Pending theory formalization; needs theory-agent work before an experimental goal can be drafted.",
            },
            {
                "item": "Round-2 direction C3 — function-field Heegner/Drinfeld special-cycle heights",
                "kind": "research direction",
                "status": "unstaffed",
                "decision": "deferred",
                "reason": "Pending theory formalization; needs theory-agent work before an experimental goal can be drafted.",
            },
        ],
    }


def main():
    check_acyclic()
    bodies = extract_goal_bodies()

    master = build_master(bodies)
    master_path = ROOT / "research_goals_20260723.md"
    master_path.write_text(master, encoding="utf-8")

    registry = build_registry()
    reg_path = ROOT / "coordination/goals30/registry.yaml"
    reg_path.write_text(yaml.safe_dump(registry, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")

    # Verification
    headings = re.findall(r"^## G30-", master, flags=re.M)
    print(f"master doc '## G30-' headings: {len(headings)} (expected 30)")
    assert len(headings) == 30, "heading count mismatch"

    loaded = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    n = len(loaded["goals"])
    print(f"registry goals: {n} (expected 30); deferrals: {len(loaded['deferrals'])}")
    assert n == 30
    ids = [g["id"] for g in loaded["goals"]]
    assert ids == [f"G30-{i:03d}" for i in range(1, 31)], "goal IDs out of order"
    # cross-check: every dependency references an existing goal
    for g in loaded["goals"]:
        for d in g["dependencies"]:
            assert d in ids, f"unknown dep {d} in {g['id']}"
    print("registry YAML parses; IDs ordered; dependencies resolvable; DAG acyclic.")
    print(f"wrote: {master_path}")
    print(f"wrote: {reg_path}")


if __name__ == "__main__":
    main()
