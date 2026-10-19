#!/usr/bin/env python3
"""Write REPORT.md, verdicts.svg, findings.yaml and report.pdf from verdicts.jsonl."""
from __future__ import annotations
import json, collections, re
from pathlib import Path

CASE = Path(__file__).resolve().parents[1]
V = [json.loads(l) for l in open(CASE / "verdicts.jsonl")]
UN = json.load(open(CASE / "unaudited_ids.json"))
SHA = "d0f70c0a09"
ORDER = ["replicated", "strong", "moderate", "malformed", "enum_other"]
LABEL = {"replicated": "replicated", "strong": "strong", "moderate": "moderate (not in schema)",
         "malformed": "malformed (n/a, prose, missing)", "enum_other": "anecdotal (beyond scope)"}


def cl(v):
    return v["class"] if v["class"] in ("replicated", "strong", "moderate", "enum_other") else "malformed"


by = collections.defaultdict(list)
for v in V:
    by[cl(v)].append(v)
VERD = ["validated", "validated_with_caveats", "unvalidated", "contradicted"]
tab = {c: collections.Counter(v["verdict"] for v in by[c]) for c in ORDER}


def cnt(L, f):
    return sum(1 for v in L if f(v))


raw = collections.Counter(v["strength_claimed"] if v["class"].startswith("malformed") else None for v in V)
na = raw["n/a"]
miss = cnt(V, lambda v: v["class"] == "malformed_missing")
perr = cnt(V, lambda v: v["class"] == "malformed_parse_error")
other = cnt(by["malformed"], lambda v: v["class"] == "malformed_other")
prose = cnt(by["malformed"], lambda v: v["class"] == "malformed_other" and len(str(v["strength_claimed"])) > 30)
strongish = cnt(by["malformed"], lambda v: v["class"] == "malformed_other" and len(str(v["strength_claimed"])) > 30 and re.search("strong|decisive|replicat", str(v["strength_claimed"]), re.I))
changes = [v for v in V if v.get("recommended_strength") and v["recommended_strength"] != v["strength_claimed"] and cl(v) != "malformed"]
strong_changes = [v for v in changes if cl(v) == "strong"]
rep_changes = [v for v in changes if cl(v) == "replicated"]
mod_to_rep = [v for v in changes if cl(v) == "moderate" and v["recommended_strength"] == "replicated"]
mod_to_pre = [v for v in changes if cl(v) == "moderate" and v["recommended_strength"] == "preliminary"]
strong = by["strong"]
ind = {c: [cnt(by[c], lambda v, x=x: v["independence_ok"] is x) for x in (True, False, None)] for c in ORDER}
dig = {c: [cnt(by[c], lambda v, x=x: v["digests_ok"] is x) for x in (True, False, None)] for c in ORDER}
runs = {c: cnt(by[c], lambda v: (v.get("runs_declared") or 0) > 0) for c in ORDER}
rep_s = collections.Counter(v.get("replay_status") for v in V if "replay_status" in v)
rep_pass = cnt(V, lambda v: v["replay_ok"] is True)
mutc = [v["evidence_id"] for v in V if "run_content_modified_after_add" in v["flags"]]
mutm = [v["evidence_id"] for v in V if "run_metadata_modified_after_add" in v["flags"]]
audited = len(V)
core = sum(len(by[c]) for c in ("replicated", "strong", "moderate"))

# ---------------------------------------------------------------- svg
W, H = 860, 330
cols = {"validated": "#2a9d8f", "validated_with_caveats": "#e9c46a", "unvalidated": "#e76f51", "contradicted": "#6d2e46"}
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="sans-serif" font-size="12">',
       '<rect width="100%" height="100%" fill="#ffffff"/>',
       '<text x="20" y="24" font-size="15" font-weight="bold">Slice C: verdicts by strength label (ledger/evidence, %d audited records)</text>' % audited]
