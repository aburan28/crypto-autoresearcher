# Prior (written 2026-10-17 before reading any fix PR or re-running any check)
- S1: most likely partially fixed. Patching a skeleton verifier to reject the 4 known mutants is easy;
  a fully sound verifier (queries from transcript, FRI on LDE, composition binding) is hard. Expect
  new mutants (e.g. query-position reuse, truncated FRI layers) to still be accepted, or the fix to be
  "documented unsound" rather than sound.
- S2: likely fixed (deleting text is easy). Risk: replacement text claims a new bound not proven.
- P1: likely fixed in tex; risk the PDF not rebuilt or abstract still says curve-specific.
- L1: Lean theorem uncompiled -> build may fail; at best not_covered if toolchain fails to install.
- L6: workflows exist but may never have run (path filters) or may have run only on PR.
- P3/P4/P5: numbers corrected but 16 562 replacement may be untraced again.
- K3: plausible fix; risk other rows inconsistent with the new schema meaning.
- M1: superseded via registry; original file still unparseable, so parseability checker behaviour matters.
- M2: count will be ~287 or higher (new records since).
- R1: not fixed (stated). E1/E2/X1/X2: mixed; X1 audit-runs maybe not done.
- New regressions: fix PRs may themselves introduce untraced numbers or unsupported strong words.
