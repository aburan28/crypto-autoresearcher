"""Compose findings.yaml (sheriff.case/v1) for SHF-20261028-0f3f64 from the four
reader reports, the session's own checks and the sweep lead dispositions.
Reader findings are copied verbatim (id, severity, what, evidence, fix); the
session assigns each a beat and composes the claim verdicts."""
import yaml
from pathlib import Path

CASE = Path(__file__).resolve().parents[2]
REL = "research/sheriff/SHF-20261028-0f3f64"


def reader(name):
    return yaml.safe_load((CASE / "readers" / f"{name}.yaml").read_text())


R = {n: reader(n) for n in ("stark", "ledger", "cryptanalysis", "papers")}

BEAT = {"S2N": "B2", "LGN": "B7", "CAN": "B5", "PPN": "B8"}
BEAT_OVERRIDE = {"CAN-3": "B6", "CAN-4": "B6", "PPN-5": "B7", "PPN-6": "B7", "S2N-8": "B2"}

findings = []
for name, rep in R.items():
    for f in rep.get("findings") or []:
        fid = f["id"]
        ev = f.get("evidence") or []
        findings.append({
            "id": fid,
            "beat": BEAT_OVERRIDE.get(fid, BEAT[fid.split("-")[0]]),
            "severity": f["severity"],
            "reader": f"readers/{name}.yaml",
            "what": f["what"],
            "evidence": ev if isinstance(ev, list) else [ev],
            "fix": f.get("fix") or "see reader report",
        })

findings += [
    {"id": "LN9-R", "beat": "B3", "severity": "minor", "reader": "readers/ledger.yaml (session confirmed)",
     "what": ("L-N9 still open on main: formal/CryptoResearch/Quotient/TranslationDescent.lean:31 is still named "
              "translation_descends_iff_two_torsion and its docstring (lines 27-30) says 'descends', while the theorem "
              "proves commutation of τ_T with ι_S in an additive group; the header (lines 12-21) discloses the gap. "
              "The rename PR (#2496) is not merged; the file is unchanged since 418825c73d (2026-10-16)."),
     "evidence": ["formal/CryptoResearch/Quotient/TranslationDescent.lean"],
     "fix": "merge a rename (e.g. translation_commutes_with_iota_iff_two_torsion) with a superseding target record; keep the header disclosure"},
    {"id": "SES-1", "beat": "B8", "severity": "minor", "reader": "session",
     "what": ("Two historical records use execution-proof wording for answer/row verification: "
              "experiments/EXP-SGCP-EMBED-002/development-result-v1.md:8 heads a section 'Verified execution' (row validity and "
              "independent reconstruction, no execution proof) and ledger/evidence/EV-ICINV-8afb64.yaml:58 says "
              "'triple-independently-verified execution'. Both predate the 2026-10-16 execution-proof rule; the other ten "
              "zk.proof_language leads negate the term and are dismissed."),
     "evidence": ["experiments/EXP-SGCP-EMBED-002/development-result-v1.md", "ledger/evidence/EV-ICINV-8afb64.yaml"],
     "fix": "an additive correction record relabelling both as verified answers/rows, not verified execution (records stay immutable)"},
]
FIND = {f["id"]: f for f in findings}


def sv(name, cid):
    for s in R[name].get("suggested_verdicts") or []:
        if s.get("claim") == cid:
            return s
    raise KeyError(cid)


def claim(cid, text, location, verdict, beats, evidence, fids, scoped=None, extra=None):
    c = {"id": cid, "text": text, "location": location, "verdict": verdict, "beats": beats,
         "evidence": evidence, "findings": fids}
    if scoped:
        c["scoped_to"] = scoped
    if extra:
        c.update(extra)
    for f in fids:
        assert f in FIND, f
    return c