y0, bh, gap, x0, scale = 52, 30, 14, 230, 560
mx = max(len(by[c]) for c in ORDER)
for i, c in enumerate(ORDER):
    y = y0 + i * (bh + gap)
    svg.append(f'<text x="{x0-8}" y="{y+19}" text-anchor="end">{LABEL[c]} ({len(by[c])})</text>')
    x = x0
    for vd in VERD:
        n = tab[c][vd]
        if n:
            w = n / mx * scale
            svg.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{bh}" fill="{cols[vd]}"/>')
            if w > 22:
                svg.append(f'<text x="{x+w/2:.1f}" y="{y+19}" text-anchor="middle" fill="#111">{n}</text>')
            x += w
    ch = [v for v in changes if cl(v) == c] if c != "malformed" else []
    if ch:
        svg.append(f'<text x="{x+8:.1f}" y="{y+19}" fill="#444">{len(ch)} downgrade rec.</text>')
ly = y0 + len(ORDER) * (bh + gap) + 8
for j, vd in enumerate(VERD):
    svg.append(f'<rect x="{20+j*205}" y="{ly}" width="14" height="14" fill="{cols[vd]}"/><text x="{40+j*205}" y="{ly+12}">{vd}</text>')
svg.append(f'<text x="20" y="{ly+40}" fill="#444">0 records reached "validated": none has digests, independent reviewer artifacts and a replay or recomputation all at once.</text>')
svg.append('</svg>')
(CASE / "verdicts.svg").write_text("\n".join(svg))

# ---------------------------------------------------------------- findings.yaml
n_strong_noind = ind["strong"][1] + ind["strong"][2]
F = [
    ("F1", "major", "B7", "Run records modified in place after first commit. %d evidence records cite runs whose result or log files (raw-result, stdout, analysis) changed after they were added (%s); %d more cite runs with manifest-only edits. AGENTS.md says records are immutable and a defect is superseded by a new run. EV-ECDLP-284817 / EV-ECDLP-fd61e4 cite RUN-SEMAEV-f48dd1-grid, whose raw-results.json and analysis.yaml were rewritten by three commits on 2026-08-07 (metric correction, pseudo-replication correction). The EV-IC-002 edits are the declared duplicate-id repair (CORR-20260802-004)." % (len(mutc), ", ".join(mutc), len(mutm)),
     "Supersede the corrected runs under new RUN ids and rebind the evidence records through corrections; do not edit the old runs. The Coordinator decides."),
    ("F2", "major", "B7", "Strength vocabulary is not the schema's. schemas/evidence.schema.json allows {anecdotal, preliminary, replicated, strong, inconclusive, contradictory}. %d records say 'moderate', %d say 'n/a', %d carry other out-of-vocabulary values (%d of them long prose, %d of which read as strong, decisive or replicated), %d have no strength field and 1 does not parse. The brief counted 63 records reading 'n'; the tree has %d reading 'n/a'." % (len(by["moderate"]), na, other, prose, strongish, miss, na),
     "Coordinator to assign a schema value to each (recommended_strength in verdicts.jsonl gives the ceiling the evidence supports) or amend the enum by decision record."),
    ("F3", "major", "B7", "Most 'strong' labels have no cited independent reviewer. Of %d strong records, %d cite independent reviewer artifacts that resolve on disk, %d name the Coordinator only or nothing, and %d assert independence in prose without a cited artifact. %d strong records are recommended down: %s." % (len(strong), ind["strong"][0], ind["strong"][1], ind["strong"][2], len(strong_changes), ", ".join("%s->%s" % (v["evidence_id"], v["recommended_strength"]) for v in strong_changes)),
     "Coordinator to apply or reject the recommended downgrades; independent review is required by AGENTS.md before a claim-changing result."),
    ("F4", "major", "B7", "EV-ECDLP-81f4d4 (strong) cites RUN-ECDLP-8e13c2, which does not exist under experiments/*/runs/ (it appears only as `predecessor_run` in a later task's manifest); EV-SIG-008 cites five RUN-EXP-SIG-008-* ids that do not resolve.",
     "Supply the run records or relabel the evidence as unverified; the audit cannot resolve them."),
    ("F5", "minor", "B7", "EV-HAWK-af783e does not parse as YAML (line 48); EV-XEDN-005 and EV-XEDN-006 are stubs holding only claim_tier. Tools that load ledger/evidence cannot read them or find no strength.",
     "Re-record under new ids; records are immutable."),
    ("F6", "minor", "B7", "Digest coverage is thin. Only %d of %d audited records have a sha256 declared in a cited run record that could be re-verified; %d such records verified, %d did not (EV-CERTBIN-091c56 and EV-ICPERF-433fa5: code inputs changed after the run, bench.py matches neither its declared nor its frozen digest)." % (cnt(V, lambda v: v["digests_ok"] is not None), audited, cnt(V, lambda v: v["digests_ok"] is True), cnt(V, lambda v: v["digests_ok"] is False)),
     "Declare file digests in run manifests; pin code inputs by commit."),
    ("F7", "minor", "B8", "EV-ECDLP-284817 defines oracle_marginal_ratio as candidates_verified_B / candidates_verified_C. Recomputed from raw-results.json that ratio is 3.108 per group (2.53 pooled); the stated 3.754 +- 3.187 [1.36, 11.237] reproduces only as the mean over groups of per-cell ratios. Direction unchanged.",
     "State the metric as mean of per-cell ratios."),
    ("F8", "minor", "B7", "Audit instrument limits, disclosed: the digest walker produced 3 false mismatches (spec/snapshot digests beside file digests), found by hand and overridden; the first replay attempt was void (empty sparse checkout, all 40 not_covered, kept as *_attempt1_void_*); the replay normaliser was too narrow and 3 of its fails were re-diffed by hand (timestamps and platform only). Replay covers %d of 40 sampled records." % (rep_pass),
     "None for the ledger; a re-audit is a new SHF case."),
]
claims = []
for c, cid in (("replicated", "C1"), ("strong", "C2"), ("moderate", "C3"), ("malformed", "C4")):
    L = by[c]
    rec = collections.Counter(v["recommended_strength"] for v in L)
    if c == "replicated":
        verdict, scoped = "overclaimed", "reproduced on disk for %d of %d; %d lack any second run or cited reproduction" % (len(L) - len(rep_changes), len(L), len(rep_changes))
        fids = ["F1", "F6"]
    elif c == "strong":
        verdict, scoped = "overclaimed", "at most replicated/preliminary where recommended (%d records); the rest unconfirmed, not disproved" % len(strong_changes)
        fids = ["F1", "F3", "F4", "F7"]
    elif c == "moderate":
        verdict, scoped = "unsupported", ""
        fids = ["F2", "F6"]
    else:
        verdict, scoped = "unsupported", ""
        fids = ["F2", "F4", "F5"]
    claims.append((cid, c, len(L), verdict, scoped, fids))

