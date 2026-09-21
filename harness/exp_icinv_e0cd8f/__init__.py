"""EXP-ICINV-e0cd8f: exact symbolic Semaev geometry across one isogeny class.

NEW MODULE, owned by TASK-20260810-ab0a07. It exists because the frozen
contract (experiments/EXP-ICINV-e0cd8f/specification.yaml, version 1) forbids
editing harness/semaev.py and harness/exp_icinv.py, so that every
already-committed run of those modules stays reproducible.

THE DEFINING CONSTRAINT OF THE CONTRACT, RESTATED HERE BECAUSE IT IS EASY TO
VIOLATE BY HABIT: no factor-base membership polynomial f_V may appear in ANY
ideal built by this module. The ideal is

    I_m(E) = < S_m , dS_m/dx_1 , ... , dS_m/dx_m >

and nothing else. harness/semaev.py:118 builds
`[S_3(x1,x2,xR), fV1, fV2]`; that system MUST NOT be reused here.

Nothing in this package computes a p-value, a permutation test, a null-object
test or a dispersion statistic. The contract makes any such quantity appearing
anywhere in the output an invalidation condition.
"""