ST = f"{REL}/readers/stark.yaml"
STS = f"{REL}/scripts/readers/stark/stark_rederive.out"
LG = f"{REL}/readers/ledger.yaml"
LGO = f"{REL}/scripts/readers/ledger/out"
CA = f"{REL}/readers/cryptanalysis.yaml"
CAO = f"{REL}/scripts/readers/cryptanalysis/out"
NOCARGO = ("cargo test --release --lib zk::stark not run: the session's permission policy refused execution of "
           "code from the external crypto clone")

claims = []
for cid, text in [("C-STARK-1", "the OOD values f(z), f(ωz), Comp(z) are bound into the Fiat-Shamir transcript"),
                  ("C-STARK-2", "the verifier recomputes D(x) from the opened values"),
                  ("C-STARK-3", "the DEEP degree bound and the (λ0 + λ1·x) adjustment are correct"),
                  ("C-STARK-4", "the stated conjectured soundness ε (2^-240 default, 2^-40 fast, ε_field < 2^-215, 128-bit SHA-256 cap)"),
                  ("C-STARK-5", "the negative tests exercise each verifier check")]:
    s = sv("stark", cid)
    v = s["verdict"]
    claims.append(claim(cid, text, "crypto#2439; crypto:src/zk/stark_v2.rs", v,
                        {"B2": "fail" if v == "overclaimed" else "not_covered"},
                        [ST, STS, "crypto:src/zk/stark_v2.rs"], s.get("findings") or [],
                        scoped=s["scoped_to"] + " " + NOCARGO + "."))

for cid, text in [("C-MAN-1", "complete_manifest() never invents values"),
                  ("C-MAN-2", "complete_manifest() refuses contradictions between the driver envelope and the plan"),
                  ("C-MAN-3", "complete_manifest() gates on validate_ledger's check_run"),
                  ("C-MAN-4", "complete_manifest() preserves the driver's bytes")]:
    s = sv("ledger", cid)
    v = s["verdict"]
    claims.append(claim(cid, text, "crypto-autoresearcher#2488; tools/experiment_execution.py:247", v,
                        {"B7": "fail" if v == "overclaimed" else "pass"},
                        [LG, f"{LGO}/complete_manifest_adversarial.json", "tools/experiment_execution.py"],
                        s.get("findings") or [], scoped=s["scoped_to"]))

for cid, text, loc in [("C-LED-1", "PR #2497 took validate_ledger new errors from 143 to 126", "crypto-autoresearcher#2497; ledger/decisions/DEC-20261023-5c9671.yaml"),
                       ("C-LED-2", "the AES and five flat-run manifest_v2 records are faithful to the archived bytes", "crypto-autoresearcher#2497; experiments/EXP-AES-14352a/runs/*/manifest_v2.yaml"),
                       ("C-LED-3", "the rulings DEC-20261023-5c9671 left in place are justified", "ledger/decisions/DEC-20261023-5c9671.yaml")]:
    s = sv("ledger", cid)
    v = s["verdict"]
    claims.append(claim(cid, text, loc, v, {"B7": "fail" if v == "overclaimed" else "pass"},
                        [LG, f"{LGO}/validate_ledger_main.txt", "ledger/decisions/DEC-20261023-5c9671.yaml"],
                        s.get("findings") or [], scoped=s["scoped_to"]))

kob_beats = {"C-KOB-1": {"B7": "not_covered"}, "C-KOB-2": {"B5": "pass", "B6": "pass", "B7": "not_covered"},
             "C-KOB-3": {"B5": "pass", "B8": "pass"}, "C-KOB-4": {"B5": "pass", "B8": "pass"}}
kob_ev = {"C-KOB-1": [CA, "cryptanalysis:experiments/koblitz-n83-opcounts-20261023/run_github_39882571652/SHA256SUMS"],
          "C-KOB-2": [CA, f"{CAO}/reimpl_result.json", f"{CAO}/run_reimpl.stdout.txt"],
          "C-KOB-3": [CA, f"{CAO}/doc_numbers_check.json", "cryptanalysis:docs/ic/baselines.json", "cryptanalysis:docs/ic/BASELINES.md"],
          "C-KOB-4": [CA, f"{CAO}/reimpl_result.json", "cryptanalysis:docs/ic/BASELINES.md"]}
