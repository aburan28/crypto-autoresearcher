"""Retrieve public period primary sources; retain failures; exclude source bytes from Git."""
import pathlib,subprocess,datetime,json,hashlib,concurrent.futures
P=pathlib.Path(__file__).resolve().parent;W=P/'.work';UA='Mozilla/5.0'
urls=[('official-pdf','https://publikationen.sulb.uni-saarland.de/bitstream/20.500.11880/25777/1/VolkerMueller_ProfDrJohannesBuchmann.pdf'),('official-download-query','https://publikationen.sulb.uni-saarland.de/bitstream/20.500.11880/25777/1/VolkerMueller_ProfDrJohannesBuchmann.pdf?sequence=1&isAllowed=y'),('author-ftp','ftp://ftp.informatik.tu-darmstadt.de/pub/TI/reports/vmueller.diss.ps.gz'),('author-https','https://ftp.informatik.tu-darmstadt.de/pub/TI/reports/vmueller.diss.ps.gz')]
def get(t):
 name,url=t;dst=W/(name+'.bin');cmd=['/usr/bin/curl','--location','--fail','--connect-timeout','10','--max-time','30','--user-agent',UA,'--output',str(dst),'--write-out','%{http_code}\n%{url_effective}\n',url];start=datetime.datetime.now(datetime.timezone.utc).isoformat();r=subprocess.run(cmd,capture_output=True);(W/(name+'.stdout')).write_bytes(r.stdout);(W/(name+'.stderr')).write_bytes(r.stderr);row={'name':name,'url':url,'started_at':start,'returncode':r.returncode,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stdout':r.stdout.decode(errors='replace'),'stderr':r.stderr.decode(errors='replace'),'url_provenance':'institutional catalog link' if name.startswith('official') else 'historical author FTP URL printed in published bibliography; https transport variant explicit','command':cmd}
 if dst.exists():d=dst.read_bytes();row.update(bytes=len(d),sha256=hashlib.sha256(d).hexdigest(),header_hex=d[:12].hex())
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(get,urls))
(P/'RETRIEVAL.json').write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n')
for r in rows:print(json.dumps({k:v for k,v in r.items() if k in ['name','returncode','stdout','bytes','sha256','header_hex']}))
