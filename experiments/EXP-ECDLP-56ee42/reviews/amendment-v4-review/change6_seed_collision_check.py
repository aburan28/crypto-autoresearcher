"""
Independent verification of V4-CHG-6's seed_schedule collision-freedom claim.

Generates EVERY seed value the frozen contract + v4's change_6 would ever
produce (the real NULL-2 schedule per change_4's arm_index pinning, plus
change_6's placement/genuine/reading2 blocks across all rep/rung_idx/draw_idx
combinations) and checks for duplicates directly, rather than trusting the
amendment's own "by inspection" argument.
"""
BASE = 0x56EE42

seeds = {}
collisions = []


def add(name, val):
    if val in seeds:
        collisions.append((name, seeds[val], val))
    else:
        seeds[val] = name


# Real NULL-2 schedule (change_4 pinning): arm_index 0..7 (T1..POS-B=0..6,
# C2A-COMPARATOR=7), shuffle_index 0..7.
for arm_index in range(8):
    for shuffle_index in range(8):
        add(f"real_null2(arm={arm_index},shuf={shuffle_index})",
            BASE + 1000 + 10 * arm_index + shuffle_index)

# change_6 placement seeds: rep 0..19, rung_idx 0..5.
for rep in range(20):
    for rung_idx in range(6):
        add(f"placement(rep={rep},rung={rung_idx})",
            BASE + 90000 + 1000 * rep + 10 * rung_idx)

# change_6 genuine-shuffle seeds: rep 0..19, rung_idx 0..5, draw_idx 0..7.
for rep in range(20):
    for rung_idx in range(6):
        for draw_idx in range(8):
            add(f"genuine(rep={rep},rung={rung_idx},draw={draw_idx})",
                BASE + 190000 + 1000 * rep + 10 * rung_idx + draw_idx)

# change_6 reading-2 seeds: rep 0..19, rung_idx 0..5, draw_idx 0..7.
for rep in range(20):
    for rung_idx in range(6):
        for draw_idx in range(8):
            add(f"reading2(rep={rep},rung={rung_idx},draw={draw_idx})",
                BASE + 290000 + 1000 * rep + 10 * rung_idx + draw_idx)

expected_total = 8 * 8 + 20 * 6 + 20 * 6 * 8 + 20 * 6 * 8
print(f"Total seed slots generated: {len(seeds) + len(collisions)}")
print(f"Expected total (no collisions): {expected_total} "
      f"= 64 (real) + 120 (placement) + 960 (genuine) + 960 (reading2)")
print(f"Distinct values actually stored: {len(seeds)}")
print(f"Collisions found: {len(collisions)}")
for c in collisions:
    print("  COLLISION:", c)

real_vals = [BASE + 1000 + 10 * ai + si for ai in range(8) for si in range(8)]
placement_vals = [BASE + 90000 + 1000 * rep + 10 * ri for rep in range(20) for ri in range(6)]
genuine_vals = [BASE + 190000 + 1000 * rep + 10 * ri + di
                for rep in range(20) for ri in range(6) for di in range(8)]
reading2_vals = [BASE + 290000 + 1000 * rep + 10 * ri + di
                 for rep in range(20) for ri in range(6) for di in range(8)]

print()
print("Block ranges (offset from BASE), confirming disjointness by inspection:")
print(f"  real:       [{min(real_vals)-BASE}, {max(real_vals)-BASE}]")
print(f"  placement:  [{min(placement_vals)-BASE}, {max(placement_vals)-BASE}]")
print(f"  genuine:    [{min(genuine_vals)-BASE}, {max(genuine_vals)-BASE}]")
print(f"  reading2:   [{min(reading2_vals)-BASE}, {max(reading2_vals)-BASE}]")

assert len(collisions) == 0
assert len(seeds) == expected_total
print()
print("VERIFIED: change_6's seed schedule is collision-free across all")
print("2104 generated seed slots (the real NULL-2 schedule plus all")
print("20 x 6 placement, 20x6x8 genuine, and 20x6x8 reading-2 slots).")
print("Note: the placement block's own max offset (109050) DOES exceed the")
print("literal number 100000 the amendment's phrase 'far below the next")
print("block's 100000 spacing' might suggest at a skim -- but the correct")
print("reading is intra-block SPAN (<=19057) vs inter-block SPACING")
print("(100000), which is what actually matters for collision-freedom, and")
print("that comparison is correct. No collision exists.")
