# EXP-ICEX-153c34 implementation note

Task `TASK-20261001-4862b6` is scoped to the S0 gates for the approved G1
instrument. The package contains:

* `panel_fixtures.py`, the exact Sage implementation of the frozen-L panel
  generation rule and its rejection receipt;
* `g1_s0.py`, the own-arithmetic Semaev/resultant and sparse lex-Buchberger
  primitives needed by the S0 instrument; and
* `s0_driver.py`, the fail-closed S0 runner and report writer.

The runner was invoked once with owner `executor-codex`, epoch `1`, under the
required single-worker, `nice -n 10`, 8 GiB RSS, and C-7 machine-protection
contract. It refused before fixture derivation because the launch readings
exceeded the load and free-space limits. Consequently no scientific gate
computation was started and there are no pass/fail observations from G0-1 to
G0-6. This is an infrastructure stop, not evidence about G1 or the hypothesis.

No frozen fixture, protocol-labelled draw, charged run, `RUN-*` directory,
specification, fixture, hypothesis, ledger, or other task scope was edited.
The exact refusal and readings are in `s0_gates_report.yaml`; all package file
hashes are in `implementation_report.yaml`.
