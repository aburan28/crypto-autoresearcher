# RESULTS-stage2-repl — EXP-CERTBIN-1bfef5 / RUN-CERTBIN-0dc7c4

Independent Stage-2 replication of RUN-CERTBIN-a93cf9 after EV-CERTBIN-5c2947 /
DEC-20261003-b415ff (`replicate`). Seed `2026092691` (frozen protocol has no
holdout seed). AMD-20261003-09f9ef names this RUN only. Live `RESULTS.md` and
`stage2/*` from a93cf9 were not overwritten in the committed tree.

Producer `run.py` output follows (also at
`runs/RUN-CERTBIN-0dc7c4/RESULTS.md`). Amendment id in the producer text is
the frozen STAGE2_AMENDMENT_ID constant AMD-20261003-d292c9; the replication
RUN-id AMD is AMD-20261003-09f9ef.

# RESULTS — EXP-CERTBIN-1bfef5

Label: **O-E-POLY**

- hypothesis: H-CERTBIN-4d3853
- approved_by: DEC-20261002-711879
- admit_by: DEC-20261003-f1d0f6
- stage2_admit_by: DEC-20261003-ed98c2
- amendment_id: AMD-20261003-d292c9
- prior_stage2_amendment_id: AMD-20261003-894083
- task_id: TASK-20261003-737cc7
- stage1_precondition: O-ARM-A-PASS 288/288 (EV-CERTBIN-f218ae / DEC-20261003-b8f938)
- prior_stage2_void: EV-CERTBIN-383c07 / DEC-20261003-c7e6d1 / RUN-CERTBIN-9dcb6d (immutable)
- structured_w4_rates: {"V_N": 0.451612903225806, "V_S_min": 0.274193548387097, "V_S_octic1": 0.274193548387097, "V_S_octic2": 0.564516129032258}
- reason: Structured W_4 rate <= 0.5: V_N=0.4516, V_S_min=0.2742
- claims: break=false, exponent_move=false
- amazon_bedrock: NOT SELECTED
- note: Stage-2 arms (b)–(d) under S62/oracle localization AMD; prior Stage-0/1/first-Stage-2 RUNs immutable.
- note: Archive-S62 non-transfer under new V is observational; O-ARTIFACT only on current-V soundness failure.
