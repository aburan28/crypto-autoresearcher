import sys, re, collections
tot=collections.Counter(); rows=[]
maxratio_overall=(-1,None)
for path in sys.argv[1:]:
    for line in open(path):
        if not line.startswith("SUMMARY"): continue
        kv=dict(x.split("=",1) for x in line.split()[1:])
        for k in ("ncand","violations","degenerate","degD_gt_bound","notdiv","AB_dis","C_dis",
                  "boundary_lead_survive","boundary_lead_cancel"):
            tot[k]+=int(kv[k])
        mr=float(kv["maxratio"])
        if mr>maxratio_overall[0]: maxratio_overall=(mr,line.strip())
        rows.append(kv)
        tot["cells"]+=1
        if int(kv["dq1"])==int(kv["pnr"]): tot["boundary_rows"]+=1; tot["boundary_ncand"]+=int(kv["ncand"])
print("(p,n,n',d) rows :", tot["cells"])
print("candidates      :", tot["ncand"])
print("VIOLATIONS N>bound            :", tot["violations"])
print("deg D > bound                 :", tot["degD_gt_bound"])
print("K-root-set of L does NOT | D  :", tot["notdiv"])
print("brute-vs-gcd disagreements    :", tot["AB_dis"])
print("injection-vs-gcd disagreements:", tot["C_dis"])
print("degenerate (D == 0)           :", tot["degenerate"])
print("equal-degree-boundary rows    :", tot["boundary_rows"], "covering", tot["boundary_ncand"], "candidates")
print("  of which deg D == max (leading terms survive):", tot["boundary_lead_survive"])
print("  of which deg D <  max (leading terms cancel ):", tot["boundary_lead_cancel"])
print("largest N/bound anywhere      :", maxratio_overall[0])
print("   at:", maxratio_overall[1])
