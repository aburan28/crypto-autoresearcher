import sys; sys.dont_write_bytecode=True
sys.path.insert(0,"/tmp/claude-0/validator")
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-e76704/src")
import run_separation as R
from recomb_search import recombine
from truekernel import gl_rowsets
import boolring as B
import importlib.util
spec=importlib.util.spec_from_file_location("h","/tmp/claude-0/validator/hps_def6.py")
src=open("/tmp/claude-0/validator/hps_def6.py").read().split("for name,G in")[0]   # reuse function defs only
ns={}; exec(src.replace("N=6","N=4"),ns)
hps=ns["hps"]
for nm,gs in (("semaev(4,2)",R.cell_systems(4,2)[0]),("null(4,2)",R.cell_systems(4,2)[1])):
    def hffd(G):
        for D in range(2,5):
            if hps(G,D)[2]>0: return D
        return None
    base=hffd([B.from_set(f) for f in gs]); dist={}
    for M in gl_rowsets(4):
        d=hffd([B.from_set(f) for f in recombine(gs,M)]); dist[d]=dist.get(d,0)+24
    print(nm,"HPS-style nontrivial first fall: identity",base," distribution over GL_4:",dist)
