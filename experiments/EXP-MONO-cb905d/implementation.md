# EXP-MONO-cb905d implementation notes

## What this implements

`experiments/EXP-MONO-cb905d/implementation/run_experiment.py` implements the
frozen `specification.yaml` exactly:

- **Part A (primary, headline).** OBJ-6's transversal-vs-group-uniform
  sampling control, applied to the SAME matched (p=617, N=580, tau=4) pair
  EXP-MONO-64aaa4 tested. The transversal arm's counts are reused directly
  from `experiments/EXP-MONO-64aaa4/runs/RUN-MONO-64aaa4-1/raw-result.json`
  (never redrawn). The group-uniform arm is new: 20000 fresh draws per curve
  under the rejection-sampling rule in `inputs.seed_derivation_rule_part_a_group_uniform_arm`.
- **Part B (exploratory, secondary).** Fresh transversal-only ("fixed" arm
  only) Stage 1-2 measurements on all 100 cross-prime matched-(N,tau) cells
  enumerated from `experiments/EXP-MONO-64aaa4/runs/RUN-MONO-64aaa4-1/stage0_transcript.json`,
  in a deterministic order (smallest p_ord+p_cm first) fixed before any
  measurement is taken. The p=617 same-prime cell is reused directly from
  EXP-MONO-64aaa4's own archived result, never re-measured.

## Code reuse discipline

`EXP-MONO-64aaa4/implementation/run_experiment.py` is loaded **read-only** by
file path via `importlib.util.spec_from_file_location` and never copied or
edited. Every helper function used from it (`seed_bytes`, `draw_uniform`,
`quad_char`, `construct_ordinary`, `construct_cm_j1728`, `ec_neg`, `ec_add`,
`sqrt_mod_p`, `build_factor_base`, `measure_curve`, `predicted_rate`,
`binomial_se_pairs`, `fisher_exact_2x2`, `SIGN_CLASSES`, `NCLASSES`, `NPAIRS`)
is called directly from the loaded module object, satisfying the contract's
"byte-identical code reuse" requirement.

The loaded module's own module-level `DOMAIN` constant starts as
`"EXP-MONO-64aaa4/v1"` (as set by that file itself). This script uses that
UNCHANGED domain for exactly one purpose: the Part-A curve re-derivation
stopping-rule check (calling `construct_ordinary(617)` and
`construct_cm_j1728(617)` and requiring an EXACT match against the archived
transcript's `(A,B,N,tau)`). Only after that check passes does this script
reassign `m64.DOMAIN = "EXP-MONO-cb905d/v1"` for every subsequent NEW draw
(Part A's group-uniform arm, Part B's fresh transversal draws), per
`inputs.seed_derivation_rule_part_a_group_uniform_arm` and
`inputs.seed_derivation_rule_part_b`, both of which explicitly declare the
new domain.

## Interpretation decisions and disclosed readings (not silent deviations)

1. **"transversal rate" = `rate_pairs_per_tuple`.** EXP-MONO-12ce1c's own
   OBJ-6 finding (red-team-report.yaml) reports "mean D" values (e.g.
   J1728 0.01650 -> 0.03033), which match EXP-MONO-64aaa4's own
   `observed_rate_pairs_per_tuple` field exactly in shape (total
   pairwise-colliding sign-class pairs divided by tuple count, out of
   `NPAIRS=6` possible pairs per tuple). This script uses
   `rate_pairs_per_tuple` as the collision-rate quantity `D` for P1/P2/P3,
   consistent with that prior record's own metric.
2. **"transversal" arm = EXP-MONO-64aaa4's factor-base construction.** That
   construction draws x only from the factor base (nonzero quadratic
   residues of `f(x)`), which by construction excludes `f(x)=0` (i.e.
   excludes 2-torsion) -- this is exactly OBJ-6's own description of the
   "transversal" sampling domain (one point per factor-base x, 2-torsion
   necessarily excluded).
3. **Dual-convention control not re-run.** `arms_and_controls.dual_convention_control`
   is explicit that this is proven tautological (both EXP-MONO-64aaa4
   reviewers and OBJ-6 independently). This script reuses EXP-MONO-64aaa4's
   own "fixed" arm counts for Part A's transversal baseline (confirmed
   identical to "random" in the archived data), and measures ONLY the
   "fixed" arm for Part B's fresh cross-prime cells (never re-running the
   empty random-sign check).
