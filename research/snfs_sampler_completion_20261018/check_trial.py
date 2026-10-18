"""Replay all trace arithmetic with Fractions; exact Sage checks for catalog rows."""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
import tarfile
os.environ.setdefault("DOT_SAGE", "/workspace/snfs-toolchains/sage-state")
os.environ["PATH"]="/workspace/snfs-toolchains/sage-pixi/.pixi/envs/default/bin:"+os.environ.get("PATH", "")
os.environ.setdefault("SINGULARPATH", "/workspace/snfs-toolchains/sage-pixi/.pixi/envs/default/share/singular/LIB")

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SPEC=importlib.util.spec_from_file_location("independent_field_arithmetic",ROOT/"experiments/EXP-ECDLP-4c6a09/implementation/check.py")
ARITH=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(ARITH)


def check_stream(events,inp,result):
    points=set();residues=set();rational=missing=0;rungs=[];finished=0
    g=inp["g"];p=int(inp["p"]);root=int(inp["root"])
    last_work=0
    for event in events:
        if event["event"]=="point":
            assert finished==0
            x=[Fraction(v) for v in event["x"]];y=[Fraction(v) for v in event["y"]]
            assert len(x)==len(y)==len(g)-1
            assert ARITH.poly_mul_mod(y,y,g)==ARITH.rhs(x,Fraction(inp["A"]),Fraction(inp["B"]),g)
            k=(tuple(x),tuple(y));assert k not in points;points.add(k)
            rx,ry=ARITH.embed(x,p,root),ARITH.embed(y,p,root)
            is_rational=all(v==0 for v in x[1:]+y[1:]);assert event["rational"]==is_rational
            if rx is None or ry is None:
                assert event["residue"] is None;missing+=1
            else:
                assert event["residue"]==[str(rx),str(ry)]
                assert (ry*ry-rx**3-int(inp["A"])*rx-int(inp["B"]))%p==0
                residues.add((rx,ry));rational+=is_rational
            assert event["work"]>=last_work;last_work=event["work"]
        elif event["event"] in ("checkpoint","finished"):
            row=event["snapshot"]
            assert row["work"]>=last_work;last_work=row["work"]
            assert (row["points_found_cumulative"],row["distinct_residues"],row["rational_points_seen"],row["points_without_residue"])==(len(points),len(residues),rational,missing)
            if event["event"]=="checkpoint":
                assert finished==0 and row["boundary"]=="before_candidate";rungs.append(row)
            else:
                assert row["boundary"]=="after_search_end" and row==result["final"];finished+=1
        elif event["event"]=="shell":
            assert event["work"]>=last_work and finished==0;last_work=event["work"]
        else:raise AssertionError("unknown event")
    assert finished==1 and rungs==result["rungs"]
    return len(points)


def check_panel(data,contents):
    panel=json.loads((HERE/"panel.json").read_text())
    inputs={i["id"]:i for i in panel["inputs"]}
    assert len(data["rows"])==len(panel["jobs"])==102
    assert contents["panel-result.json"]== (json.dumps(data,indent=2)+"\n").encode() or json.loads(contents["panel-result.json"])==data
    old=json.loads((ROOT/panel["source_raw"]).read_text())["cells"]
    assert hashlib.sha256((ROOT/panel["source_raw"]).read_bytes()).hexdigest()==panel["source_sha256"]
    checked=0
    seen={}
    for row,job in zip(data["rows"],panel["jobs"]):
        assert row["job"]==job and row["input_id"]==job["input_id"]
        payload=contents[job["id"]+".jsonl"]
        checked+=check_stream([json.loads(line) for line in payload.splitlines()],inputs[job["input_id"]],row["observations"])
        assert [r["work"] for r in row["observations"]["rungs"]]==panel["ladder"]
        if job["role"]=="same_seed_replay":
            assert payload==contents[job["replay_of"]+".jsonl"]
            assert row["observations"]==seen[job["replay_of"]]["observations"]
        if job["role"]=="legacy_control":
            prior=old[job["source_row"]]
            for a,b in zip(row["observations"]["rungs"],prior["rungs"]):
                for key in ("work","shells_completed","points_found_cumulative","distinct_residues","rational_points_seen","points_without_residue"):
                    assert a[key]==b[key],(job["id"],key,a[key],b[key])
        seen[job["id"]]=row
    expected={j["id"]+".jsonl" for j in panel["jobs"]}|{"panel-result.json"}
    assert set(contents)==expected
    return dict(jobs=len(data["rows"]),point_events_checked=checked,legacy_controls=11,exact_replays=7)


