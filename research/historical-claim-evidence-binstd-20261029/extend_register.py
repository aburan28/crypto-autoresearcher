#!/usr/bin/env python3
"""Add two source-bound BINSTD rows; never run Lean or promote research status."""
import argparse
import json
from pathlib import Path
from tools.claim_evidence_matrix import digest, git

ARCHIVE = 'e3fe39bed74e607855a3f6fa238ab5144b2bf232'
NATIVE = '8ef2a271eb45801d12b431e85165b378d3f5176b'
SEED = 'research/historical-claim-evidence-20261029/matrix.json'
PACKET = 'research/binstd_formal_review_type_supplement_20261028/'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    matrix = json.loads(git(args.repo, 'show', f'{ARCHIVE}:{SEED}'))
    original_claims = json.loads(json.dumps(matrix['claims']))
    content = {}

    def bind(sid, path, commit=ARCHIVE):
        data = git(args.repo, 'show', f'{commit}:{path}')
        oid = git(args.repo, 'rev-parse', f'{commit}:{path}').decode().strip()
        matrix['sources'].append(dict(id=sid, kind='git', repo='auto', commit=commit,
                                     path=path, blob_oid=oid, sha256=digest(data)))
        content[sid] = data
        return sid

    shared = {}
    for role, name in [('toolchain','lean-toolchain'), ('dependencies','lake-manifest.json')]:
        shared[role] = [bind('binstd-native-'+role, 'formal/'+name, NATIVE)]
    shared['dependencies'] += [bind('binstd-native-lakefile','formal/lakefile.toml',NATIVE),
                               bind('binstd-factor-definitions','formal/CryptoResearch/Binstd/Factorization.lean',NATIVE)]
    shared['fidelity_review'] = [
        bind('binstd-j1-source-review','research/binstd_formal_review_round2_20261027/reports/TASK-20261027-b17d01/report.md'),
        bind('binstd-j2-blind-math','research/binstd_formal_review_round2_20261027/reports/TASK-20261027-b17d02/report.md'),
        bind('binstd-j3-types-review',PACKET+'reports/TASK-20261028-68ff01/report.md')]
    shared['controls'] = [bind('binstd-kernel-controls',PACKET+'machine/repair-kernel-controls.json'),
                          bind('binstd-blind-controls','research/binstd_formal_review_round2_20261027/reports/TASK-20261027-b17d02/results.json')]
    shared['context'] = [bind('binstd-supplement-scope',PACKET+'report.md'),
                         bind('binstd-supplement-bindings',PACKET+'inputs.json')]
    for slug, filename, theorem, statement in [
        ('degree-eight-irreducibility','Irreducibility.lean','factor8_irreducible_pair',
         'The fixed polynomials factor8a and factor8b over ZMod 2, with binary masks 313 and 471, are irreducible.'),
        ('canonical-frobenius','CanonicalFrobenius.lean','canonicalFrobenius_order_and_minpoly',
         'Frobenius on the canonical GaloisField 2 17 has order 17 and minimal polynomial factor1 * factor8a * factor8b.')]:
        sid = bind('binstd-'+slug+'-source','formal/CryptoResearch/Binstd/'+filename,NATIVE)
        target = 'binstd-x17-degree-eight-irreducible' if slug.startswith('degree') else 'binstd-canonical-frobenius-minpoly'
        rid = bind('binstd-'+slug+'-receipt',PACKET+'machine/'+target+'.json')
        aid = bind('binstd-'+slug+'-types',PACKET+'machine/'+target+'-audit.txt')
        receipt = json.loads(content[rid])
        if receipt['provenance']['theorem_sha256'] != digest(content[sid]):
            raise ValueError('native theorem bytes do not match selected source')
        if receipt['verification']['theorem_name'] != 'CryptoResearch.Binstd.'+theorem:
            raise ValueError('native theorem identity mismatch')
        lines = content[sid].decode().splitlines(keepends=True)
        start, = [i for i,line in enumerate(lines) if line.startswith('theorem '+theorem+' :')]
        end = next(i for i in range(start,len(lines)) if ':=' in lines[i])
        text = ''.join(lines[start:end+1])
        evidence = {k:list(v) for k,v in shared.items()}
        evidence.update(formal_source=[sid],native_build=[rid],axiom_audit=[rid,aid],elaborated_types=[aid])
        matrix['claims'].append(dict(id='binstd/'+slug,classification='mathematical',source_id=sid,
            excerpt=dict(start_line=start+1,end_line=end+1,text=text,sha256=digest(text.encode())),
            statement=statement,assumptions=[
                'Fixed closed declarations with their pinned definitions; no historical runner representation is assumed.',
                'Ordinary pinned Lean/Lake, dependency and binary trust; standard propext, Classical.choice and Quot.sound axioms.',
                'Named supplemental targets passed; supplemental overall run failed on another target and its original control job failed during setup.'],
            evidence=evidence,open_obligations=[
                'Prove bit encoding, quotient-field and arithmetic refinement for the actual historical implementation.',
                'Prove canonical-field/Frobenius conjugacy, matrix evaluation and invariant-subspace/constructor bridges.',
                'Bind original historical execution, selected inputs, complete outputs and timing separately; no yield or speed claim follows.',
                'This register adds custody links to existing reviews, not a new independent proof or scientific status decision.']))
    if matrix['claims'][:len(original_claims)] != original_claims:
        raise ValueError('existing claim changed')
    matrix['scope']['omissions'][0] = 'Eight selected rows only; the full individual-claim denominator remains unknown.'
    with args.output.open('x') as f:
        f.write(json.dumps(matrix,indent=2)+'\n')


if __name__ == '__main__':
    main()
