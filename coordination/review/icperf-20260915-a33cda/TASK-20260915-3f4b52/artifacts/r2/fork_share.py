import mmap, os, time, sys
m = mmap.mmap(-1, 1 << 30, flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS)
for off in range(0, 1 << 30, 4096): m[off] = 1
pid = os.fork()
if pid == 0:
    time.sleep(3); os._exit(0)
def rss(p):
    for ln in open(f"/proc/{p}/status"):
        if ln.startswith(("VmRSS","RssAnon","RssShmem")): print(f"  pid {p} {ln.strip()}")
time.sleep(0.5)
print("parent", os.getpid(), "child", pid, flush=True); rss(os.getpid()); rss(pid)
os.waitpid(pid, 0)