def y(s):
    return json.dumps(s)

lines = ["# Slice C case; verdicts per record are in verdicts.jsonl; check-case passes.",
         "sheriff_case:", "  schema: sheriff.case/v1", f"  id: {CASE.name}",
         "  target: ledger/evidence of crypto-autoresearcher at origin/main %s (sibling repositories are other slices)" % SHA,
         "  prior: see PRIOR.md, written before any record was read",
         "  readers:",
         "    - {role: validator-sweep, model: claude-haiku-5-5, joint: \"B7 mechanical: run/ref/digest resolution, immutability from git, nonce-sampled replay\", report: shards/}",
         "    - {role: sheriff (session), model: claude-sonnet-5-5, joint: \"B1/B6/B8 statement fidelity, independence, strength labels, flagged re-checks, verdicts\", report: REPORT.md}",
         "  claims:"]
for cid, c, n, verdict, scoped, fids in claims:
    lines += [f"    - id: {cid}", f"      text: {y('Evidence records labelled %s (%d audited) carry that label with supporting runs, digests and independent replication' % (c, n))}",
              f"      location: ledger/evidence ({c})", f"      verdict: {verdict}"]
    if scoped:
        lines.append(f"      scoped_to: {y(scoped)}")
    lines += ["      beats: {B2: n/a, B3: n/a, B4: not_covered, B5: not_covered, B6: not_covered, B7: fail, B8: not_covered}",
              "      findings: [%s]" % ", ".join(fids), "      evidence: [verdicts.jsonl, census.json]"]
lines.append("  findings:")
for fid, sev, beat, what, fix in F:
    lines += [f"    - id: {fid}", f"      severity: {sev}", f"      beat: {beat}", f"      what: {y(what)}", f"      fix: {y(fix)}"]
(CASE / "findings.yaml").write_text("\n".join(lines) + "\n")