for s in R["cryptanalysis"]["suggested_verdicts"]:
    cid = s["claim"]
    v = s["verdict"]
    claims.append(claim(cid, s["statement"], "cryptanalysis#1077; cryptanalysis:experiments/koblitz-n83-opcounts-20261023",
                        v, kob_beats[cid], kob_ev[cid], s.get("findings") or [], scoped=s["scoped_to"]))

claims += [
    claim("C-LEAN-1", "formal/CryptoResearch/Quotient/TranslationDescent.lean builds on the pinned toolchain with standard axioms only",
          "formal/CryptoResearch/Quotient/TranslationDescent.lean; formal/targets/quotient-translation-descent.yaml",
          "not_covered", {"B3": "not_covered"}, ["formal/CryptoResearch/Quotient/TranslationDescent.lean"], [],
          extra={"not_covered_reason": ("no lake/lean in the container; installing elan (elan-init.sh) was refused by the session's "
                                        "permission policy as external code. Text scan: no sorry/axiom/native_decide; imports "
                                        "Mathlib.Tactic.Abel only; file unchanged since 418825c73d, the commit SHF-20261017-e4d7f6 built."),
                 "would_cover": "./formal/setup.sh (pinned v4.35.0-rc1, Mathlib 7fa22735); lake build CryptoResearch.Quotient.TranslationDescent; lake env lean AxiomAudit.lean"}),
    claim("C-LEAN-2", "translation_descends_iff_two_torsion: translation by T descends through the degree-2 quotient iff 2T = 0 (name and docstring)",
          "formal/CryptoResearch/Quotient/TranslationDescent.lean:27-31", "overclaimed", {"B3": "fail"},
          ["formal/CryptoResearch/Quotient/TranslationDescent.lean"], ["LN9-R"],
          scoped="the theorem proves τ_T commutes with ι_S = [-1]∘τ_S iff 2•T = 0 in any additive commutative group; descent is argued in prose only (header discloses)"),
    claim("C-DEF-1", "the rank-finder producer's §5a band is 'Not computable from this run' (counters not yet ported), as disclosed",
          "cryptanalysis:docs/ic/baselines.json (rankfinder row, open[5])", "upheld_scoped", {"B5": "pass", "B8": "pass"},
          [CA, "cryptanalysis:docs/ic/baselines.json"], [],
          scoped="the disclosure is accurate: no count or band artifact exists for koblitz-n83-rankfinder-20261021 and the stacked band does not transfer to that row; the band itself remains unmeasured"),
    claim("C-DEF-2", "the lean-verification (and validate, main-health) workflows are disabled",
          "SHF-20261017-e4d7f6 CI1; .github/workflows/lean-verification.yml", "not_covered", {"B7": "not_covered"},
          [".github/workflows/lean-verification.yml"], [],
          extra={"not_covered_reason": "the Actions API was not reachable (gh refused, GitHub MCP actions tools not loaded in readers); workflow files still define triggers",
                 "would_cover": "gh api repos/isogeny-labs/crypto-autoresearcher/actions/workflows --jq '.workflows[]|[.name,.state]'"}),
    claim("C-SWEEP", "the deterministic sweep (canary 15/15) caught every planted defect and its leads are dispositioned",
          f"{REL}/sweep.json; {REL}/checks/sweep-home/sweep.json", "upheld_scoped", {"B7": "pass", "B9": "not_covered"},
          [f"{REL}/sweep.json", f"{REL}/checks/sweep-home/sweep.json"], ["SES-1", "LGN-9"],
          scoped=("canary passed in both sweeps; blocker/major/minor leads dispositioned below; 1,124 info-level strong-word and "
                  "metaprogram leads and 412 outside-sparse roots are not_covered (not read)")),
]

