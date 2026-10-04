import subprocess, sys, time, resource, json, datetime

start_wall = time.time()
start_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
proc = subprocess.run([sys.executable, "compute.py"], capture_output=True, text=True)
end_wall = time.time()
end_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

with open("raw-result.json", "w") as f:
    f.write(proc.stdout)
with open("stdout.log", "w") as f:
    f.write(proc.stdout[:2000] + ("\n...TRUNCATED, full content in raw-result.json...\n" if len(proc.stdout) > 2000 else ""))
with open("stderr.log", "w") as f:
    f.write(proc.stderr)

ru = resource.getrusage(resource.RUSAGE_CHILDREN)
meta = {
    "exit_code": proc.returncode,
    "started_at": start_iso,
    "finished_at": end_iso,
    "wall_seconds": end_wall - start_wall,
    "cpu_seconds_user": ru.ru_utime,
    "cpu_seconds_system": ru.ru_stime,
    "peak_rss_kb": ru.ru_maxrss,
}
with open("resource_usage.json", "w") as f:
    json.dump(meta, f, indent=2)
print(json.dumps(meta, indent=2))