# ---------------------------------------------------------------- REPORT.md
md = []
A = md.append
A(f"# Sheriff case {CASE.name}: ledger/evidence, slice C\n")
A(f"Audit record of `ledger/evidence/` in `aburan28/crypto-autoresearcher` at `origin/main` `{SHA}`. It changes no research state, edits no record and applies no downgrade; `recommended_strength` is a recommendation to the Coordinator. Per-record verdicts: `verdicts.jsonl` ({audited} rows). Sibling repositories `crypto` and `cryptanalysis` are other slices and are not checked out here.\n")
A("## Headline\n")
A(f"- **No record reached `validated`.** {audited} records audited; every one is `validated_with_caveats` or `unvalidated` ({sum(tab[c]['unvalidated'] for c in ORDER)} unvalidated). No record has digests, a cited independent reviewer artifact and a replay or recomputation all at once.")
A(f"- **Downgrades recommended:** {len(strong_changes)} of {len(strong)} `strong`, {len(rep_changes)} of {len(by['replicated'])} `replicated`; the {len(by['moderate'])} `moderate` records use a label the schema does not have ({len(mod_to_rep)} map to `replicated`, {len(mod_to_pre)} to `preliminary`); {len(by['malformed'])} malformed labels need a Coordinator assignment.")
A(f"- **Independence is the weak joint.** Of {len(strong)} `strong` records, {ind['strong'][0]} cite independent reviewer artifacts; {ind['strong'][1]} are Coordinator-only or unreviewed; {ind['strong'][2]} assert independence in prose only.")
A(f"- **Run records were edited in place** for {len(mutc)} evidence records (F1), including the `strong` EV-ECDLP-284817 and EV-ECDLP-fd61e4.")
A("- **Counts differ from the brief** (see Census). Where this audit's count differs it is the on-disk count.\n")
A("## Prior\n")
A("Written before reading any record (`PRIOR.md`). Held: most `replicated` rest on one instrument; `strong` outruns its cited reviewers; `moderate` is schema-invalid; digests rarely declared; the brief's counts do not match. Not anticipated: records cite their evidence by prose path or task id rather than `run_ids` (my first pass wrongly marked 55 such records unvalidated; fixed and disclosed below), and the run-record rewrites.\n")
A("## Census\n")
A("| class | brief | on disk | note |\n| --- | --- | --- | --- |")
A(f"| replicated | ~101 | {len(by['replicated'])} | |\n| strong | 41 | {len(by['strong'])} | |\n| moderate | 39 | {len(by['moderate'])} | label not in schema |\n| strength reads `n` | 63 | {na} read `n/a` | plus {other} other non-enum values ({prose} long prose), {miss} missing, {perr} unparsable (malformed total {len(by['malformed'])}) |")
A(f"| preliminary | 301 | {len(UN['preliminary'])} | listed, not audited |\n| inconclusive | 123 | {len(UN['inconclusive'])} | listed, not audited |")
A(f"\n`anecdotal` ({len(by['enum_other'])} records) is a valid schema value that my harness bucketed with the malformed; they were audited and are shown separately. Total audited {audited}; core scope (replicated+strong+moderate) {core}.\n")
A("## Verdicts\n")
A("| class | n | validated | with caveats | unvalidated | contradicted |\n| --- | --- | --- | --- | --- | --- |")
for c in ORDER:
    A(f"| {LABEL[c]} | {len(by[c])} | {tab[c]['validated']} | {tab[c]['validated_with_caveats']} | {tab[c]['unvalidated']} | {tab[c]['contradicted']} |")
A("\n![verdicts](verdicts.svg)\n")
A("`validated_with_caveats` is the default when everything cited resolves and nothing failed; it does **not** mean the claim was checked beyond that. Nothing is `contradicted`: the one record I recomputed (EV-ECDLP-284817) reproduces, with a metric-definition caveat.\n")
A("### Per-class checks\n")
A("| class | with run_ids | digests ok / bad / none | independence ok / no / asserted-only |\n| --- | --- | --- | --- |")
for c in ORDER:
    A(f"| {LABEL[c]} | {runs[c]} | {dig[c][0]} / {dig[c][1]} / {dig[c][2]} | {ind[c][0]} / {ind[c][1]} / {ind[c][2]} |")
