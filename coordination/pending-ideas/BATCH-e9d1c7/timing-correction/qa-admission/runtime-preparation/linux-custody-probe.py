import sys,sysconfig,pathlib,os,hashlib,json,importlib.metadata,platform,shutil
H=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
root=pathlib.Path(sysconfig.get_path('stdlib')).resolve();files=[];aliases=[];links=[]
for b,ds,ns in os.walk(root,followlinks=False):
 ds[:]=sorted(d for d in ds if d not in ('site-packages','dist-packages','__pycache__'))
 for n in sorted(ns):
  p=pathlib.Path(b)/n
  if n.endswith(('.py','.so','.dylib','.zip')):
   if p.is_symlink():aliases.append(str(p))
   if p.stat().st_nlink!=1:links.append(str(p))
   files.append({'path':str(p),'sha256':H(p)})
dists=[]
for name in ['PyYAML','jsonschema','attrs','jsonschema-specifications','referencing','rpds-py','typing-extensions']:
 d=importlib.metadata.distribution(name);paths=sorted(str(pathlib.Path(d.locate_file(f)).resolve()) for f in d.files or [] if not str(f).endswith('.pyc') and pathlib.Path(d.locate_file(f)).is_file())
 for p in paths:
  if pathlib.Path(p).stat().st_nlink!=1:links.append(p)
 dists.append({'name':name,'version':d.version,'files':[{'path':p,'sha256':H(p)} for p in paths]})
exe=pathlib.Path(sys.executable).resolve();tools={}
for n in ['git','ps']:
 p=pathlib.Path(shutil.which(n,path='/usr/bin:/bin')).resolve();tools[n]={'path':str(p),'sha256':H(p),'nlink':p.stat().st_nlink}
print(json.dumps({'python':{'executable':str(exe),'version':sys.version,'sha256':H(exe)},'stdlib':{'root':str(root),'files':files},'distributions':dists,'tools':tools,'stdlib_aliases':aliases,'nonunit_links':links,'platform':platform.platform(),'uid':os.geteuid(),'scope':'Actual Linux container file/version metadata only; no admission or worker execution.'},sort_keys=True))