prior = []
for name in ("stark", "ledger", "cryptanalysis", "papers"):
    for p in R[name].get("prior_finding_verdicts") or []:
        prior.append({"id": p.get("id"), "verdict": p.get("verdict"), "reader": f"readers/{name}.yaml",
                      "why": p.get("why") or p.get("basis") or p.get("evidence_summary") or ""})
prior += [
    {"id": "L1", "verdict": "fixed", "reader": "session",
     "why": "research/THM_QUOTIENT_DESCENT1.lean is gone; the formal module has no sorry/axiom (text). Build not_covered here (C-LEAN-1); residual L-N9 (LN9-R)."},
    {"id": "L2", "verdict": "fixed", "reader": "session",
     "why": "research/THM_QUOTIENT_DESCENT1.md:17,26-31 takes S ∈ E(k) with a dated correction."},
    {"id": "P6", "verdict": "fixed", "reader": "session",
     "why": "paper.tex cites EXP-SMON-e5cbe6; the six sweep untraced-number leads all trace to raw-result.json as sums, a rounding or tokenisation (scripts/session/semaev_untraced.out)."},
    {"id": "X3", "verdict": "fixed", "reader": "session",
     "why": "sweep records instrument path/sha256/head; canary 15/15 caught, 0 missed, 0 false positives in both sweeps."},
    {"id": "I1", "verdict": "fixed", "reader": "session",
     "why": "sweep.json repos[*] now carry head_tree and worktree_digest (distinct per repo), not the constant tree_digest."},
]
for p in prior:
    if p["id"] == "L-N9":
        p["verdict"] = "not_fixed"
        p["why"] = ("still open as the brief expected: name and docstring unchanged (LN9-R); the ledger reader's "
                    "'partially_fixed' credits disclosure text added beside two citations. #2496 unmerged.")
    if p["id"] == "X1":
        p["why"] = (p["why"] or "") + " The two named sessions are audited; four new sessions await audit (LGN-9)."

leads = [
    {"rule": "lean.sorry, lean.axiom (13 blockers)", "repo": "crypto-autoresearcher", "disposition": "dismissed",
     "why": "all under research/lean_review_evidence_20261018/reports/*/artifacts/control-sources/: planted negative-control fixtures of the Lean review gate, never imported by formal/"},
    {"rule": "lean.no_axiom_audit (30), lean.no_ci (68), lean.vacuous (29)", "repo": "crypto-autoresearcher", "disposition": "dismissed",
     "why": "all but formal/smoke and one docs/reports evidence file are the same control-source fixtures; formal/smoke is a one-import smoke project with no theorems"},
    {"rule": "lean.unpinned", "repo": "crypto-autoresearcher", "path": "docs/reports/2026-10-22-semaev-first-fall-replay/evidence/finite-equation-lean-eval.lean",
     "disposition": "not_covered", "why": "66 unpinned #eval evidence files; reproducibility of that replay not checked here"},
    {"rule": "paper.untraced_number (6)", "repo": "crypto-autoresearcher", "path": "papers/semaev-conservation-specialization/paper.tex",
     "disposition": "dismissed", "why": "all six trace (scripts/session/semaev_untraced.out)"},
    {"rule": "zk.proof_language (12)", "repo": "crypto-autoresearcher", "disposition": "confirmed (2) / dismissed (10)",
     "why": "two positive historical uses become SES-1; ten negate or scope the term"},
    {"rule": "zk.no_negative_test", "repo": "crypto", "path": "src/zk/groth16.rs", "disposition": "confirmed", "why": "S2N-9"},
    {"rule": "zk.discarded_value", "repo": "crypto", "path": "src/zk/plonk.rs:368", "disposition": "confirmed", "why": "S2N-10"},
    {"rule": "lean.sorry/axiom/native_decide", "repo": "crypto, cryptanalysis", "path": "tools/lean/selftest/*",
     "disposition": "dismissed", "why": "proof-gate selftest fixtures by path"},
    {"rule": "check.runbook-pending-audits", "repo": "crypto-autoresearcher", "disposition": "confirmed", "why": "LGN-9"},
    {"rule": "check.ledger", "repo": "crypto-autoresearcher", "disposition": "confirmed", "why": "67 new errors; LGN-1, LGN-8"},
    {"rule": "check.run-source-provenance (advisory)", "repo": "crypto-autoresearcher", "disposition": "not_covered",
     "why": "3,421 unpinned/unreadable legacy manifests listed; not triaged in this case"},
    {"rule": "prose.strong_claim (315 listed + 363 over cap), lean.metaprogram (201)", "repo": "all", "disposition": "not_covered",
     "why": "info-level lead lists not read one by one"},
]