def check_support(data,contents):
    from sage.all import PolynomialRing,QQ,ZZ
    ring=PolynomialRing(QQ,"x")
    coefficients=json.loads((HERE/"coefficients.json").read_text())
    source=[json.loads(line) for line in contents["source-screen.jsonl"].splitlines()]
    assert json.loads(contents["support-catalog.json"])==data
    assert len(data["rows"])==len(source)==len(coefficients)==3232
    for row,base,coef in zip(data["rows"],source,coefficients):
        assert row["g"]==base["g"]==coef["g"] and row["shape"]==coef["shape"]
        for key,value in base.items():
            if key!="values":assert row[key]==value
        f=ring(row["g"])
        assert row["q_irreducible"]==bool(f.is_irreducible())
        product=ring(1)
        for factor in row["q_factorization"]:
            product*=ring(factor["g"])**factor["multiplicity"]
        assert product==f and str(ZZ(f.discriminant()))==row["discriminant"]
        assert len(row["values"])==len(base["values"])==9
        assert [v["k"] for v in row["values"]]==list(range(4,13))
        for value,source_value in zip(row["values"],base["values"]):
            for key,v in source_value.items():assert value[key]==v
            assert int(value["p"])==sum(c*(1<<value["k"])**i for i,c in enumerate(row["g"]))
            assert value["prime_proof_enabled"]==bool(ZZ(value["p"]).is_prime(proof=True))
            assert value["exact_eligible_prime"]==(int(value["p"])>=4096 and value["prime_proof_enabled"])
        assert row["exact_admissible"]==(row["q_irreducible"] and any(v["exact_eligible_prime"] for v in row["values"]))
        assert row["source_admissible"]==(row["source_irreducibility_witness"] is True and any(v["source_prime_screen"] for v in row["values"]))
        eligible=[v["k"] for v in row["values"] if v["exact_eligible_prime"]]
        assert row["first_exact_eligible"]==(eligible[0] if eligible else None)
    for shape,summary in data["summary"].items():
        rs=[r for r in data["rows"] if r["shape"]==shape]
        expected=dict(coefficient_patterns=len(rs),q_irreducible=sum(r["q_irreducible"] for r in rs),
                      source_witnessed=sum(r["source_irreducibility_witness"] is True for r in rs),
                      source_witness_disagreements=sum(r["source_irreducibility_witness"] is True and not r["q_irreducible"] for r in rs),
                      exact_admissible=sum(r["exact_admissible"] for r in rs),source_admissible=sum(r["source_admissible"] for r in rs),
                      exact_admissible_without_source_witness=sum(r["exact_admissible"] and r["source_irreducibility_witness"] is not True for r in rs),
                      source_prime_screen_disagreements=sum(v["source_prime_screen"]!=v["exact_eligible_prime"] for r in rs for v in r["values"]))
        assert summary==expected
    assert set(data["summary"])=={"P-192","P-224","P-256","P-384"}
    assert set(contents)=={"source-screen.jsonl","support-catalog.json"}
    return dict(coefficient_patterns=3232,prime_values_checked=3232*9)


def main(run):
    for binding in json.loads((HERE/"runtime-bindings.json").read_text()).values():
        assert hashlib.sha256(Path(binding["path"]).read_bytes()).hexdigest()==binding["sha256"], "runtime binding changed"
    raw=json.loads((run/"raw-result.json").read_text())
    manifest=json.loads((run/"manifest.yaml").read_text())["run"]
    launch=json.loads((run/"launch.json").read_text())
    environment=json.loads((run/"environment.json").read_text())
    assert manifest["code"]["commit"]==environment["commit"]
    assert manifest["code"]["command"]==launch["argv"]
    assert manifest["result"]["certificate"]["kind"]=="none"
    assert manifest["result"]["raw_sha256"]==hashlib.sha256((run/"raw-result.json").read_bytes()).hexdigest()
    assert manifest["result"]["instrument_sha256"]==hashlib.sha256((run/"instrument.tar.gz").read_bytes()).hexdigest()
    index=json.loads((run/"instrument-index.json").read_text())
    contents={}
    with tarfile.open(run/"instrument.tar.gz","r:gz") as archive:
        for member in archive.getmembers():
            assert member.isfile() and "/" not in member.name and member.name not in contents
            contents[member.name]=archive.extractfile(member).read()
    assert len(index)==len(contents)
    for row in index:
        assert len(contents[row["name"]])==row["bytes"]
        assert hashlib.sha256(contents[row["name"]]).hexdigest()==row["sha256"]
    result=check_panel(raw["data"],contents) if raw["mode"]=="panel" else check_support(raw["data"],contents)
    print(json.dumps(dict(scope="Built-in mechanical replay, not independent scientific review",**result)))


if __name__=="__main__":main(Path(sys.argv[1]))
