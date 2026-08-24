"""Control driver for EXP-INSTR-36c8cf (GOAL-ENDO-001 / BATCH-d7e255).

New package, owned by TASK-20260810-c98659. It is a DRIVER OVER
harness/exp_icinv.py, harness/exp_icinv_fullgroup.py, harness/isogeny_class.py
and harness/toycurve.py; none of those is edited (contract
source_constraints).

Every reference value used here is READ FROM A COMMITTED RECORD AT RUN TIME and
bound by a sha256 in baseline-provenance.json. No reference value is
transcribed into this source at any precision (EXP-ICINV-4d33aa amendment v2
change A4, CORR-20260807-a24675).
"""
