#!/usr/bin/env python3
"""Compile exactly the modules missing from the extracted Mathlib cache that a
target file transitively needs, resolving nested missing deps with a worklist."""
import os, re, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).parent.resolve()
os.chdir(ROOT)
PKGS = sorted((ROOT/".lake"/"packages").glob("*"))
LEAN_PATH = ":".join(str(p/".lake"/"build"/"lib"/"lean") for p in PKGS
                     if (p/".lake"/"build"/"lib"/"lean").is_dir())
ENV = {**os.environ, "LEAN_PATH": LEAN_PATH,
       "PATH": os.path.expanduser("~/.elan/bin") + ":" + os.environ["PATH"]}
MISSING = re.compile(r"of module ([A-Za-z0-9_.]+) does not exist")

def find_src(mod):
    rel = mod.replace(".", "/") + ".lean"
    for p in PKGS:
        for cand in (p/rel, p/p.name/rel):
            if cand.is_file(): return cand, p
    return None, None

def run_lean(args):
    return subprocess.run(["lean", *args], env=ENV, capture_output=True, text=True)

def compile_mod(mod):
    src, pkg = find_src(mod)
    if src is None: return "NOSRC", None
    out = pkg/".lake"/"build"/"lib"/"lean"/(mod.replace(".", "/") + ".olean")
    out.parent.mkdir(parents=True, exist_ok=True)
    r = run_lean(["-o", str(out), str(src)])
    if out.is_file(): return "OK", None
    m = MISSING.search(r.stdout + r.stderr)
    if m: return "DEP", m.group(1)
    return "ERR", (r.stdout + r.stderr)[:400]

target = sys.argv[1] if len(sys.argv) > 1 else "CryptoResearch/Semaev/DegreeTwoFall.lean"
built = 0
for outer in range(2000):
    r = run_lean([target])
    m = MISSING.search(r.stdout + r.stderr)
    if not m:
        print(f"TARGET RESOLVED after building {built} module(s)")
        print((r.stdout + r.stderr).strip()[:2000] or "(no diagnostics)")
        sys.exit(0)
    stack = [m.group(1)]
    while stack:
        mod = stack[-1]
        status, info = compile_mod(mod)
        if status == "OK":
            stack.pop(); built += 1
            if built % 25 == 0: print(f"  ... {built} built", flush=True)
        elif status == "DEP":
            if info in stack: print("CYCLE", info); sys.exit(2)
            stack.append(info)
        else:
            print(f"FAILED {mod}: {status} {info}"); sys.exit(3)
print("gave up")
