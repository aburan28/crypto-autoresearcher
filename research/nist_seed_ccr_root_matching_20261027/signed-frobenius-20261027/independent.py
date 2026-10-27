import json,pathlib,subprocess
from arithmetic import D,CONTROLS
x=json.loads((D/'prior-inputs.json').read_text());src=(D/'eigen.gp').read_text();cases=[]
for i,r in enumerate(CONTROLS+[CONTROLS[-1]]):cases.append([-1,i]+[r[k] for k in ('p','A','b','n','ell')]+[1])
for i,z in enumerate(x['rows']):
 r=z['row']
 for ell in x['levels']:cases.append([i,ell,int(r['p']),-3,int(r['b']),int(r['n']),ell,0])
for i,k,p,A,b,n,ell,ctrl in cases:
 guard=''
 if ctrl:
  ex=(CONTROLS+[CONTROLS[-1]])[k]['expected'];guard=f'if([z[2],z[3],z[4]]!={ex} || ellcard(ellinit([Mod({A},{p}),Mod({b},{p})]))!={n},quit(13));'
 src+=f'{{my(z);iferr(z=one({p},{A},{b},{n},{ell},{ctrl}),ERR,quit(14));{guard}print([{i},{k},z[1],z[2],z[3],z[4],Vec(z[5][,1]),Vec(z[5][,2]),z[6],z[7],z[8]]);}}\n'
src+='quit;\n';(D/'independent-inputs.gp').write_text(src);r=subprocess.run(['/opt/homebrew/bin/gp','-fq',str(D/'independent-inputs.gp')],capture_output=True,text=True,timeout=300);(D/'gp.stdout').write_text(r.stdout);(D/'gp.stderr').write_text(r.stderr);assert r.returncode==0 and not r.stderr.strip(),r.stderr[:1000]
rr=[json.loads(s) for s in r.stdout.splitlines() if s.strip()];assert len(rr)==len(cases);out=[];ctrl=[];names=['scalar','jordan','split','nonsplit']
for row in rr:
 i,k,kind,fo,xo,po,degs,cnts,ev,cost,ss=row;z={'kind':names[kind],'full_order':fo,'x_order':xo,'projective_order':po,'factor_degrees':list(map(list,zip(degs,cnts))),'eigenvalues':ev,'cost':cost,'scalar':ss}
 if i<0:ctrl.append(z)
 else:out.append({'index':i,'ell':k,**z})
for i,c in enumerate(CONTROLS):assert [ctrl[i][k] for k in ('full_order','x_order','projective_order')]==c['expected']
assert ctrl[-1]==ctrl[-2]
(D/'eigen.json').write_text(json.dumps({'status':'PASS','cells':out,'cell_count':len(out),'controls':ctrl},indent=2,sort_keys=True)+'\n');print('eigen cells',len(out))
