#!/usr/bin/env python3
"""Bind authentic period NTL payloads and derive a narrow default-call count."""
import base64
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OBJECTS=[
 ("march_archive","/private/tmp/nist-ntl-march1997.tar.Z","ntl.tar.Z","72145a0816ea3b2686e1b86fef690ec179f131015b8a2819a930083c364b9b53"),
 ("august_archive","/private/tmp/nist-ntl-1.5-aug1997.tar.Z","ntl-1.5.tar.Z","c2d80c5293c824b16f89ac7e5e0aeb29e3996f8560b877c44858f41c43717e1c"),
 ("may_homepage","/private/tmp/nist-ntl-index-may1997.html","index.html",None),
 ("march_tour","/private/tmp/nist-ntl-tour-march1997.html","tour.html",None),
]

def sha(data):return hashlib.sha256(data).hexdigest()
def extract(path,name):return subprocess.check_output(["tar","-xOf",str(path),name]).decode("latin1")
def normalized(s):return re.sub(r"\s+","",re.sub(r"/\*.*?\*/|//[^\n]*","",s,flags=re.S))
def span(s,start,end):return s[s.index(start):s.index(end,s.index(start))]

def main():
    out=HERE/"analysis.json";assert not out.exists()
    cdx_path=HERE/"cdx.json"
    assert sha(cdx_path.read_bytes())=="a06e06adadadf9769b819a0287c8e4f5fd32674455f1be23483646902d9fba7d"
    cdx=json.loads(cdx_path.read_text())[1:]
    objects=[];functions={}
    for label,filename,suffix,expected in OBJECTS:
        path=Path(filename);payload=path.read_bytes()
        entry=next(r for r in cdx if r[2].endswith('/'+suffix))
        archive_sha1=base64.b32encode(hashlib.sha1(payload).digest()).decode().rstrip('=')
        assert archive_sha1==entry[5]
        if expected:assert sha(payload)==expected
        item={"label":label,"local_path":str(path),"bytes":len(payload),"sha256":sha(payload),"cdx_sha1_base32":archive_sha1,"capture_timestamp":entry[1],"original_url":entry[2],"archive_url":"https://web.archive.org/web/"+entry[1]+"id_/"+entry[2],"cdx_payload_matches":True}
        if label.endswith("archive"):
            zz,header,lip=(extract(path,x) for x in ("ZZ.c","ZZ.h","lip.c"))
            prob=span(zz,"long ProbPrime(const ZZ& n, long NumTrials)","void RandomPrime")
            sqrt=span(zz,"void SqrRootMod(ZZ& x, const ZZ& aa, const ZZ& nn)","long CRT")
            randlen=span(zz,"long RandomLen(long l)","long RandomPrime(long")
            randomb=span(lip,"void zrandomb(","void zrandoml(")
            assert "RandomLen(ZZ_NBITS)" in prob and "RandomBnd(W, n)" in prob
            assert "for(i=0;i<NumTrials;i++)" in normalized(prob)
            assert re.search(r"ProbPrime\(const ZZ& n, long NumTrials\s*=\s*10\)",header)
            assert "returnRandomBnd(1L<<(l-1))+(1L<<(l-1));" in normalized(randlen)
            assert "returnzrandom(n);" in normalized(header)
            assert "zrandomb(n.rep,&x.rep);" in normalized(header)
            assert "i=bnd[0]+1" in normalized(randomb)
            assert "RandomBnd(t, n)" in sqrt and "that a is a square mod n" in header
            item["source_files_sha256"]={"ZZ.c":sha(zz.encode("latin1")),"ZZ.h":sha(header.encode("latin1")),"lip.c":sha(lip.encode("latin1"))}
            item["function_fingerprints"]={"ProbPrime":sha(normalized(prob).encode()),"SqrRootMod":sha(normalized(sqrt).encode())}
            item["inventory"]=subprocess.check_output(["tar","-tf",str(path)],text=True).splitlines()
            item["curve_filename_hits"]=[x for x in item["inventory"] if re.search(r"elliptic|schoof|curve",x,re.I)]
            functions[label]=item["function_fingerprints"]
        if label=="may_homepage":assert "NEW - NTL 1.5" in payload.decode("latin1")
        objects.append(item)
    traits_path=ROOT/"research/nist_seed_skipped_curves_20261016/traits.json"
    assert sha(traits_path.read_bytes())=="a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67"
    published=json.loads(traits_path.read_text())["published_controls"]
    names=["prime192v1","prime239v1","prime239v2","prime239v3","prime192v2","prime192v3"]
    rows=[]
    for name in names:
        row=published[name]
        for argument in ("p","n"):
            value=int(row[argument+"_hex"],16)
            words=(value.bit_length()+25)//26
            rows.append({"name":name,"curve_uid":row["identity"]["curve_uid"],"argument":argument,"argument_value":str(value),"limb_bits":26,"input_limbs":words,"draws_per_RandomBnd":words+1,"default_trials":10,"minimum_rng_advances":1+10*(words+1),"observed_prefix":7})
    record={"method":"retrospective source audit; no NTL executable run","recorded_utc":datetime.now(timezone.utc).isoformat(),"objects":objects,"cdx_sha256":sha(cdx_path.read_bytes()),"input_sha256":sha(traits_path.read_bytes()),"scope_sha256":sha((HERE/"SCOPE.md").read_bytes()),"code_sha256":sha(Path(__file__).read_bytes()),"head":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),"dirty":subprocess.check_output(["git","status","--porcelain"],text=True),"function_bodies_equal":functions["march_archive"]==functions["august_archive"],"rows":rows}
    out.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"authenticated_payloads":len(objects),"same_function_bodies":record["function_bodies_equal"],"rows":len(rows),"minimum_advances":sorted({r["minimum_rng_advances"] for r in rows})}))

if __name__=="__main__":main()