A("\n`independence_ok` is a cited-artifact check: true only when a non-Coordinator reviewer is named and its report or task resolves on disk. I did not read each reviewer's authorship; instrument and author difference is therefore established for the cited artifacts, not proven. Theoretical records with no review cited are `false`.\n")
A("## Recommended strength changes (not applied)\n")
A("| evidence | claimed | recommended | basis |\n| --- | --- | --- | --- |")
for v in strong_changes + rep_changes:
    A(f"| {v['evidence_id']} | {v['strength_claimed']} | {v['recommended_strength']} | {v['downgrade_basis']} |")
A(f"\nThe {len(mod_to_rep)+len(mod_to_pre)} `moderate` records and the malformed ones are in `verdicts.jsonl` (`recommended_strength`, `strength_ceiling_supported`). Rule: empirical `replicated` needs a second run or experiment or a cited independent reproduction; `strong` additionally needs a cited independent reviewer, else `replicated`. If the Coordinator's policy does not require independent review for `strong`, {sum(1 for v in strong_changes if v['recommended_strength']=='replicated')} of the strong downgrades fall away. Theoretical or analytical records keep their label as **unconfirmed**, not endorsed: the derivations were not re-derived here.\n")
A("## Findings (blockers first; none is a blocker)\n")
for fid, sev, beat, what, fix in F:
    A(f"**{fid} ({sev}, {beat}).** {what}  \n*Would fix:* {fix}\n")
A("## Per-beat results\n")
A("- **B1 claim inventory:** one claim per label class (C1-C4 in `findings.yaml`); per-record statements are in `verdicts.jsonl`.")
A("- **B2 execution proofs, zk:** n/a; no audited record cites a verifier. Execution proofs are open (docs/execution-proof-chain.md), so nothing here is execution-verified.")
A("- **B3 Lean:** n/a; none of the audited records references a `.lean` file, so `statement_fidelity_ok` is not a Lean check anywhere. It is null except EV-ECDLP-284817 (false, metric definition). Statement fidelity beyond that was not covered for the remaining records.")
A("- **B4 certificates:** `certificate_refs` were checked for existence only; no certificate was re-verified. `recomputed_ok` is null for all records but EV-ECDLP-284817.")
A(f"- **B5 cost accounting:** not covered (no matched-rho comparison audited).")
A("- **B6 statistics/prereg:** not covered, except the pseudo-replication point inside EV-ECDLP-284817 (n_eff=8 of 40).")
A(f"- **B7 provenance:** run resolution, digests, immutability from git history; F1-F6.")
A("- **B8 numbers:** a 4+-digit decimal trace (not a recompute) is recorded in each record's notes.\n")
A("## Replay\n")
A(f"Seed committed before any replay (`replay_seed.txt`, commit `c958749f69`). Eligible = records whose cited run has `command.txt`: 113. 40 sampled with `random.Random(int(nonce,16)).sample` over the sorted ids. Results (Haiku shards `replay_out*.jsonl`): {dict(rep_s)}. {rep_pass} replays reproduced their committed result files; 3 flagged 'fail' were re-run by me and differ only in timestamps, platform, python version and a regenerated `preregistered_at` (EV-FALSIFY-440677, EV-SEMBIN-07960c, EV-MONO-d90e9c). `not_covered` dominates because most commands are not a single repo-local python3 script (multi-line, shell, rust, external paths) and 7 failed on environment (absolute scratch paths, missing env vars, a perf meter self-test). A replay proves nothing about the 308 records not sampled; 40 of 113 eligible gives low power against sparse fabrication.\n")
A("## Division of labour\n")
A("Haiku 5.5 (`validator-sweep`, frozen command cards, no interpretation): ran the audit harness over four shards, ran the replay shards. Sonnet 5.5 (this session): wrote the harness and composer, re-checked every flag (5 digest mismatches: 3 were instrument false positives, 2 real code drift; 3 replay fails: noise; the run rewrites; the unresolved runs), recomputed EV-ECDLP-284817 from raw cells, read about 12 records for strength and fidelity, and made every verdict. The first replay attempt was void because my script's sparse checkout failed (`git sparse-checkout init -q`), leaving every row not_covered; the outputs are kept as `*_attempt1_void_*`.\n")
A("## Not covered, and what would cover it\n")
A("- Re-derivation of metrics for all records except one: needs a per-record recomputation script; start with `ledger/evidence` records citing `raw-result.json` with cell-level data.\n- Reviewer authorship and instrument identity: read each cited `validation_report.yaml` / `red_team_report.yaml`.\n- Theoretical derivations: independent re-derivation.\n- `python3 tools/sheriff.py sweep --target all --deep` (Lean builds, ledger validator, merge hygiene) and the sibling repositories: other slices.\n- Replay of non-python commands and runs needing external data or credentials.\n- The pending runbook-session audit `RBS-XEDN-a7cd25` (`tools/runbook.py pending-audits`) concerns EXP-XEDN-0c0182; I did not run it, and EV-XEDN-005/006 are stubs that cite nothing.\n")
A("## What this case does not establish\n")
A("That any record's science is right or wrong. `validated_with_caveats` means the cited artifacts exist and nothing failed, not that the claim was verified. A bounded replay, a zero-hit count or an unread record proves no absence. Recommended downgrades are a reading of the on-disk evidence under the stated rules, for the Coordinator to apply or reject.\n")
A("## Appendix: records listed, not audited\n")
A(f"Preliminary ({len(UN['preliminary'])}): " + ", ".join(UN["preliminary"]) + "\n")
A(f"Inconclusive ({len(UN['inconclusive'])}): " + ", ".join(UN["inconclusive"]) + "\n")
(CASE / "REPORT.md").write_text("\n".join(md))

