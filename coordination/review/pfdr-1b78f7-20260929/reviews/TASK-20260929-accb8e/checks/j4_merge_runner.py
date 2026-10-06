"""J4(b) runner: re-execute the ARCHIVED merge_census.py `merge` (file unedited, sha256
checked) against the detached worktree at a32e70808, into my scratch directory.

The archived harness hard-codes REPO = "/home/user/crypto-autoresearcher" (the shared
working tree) in merge_census.py, run_jobs.py and run_wrapper.py. RV-1 forbids reading
anything but the committed package, so the ONLY adaptation is: the module constant REPO
is set to the detached worktree path after each archived module is loaded (merge_census
itself, and every module it or run_jobs loads through their load_module helpers).
No line of any archived file is edited. GIT_OPTIONAL_LOCKS=0 keeps the harness's git
status calls from writing git's index. Outputs go to --out (scratch, absolute path).
Usage: python j4_merge_runner.py <merge args ...>"""
import hashlib, importlib.util, os, sys
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-census-a32e70808"
MC = os.path.join(WT, "experiments/EXP-PFDR-1b78f7/amd-430f44/merge_census.py")
EXPECT = "143ea699f9c891702f0dc39586090dc68897eafc2a61c07d54579537f0a6c165"  # post-DEV-A pin (archived)

os.environ["GIT_OPTIONAL_LOCKS"] = "0"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True
h = hashlib.sha256(open(MC, "rb").read()).hexdigest()
if h != EXPECT:
    raise SystemExit(f"merge_census.py sha256 {h} != archived pin {EXPECT}")

spec = importlib.util.spec_from_file_location("merge_census_archived", MC)
mc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc)
mc.REPO = WT


def _redirect(mod):
    if hasattr(mod, "REPO"):
        mod.REPO = WT
    if hasattr(mod, "load_module") and not getattr(mod.load_module, "_redirected", False):
        orig = mod.load_module

        def wrapped(*args, **kw):
            m = orig(*args, **kw)
            _redirect(m)
            return m
        wrapped._redirected = True
        mod.load_module = wrapped
    return mod


_redirect(mc)
sys.argv = ["merge_census.py"] + sys.argv[1:]
print(f"# runner: merge_census.py sha256 {h}; REPO redirected to {WT}", flush=True)
raise SystemExit(mc.main())
