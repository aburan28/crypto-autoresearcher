#!/usr/bin/env python3
"""Bounded call-level FreeLIP prefix replay; never overwrite a prior run."""
import argparse
import datetime as dt
import hashlib
import json
import platform
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
INPUT=ROOT/"research/nist_seed_skipped_curves_20261016"
SEEDS={"prime192v1":20000,"prime239v1":20420,"prime239v2":20507,"prime239v3":20509,"prime192v2":20512,"prime192v3":20517}
SHAS={"traits.json":"a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67","assessed.json":"370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841"}
TAR_SHA="cd168c2ba0f9052d84072664b559219506050f583fdf58060517d59422f5bccc"

def sha(data): return hashlib.sha256(data).hexdigest()
def write(path,value): path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
def command(cmd,timeout):
    started=time.monotonic()
    try:
        p=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
        return {"command":cmd,"exit_code":p.returncode,"stdout":p.stdout,"stderr":p.stderr,"elapsed_seconds":time.monotonic()-started}
    except subprocess.TimeoutExpired as e:
        return {"command":cmd,"exit_code":None,"stdout":str(e.stdout or ""),"stderr":str(e.stderr or ""),"timeout":True,"elapsed_seconds":time.monotonic()-started}

def parse(stdout):
    data={}
    for line in stdout.splitlines():
        words=line.split(); key=words[0]; values=list(map(int,words[1:]))
        if key in ("NBITS","RETURN","TRIES"): data[key.lower()]=values[0]
        else:
            length=values[0]; assert length==len(values)-1
            data[key.lower()]=str(sum(v << (data["nbits"]*i) for i,v in enumerate(values[1:])))
    return data

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--tarball",type=Path,required=True);parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    assert sha(args.tarball.read_bytes())==TAR_SHA
    for name,digest in SHAS.items(): assert sha((INPUT/name).read_bytes())==digest
    traits=json.loads((INPUT/"traits.json").read_text())["published_controls"]
    omitted=json.loads((INPUT/"assessed.json").read_text())["candidate_rows"]
    record={"started_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"command":sys.argv,"platform":platform.platform(),"python":sys.version,"source_archive_sha256":TAR_SHA,"input_sha256":SHAS,"protocol_sha256":sha((HERE/"PROTOCOL.md").read_bytes()),"launcher_sha256":sha(Path(__file__).read_bytes()),"wrapper_sha256":sha((HERE/"replay.c").read_bytes()),"head":command(["git","rev-parse","HEAD"],5),"dirty":command(["git","status","--porcelain"],5),"compiler":command(["clang","--version"],5),"builds":[],"cases":[]}
    write(args.out/"started.json",record)
    try:
        for bits,configuration in ((26,"#define SINGLE_MUL 1\n"),(30,"#define PLAIN 1\n")):
            with tempfile.TemporaryDirectory(prefix="nist-freelip-prefix-") as td:
                build=Path(td)
                with tarfile.open(args.tarball,"r:gz") as archive:
                    for name in ("lip.c","lip.h"):
                        content=archive.extractfile("freelip-1.0.orig/"+name).read()
                        if name=="lip.c": assert sha(content)=="5c507451e8c13323f106a66b5f76cdf17dfbe9eb7f289eb1ac0c706855625bff"
                        (build/name).write_bytes(content)
                (build/"lippar.h").write_text(configuration)
                (build/"malloc.h").write_text("#include <stdlib.h>\n")
                (build/"replay.c").write_bytes((HERE/"replay.c").read_bytes())
                exe=build/"replay"
                compiled=command(["clang","-std=gnu89","-O0","-DSIZEOFLONG=8","-I",str(build),"-include","string.h",str(build/"lip.c"),str(build/"replay.c"),"-lm","-o",str(exe)],10)
                compiled.update({"nbits":bits,"configuration":configuration})
                record["builds"].append(compiled);write(args.out/f"build_{bits}.json",compiled)
                if compiled["exit_code"]!=0: raise RuntimeError("library build failed")
                compiled["executable_sha256"]=sha(exe.read_bytes())
                cases=[]
                routes=[("direct",7),("prob-p",7),("prob-n",7),("prime-p",8),("prime-n",8),("direct",0),("direct",6),("direct",8)] if bits==26 else [("direct",7)]
                for name,seed in SEEDS.items():
                    row=traits[name]
                    for mode,rounds in routes:
                        cases.append({"name":name,"kind":"point","mode":mode,"rounds":rounds,"seed":seed,"curve_uid":row["identity"]["curve_uid"],"p":str(int(row["p_hex"],16)),"b":str(int(row["b_hex"],16)),"n":str(int(row["n_hex"],16)),"expected_gx":str(row["identity"]["curve"]["generator"][0])})
                if bits==26:
                    orders=[("published",name,row) for name,row in traits.items()]+[("omitted",row["identity"]["curve_id"],row) for row in omitted]
                    assert len(orders)==21
                    for kind,name,row in orders:
                        cases.append({"name":name,"kind":kind,"mode":"classify-n","rounds":8,"seed":7157891,"curve_uid":row["identity"]["curve_uid"],"p":str(int(row["p_hex"],16)),"b":str(int(row["b_hex"],16)),"n":str(int(row["n_hex"],16)),"expected_return":1})
                    for n,expected in ((101,1),(15,0)):
                        cases.append({"name":f"control_{n}","kind":"control","mode":"classify-n","rounds":8,"seed":7157891,"p":"101","b":"1","n":str(n),"expected_return":expected})
                for case in cases:
                    remaining=120-(time.monotonic()-start)
                    if remaining<=0: raise TimeoutError("whole-launch watchdog")
                    result=command([str(exe),case["mode"],str(case["seed"]),str(case["rounds"]),case["p"],case["b"],case["n"]],min(10,remaining))
                    case.update(result);case["nbits"]=bits
                    record["cases"].append(case)
                    write(args.out/f"case_{len(record['cases']):02d}.json",case)
                    if result["exit_code"]!=0: raise RuntimeError("call failed: "+case["name"])
                    case["parsed"]=parse(result["stdout"])
                    assert case["parsed"]["nbits"]==bits
                    if case["kind"]=="point":case["gx_matches"]=case["parsed"]["x"]==case["expected_gx"]
                    else:assert case["parsed"]["return"]==case["expected_return"]
        assert len(record["cases"])==77
        record.update({"status":"completed","finished_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"elapsed_seconds":time.monotonic()-start})
        write(args.out/"results.json",record)
        print(json.dumps({"cases":len(record["cases"]),"point_matches":sum(c.get("gx_matches",False) for c in record["cases"])}))
    except Exception as e:
        record.update({"status":"failed","failure":f"{type(e).__name__}: {e}","elapsed_seconds":time.monotonic()-start})
        write(args.out/"failure.json",record)
        raise

if __name__=="__main__":main()