4. **Group-uniform sampling never explicitly draws the point at infinity.**
   `inputs.seed_derivation_rule_part_a_group_uniform_arm`'s prose says the
   group-uniform arm draws from "E(F_p) INCLUDING the point at infinity",
   but its own precise operational definition is a strict 3-branch
   rejection rule over `x` drawn uniformly in `F_p` (not `F_p` plus an
   extra slot for infinity): nonzero-square -> one of two affine roots,
   zero -> the affine 2-torsion point directly, non-residue -> reject and
   redraw. This 3-branch rule, followed literally, samples uniformly over
   the `N-1` AFFINE points of `E(F_p)` and never returns `O`. This script
   implements the literal 3-branch rule exactly as given (down to the
   `gu-x`/`gu-sign` labels), because the precise operational text is more
   specific and more testable than the summary phrase, and per
   `invalidation_rules` this script may not alter "the group-uniform
   sampling construction ... after any Stage-1 or Stage-3 number has been
   observed" -- so this reading was fixed BEFORE any draw was performed
   and is disclosed here rather than silently resolved. This is a
   disclosed protocol-interpretation, not a deviation from a construction
   the frozen contract stated unambiguously in one place; it is recorded
   per the Executor's obligation to record every interpretation choice.
5. **Distinctness rule for group-uniform's 3 drawn points.** EXP-MONO-64aaa4's
   own transversal construction enforces distinctness of the 3 drawn
   factor-base x-INDICES (not points). The group-uniform arm has no factor
   base to index into, so this script enforces the analogous rule at the
   level available to it: the 3 drawn points must have distinct
   x-coordinates. Documented here as the literal generalization of "3
   drawn points" per `arms_and_controls.part_a_group_uniform_arm`'s
   "otherwise reuse EXP-MONO-64aaa4's own m=4 construction (3 drawn points,
   4 canonical sign classes) unmodified".
6. **Per-curve caching in Part B.** A given (role, p) transversal
   measurement is deterministic and identical every time it is computed
   (the seed stream depends only on domain, label, p, role, draw index, and
   counter -- never on which partner curve a cell pairs it with). Since
   many of the 100 cross-prime cells share an ordinary or CM curve at the
   same prime, this script caches each curve's own measurement the first
   time it is computed and reuses it for every later cell that needs the
   same curve. This changes nothing about any individual number; it only
   avoids redundant recomputation. Confirmed by re-running the full script
   twice (see below) and observing byte-identical Part A and Part B
   numbers both times.

## Reproducibility check performed

The script was run twice end-to-end (once during development, once as the
canonical run in `runs/RUN-MONO-cb905d-1/`). Both runs produced identical
Part A metrics (P1=2.9559543230016314, P2=2.6857562408223203,
P3 ratio-of-ratios=1.100604097301318) and identical Part B summary numbers
(100/100 cells measured, 0 errors, same P5/P6 distribution counts),
confirming the run reproduces deterministically from the recorded command
and revision, as the completion gate requires.

## Protocol deviations

None from the frozen contract's explicit requirements. Item 4 above is an
interpretation of an internally inconsistent sentence in the contract's own
`inputs` block (a summary phrase vs. a precise operational rule in the same
paragraph), resolved in favor of the precise operational rule and disclosed
here, in the run manifest, and in the execution report, per the Executor's
obligation not to silently resolve ambiguity.

## Anomalies

- Part A's group-uniform/transversal ratios (P1=2.956, P2=2.686) both fall
  OUTSIDE EXP-MONO-12ce1c OBJ-6's own previously-measured 1.84-2.08x range,
  on BOTH curves, at the SAME m=4 arity and 20000-tuple count. This is
  reported prominently per the stopping_rules/falsification_criterion text,
  as a measured observation only -- not absorbed into a "confirmed" or
  "reproduced" framing. See execution_report.yaml for full context.
- An `/usr/bin/time -l` invocation used during pre-canonical-run tuning to
  probe peak RSS failed with `sysctl kern.clockrate: Operation not
  permitted` (a sandbox restriction on the tooling, not on the experiment
  script itself; the underlying Python process completed successfully with
  `status: completed_valid` both times). Classified `infrastructure_error`
  in tooling only; peak RSS for the canonical run was instead captured
  in-process via `resource.getrusage(resource.RUSAGE_SELF).ru_maxrss`,
  added to the script before the canonical run. This did not affect any
  Part A or Part B measurement, seed, or draw.
