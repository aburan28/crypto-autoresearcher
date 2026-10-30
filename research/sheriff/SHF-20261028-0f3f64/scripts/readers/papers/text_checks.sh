#!/usr/bin/env bash
# Read-only text checks for the B3/B7/B8 papers reader of SHF-20261028-0f3f64.
# Uses git, grep, sed, pdftotext and pdfinfo only; executes nothing from the
# crypto clone. Usage: bash text_checks.sh /home/user/crypto <rev> > text_checks.out
set -u
C=${1:?crypto repo}; R=${2:?rev}
g() { git -C "$C" -c gc.auto=0 "$@"; }
s() { g show "$R:$1"; }
hdr() { printf '\n===== %s\n' "$*"; }

hdr "binding"; g rev-parse "$R" origin/main; g log -1 --format='%H %cI %s' "$R"

hdr "P1/P-N1/P-N2: note sources and PDF currency"
g log --format='%h %cI %s' "$R" -- papers/lll-degeneracy-note/lll_degeneracy_note.tex papers/lll-degeneracy-note/lll_degeneracy_note.pdf
pdfinfo "$C/papers/lll-degeneracy-note/lll_degeneracy_note.pdf" | grep -E 'CreationDate|Pages'
pdftotext -layout "$C/papers/lll-degeneracy-note/lll_degeneracy_note.pdf" - | grep -n -E 'Correction \(2026-10-17\)|not isolated|0 / 3|6 / 6|390|catastrophic'
s papers/lll-degeneracy-note/lll_degeneracy_note.tex | sed -n '24,44p;69,87p;163,173p;199,215p'
hdr "probe source and lattice.rs unchanged since the re-run commit (empty stat = unchanged)"
cat <(s research/lll_degeneracy_rerun_20261016/logs/commit.txt)
g diff --stat 97d89f0fd52a7ecb667ac5212494bb91906b9d1f "$R" -- tests/lll_degeneracy_probe.rs src/cryptanalysis/lattice.rs
hdr "num-bigint versions locked by crypto"; s Cargo.lock | grep -n -A1 'name = "num-bigint"'
hdr "analysis note cited by the LLL note (RESEARCH_LLL_GS_ANALYSIS.md §10.1-10.2)"
s research/notes/lattice-hnp/RESEARCH_LLL_GS_ANALYSIS.md | sed -n '258,296p'
g log --format='%h %cI %s' "$R" -- research/notes/lattice-hnp/RESEARCH_LLL_GS_ANALYSIS.md

hdr "P3/P4/P5/P-N4/P-N5/P-N6: structural-completeness"
s papers/structural-completeness/structural_completeness.tex | sed -n '72,88p;145,148p;368,392p;436,445p;960,962p'
s papers/structural-completeness/structural_completeness.tex | grep -n -E 'Total.*3533|mechanically verifiable'
pdftotext -layout "$C/papers/structural-completeness/structural_completeness.pdf" - | grep -n -E '24 476|26 278|336 and 249|330 primes|not yet independently|3533|mechanically'
pdfinfo "$C/papers/structural-completeness/structural_completeness.pdf" | grep -E 'CreationDate'
g log --format='%h %cI %s' "$R" -- papers/structural-completeness/structural_completeness.tex papers/structural-completeness/structural_completeness.pdf
hdr "recount provenance (P-N5)"
for f in exp_zprime_l_residue.py exp_zprime2_generalized_lemma.py thread12_cm73_sweep.gp exp_zdoubleprime_lemma_extended.py; do
  echo "-- $f: last commits"; g log --format='%h %cI %s' "$R" -- "secp256k1_cm_audit/$f" | head -2
done
echo "-- diff 8b6b8c8ba..$R of the four scripts (stat)"; g diff --stat 8b6b8c8ba "$R" -- secp256k1_cm_audit/exp_zprime_l_residue.py secp256k1_cm_audit/exp_zprime2_generalized_lemma.py secp256k1_cm_audit/thread12_cm73_sweep.gp secp256k1_cm_audit/exp_zdoubleprime_lemma_extended.py
echo "-- regenerated output diff 11aa00591..$R"; g diff 11aa00591 "$R" -- papers/structural-completeness/recount/exp_zdoubleprime_lemma_extended.txt
s papers/structural-completeness/recount/README.md | sed -n '3,16p'
hdr "Markdown twin (P-N6)"
s research/notes/cm-isogeny/PAPER_STRUCTURAL_COMPLETENESS.md | sed -n '32,53p'
s research/notes/cm-isogeny/PAPER_STRUCTURAL_COMPLETENESS.md | grep -n -iE 'unconditional|proven|mechanically'

