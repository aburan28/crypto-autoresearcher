#!/usr/bin/env python3
"""run_instance.py SYSTEM.ms OUTDIR [threads] [extra closure args...]: the full per-instance pipeline
(parse -> masks -> closure (C) -> postcheck (eval-kernel ground truth + Apriori N_std)).  Writes OUTDIR/<name>.closure.json,
<name>.lm, <name>.postcheck.json and <name>.run.txt (wall, peak RSS)."""
import sys, os, subprocess, json, time, resource, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
ms, outdir = sys.argv[1], sys.argv[2]
threads = sys.argv[3] if len(sys.argv) > 3 else '2'
extra = sys.argv[4:]
os.makedirs(outdir, exist_ok=True)
name = os.path.basename(ms)[:-3]
masks = os.path.join(outdir, name + '.masks')
subprocess.check_call([sys.executable, os.path.join(HERE, 'to_masks.py'), ms, masks])
prefix = os.path.join(outdir, name)
t = time.time()
p = subprocess.Popen([os.path.join(HERE, 'closure'), masks, '-o', prefix, '-t', threads] + extra, stdout=subprocess.PIPE, stderr=open(prefix + '.closure.log', 'w'), text=True)
out, _ = p.communicate()
wall = time.time() - t
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
open(prefix + '.closure.json', 'w').write(out)
open(prefix + '.run.txt', 'w').write('closure wall_s=%.1f maxrss_kb=%d rc=%d threads=%s extra=%s\n' % (wall, ru.ru_maxrss, p.returncode, threads, ' '.join(extra)))
print(name, 'closure rc', p.returncode, 'wall %.1f' % wall, 'maxrss_kb', ru.ru_maxrss)
sys.exit(p.returncode)
