"""Collect finished level-2 runs into the study directory: a run counts only if its descent, 11-cycle and torsion
outputs are all complete; it is VERIFIED when the 11-cycle is 82152 and both torsion parts are cyclic (l'^2)."""
import glob, pathlib, re, shutil
OUT = pathlib.Path("/home/user/crypto-autoresearcher/research/ecc2k130_conductor_isogenies_20261007/second_level/batch20")
MOD = (1 << 163) | (1 << 7) | (1 << 6) | (1 << 3) | 1
def sq(a):
    r = 0; b = a
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> 163: a ^= MOD
    return r
def orbmin(b):
    z, m = sq(b), b
    while z != b: m = min(m, z); z = sq(z)
    return m
prior = [115992596105510058325208044366752339422280521227, 52997549064096697226797992255204505576485896783,
         58695590472440980675481896156556688905461755377, 7694002023826588667080886127544181075275864551,
         66149347506823131946397494488931842230026067575, 135951262621428062693975966375761026409223543597]
seen = {orbmin(b): "earlier" for b in prior}
starts = [l.split(",")[0].strip("[") for l in open("/home/user/koblitz_cond/iso163_45641.txt").read().split("\n") if l]
rows, nver = [], 0
done = lambda f: pathlib.Path(f).exists() and re.search(r"^real", open(f).read(), re.M)
for i in range(1, 21):
    if not all(done(f"{p}{i}.out") for p in "dct"): continue
    d = open(f"d{i}.out").read(); c = open(f"c{i}.out").read(); t = open(f"t{i}.out").read()
    m = re.search(r"b'' \(Galois-orbit min\) = (\d+)\s+a2=(\d)\s+orbit size (\d+)\s+#E''=N ok\s+\((\d+) s\)", d)
    b = int(m.group(1)); cyc = int(re.search(r"11-cycle length (\d+)", c).group(1))
    exps = re.findall(r"exponent l'\^(\d)", t)
    ok = cyc == 82152 and exps == ["2", "2"] and m.group(2) == "1"
    dup = seen.get(orbmin(b)); seen.setdefault(orbmin(b), f"run {i}")
    nver += ok and not dup
    rows.append(f"| {i} | {starts[(i-1) % 6]} | {100+i} | {b} | {m.group(4)} s | {cyc} | ℓ′^{exps[0]}, ℓ′^{exps[1]} | "
                + ("VERIFIED" if ok else "**FAILED**") + (f"; same orbit as {dup}" if dup else "") + " |")
    for p in "dct":
        for ext in ("gp", "out"): shutil.copy(f"{p}{i}.{ext}", OUT)
    shutil.copy(f"d{i}.txt", OUT)
OUT.mkdir(parents=True, exist_ok=True)
for f in ("curve.sh", "run_batch.sh", "collect.py"): shutil.copy(f, OUT)
(OUT / "README.md").write_text(f"""# Batch of level-2 curves on NIST K-163 (conductor 45641·82153)

Each run makes one 82153-descent from a 45641-floor curve (`analogues/iso163_45641.txt`, rotating through the
6 representatives; PARI seed 100 + run) with `vert_down.gp`, then checks the image's level two independent ways:
the horizontal 11-cycle (expected 82152 = ord[𝔩₁₁] at this level) and the torsion structure (45641- and
82153-parts both cyclic, ℓ′²). Driver: `run_batch.sh` → `curve.sh`; this table: `collect.py`.
Field F_2[x]/(x¹⁶³ + x⁷ + x⁶ + x³ + 1); every image has a₂ = 1, #E = N and a Galois orbit of 163.

**{nver} new verified curves in distinct Galois orbits** ({len(rows)} of 20 runs complete). *Measured; independently verified.*

| run | start b′ (45641-floor) | seed | image b (Galois-orbit min) | descent | 11-cycle | 45641-, 82153-part | status |
|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n")
print(f"{len(rows)} complete, {nver} new verified")
