ps = [523, 1033, 2063, 4111, 8219, 16417, 32779, 65539]

data = {
    "popcount":      [2.0699, 2.5702, 2.7742, 2.8895, 2.9226, 3.1282, 3.0443, 3.3045],
    "popcount SHUF": [2.0381, 2.4457, 2.7080, 2.8404, 2.8774, 3.0796, 3.0271, 3.2819],
    "digitsum":      [1.2193, 1.1662, 1.2057, 1.3177, 1.5296, 1.8069, 2.2063, 2.6656],
    "digitsum SHUF": [1.1726, 1.1434, 1.1737, 1.2728, 1.4780, 1.7572, 2.1636, 2.6267],
    "P2":            [4.0620, 5.0466, 6.5399, 8.0308, 10.0245, 12.5190, 16.0156, 20.0122],
    "P2 SHUF":       [1.0640, 1.0414, 1.0265, 1.0161, 1.0102, 1.0064, 1.0049, 1.0030],
    "sha":           [1.3271, 1.2723, 1.1921, 1.1438, 1.1186, 1.1181, 1.1133, 1.0742],
}

def ratios_minus1(base, shuf):
    return [(s-1)/(b-1) for b, s in zip(base, shuf)]

def ratios_plain(base, shuf):
    return [s/b for b, s in zip(base, shuf)]

for name in ["popcount", "digitsum", "P2"]:
    base = data[name]
    shuf = data[name + " SHUF"]
    rm1 = ratios_minus1(base, shuf)
    rp = ratios_plain(base, shuf)
    print(f"\n{name}:")
    for p, b, s, m1, pl in zip(ps, base, shuf, rm1, rp):
        print(f"  p={p:>6} G={b:.4f} SHUF={s:.4f}  (G-1)ratio={m1:.4f}  plainG_ratio={pl:.4f}")
    print(f"  (G-1)ratio range: [{min(rm1):.4f}, {max(rm1):.4f}]")
    print(f"  plainG   range:   [{min(rp):.4f}, {max(rp):.4f}]")
