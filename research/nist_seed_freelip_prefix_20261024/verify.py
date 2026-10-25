#!/usr/bin/env python3
"""Independent integer RNG and point replay of the actual FreeLIP calls."""
import hashlib
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
M=(1<<107)-1
MULTIPLIER=pow(3,121,M)

class Random:
    def __init__(self,seed):self.state=seed;self.advances=0
    def draw(self,bound):
        ceiling=M-(M%bound)
        while True:
            self.state=self.state*MULTIPLIER%M;self.advances+=1
            if self.state<ceiling:return self.state%bound

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(directory):
    result=json.loads((directory/"results.json").read_text())
    assert result["status"]=="completed" and len(result["cases"])==77
    assert result["protocol_sha256"]==digest(HERE/"PROTOCOL.md")
    assert result["build_amendment_sha256"]==digest(HERE/"BUILD_AMENDMENT.md")
    assert result["launcher_sha256"]==digest(HERE/"run.py")
    assert result["wrapper_sha256"]==digest(HERE/"replay.c")
    source={}
    for name,sha in result["input_sha256"].items():
        path=ROOT/"research/nist_seed_skipped_curves_20261016"/name
        assert digest(path)==sha
        data=json.loads(path.read_text())
        entries=data["candidate_rows"] if name=="assessed.json" else data["published_controls"].values()
        for row in entries:source[row["identity"]["curve_uid"]]=row
    assert len(source)==21
    route_matches=[];controls=[];large_orders=0;small_controls=0
    for case in result["cases"]:
        if "curve_uid" in case:
            row=source[case["curve_uid"]]
            assert (int(case["p"]),int(case["b"]),int(case["n"]))==tuple(int(row[k],16) for k in ("p_hex","b_hex","n_hex"))
            if case["kind"]=="point":assert int(case["expected_gx"])==row["identity"]["curve"]["generator"][0]
        assert case["exit_code"]==0
        bits=case["nbits"];radix=1<<bits
        capture={}
        for line in case["stdout"].splitlines():
            words=line.split();key=words[0].lower();ints=list(map(int,words[1:]))
            if key in ("nbits","return","tries"):capture[key]=ints[0]
            else:
                assert ints[0]==len(ints)-1
                capture[key]=str(sum(v*radix**i for i,v in enumerate(ints[1:])))
        assert capture==case["parsed"] and capture["nbits"]==bits
        assert int(capture["initial"])==case["seed"]
        rng=Random(case["seed"])
        if case["mode"]=="direct":
            for _ in range(case["rounds"]):rng.draw(radix)
            expected_return=-1
        else:
            tested=int(case["p"] if case["mode"].endswith("-p") else case["n"])
            expected_return=case.get("expected_return",1)
            if case["kind"]=="control":
                assert tested in (15,101)
            else:
                assert tested>radix
                sm=(tested%radix)-3
                if sm<=(1<<(bits//2))-3:sm=radix-4
                random_tests=case["rounds"] if case["mode"].startswith("prob") else case["rounds"]-1
                for _ in range(random_tests):rng.draw(sm)
                assert random_tests==7 and rng.advances==7
        assert capture["return"]==expected_return
        assert int(capture["prefix"])==rng.state
        if case["kind"]=="point":
            p,b=int(case["p"]),int(case["b"])
            limbs=(p.bit_length()+bits-1)//bits+1
            for tries in range(1,33):
                x=0
                for _ in range(limbs):x=x*radix+rng.draw(radix)
                x%=p
                if pow((x*x*x-3*x+b)%p,(p-1)//2,p)==1:break
            else:raise AssertionError("point-search bound exhausted")
            assert capture["tries"]==tries and int(capture["x"])==x and int(capture["final"])==rng.state
            assert case["gx_matches"]==(x==int(case["expected_gx"]))
            if bits==26 and ((case["mode"]=="direct" and case["rounds"]==7) or case["mode"]!="direct"):
                route_matches.append(case["gx_matches"])
            else:controls.append(case["gx_matches"])
        else:
            assert capture["tries"]==0 and int(capture["final"])==rng.state
            if case["kind"]=="control":small_controls+=1;assert rng.advances==0
            else:large_orders+=1;assert rng.advances==7 and expected_return==1
    assert len(route_matches)==30 and all(route_matches)
    assert len(controls)==24 and large_orders==21 and small_controls==2
    return {"status":"passed","cases":77,"proposed_point_routes":30,"proposed_route_matches":sum(route_matches),"point_controls":24,"point_control_matches":sum(controls),"large_prime_order_calls":21,"large_order_seven_advance_matches":large_orders,"small_controls_without_rng_draws":small_controls,"results_sha256":digest(directory/"results.json"),"verifier_sha256":digest(Path(__file__))}

if __name__=="__main__":
    directory=Path(sys.argv[1]);out=directory/"verification.json"
    assert not out.exists()
    record=verify(directory)
    out.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print(json.dumps(record,sort_keys=True))
