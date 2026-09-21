#!/usr/bin/env python3
"""Launches a command, polls /proc/<pid>/status for VmHWM (kernel-tracked
peak resident set size, monotonically non-decreasing) at a short interval
until the process exits, and reports the maximum VmHWM sample observed.
Used because /usr/bin/time -v is not installed in this environment (verified
absent: `command -v time` finds only the bash builtin, no /usr/bin/time
binary). VmHWM is the same kernel-maintained "peak RSS" field /usr/bin/time -v
itself reads via getrusage()/proc, so this is a measurement, not an
allocation-arithmetic estimate.
"""
import subprocess, sys, time, os, json

def read_vmhwm(pid):
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmHWM:"):
                    parts = line.split()
                    return int(parts[1])  # kB
    except (FileNotFoundError, ProcessLookupError):
        return None
    return None

def main():
    outfile = sys.argv[1]
    cmd = sys.argv[2:]
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    peak_kb = 0
    samples = 0
    while True:
        ret = proc.poll()
        v = read_vmhwm(proc.pid)
        if v is not None:
            peak_kb = max(peak_kb, v)
            samples += 1
        if ret is not None:
            # one more read attempt (process may already be gone, harmless)
            v = read_vmhwm(proc.pid)
            if v is not None:
                peak_kb = max(peak_kb, v)
            break
        time.sleep(0.05)
    t1 = time.time()
    stdout, stderr = proc.communicate()
    result = {
        "cmd": cmd,
        "returncode": proc.returncode,
        "wall_seconds": t1 - t0,
        "peak_vmhwm_kb": peak_kb,
        "peak_vmhwm_gb": peak_kb / 1e6 if peak_kb else None,
        "poll_samples": samples,
        "method": "VmHWM polled from /proc/<pid>/status at 50ms intervals until exit; /usr/bin/time -v not installed in this environment",
    }
    with open(outfile, "w") as f:
        json.dump(result, f, indent=2)
    sys.stdout.write(stdout.decode(errors="replace"))
    sys.stderr.write(stderr.decode(errors="replace"))
    print(json.dumps(result), file=sys.stderr)
    sys.exit(proc.returncode)

if __name__ == "__main__":
    main()
