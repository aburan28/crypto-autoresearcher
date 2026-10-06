import json, sys
import os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
exec(open(__file__.replace("cp6_sweep.py", "cp6_chain.py")).read().split("t0 = time.time()\ngens, cheap")[0].split("from harness.endosweep.toyverify import Curve")[0])
from harness.endosweep.sweep import sweep_target, SweepOptions, to_jsonable, markdown_report
T.verified, T.verification = True, "order pinned externally: h*n in Hasse interval, (h*n)*G = O, h*G of prime order n (cp6_chain.py)"
res = sweep_target(T, SweepOptions())
json.dump(to_jsonable(res), open("cp6_782_sweep.json", "w"), indent=1, default=str)
open("cp6_782_sweep.md", "w").write(markdown_report([res], SweepOptions()))
print(open("cp6_782_sweep.md").read()[:6000])