# ---------------------------------------------------------------- PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, String
from xml.sax.saxutils import escape

ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=8.6, leading=11)
small = ParagraphStyle("s", parent=body, fontSize=7.2, leading=9)
h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=15)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=11.5)
story = []


def inline(t):
    t = escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", t)
    t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
    return t


i = 0
mdl = md if False else "\n".join(md).split("\n")
while i < len(mdl):
    ln = mdl[i]
    if ln.startswith("# "):
        story.append(Paragraph(inline(ln[2:]), h1))
    elif ln.startswith("## ") or ln.startswith("### "):
        story.append(Paragraph(inline(ln.lstrip("# ")), h2))
    elif ln.startswith("!["):
        d = Drawing(520, 210)
        d.add(String(0, 196, "Verdicts by strength label (%d audited)" % audited, fontSize=9))
        mxn = max(len(by[c]) for c in ORDER)
        for k, c in enumerate(ORDER):
            yy = 160 - k * 34
            d.add(String(0, yy + 8, "%s (%d)" % (LABEL[c], len(by[c])), fontSize=7))
            x = 150
            for vd in VERD:
                n = tab[c][vd]
                if n:
                    w = n / mxn * 330
                    d.add(Rect(x, yy, w, 22, fillColor=colors.HexColor(cols[vd]), strokeColor=None))
                    if w > 16:
                        d.add(String(x + w / 2 - 4, yy + 7, str(n), fontSize=7))
                    x += w
        for j, vd in enumerate(VERD):
            d.add(Rect(j * 130, 0, 9, 9, fillColor=colors.HexColor(cols[vd]), strokeColor=None))
            d.add(String(j * 130 + 12, 1, vd, fontSize=6.5))
        story.append(d)
    elif ln.startswith("|"):
        rows = []
        while i < len(mdl) and mdl[i].startswith("|"):
            if not re.match(r"^\|[\s:|-]+\|$", mdl[i]):
                rows.append([Paragraph(inline(c.strip()), small) for c in mdl[i].strip("|").split("|")])
            i += 1
        nc = max(len(r) for r in rows)
        rows = [r + [Paragraph("", small)] * (nc - len(r)) for r in rows]
        w = (A4[0] - 3.2 * 28.35) / nc
        t = Table(rows, colWidths=[w] * nc, repeatRows=1)
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        story.append(t)
        continue
    elif ln.startswith("- "):
        story.append(Paragraph("• " + inline(ln[2:]), body))
    elif ln.strip():
        story.append(Paragraph(inline(ln), small if ln.startswith(("Preliminary (", "Inconclusive (")) else body))
    i += 1
SimpleDocTemplate(str(CASE / "report.pdf"), pagesize=A4, leftMargin=45, rightMargin=45, topMargin=45, bottomMargin=45,
                  title=f"Sheriff case {CASE.name}").build(story)
print("wrote REPORT.md verdicts.svg findings.yaml report.pdf")