case = {"sheriff_case": {
    "schema": "sheriff.case/v1",
    "id": "SHF-20261028-0f3f64",
    "target": ("all (deep) on origin/main: crypto-autoresearcher b7d5e65b9f, isogeny-labs/crypto 669809d5c6, "
               "isogeny-labs/cryptanalysis f3cce49955; the five named changes (crypto#2439, #2488, #2497, cryptanalysis#1077, "
               "Lean L-N9) and every finding of SHF-20261016-3caa6f and SHF-20261017-e4d7f6"),
    "prior": "prior.md (written before reading any audited change)",
    "supersedes_nothing": "earlier cases stay as written; this is a new case (write-once)",
    "impediments": [
        "isogeny-labs/crypto and cryptanalysis could not be attached with add_repo (refused by the permission policy); read-only partial clones of the public repositories were used, sparse",
        NOCARGO + "; no mutation controls were executed",
        "Lean toolchain install (elan) refused as external code: no Lean build or axiom audit",
        "sibling-repo checkers of tools/sheriff.py were not run (they execute sibling code); the main sweep used --no-checkers and a second sweep ran crypto-autoresearcher checkers only (checks/sweep-home)",
    ],
    "readers": [
        {"role": "validator", "model": "claude-opus-5-5", "joint": "B2 stark_v2 DEEP-ALI verifier, ε, negative tests; S1/S2/V1-V3", "report": "readers/stark.yaml"},
        {"role": "validator", "model": "claude-opus-5-5", "joint": "B7 complete_manifest, ledger counts, manifest_v2 fidelity, rulings; M1/M2/M2-R/CI1/L-N8/L-N9/X1", "report": "readers/ledger.yaml"},
        {"role": "red-team", "model": "claude-opus-5-5", "joint": "B5/B6/B7 cryptanalysis#1077 receipts, band, rho gap; K/R/X findings", "report": "readers/cryptanalysis.yaml"},
        {"role": "validator", "model": "claude-opus-5-5", "joint": "B3/B8 crypto papers and Lean text, ecbench; P/L/E findings", "report": "readers/papers.yaml"},
        {"role": "session (sheriff)", "model": "claude-opus-5-5", "joint": "sweeps, lead dispositions, Lean attempt, spot re-checks of S2N-1, LGN-1, LGN-2, the 29.00 band cell", "report": "REPORT.md"},
    ],
    "original_cases": ["research/sheriff/SHF-20261016-3caa6f", "research/sheriff/SHF-20261017-e4d7f6"],
    "prior_finding_verdicts": prior,
    "claims": claims,
    "findings": findings,
    "lead_dispositions": leads,
}}

class D(yaml.SafeDumper):
    pass
D.add_representer(str, lambda d, s: d.represent_scalar("tag:yaml.org,2002:str", s, style="|" if "\n" in s else None))
header = ("# Sheriff case SHF-20261028-0f3f64. Composed by scripts/session/compose.py from readers/*.yaml.\n"
          "# Paths: bare = crypto-autoresearcher; crypto: / cryptanalysis: = isogeny-labs siblings at the heads in sweep.json.\n")
(CASE / "findings.yaml").write_text(header + yaml.dump(case, Dumper=D, sort_keys=False, allow_unicode=True, width=110))
print(len(claims), "claims;", len(findings), "findings;", len(prior), "prior verdicts")
