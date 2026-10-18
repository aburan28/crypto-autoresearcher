#!/usr/bin/env python3
"""Produce and independently check closure certificates for named instances.

usage: cert_batch.py WORKERS D FILE:NAME [FILE:NAME ...]
FILE is a results/*.json file (instances.json, instances_sat.json or instances_t3.json) and NAME an instance in it.
For each instance: code/mksys.py (or mksys3.py for instances_t3.json) writes the system, code/lfdclose2 D writes the
certificate (if 1 is not in W_D), and verify/cert_check.py checks it. Logs: logs/NAME.{closure,check}.txt;
summary line per instance: logs/summary.txt (with the sha256 of the certificate file, which is canonical:
it depends only on W_D and the column order, not on the elimination).
Run from the directory that holds code/, verify/ and results/ (here the work directory)."""
import hashlib, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

workers, D = int(sys.argv[1]), sys.argv[2]
items = [a.split(":") for a in sys.argv[3:]]
os.makedirs("sys", exist_ok=True); os.makedirs("cert", exist_ok=True); os.makedirs("logs", exist_ok=True)

def run(item):
    jf, name = item
    t3 = "t3" in os.path.basename(jf)
    rec = {r["name"]: r for r in json.load(open(jf))}[name]
    sysf, cert = f"sys/{name}.sys", f"cert/{name}.D{D}.cert"
    t0 = time.time()
    subprocess.run(["python3", "code/mksys3.py" if t3 else "code/mksys.py", jf, name, sysf], check=True, stdout=subprocess.DEVNULL)
    with open(f"logs/{name}.closure.txt", "w") as fh:
        subprocess.run(["code/lfdclose2", D, "0", "60000", cert], stdin=open(sysf), stdout=fh, stderr=subprocess.STDOUT, check=True)
    closure = open(f"logs/{name}.closure.txt").read()
    t1 = time.time()
    if not os.path.exists(cert):
        line = f"{name}: no certificate (1 in W_{D}?) :: " + closure.strip().splitlines()[-1]
    else:
        args = ["python3", "verify/cert_check.py"] + (["--t3"] if t3 else []) + [cert, str(rec["n"]), rec["modulus_hex"], str(rec["a2"]),
                rec["a6_hex"], rec["z_hex"]] + rec["V_basis_hex"]
        with open(f"logs/{name}.check.txt", "w") as fh:
            r = subprocess.run(args, stdout=fh, stderr=subprocess.STDOUT)
        check = open(f"logs/{name}.check.txt").read().strip().splitlines()
        sha = hashlib.sha256(open(cert, "rb").read()).hexdigest()
        W = [l for l in closure.splitlines() if l.startswith("W")][0]
        line = (f"{name}: {'VALID' if r.returncode == 0 and check and check[-1].startswith('VALID') else 'REJECTED'} "
                f"cert_sha256={sha} closure[{t1-t0:.0f}s] check[{time.time()-t1:.0f}s] :: {W} :: {check[-1] if check else '?'}")
        os.remove(cert)     # canonical and reproducible; the sha256 is kept
    with open("logs/summary.txt", "a") as fh:
        fh.write(line + "\n")
    print(line, flush=True)

with ThreadPoolExecutor(workers) as ex:
    list(ex.map(run, items))
