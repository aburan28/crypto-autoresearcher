#!/usr/bin/env python3
"""Drive the validator's two null objects through a given tree's bench.Runner.run (the
instrument's own limit path, unmodified).  Usage: drive_null.py <tree> <run_dir> <which>
which = hog | reserve.  The driver sets its own oom_score_adj=1000 (inherited) so that if the
kernel OOM killer fires on this swapless guest it takes the null object, not a peer."""
import json, os, sys, time
from pathlib import Path
TREE, RUN_DIR, WHICH = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
RUN_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, TREE)
import bench  # noqa
open('/proc/self/oom_score_adj', 'w').write('1000\n')
HERE = Path(__file__).resolve().parent
argv = {"hog": [sys.executable, str(HERE / "hog_resident.py"), "12", "0.05"],
        "reserve": [sys.executable, str(HERE / "reserve_addrspace.py"), "64", "384"]}[WHICH]
R = bench.Runner(RUN_DIR, dry=False)
pre = {"loadavg": os.getloadavg(), "mem_available_kb": [int(l.split()[1]) for l in open('/proc/meminfo') if l.startswith('MemAvailable')][0],
       "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "tree": TREE,
       "tree_limit": {"RSS_LIMIT_GB": getattr(bench, "RSS_LIMIT_GB", None), "MEM_LIMIT_GB": getattr(bench, "MEM_LIMIT_GB", None),
                      "RSS_POLL_INTERVAL_S": getattr(bench, "RSS_POLL_INTERVAL_S", None)}}
rec = R.run(argv, f"null_{WHICH}", 300)
out = (RUN_DIR / rec["stdout"]).read_text(errors='replace').splitlines()
err = (RUN_DIR / rec["stderr"]).read_text(errors='replace').splitlines()
res = {"pre_launch": pre, "row": rec, "child_stdout_head": out[:3], "child_stdout_tail": out[-4:], "child_stderr_tail": err[-6:],
       "child_stdout_lines": len(out)}
print(json.dumps(res, indent=1))
(RUN_DIR / f"validator_{WHICH}.json").write_text(json.dumps(res, indent=1))
