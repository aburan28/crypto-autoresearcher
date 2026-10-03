"""Integer freeze keys for EXP-LHW-b49bc6. No floats as freeze keys."""
from __future__ import annotations

EXPERIMENT_ID = "EXP-LHW-b49bc6"
HYPOTHESIS_ID = "H-LHW-e54b1b"
APPROVED_BY = "DEC-20261003-1c5b5a"
SOURCE_IDEA = "IDEA-20260930-79abd9"
QUESTION_ID = "RQ-LHW-1877bb"

# Cells of IDEA M2. Integer keys only.
CELLS = ((20, 2), (20, 3), (20, 5), (24, 3), (24, 4), (24, 6))
BINOM = {
    (20, 2): 190,
    (20, 3): 1140,
    (20, 5): 15504,
    (24, 3): 2024,
    (24, 4): 10626,
    (24, 6): 134596,
}
POW2M = {20: 1048576, 24: 16777216}
# Least prime strictly above 2^{m+2}. Dual-route Stage 0 must reproduce these.
L_PRIME = {20: 4194319, 24: 67108879}
# Bitmap covers [-2^{m+2}, 2^{m+2}].
BITMAP_HALF = {20: 1 << 22, 24: 1 << 26}

T_GRID = (16, 64, 256, 1024, 4096)
E1_T_MIN = 64
E1_MAX_MILLIRHO = 2000
E2_T = 1024
E2_T_RISE = 4096
E2_MIN_MILLIRHO = 8000
WAP_MIN_MILLIRHO_T1024 = 8000

# alpha < 11/100 is the exponent-gap slice (only (20,2) on this ladder).
GAP_NUM = 11
GAP_DEN = 100
# R3/R4 balanced crossover alpha ~ 174/1000 (formula-level; not a Stage-1 gate).
XOVER_NUM = 174
XOVER_DEN = 1000

WALK_COUNT = 10
WPRIME_COUNT = 5
Q_PCTS = (0, 25, 50, 75, 100)
WALK_SEED0 = 2026100310
WPRIME_SEED0 = 2026100320
WAP_START = 0
RADDING_R = 16
UNIT_MAX = 16

FAMILIES = ("Ja_radding", "Jb_signed_bits", "Jc_exchanges", "Jd_unit")

AMAZON_BEDROCK = "NOT SELECTED"


def is_gap_cell(m: int, w: int) -> bool:
    return GAP_DEN * w < GAP_NUM * m
