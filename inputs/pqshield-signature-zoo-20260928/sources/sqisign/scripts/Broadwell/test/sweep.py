import importlib.util, sys
spec = importlib.util.spec_from_file_location("m", "/data/bhe/bw-phase0/gen_noguard.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
rows = []
for c in [3,5,7,9,17,27,33,65,127,129,255,257,511,513]:
    for t in range(240, 530):
        p = c*(1<<t)-1; bits = p.bit_length(); N = (bits+63)//64
        if N < 3 or t < 64*(N-1): continue
        spare = 64*N - bits
        if spare <= 8: rows.append((spare, c, t, bits, N))
rows.sort()
per = {}
sel = []
for spare, c, t, bits, N in rows:
    if per.get(spare, 0) >= 2: continue
    per[spare] = per.get(spare, 0) + 1
    sel.append((spare, c, t, bits, N))
print("%5s %5s %5s %5s %3s  %s" % ("spare","c","t","bits","N","guard"))
for spare, c, t, bits, N in sel:
    print("%5d %5d %5d %5d %3d  %s" % (spare, c, t, bits, N, "accept" if spare>=4 else "REJECT"))
    with open("/tmp/sw_%d_%d.S" % (c,t), "w") as f:
        try:
            P, asm = m.generate(c, t); f.write(asm)
        except Exception as e:
            print("      generation failed:", e)
