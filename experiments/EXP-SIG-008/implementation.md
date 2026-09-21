# EXP-SIG-008 implementation

Driver: experiments/EXP-SIG-008/SIG8_run.sage (pinned instruments in src/:
h013_f5_signatures.sage 1ba96fe4..., semaev_tree.py e9f1681b...,
ic_first_fall_fast.py f1c98bd8..., macaulay_export.py c00b8aad...).

Modes: gate | build2 | n1d345 | n1s1 | rank6 | sems1 | sems2.
Common flags: --arm null|sem --n 12 --seed 2 --budget 225 --chunk-force N --out raw.json.

Key machinery:
- int-mask row/column builder (numpy int64 bitmask per nb=24 block vars), cross-checked
  against the pinned builder at D3/D4 in gate mode.
- N1 construction: safe column pools + seeded greedy set-cover + swap repairs until the
  D6 column set equals the sem's exactly (work/n1_ms.pkl, work/n1_ms.json).
- rank engine: resumable block-m4ri staircase (algorithm of SIG7 src/h012c_block_m4ri.py):
  per unit c columns: build c x nrows, reduce against all carries (B += H*B[P]),
  echelonize, extract RREF pivot rows as new carry (P,H); carries flushed every 2 units
  and at exit; state.json written atomically after flushes; sha256 verified on load.
  Checkpoints: work/null_rank6/ (null), work/sem_rank6/ (sem, pending).
- rankK via m4ri on the K-family row positions (work/null_rankK6.json = 26,792).
- sems1/sems2: staged closure engine for gate 2 (self-staging, resume-safe; stage-1
  asserts the D5 closure anchor before any D6 quantity).

All sage-Integer/numpy hazards fixed via int(); gc disabled inside the staircase;
budget guard pred = last_cost*1.25 + 10 before each unit.
