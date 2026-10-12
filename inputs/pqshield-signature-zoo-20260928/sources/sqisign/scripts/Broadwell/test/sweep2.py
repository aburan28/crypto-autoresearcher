import importlib.util, math
spec = importlib.util.spec_from_file_location("m", "/data/bhe/bw-phase0/gen_noguard.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
N = 4
out = []
for c in [3,5,7,9,15,17,27,31,33,63,65,127,129,255,257]:
    bl = c.bit_length()
    frac = bl - math.log2(c)          # real headroom above `spare`, in (0,1]
    for s in [1,2,3,4]:
        bits = 64*N - s
        t = bits - bl
        if t < 64*(N-1): continue
        p = c*(1<<t)-1
        if p.bit_length() != bits: continue
        try:
            P, asm = m.generate(c, t)
            open("/tmp/s2_%d_%d.S" % (c,t), "w").write(asm)
            out.append((s, c, t, round(s+frac,3)))
        except Exception as e:
            out.append((s, c, t, None))
for s, c, t, hr in sorted(out):
    print("%d %d %d %s" % (s, c, t, hr))
