# Batch of level-2 curves on NIST K-163 (conductor 45641·82153)

Each run makes one 82153-descent from a 45641-floor curve (`analogues/iso163_45641.txt`, rotating through the
6 representatives; PARI seed 100 + run) with `vert_down.gp`, then checks the image's level two independent ways:
the horizontal 11-cycle (expected 82152 = ord[𝔩₁₁] at this level) and the torsion structure (45641- and
82153-parts both cyclic, ℓ′²). Driver: `run_batch.sh` → `curve.sh`; this table: `collect.py`.
Field F_2[x]/(x¹⁶³ + x⁷ + x⁶ + x³ + 1); every image has a₂ = 1, #E = N and a Galois orbit of 163.

**0 new verified curves in distinct Galois orbits** (0 of 20 runs complete). *Measured; independently verified.*

| run | start b′ (45641-floor) | seed | image b (Galois-orbit min) | descent | 11-cycle | 45641-, 82153-part | status |
|---|---|---|---|---|---|---|---|

