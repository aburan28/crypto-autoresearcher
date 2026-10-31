"""Read-only public-paper retrieval. Paper bytes stay in the ignored private cache."""
import concurrent.futures,datetime,hashlib,json,pathlib,urllib.request
P=pathlib.Path(__file__).resolve().parent;D=P/'.work'/'private-sources';D.mkdir(exist_ok=True)
urls=[('isog-cycles','https://www.lix.polytechnique.fr/~morain/Articles/isog-cycles.pdf'),('dewaghe-citeseer','https://citeseerx.ist.psu.edu/document?doi=27248fbdf3f5828305c3f0fcd1b02af5cf1e8e97&repid=rep1&type=pdf'),('dewaghe-journal-copy','https://electronicsandbooks.com/edt/manual/Magazine/M/Mathematics%20of%20Computation/1960-2002/pdf/1998_v067_n223/2585182.pdf')]
def one(pair):
 name,url=pair;r={'name':name,'url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=25) as f:data=f.read(20*1024*1024+1);r.update(status=f.status,content_type=f.headers.get('Content-Type'))
  r.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),pdf_header=data.startswith(b'%PDF-'));assert len(data)<=20*1024*1024
  (D/(name+('.pdf' if data.startswith(b'%PDF-') else '.response'))).write_bytes(data)
 except Exception as e:r.update(error=type(e).__name__+': '+str(e))
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:r=list(ex.map(one,urls))
(P/'SOURCE-RETRIEVAL.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r,indent=2))
