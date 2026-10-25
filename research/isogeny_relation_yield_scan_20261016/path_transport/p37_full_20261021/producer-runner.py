#!/usr/bin/env python3
"""Keep a Conductor fence alive while a bounded, resumable P37 path run executes."""
import json
import os
from pathlib import Path
import signal
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request

worktree = Path(sys.argv[1]).resolve()
fence = json.loads(Path(sys.argv[2]).read_text())
creds = json.loads((Path.home() / ".conductor/credentials").read_text())
ctx = ssl.create_default_context(cafile="/Users/adamburan/.conductor/certs/ca.pem")
url = "https://127.0.0.1:8443/v1/leases/heartbeat"
logdir = Path(sys.argv[3])
logdir.mkdir(exist_ok=False)
cmd = ["gtimeout", "7200", "/usr/bin/time", "-l", "sage", "-sh", "-c",
       "DOT_SAGE=/tmp/ectd-p37-full-sage PYTHONDONTWRITEBYTECODE=1 "
       "python3 research/isogeny_relation_yield_scan_20261016/path_transport/transport_path.py "
       "--stratum P37 --max-edges 256 "
       "--output-dir research/isogeny_relation_yield_scan_20261016/path_transport/controls/p37-twoedge-attempt1 --resume"]
(logdir / "command.json").write_text(json.dumps({"argv": cmd, "cwd": str(worktree),
    "fence": fence, "start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=2))

def heartbeat():
    request = urllib.request.Request(url, data=json.dumps(fence).encode(), method="POST",
        headers={"Authorization": "Bearer " + creds["token"], "Content-Type": "application/json"})
    with urllib.request.urlopen(request, context=ctx, timeout=25) as response:
        body = json.load(response)
        if response.status != 200:
            raise RuntimeError("heartbeat HTTP " + str(response.status))
        return body

heartbeat()
last_ok = time.monotonic()
with (logdir / "stdout.log").open("w") as stdout, (logdir / "stderr.log").open("w") as stderr:
    proc = subprocess.Popen(cmd, cwd=worktree, stdout=stdout, stderr=stderr, start_new_session=True)
    try:
        while proc.poll() is None:
            time.sleep(5)
            if time.monotonic() - last_ok >= 15:
                try:
                    heartbeat()
                    last_ok = time.monotonic()
                except Exception as exc:
                    with (logdir / "heartbeat-errors.log").open("a") as out:
                        out.write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + " " + repr(exc) + "\n")
                    if isinstance(exc, urllib.error.HTTPError) and exc.code == 409 or time.monotonic() - last_ok >= 45:
                        os.killpg(proc.pid, signal.SIGTERM)
                        raise RuntimeError("lease heartbeat lost or failed for 45 seconds") from exc
    finally:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(timeout=15)
    (logdir / "exit.json").write_text(json.dumps({"returncode": proc.returncode,
        "end_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=2))
    print(json.dumps({"returncode": proc.returncode, "logdir": str(logdir)}), flush=True)
    sys.exit(proc.returncode)
