"""Declared 12-instance subsample, transcribed from
ledger/handoffs/TASK-20260904-42b33a.yaml -> review_plan.blind_rederivation.parameters.

Ladder m = 2, d = 2, s in {2,3,4,5}, D_max = 7, planting window [0,4).
(p ; curve seed: a, b ; target seed: x_R)
"""

INSTANCES = [
    # (p, curve_seed, a, b, target_seed, x_R)
    (4099, 3101, 3245, 455, 1, 1960),
    (4099, 3101, 3245, 455, 2, 3677),
    (4099, 3102, 204, 2744, 1, 1609),
    (4099, 3102, 204, 2744, 2, 1549),
    (16411, 3101, 11098, 12143, 1, 13300),
    (16411, 3101, 11098, 12143, 2, 4634),
    (16411, 3102, 5359, 13149, 1, 13011),
    (16411, 3102, 5359, 13149, 2, 5497),
    (65537, 3101, 11583, 22898, 1, 3044),
    (65537, 3101, 11583, 22898, 2, 15414),
    (65537, 3102, 46541, 19029, 1, 7111),
    (65537, 3102, 46541, 19029, 2, 7091),
]

S_VALUES = [2, 3, 4, 5]
D_MAX = 7
WINDOW = 4  # planting window [0, 4)

# Duplicate generator systems declared in the plan's note for joint V3:
DECLARED_DUPLICATES = [
    "p=4099 curve 3101 target seeds 1 and 5 both x_R = 1960",
    "p=16411 curve 3101 target seeds 2 and 3 both x_R = 4634",
]
