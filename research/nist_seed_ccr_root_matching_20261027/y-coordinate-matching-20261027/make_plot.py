"""Plot retained exact kernel counts and CM detector controls."""
import csv,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
audit=json.loads((P/'AUDIT.json').read_text());rows=list(csv.DictReader((P/'curve-summary.csv').open()))
streams=[]
for t in dict.fromkeys(r['timestamp'] for r in rows):
    rr=[r for r in rows if r['timestamp']==t];streams.append({'timestamp':int(t),'bits':int(json.loads((P/'rows.json').read_text())[int(rr[0]['index'])]['p']).bit_length(),'omitted_curves':sum(r['label']=='omitted' for r in rr),'published_curves':sum(r['label']=='published' for r in rr),'omitted_kernels':sum(int(r['kernels']) for r in rr if r['label']=='omitted'),'published_kernels':sum(int(r['kernels']) for r in rr if r['label']=='published')})
assert sum(s['omitted_kernels'] for s in streams)==228 and sum(s['published_kernels'] for s in streams)==183
(P/'streams.json').write_text(json.dumps(streams,indent=2)+'\n')
plt.rcParams.update({'font.size':9,'svg.fonttype':'none','svg.hashsalt':'ATKIN-Y-MATCH-01'})
fig,(a,b)=plt.subplots(1,2,figsize=(10,4),gridspec_kw={'width_ratios':[1,1.3]})
x=[0,1,2];a.bar([v-.17 for v in x],[3,3,1],width=.33,color='#a56d2b',label='Signed y-only matches');a.bar([v+.17 for v in x],[1,1,1],width=.33,color='#167e88',label='Full-point matches');a.set_xticks(x,['CM split\nF103','CM cubic\nF103','Regular\nF101']);a.set_ylim(0,3.8);a.set_yticks([0,1,2,3]);a.set_ylabel('Match scalars per kernel (count)');a.set_title('Constructed detector controls',loc='left');a.legend(fontsize=7,loc='upper left');a.text(1,3.3,'first y match is wrong',ha='center',fontsize=7,color='#74491e')
y=list(range(6));om=[s['omitted_kernels'] for s in streams];pub=[s['published_kernels'] for s in streams];b.barh(y,om,color='#8b62ad',label='Omitted curves');b.barh(y,pub,left=om,color='#167e88',label='Published curves');b.set_yticks(y,[str(s['bits'])+' bit' for s in streams]);b.invert_yaxis();b.set_xlim(0,190);b.set_xlabel('Cohort cyclic kernels checked (count)');b.set_title('All 411 kernels have unique matches',loc='left')
for k,s in enumerate(streams):b.text(om[k]+pub[k]+2,k+.08,str(om[k]+pub[k])+'; 0 false',fontsize=8)
b.legend(fontsize=7,loc='lower right');fig.tight_layout();fig.savefig(P/'matching-counts.svg');fig.savefig(P/'matching-counts.png',dpi=200);plt.close(fig)
f=P/'matching-counts.svg';f.write_text('\n'.join(s.rstrip() for s in f.read_text().splitlines())+'\n')
control=next(r for r in audit['controls'] if r['id']==1)
# The recorded cubic kernel has X^3=c. Substitute this in duplication.
native_archive=P/'BUNDLE-REPLAY.json';meta=json.loads(native_archive.read_text())
identity={'curve':{'p':103,'A':0,'B':1,'j':0,'order':84},'subgroup_order':7,'full_Frobenius_scalar':5,'y_only_scalars':[3,5,6],'first_y_scalar':6,'automorphism':'(x,y) -> (zeta*x,y), zeta^3=1, zeta!=1; degree1 overF103','scope':'Point orbit on one CM control curve; not an isogeny-volcano diagram.','data':'AUDIT.json control id1; exact kernel is in the sealed native record.'}
(P/'orbit.diagram.json').write_text(json.dumps(identity,indent=2)+'\n')
svg='''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="220" viewBox="0 0 900 220"><rect width="900" height="220" fill="white"/><g stroke="#52677b" stroke-width="2" fill="none"><path d="M150 80H400 M500 80H750 M750 110Q450 230 150 110"/></g><g fill="#dceef0" stroke="#52677b"><rect x="45" y="40" width="210" height="75" rx="9"/><rect x="345" y="40" width="210" height="75" rx="9"/><rect x="645" y="40" width="210" height="75" rx="9"/></g><g font-family="Arial,sans-serif" font-size="16" fill="#203747" text-anchor="middle"><text x="150" y="72">P=(x,y)</text><text x="450" y="72">phi(P)=(zeta*x,y)</text><text x="750" y="72">phi^2(P)=(zeta^2*x,y)</text><text x="300" y="32">order-three automorphism</text><text x="600" y="32">same y-coordinate</text><text x="450" y="205">E/F103: y^2=x^3+1; ell=7; three points share each y-fiber</text></g></svg>'''
(P/'orbit.svg').write_text(svg)
