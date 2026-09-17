"""J4 extra: run the INDEPENDENT C implementation gf2rc.c on all 1260 Stage-1
candidates and compare with the archived I1/I2/I3.  The run itself never did
this (stage1.py dispatches to gf2rc only when n' >= 10, and every Stage-1 cell
has n' <= 7), so every one of the 1260 archived agreements was produced by three
routines inside one Python module."""
import json, glob, subprocess, os, collections
HERE=os.path.dirname(os.path.abspath(__file__))
BIN=os.path.join(HERE,"faultcopy","gf2rc")
rows=[]
for f in sorted(glob.glob("/home/user/crypto-autoresearcher/experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S1/cells/*.json")):
    c=json.load(open(f))
    for r in c["rows"]: rows.append(r)
print("archived Stage-1 rows:", len(rows))
inp="".join("%d %d %x\n"%(r["n"], r["n_prime"], r["lambda_bits"]) for r in rows)
out=subprocess.run([BIN], input=inp, capture_output=True, text=True, check=True).stdout.strip().split("\n")
got=[int(l.split()[-1]) for l in out if l.strip()]
assert len(got)==len(rows), (len(got), len(rows))
dis=[]; dist=collections.Counter()
for r,g in zip(rows,got):
    dist[(r["I1"]==r["I2"]==r["I3"]==g)]+=1
    if not (r["I1"]==r["I2"]==r["I3"]==g):
        dis.append((r["n"],r["n_prime"],r["lambda_printed"],r["I1"],r["I2"],r["I3"],g))
print("gf2rc (C) agrees with all three archived Python instruments on:", dist[True], "of", len(rows))
print("disagreements:", len(dis), dis[:10])
print("rejected inputs (-1):", sum(1 for g in got if g<0))
