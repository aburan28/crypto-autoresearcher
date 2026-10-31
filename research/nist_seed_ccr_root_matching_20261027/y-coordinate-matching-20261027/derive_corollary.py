"""Bind a symbolic consequence of the previously sealed derivative guards.

No new curve operation or point-counter call. This derived interpretation
does not alter the prospectively frozen 415-call matching design.
"""
import hashlib,json,shutil,time
from pathlib import Path
P=Path(__file__).resolve().parent;H=P.parent
E=H/'modular-archive-relocation/evidence';C=E/'canonical-equations-01'
ROOT=Path('/Volumes/SSD990/llm/tmp/nist-ecpp-cohort-admission-20261026/repository')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((E/'MANIFEST.json').read_text())
names=['AUDIT.json','FIBER-AUDIT.json','TABLES.json','cohort-inputs.json']
for n in names:assert sha(C/n)==manifest['canonical-equations-01/'+n]
a=json.loads((C/'AUDIT.json').read_text());f=json.loads((C/'FIBER-AUDIT.json').read_text())
assert a['status']==f['status']=='PASS'
assert a['cohort_nonconstant_gcd_X']==a['cohort_nonconstant_gcd_J']==a['cohort_zero_parameter_cases']==0
cells=[r for r in f['cells'] if r['type']==1 and r['index']<21]
assert len(cells)==966 and sum(len(r['roots']) for r in cells)==886
rows=json.loads((P/'rows.json').read_text())
assert len(rows)==21 and all(int(r['b'])%int(r['p']) for r in rows)
assert all(r['j'] not in [0,1728%r['p']] and r['p']>293*12 for r in cells)
ante=P/'antecedent-proof';ante.mkdir()
for n in names:shutil.copyfile(C/n,ante/n)
shutil.copyfile(E/'MANIFEST.json',ante/'parent-MANIFEST.json')
record={'status':'DERIVED_CONDITIONAL_COROLLARY','recorded_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'relation_to_frozen_run':'Additive symbolic interpretation after matcher launch; no new point-counter/curve operation, no changed kernel input, no changed415-call design.','canonical_parameters':886,'canonical_cells':966,'levels':46,'curves':21,'antecedent_manifest_sha256':sha(E/'MANIFEST.json'),'antecedent_hashes':{n:sha(C/n) for n in names},'parent_archive':'research/nist_seed_modular_coordinate_guards_20261027/evidence.tar.zst','parent_archive_sha256':sha(ROOT/'research/nist_seed_modular_coordinate_guards_20261027/evidence.tar.zst'),'source_url':'https://www.lix.polytechnique.fr/~morain/AtkinEmails/19930303.txt','source_sha256':sha(H/'source-recovery-01/author-and-release-links/payload-05.raw'),'source_formula':'S1=(ell*gcd(12,ell-1)/2)*(E6/E4)*(j*Phi_j)/(F*Phi_F).','premises':['Cohort E4=1 and E6=-b/2 are nonzero; j and the parameter F are nonzero.','The existing exact Bezout guards exclude Phi_F=0 and Phi_j=0 on every algebraic parameter root, hence on every rational parameter.','The normalizing integer ell*gcd(12,ell-1)/2 is nonzero modulo each large cohort field.','When the canonical formula supplies a valid cyclic half-kernel, S1 is its first root sum.'],'conclusion':'Every valid cyclic half-kernel reached through these886 canonical parameters has nonzeroS1 and therefore unique signed complete-y-function matching. These886 matches are proved conditionally via source formula/previous guards, not newly executed here.','limits':['Modern coefficient tables; original period tables/caller unestablished.','Full prior Bezout/fiber replay is in the parent archive, not relabeled a new experiment.','Does not cover a fingerprint evaluated at one point, an improper factor, or arbitrary historical implementation faults.']}
(P/'SOURCE-COROLLARY.json').write_text(json.dumps(record,indent=2)+'\n');print('derived canonical nonzero-S1 scope',886,flush=True)
