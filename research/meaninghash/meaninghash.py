"""Deterministic rule-aware SimHash baseline; NOT a general semantic model."""
import hashlib, json, re, sqlite3, argparse
from collections import Counter

STOP={'the','a','an','is','are','was','were','by','using','instead','of','to','that','this','it','for','in','on','and','or','than','does','do'}
ALIASES={'graphics processing unit':'gpu','central processing unit':'cpu','accelerated':'faster','accelerates':'faster','outperforms':'faster','quicker':'faster','slower':'slower','not':'not','never':'not','cannot':'not','can’t':'not','doesn’t':'not','isn’t':'not'}
PATTERNS=[(re.compile(r'^(\w+) (?:is |runs |performs )?(faster|slower) than (\w+)$'), 'compare'),(re.compile(r'^(\w+) (?:does |is )?not (?:use|support) (\w+)$'),'negative'),(re.compile(r'^(\w+) (?:uses|supports) (\w+)$'),'positive')]

def normalize(s):
 s=s.lower().replace('’',"'")
 for a,b in sorted(ALIASES.items(),key=lambda p:-len(p[0])): s=re.sub(r'\b'+re.escape(a)+r'\b',b,s)
 return ' '.join(re.findall(r"[a-z0-9_]+",s))

def proposition(s):
 n=normalize(s)
 for pat,kind in PATTERNS:
  m=pat.fullmatch(n)
  if m:
   if kind=='compare':return ('compare',m.group(1),m.group(2),m.group(3))
   a,b=m.groups();return (kind,a,b)
 return None

def features(s):
 n=normalize(s); toks=[w for w in n.split() if w not in STOP]
 out=Counter('word:'+w for w in toks)
 out.update('pair:'+a+':'+b for a,b in zip(toks,toks[1:]))
 p=proposition(s)
 if p:
  out['role:'+':'.join(p)]+=5;out['predicate:'+p[0]]+=2
  for i,x in enumerate(p[1:]):out[f'arg{i}:{x}']+=2
 return out

def sketch(s,bits=256):
 if bits%8:raise ValueError('bits must be divisible by 8')
 accum=[0]*bits
 for feat,weight in features(s).items():
  for j in range((bits+255)//256):
   digest=hashlib.sha256((str(j)+'|'+feat).encode()).digest()
   for k in range(min(256,bits-j*256)):
    accum[j*256+k]+=weight if (digest[k//8]>>(k%8))&1 else -weight
 return bytes(sum((1<<k) for k in range(8) if accum[i*8+k]>=0) for i in range(bits//8))

def identity(s):
 p=proposition(s)
 if p is None:return None
 return hashlib.sha256(json.dumps(p,separators=(',',':')).encode()).hexdigest()

def distance(a,b):
 if len(a)!=len(b):raise ValueError('hash lengths differ')
 return sum((x^y).bit_count() for x,y in zip(a,b))

class Index:
 def __init__(self,path):
  self.db=sqlite3.connect(path)
  self.db.execute('CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY,text TEXT NOT NULL,identity TEXT,code BLOB NOT NULL)')
  self.db.execute('CREATE INDEX IF NOT EXISTS ix_identity ON items(identity)')
 def add(self,text):
  code=sketch(text);ident=identity(text)
  cur=self.db.execute('INSERT INTO items(text,identity,code) VALUES(?,?,?)',(text,ident,code));self.db.commit();return cur.lastrowid
 def query(self,text,k=5):
  code=sketch(text);ident=identity(text)
  rows=self.db.execute('SELECT id,text,identity,code FROM items')
  result=[{'id':i,'text':t,'distance':distance(code,c),'canonical_match':bool(ident and ident==v)} for i,t,v,c in rows]
  return sorted(result,key=lambda x:(not x['canonical_match'],x['distance']))[:k]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--db',default='meaninghash.sqlite3');sp=ap.add_subparsers(dest='cmd',required=True)
 for cmd in ('hash','add','query'):sp.add_parser(cmd).add_argument('text')
 a=ap.parse_args()
 if a.cmd=='hash':print(json.dumps({'text':a.text,'hash256':sketch(a.text).hex(),'canonical_sha256':identity(a.text)}))
 elif a.cmd=='add':print(Index(a.db).add(a.text))
 else:print(json.dumps(Index(a.db).query(a.text),indent=2))
if __name__=='__main__':main()
