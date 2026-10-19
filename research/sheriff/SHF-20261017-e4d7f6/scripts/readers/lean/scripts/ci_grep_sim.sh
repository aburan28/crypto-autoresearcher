#!/usr/bin/env bash
# Re-run, read-only, the forbidden-construct grep steps of the three crypto workflows
# against the sources at the audited commit. Arg: crypto checkout root.
C="$1"
echo "## tree-split-structured-v-lean.yml step 'No sorry, admit or custom axioms; native_decide only in replay_ok'"
cd "$C/research/ic_tree_split_structured_v_20261011/lean"
if grep -rnE '\bsorry\b|\badmit\b|^\s*axiom\s' TreeSplit AxiomAudit.lean; then echo "RESULT: forbidden construct found (CI would fail)"; else echo "RESULT: no forbidden construct"; fi
uses=$(grep -rnE '(^|[^`])\bnative_decide\b' TreeSplit AxiomAudit.lean || true)
echo "$uses"
n=$(printf '%s\n' "$uses" | grep -c .)
echo "native_decide tactic uses: $n (CI requires exactly 1, in replay_ok)"
printf '%s\n' "$uses" | grep -qE '^TreeSplit/Replay\.lean:[0-9]+:theorem replay_ok :' && echo "RESULT: only replay_ok" || echo "RESULT: unexpected native_decide site"
echo
echo "## conductor-gap-lean.yml step 'No sorry, admit, native_decide or custom axioms'"
cd "$C/research/conductor_gap_cm_pairs_20261010/lean"
if grep -nE '\bsorry\b|\badmit\b|native_decide|^axiom ' GenericInvariance.lean TransferBound.lean AxiomAudit.lean; then echo "RESULT: forbidden construct found (CI would fail)"; else echo "RESULT: no forbidden construct"; fi
echo
echo "## rootfinding-s3roots-lean.yml step 'No sorry, admit, native_decide or custom axioms'"
cd "$C/papers/rootfinding-decomposition/lean"
if grep -nE '\bsorry\b|\badmit\b|native_decide|^axiom ' S3Roots.lean AxiomAudit.lean; then echo "RESULT: forbidden construct found (CI would fail)"; else echo "RESULT: no forbidden construct"; fi
echo
echo "## longest '#print axioms' line each audit can emit (wrap risk if > ~120 chars at default width)"
for f in "$C/research/conductor_gap_cm_pairs_20261010/lean/AxiomAudit.lean" "$C/papers/rootfinding-decomposition/lean/AxiomAudit.lean" "$C/research/ic_tree_split_structured_v_20261011/lean/AxiomAudit.lean"; do
  m=$(grep -oE '^#print axioms [A-Za-z0-9_.]+' "$f" | awk '{print length($3)}' | sort -n | tail -1)
  echo "$(basename $(dirname $f))/AxiomAudit.lean: longest name $m chars -> line ~ $((m + 2 + 21 + 39)) chars with all three std axioms"
done
