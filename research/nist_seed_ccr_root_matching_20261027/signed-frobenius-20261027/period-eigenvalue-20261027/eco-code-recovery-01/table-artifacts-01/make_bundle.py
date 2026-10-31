"""Seal source collation metadata; retain source bodies privately."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

P=Path(__file__).resolve().parent
FILES=['PLAN.md','fetch.py','inspect_artifacts.py','record_sources.py',
       'period-sites-ACCESS.json','named-table-indexes-ACCESS.json','history-snapshot-ACCESS.json',
       'OLD-IO-SOURCES.json','LATER-READER-SOURCE.json','SOURCE-REVIEW.json',
       'HISTORY-REVIEW.json','SEARCH-NOTES.json','COLLATION.json','cohort-gap-crosswalk.csv',
       'collation-check.stdout','collation-check.stderr']


def binding(b):
    return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}


manifest={n:binding((P/n).read_bytes()) for n in FILES}
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w') as tar:
    for n in FILES:
        b=(P/n).read_bytes();m=tarfile.TarInfo('evidence/'+n)
        m.size,m.mode,m.mtime=len(b),0o644,0
        tar.addfile(m,io.BytesIO(b))
raw=gzip.compress(buf.getvalue(),mtime=0)
assert len(raw)<65536
q=P/'public-evidence.tar.gz';assert not q.exists();q.write_bytes(raw)
r={'kind':'source collation metadata; not a scientific experiment export',
   'files':manifest,'sealed_files':len(FILES),
   'archive':{'path':q.name,**binding(raw)},'external_components':{},
   'new_scientific_trials':0,'historical_criterion_identified':False,
   'excluded':'All original package, code, HTML, PDF/PS, page-image and OCR bodies remain private.'}
q=P/'BUNDLE.json';assert not q.exists();q.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in r.items() if k!='files'}))
