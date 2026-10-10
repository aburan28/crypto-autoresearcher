"""Conservative proof-carrying fingerprints; not unrestricted semantic equivalence."""
import hashlib, json, sqlite3
from meaninghash import sketch, distance, proposition
VERSION='meaninghash-v2-rule1'
def canonical(text):
 p=proposition(text)
 return {'version':VERSION,'proposition':list(p)} if p is not None else None
def serialize(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(data):return hashlib.sha256(data).hexdigest()
def commit(text):
 c=canonical(text)
 return digest(serialize(c)) if c is not None else None
def witness(a,b):
 ca,cb=canonical(a),canonical(b)
 if ca is None or cb is None or ca!=cb:return None
 return {'version':VERSION,'left':digest(serialize(ca)),'right':digest(serialize(cb)),'canonical':ca,'rule':'identical-canonical-proposition'}
def verify(a,b,proof):
 if not isinstance(proof,dict) or proof.get('version')!=VERSION or proof.get('rule')!='identical-canonical-proposition':return 'reject'
 ca,cb=canonical(a),canonical(b)
 if ca is None or cb is None:return 'unknown'
 if proof.get('canonical')!=ca or ca!=cb:return 'reject'
 if proof.get('left')!=digest(serialize(ca)) or proof.get('right')!=digest(serialize(cb)):return 'reject'
 return 'accept'
def merkle(texts):
 leaves=[bytes.fromhex(commit(t)) if commit(t) else hashlib.sha256(b'raw\0'+t.encode()).digest() for t in texts]
 level=[hashlib.sha256(b'leaf\0'+x).digest() for x in leaves]
 if not level:return digest(b'empty\0')
 while len(level)>1:
  if len(level)%2:level.append(level[-1])
  level=[hashlib.sha256(b'node\0'+level[i]+level[i+1]).digest() for i in range(0,len(level),2)]
 return level[0].hex()
class IndexedStore:
 def __init__(self,path=':memory:'):
  self.db=sqlite3.connect(path)
  self.db.executescript('CREATE TABLE IF NOT EXISTS docs(id INTEGER PRIMARY KEY,text TEXT NOT NULL,code BLOB NOT NULL,canonical TEXT);CREATE INDEX IF NOT EXISTS ix_docs_canonical ON docs(canonical);CREATE TABLE IF NOT EXISTS bands(band INTEGER NOT NULL,value BLOB NOT NULL,doc_id INTEGER NOT NULL,PRIMARY KEY(band,value,doc_id));')
 def add(self,text):
  code=sketch(text);c=commit(text)
  with self.db:
   i=self.db.execute('INSERT INTO docs(text,code,canonical) VALUES(?,?,?)',(text,code,c)).lastrowid
   self.db.executemany('INSERT INTO bands VALUES(?,?,?)',[(j,code[j*4:j*4+4],i) for j in range(8)])
  return i
 def query(self,text,k=5,full_scan=False):
  code=sketch(text);c=commit(text);ids=set()
  for j in range(8):ids.update(i for (i,) in self.db.execute('SELECT doc_id FROM bands WHERE band=? AND value=?',(j,code[j*4:j*4+4])))
  if c:ids.update(i for (i,) in self.db.execute('SELECT id FROM docs WHERE canonical=?',(c,)))
  if full_scan:ids.update(i for (i,) in self.db.execute('SELECT id FROM docs'))
  result=[]
  for i in ids:
   row=self.db.execute('SELECT text,code,canonical FROM docs WHERE id=?',(i,)).fetchone()
   result.append({'id':i,'text':row[0],'hamming':distance(code,row[1]),'canonical_match':bool(c and c==row[2])})
  return sorted(result,key=lambda r:(not r['canonical_match'],r['hamming'],r['id']))[:k]
