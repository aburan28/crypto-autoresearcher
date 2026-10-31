"""Public institutional/author/archive GETs, with all outcomes retained."""
import pathlib,subprocess,datetime,json,hashlib,concurrent.futures,urllib.parse
P=pathlib.Path(__file__).resolve().parent;W=P/'.work'
def cdx(url):return 'https://web.archive.org/cdx/search/cdx?'+urllib.parse.urlencode({'url':url,'output':'json','filter':'statuscode:200','collapse':'urlkey','fl':'timestamp,original,mimetype,statuscode,digest','limit':'100'})
urls=[('archive-reports',cdx('ftp.informatik.tu-darmstadt.de/pub/TI/reports/*')),('archive-ecc',cdx('www.informatik.tu-darmstadt.de/TI/Forschung/ECC/*')),('saarland-atkin','https://publikationen.sulb.uni-saarland.de/simple-search?query=Atkin'),('shoup-papers','https://shoup.net/papers/'),('shoup-home','https://shoup.net/'),('orbilu-maurer','https://orbilu.uni.lu/browse?type=author&value=Maurer%2C+Markus')]
if (P/'GET-RECEIPTS.json').exists():raise SystemExit('Refuse to overwrite retained retrieval receipt; use a new attempt directory.')
def one(t):
 name,url=t;dst=W/(name+'.bin');cmd=['/usr/bin/curl','--location','--fail','--connect-timeout','8','--max-time','25','--output',str(dst),'--write-out','%{http_code}\n%{url_effective}\n',url];stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();r=subprocess.run(cmd,capture_output=True);(W/(name+'.stderr')).write_bytes(r.stderr);(W/(name+'.stdout')).write_bytes(r.stdout);row={'name':name,'url':url,'started_at':stamp,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':r.returncode,'stdout':r.stdout.decode(errors='replace'),'stderr':r.stderr.decode(errors='replace')}
 if dst.exists():b=dst.read_bytes();row.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),header_hex=b[:12].hex())
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(one,urls))
(P/'GET-RECEIPTS.json').write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n')
for r in rows:print(json.dumps({k:r[k] for k in r if k in ['name','returncode','stdout','bytes','sha256']}))
