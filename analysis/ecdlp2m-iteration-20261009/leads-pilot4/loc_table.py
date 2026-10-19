from loc_cost import *
P = W.DEFAULTS
print("bitops/rho", W.LOG2_BITOPS_PER_RHO)
rows = []
for m in [4,5,6,8,10,12,16]:
    b, l = W.d3_budget(m, P)
    bud = b + W.LOG2_BITOPS_PER_RHO
    k = round(l)
    full = log2(count_L(131,k,m,99)); l1 = log2(count_L(131,k,m,1)); l2 = log2(count_L(131,k,m,2))
    ws = windows(131,k,m,2); wmax = log2(max(ws)); nw = len(ws)
    out = [m, round(l,2), k, round(bud,1), round(full,1), round(l2,1), round(l1,1), round(wmax,1), nw]
    for om in (2.0, 2.37, 3.0):
        cg = om*l2                         # global L2 elimination
        cw = log2(sum(x**om for x in ws))  # one pass over all windows
        out += [round(bud-cg,1), round(bud-cw,1)]
    rows.append(out)
hdr = "m l k budget log2cols_full log2cols_L2 log2cols_L1 log2win_max nwin | margin(L2 global, windowed 1 pass) at omega 2 | 2.37 | 3"
print(hdr)
for r in rows: print(*r)