hdr "L3/L4/L-N1/P-N7/L-N7: TreeSplit"
s tools/lean/trusted-native.txt
s research/ic_tree_split_structured_v_20261011/lean/TreeSplit/Leak.lean | sed -n '9,31p'
s research/ic_tree_split_structured_v_20261011/RESULTS.md | sed -n '23p;31,58p'
s research/ic_tree_split_structured_v_20261011/reports/run-20261011T2105Z/report.typ | sed -n '25p;29p'
s research/ic_tree_split_structured_v_20261011/lean/axiom-audit.log | sed -n '1,12p'
echo "-- lean/ diff since the CI-audited commit 22bd479da (stat)"; g diff --stat 22bd479dad938d1d090e3f643bd891f5d2f9b2b1 "$R" -- research/ic_tree_split_structured_v_20261011/lean/

hdr "L5/L-N2/L6/L-N7: conductor_gap"
s research/conductor_gap_cm_pairs_20261010/README.md | sed -n '1,4p;131,158p;195,206p'
s research/conductor_gap_cm_pairs_20261010/lean/TransferBound.lean | sed -n '12,31p'
s research/conductor_gap_cm_pairs_20261010/lean/axiom-audit.log | sed -n '1,14p'
echo "-- .lean files in the project"; g ls-tree --name-only "$R" research/conductor_gap_cm_pairs_20261010/lean/ | grep -c '\.lean$'
echo "-- diff since CI-audited commit e5a884227 (stat, then TransferBound code lines changed outside the /-! -/ header)"
g diff --stat e5a8842272b3efbfdd53bc1b8f65bf4c644e3948 "$R" -- research/conductor_gap_cm_pairs_20261010/lean/
g diff -U0 e5a8842272b3efbfdd53bc1b8f65bf4c644e3948 "$R" -- research/conductor_gap_cm_pairs_20261010/lean/TransferBound.lean | grep -E '^@@'
echo "-- cited code line generic.rs:275"
echo "   at $R:"; s src/cryptanalysis/ecbench/generic.rs | grep -n 'mix(g.key(&pos))'
echo "   at 11aa00591:"; g show 11aa00591:src/cryptanalysis/ecbench/generic.rs | grep -n 'mix(g.key(&pos))'
echo "   files citing generic.rs:275 at $R:"
for f in research/conductor_gap_cm_pairs_20261010/README.md research/conductor_gap_cm_pairs_20261010/PROTOCOL.md research/conductor_gap_cm_pairs_20261010/lean/README.md research/conductor_gap_cm_pairs_20261010/lean/GenericInvariance.lean; do
  printf '   %s: %s\n' "$f" "$(s "$f" | grep -c -E 'generic\.rs:275|generic.rs`,\s*$|line 275')"
done
s src/cryptanalysis/ic_boundary.rs | grep -n 'mix(self.g.key(x))'

hdr "L6/L-N7/L7: S3Roots and program abstract"
s papers/rootfinding-decomposition/lean/axiom-audit.txt | sed -n '1,13p'
echo "-- lean/ diff since e5a884227 (stat)"; g diff --stat e5a8842272b3efbfdd53bc1b8f65bf4c644e3948 "$R" -- papers/rootfinding-decomposition/lean/
s papers/ecdlp-index-calculus-program/sections/abstract.tex | sed -n '28,31p'
echo "-- Lean workflows present"; g ls-tree --name-only "$R" .github/workflows/ | grep -E 'conductor-gap-lean|rootfinding-s3roots-lean|tree-split-structured-v-lean'

hdr "E1/E2/E1-R: ecbench workflow, scope rule, audit script, audit.rs"
s .github/workflows/ecbench.yml | sed -n '15,34p;41,48p'
echo "-- schedule/cron triggers in ecbench.yml:"; s .github/workflows/ecbench.yml | grep -c -E '^\s+schedule:|cron:'
s .github/workflows/ecbench.yml | sed -n '223,237p'
s .github/workflows/ecbench.yml | grep -n -E '^\s+if: .*(workflow_dispatch|pull_request)' | head -12
s .github/scripts/ci-scope.mjs | sed -n '69,76p'
s .github/scripts/ecbench-audit-sessions.sh | sed -n '98,114p'
s src/cryptanalysis/ecbench/audit.rs | sed -n '214,226p;281,285p;336,341p;759,762p'
echo "-- records_bound / interruption surfaced by CI script or workflow:"; { s .github/scripts/ecbench-audit-sessions.sh; s .github/workflows/ecbench.yml; } | grep -c -E 'records_bound|never_finalised'
