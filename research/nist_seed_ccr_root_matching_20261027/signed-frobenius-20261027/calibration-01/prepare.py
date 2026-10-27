"""Freeze existing feature observations and the two declared reference populations."""
import hashlib,itertools,json,pathlib
P=pathlib.Path(__file__).resolve().parent;D=P/'.work';S=pathlib.Path('/Volumes/SSD990/llm/tmp/nist-historical-pointcounter-source-20261027/signed-frobenius-01');manifest=json.loads((S/'MANIFEST.json').read_text());names=['prior-rows.json','all-signatures.json','matrix.json','eigen.json','AUDIT.json']
for n in names:assert hashlib.sha256((S/n).read_bytes()).hexdigest()==manifest[n],n
rows=json.loads((S/'prior-rows.json').read_text());sig=json.loads((S/'all-signatures.json').read_text());cells=json.loads((S/'matrix.json').read_text())['cells'];assert cells==json.loads((S/'eigen.json').read_text())['cells'];groups={}
for i,r in enumerate(rows):groups.setdefault(r['p'],[]).append(i)
strata=[];choices=[];actual=sum(1<<i for i,r in enumerate(rows) if r['label']=='published');fixed=0;endpoints=0
for ids in groups.values():
 count=sum(rows[i]['label']=='published' for i in ids);mask=sum(1<<i for i in ids);strata.append((mask,count));choices.append([sum(1<<i for i in c) for c in itertools.combinations(ids,count)])
 if count==len(ids):fixed|=mask
 last=max(ids,key=lambda i:rows[i]['ordinal']);assert rows[last]['label']=='published';endpoints|=1<<last
labels=sorted(sum(t) for t in itertools.product(*choices));assert len(labels)==4480 and sum(m&endpoints==endpoints for m in labels)==126;assert actual in labels
levels=sorted({c['ell'] for c in cells});assert len(sig)==2551 and len(rows)==21 and len(levels)==61
(D/'meta.txt').write_text(' '.join(map(str,[21,len(sig),len(labels),len(strata),len(levels),actual,fixed,endpoints]))+'\n')
(D/'strata.tsv').write_text(''.join(f'{m}\t{k}\n' for m,k in strata));(D/'labels.tsv').write_text(''.join(f'{m}\t{int(m&endpoints==endpoints)}\n' for m in labels));(D/'signatures.tsv').write_text(''.join(f"{s['id']}\t{s['true']}\t{s['false']}\t{s['unknown']}\n" for s in sig));(D/'caps.tsv').write_text(''.join(f"{c['ell']}\t{c['index']}\t{c['cost'][1]}\t{min(d for d,n in c['factor_degrees'])}\n" for c in sorted(cells,key=lambda c:(c['ell'],c['index']))))
source={'schema':'nist-classifier-capacity-inputs/v1','parent_archive_sha256':'e8c128fc7f78497775b83f2e8e49cbe6b92da9a12b7c6993ef293425619bd388','source_files':{n:{'path':str(S/n),'sha256':manifest[n]} for n in names},'input_files':{n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ['meta.txt','strata.tsv','labels.tsv','signatures.tsv','caps.tsv']},'rows':rows,'strata':[{'mask':m,'published_count':k} for m,k in strata],'fixed_singleton_publications_mask':fixed,'endpoints_mask':endpoints,'actual_mask':actual,'label_assignments':4480,'endpoint_conditioned_assignments':126,'interpretation':'Exact descriptive reference populations; no new curves, historical decisions, held-out data or historical-choice probability.'};(P/'INPUTS.json').write_text(json.dumps(source,indent=2,sort_keys=True)+'\n');print('Frozen input population sizes',len(labels),sum(m&endpoints==endpoints for m in labels))
