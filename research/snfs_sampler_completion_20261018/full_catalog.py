"""Exact Q factorization and proof-enabled primality for a frozen finite support."""
from collections import Counter
from pathlib import Path
import argparse
import json
import os
os.environ.setdefault("DOT_SAGE", "/workspace/snfs-toolchains/sage-state")
os.environ["PATH"]="/workspace/snfs-toolchains/sage-pixi/.pixi/envs/default/bin:"+os.environ.get("PATH", "")
os.environ.setdefault("SINGULARPATH", "/workspace/snfs-toolchains/sage-pixi/.pixi/envs/default/share/singular/LIB")
from sage.all import PolynomialRing, QQ, ZZ
from sage.env import SAGE_VERSION


def main(screen,out):
    ring=PolynomialRing(QQ,"t")
    rows=[];counts={}
    with screen.open() as source:
        for line in source:
            row=json.loads(line)
            f=ring(row["g"])
            factors=f.factor()
            exact_irred=len(factors)==1 and factors[0][1]==1 and factors[0][0].degree()==f.degree()
            assert str(ZZ(f.discriminant()))==row["discriminant"]
            row["q_irreducible"]=bool(exact_irred)
            row["q_factorization"]=[dict(g=[int(v) for v in factor.list()],multiplicity=int(mult)) for factor,mult in factors]
            for value in row["values"]:
                value["prime_proof_enabled"]=bool(ZZ(value["p"]).is_prime(proof=True))
                value["exact_eligible_prime"]=value["meets_minimum"] and value["prime_proof_enabled"]
            primes=[v for v in row["values"] if v["exact_eligible_prime"]]
            row["first_exact_eligible"]=primes[0]["k"] if primes else None
            row["source_admissible"]=row["source_irreducibility_witness"] is True and any(v["source_prime_screen"] for v in row["values"])
            row["exact_admissible"]=bool(exact_irred and primes)
            rows.append(row)
            if len(rows)%100==0:print(f"exact catalog {len(rows)}",flush=True)
    for shape in sorted({r["shape"] for r in rows}):
        rs=[r for r in rows if r["shape"]==shape]
        counts[shape]=dict(coefficient_patterns=len(rs),q_irreducible=sum(r["q_irreducible"] for r in rs),
                           source_witnessed=sum(r["source_irreducibility_witness"] is True for r in rs),
                           source_witness_disagreements=sum(r["source_irreducibility_witness"] is True and not r["q_irreducible"] for r in rs),
                           exact_admissible=sum(r["exact_admissible"] for r in rs),source_admissible=sum(r["source_admissible"] for r in rs),
                           exact_admissible_without_source_witness=sum(r["exact_admissible"] and r["source_irreducibility_witness"] is not True for r in rs),
                           source_prime_screen_disagreements=sum(v["source_prime_screen"]!=v["exact_eligible_prime"] for r in rs for v in r["values"]))
    result=dict(schema="snfs.complete_support_observations.v1",sage_version=SAGE_VERSION,prime_proof=True,rows=rows,summary=counts)
    with out.open("x") as handle:json.dump(result,handle,indent=2);handle.write("\n")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screen",type=Path,required=True);parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args();main(args.screen,args.out)
