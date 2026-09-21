# Independent Validation — dreg-linear-law finding

Validator: independent Claude session (2026-07-20). Re-ran, did not trust the doc.
Snapshot validated: branch `claude/dreg-linear-law`, worktree
`/Volumes/Volume/crypto-autoresearcher-worktrees/claude-dreg-law`, HEAD
`1f79182481d31bb9b0bee3e85a6355c81143bf43`, working tree clean. All target
artifacts and cited receipts are tracked at HEAD (not working-tree-only).
No research status, ledger, or artifact was changed. This report is uncommitted.

```yaml
validation_report:
  id: VAL-20260720-dreg-linear-law
  task_id: unspecified-in-task-card
  run_ids: [RUN-EXP-SIG-005-h, RUN-EXP-SIG-005-k]
  snapshot:
    branch: claude/dreg-linear-law
    head: 1f79182481d31bb9b0bee3e85a6355c81143bf43
    dirty_tree: false
    artifacts_committed: true
  artifact_checks:
    - path: research/dreg-linear-law/dreg_growth_law.py
      status: present, tracked-at-HEAD, executed
    - path: research/dreg-linear-law/dreg_results.json
      status: present, tracked-at-HEAD, cross-checked
    - path: research/dreg-linear-law/FINDING.md
      status: present, tracked-at-HEAD
    - path: research/dreg-linear-law/validate_dreg.sage
      status: present, tracked-at-HEAD (n6+n9 variant; n9/D6 is expensive)
    - path: research/dreg-linear-law/validate_fast.sage
      status: MISSING — cited by FINDING.md "Reproduce" section but not in tree
    - path: experiments/EXP-SIG-005/runs/RUN-EXP-SIG-005-h/raw.json
      status: present, tracked-at-HEAD
    - path: experiments/EXP-SIG-005/runs/RUN-EXP-SIG-005-k/raw.json
      status: present, tracked-at-HEAD
    - path: experiments/EXP-SIG-005/src/h013_f5_signatures.sage
      sha256: 1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087
      status: matches value pinned in both receipts (instrument_sha256_matches_pinned=true)

  metric_recomputations:
    - check: 1  # dreg_growth_law.py re-run (pure Python, no Sage)
      verdict: PASS
      observed_dreg: {6: 5, 9: 6, 12: 7, 15: 8, 18: 9, 24: 10, 161: 46, 1000: 252, 8000: 1929}
      dreg_over_n_at_8000: 0.24113
      marginal_slope_4000_8000: 0.23900
      note: every claimed (n -> d_reg) pair and the ~0.24 density / 0.239 slope reproduce exactly

    - check: 2  # recorded receipts vs the finding's quotes
      verdict: PASS
      RUN-EXP-SIG-005-h_sem_n9_D6:   {ncols: 29332, rank: 27292, sr_pred: 28068}   # raw.json lines 124-126
      RUN-EXP-SIG-005-k_null_n9_D6:  {ncols: 31180, rank: 31179, sr_pred: 28068}   # raw.json lines 109-111
      note: FINDING.md (L79-80, L114-116) and dreg_results.json (L24-25) quote these bit-for-bit

    - check: 3  # live Sage re-run at n=6 only against the SIG-005 instrument
      verdict: PASS
      env: {sage: available at /usr/local/bin/sage, TMPDIR: /Volumes/Volume/sage-scratch-diag}
      family_n6: {nb: 12, n_eqs: 12, eq_deg_hist: {2: 6, 3: 6}, predicted_dreg: 5}
      per_degree:  # D | null_rank | sr_pred | q_null | q_sem   (matches dreg_results.json n6 block exactly)
        D2: {null_rank: 6,    sr_pred: 6,    q_null: 20,  q_sem: 7}
        D3: {null_rank: 84,   sr_pred: 84,   q_null: 149, q_sem: 77}
        D4: {null_rank: 527,  sr_pred: 531,  q_null: 243, q_sem: 171}   # -4 finite-size, as documented
        D5: {null_rank: 1584, sr_pred: 1323, q_null: 1,   q_sem: 95}    # null collapse at D=d_reg(6)=5
        D6: {null_rank: 2510, sr_pred: 2247, q_null: 0,   q_sem: 51}
      key_result: at D=5 (=predicted d_reg) q_null collapses to 1 while q_sem=95 => d_reg(sem) > d_reg(null)

    - check: 4  # family claim nb=2n, n deg-2 + n deg-3 vs eq_degs_hist in receipts
      verdict: PASS
      observed:
        n9:  {nb: 18, hist: {2: 9,  3: 9}}
        n12: {nb: 24, hist: {2: 12, 3: 12}}
        n15: {nb: 30, hist: {2: 15, 3: 15}}
        n18: {nb: 36, hist: {2: 18, 3: 18}}
        n21: {nb: 42, hist: {2: 21, 3: 21}}
        n24: {nb: 48, hist: {2: 24, 3: 24}}
        n6:  {nb: 12, hist: {2: 6,  3: 6}}   # re-derived live (no receipt exists below n=9)
      note: every receipt satisfies nb=2n with exactly n deg-2 and n deg-3 equations

  control_checks:
    - positive/negative control (support-matched null vs true Semaev): reproduced.
      null quotient collapses to 1 exactly at predicted d_reg (n=6 D5), sem quotient
      still 95 there -> Semaev structure RAISES the solving degree (contradicts the
      H-DREG-001 support clause d_reg(sem) < d_reg(null)), as the finding states.

  verdict: passed

  limitations:
    - Scope of a passed verdict: the receipts are admissible evidence and the four
      numeric claims reproduce. This does NOT support any ECDLP break, demonstrate a
      speedup, or authorize a hypothesis/status change. The finding itself claims none
      (toy scale; t=3 binary Weil-descent, a negative control for the prime-field target).
    - Doc gap (non-blocking): FINDING.md "Reproduce" cites `validate_fast.sage`, which is
      absent; the equivalent, present script is `validate_dreg.sage` (runs n=6 AND n=9).
      I ran a cheap n=6-only variant built from the same live instrument functions
      (build_boolean_semaev / boolean_null / analyze_syzygy_space) to reproduce the
      Sage evidence without the expensive n=9/D6 solve.
    - Narrative imprecision (non-blocking, not among the required checks): FINDING.md L48
      says "d_reg/sqrt(n) is strictly increasing (2.0 -> 4.4)". Direction is correct and
      supports Theta(n) not O(sqrt(n)); but the "4.4" endpoint is not reproducible from the
      tabulated points (d_reg/sqrt(n) = 3.63 at n=161, 7.97 at n=1000, 21.57 at n=8000).
    - The n=6 empirical row has no run receipt (smallest receipt is n=9); it was
      re-derived live here, which confirms it.
    - Infrastructure: root disk nearly full (~5.2Gi free); the instructed TMPDIR/SAGE_TMP
      redirect to /Volumes/Volume/sage-scratch-diag (561Gi free) was required and used.

  artifact_paths:
    - /Volumes/Volume/crypto-autoresearcher-worktrees/claude-dreg-law/research/dreg-linear-law/VALIDATION.md
```

## Bottom line

All four required checks PASS. The finding's numeric claims (linear d_reg law +
0.24 density, the bit-for-bit n=9 sem/null D6 receipts, the n=6 null-collapse /
sem-quotient control, and the nb=2n / n deg-2 + n deg-3 family) are faithfully
backed by independent re-run evidence. Only cosmetic gaps found (a stale
`validate_fast.sage` filename reference and an illustrative `4.4` figure); neither
touches a recomputed metric. Verdict: **passed** — admissible evidence, no ECDLP
or speedup claim implied or authorized.
