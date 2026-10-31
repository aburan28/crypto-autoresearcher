"""Record every interpreter and tool used by this review and the recorded interpreter of the five runs.

usage: python3 -I -B interpreters.py <repo-root> <out.json>
"""
import json
import os
import platform
import subprocess
import sys

import yaml

repo, out = sys.argv[1:3]
probe = ("import json,sys,platform;"
         "d={'version':sys.version,'version_info':list(sys.version_info[:3]),'executable':sys.executable,"
         "'implementation':sys.implementation.name,'isolated':sys.flags.isolated,'dont_write_bytecode':sys.dont_write_bytecode};"
         "\ntry:\n import numpy; d['numpy']=numpy.__version__\nexcept ImportError: d['numpy']=None\n"
         "try:\n import yaml; d['pyyaml']=yaml.__version__\nexcept ImportError: d['pyyaml']=None\n"
         "print(json.dumps(d))")
interp = {}
for exe in ("/usr/bin/python3.11", "/usr/bin/python3.13"):
    interp[exe] = json.loads(subprocess.run([exe, "-B", "-I", "-c", probe], capture_output=True, text=True, check=True).stdout)
recorded = {}
for rid in ("RUN-PFDR-e44a19", "RUN-PFDR-4d8c71", "RUN-PFDR-243425", "RUN-PFDR-cd03e2", "RUN-PFDR-089edc"):
    d = os.path.join(repo, "experiments/EXP-PFDR-bb0d26/runs", rid)
    m = yaml.safe_load(open(os.path.join(d, "manifest.yaml")))["run"]
    env = json.load(open(os.path.join(d, "environment.json")))
    recorded[rid] = {"trial": m["trial_id"], "manifest_python_version": m["environment"]["python_version"],
                     "manifest_command_executable": m["code"]["command"].split()[0],
                     "environment_json_python": env["python"], "gcc_version": m["environment"]["gcc_version"],
                     "operating_system": m["environment"]["operating_system"]}
default = subprocess.run(["python3", "-c", "import sys;print(sys.version.split()[0], sys.executable)"], capture_output=True, text=True).stdout.strip()
uses = {
    "/usr/bin/python3.11": ["replay-py311 (selftest, analyze-main, analyze-final via run.py trial)", "checkpy-py311 (check.py x5)",
                            "recount.py --sets-only (set digests of the 33 sampled jobs)"],
    "/usr/bin/python3.13": ["replay-py313 (selftest, analyze-main, analyze-final via run.py trial)", "checkpy-py313 (check.py x5)",
                            "digests.py, compare.py, integrity.py, select_sample.py, regen_curves.py, recount.py, compact_recount.py, "
                            "kernel_spotcheck.py, curve_orders.py, degenerate.py, report_page1.py, interpreters.py, inventory.py"],
}
tools = {
    "gcc": subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0],
    "gp": subprocess.run(["gp", "--version-short"], capture_output=True, text=True).stdout.strip(),
    "pdftotext": subprocess.run(["pdftotext", "-v"], capture_output=True, text=True).stderr.splitlines()[0],
    "host_platform": platform.platform(),
    "default_python3_on_host": default,
    "recorded_command_interpreter_present_on_host": os.path.exists("/usr/local/bin/python3"),
}
res = {"interpreters_used": {k: dict(v, used_for=uses[k]) for k, v in interp.items()},
       "recorded_runs": recorded,
       "comparison": {
           "recorded_python_version": sorted({v["manifest_python_version"] for v in recorded.values()}),
           "py311_replay_interpreter": interp["/usr/bin/python3.11"]["version"].split()[0],
           "same_major_minor_as_record": interp["/usr/bin/python3.11"]["version_info"][:2] == [3, 11],
           "patch_level_differs": interp["/usr/bin/python3.11"]["version"].split()[0] != "3.11.15",
           "note": ("The host has CPython 3.11.17 (not the recorded 3.11.15; recorded, not assumed). "
                    "The 3.13.17 replay is compared under the declared float tolerance only.")},
       "tools": tools}
with open(out, "w") as f:
    json.dump(res, f, indent=1)
    f.write("\n")
print(json.dumps(res["comparison"]), json.dumps(tools))
