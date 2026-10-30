#!/usr/bin/env python3
"""Rebuild the initial partial register from immutable local Git objects only."""
import argparse
import json
from pathlib import Path

from tools.claim_evidence_matrix import digest, git

AUTO = '1896454c43bede18d19fb51362d748ed3246227e'
FORMAL = '0b353c9bf78e9340c3c100b71175127bb7d91d44'
COVER = 'ed98ccabd60f6ba149a4c218d8241fe0b7132403'
ARCHIVE = '615b6d34e3636bf3745ac5c74d5de408f1934233'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('auto', 'cryptanalysis', 'crypto'):
        parser.add_argument('--' + name, required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    repos = vars(args)
    sources, content = [], {}

    def bind(sid, repo, commit, path):
        data = git(repos[repo], 'show', f'{commit}:{path}')
        oid = git(repos[repo], 'rev-parse', f'{commit}:{path}').decode().strip()
        sources.append(dict(id=sid, kind='git', repo=repo, commit=commit,
                            path=path, blob_oid=oid, sha256=digest(data)))
        content[sid] = data.decode('utf-8')
        return sid

    def excerpt(sid, first, last=None):
        lines = content[sid].splitlines(keepends=True)
        matches = [i for i, line in enumerate(lines) if first in line]
        if len(matches) != 1:
            raise ValueError(f'ambiguous excerpt: {sid} {first}')
        start = end = matches[0]
        if last:
            end = next(i for i in range(start, len(lines)) if last in lines[i])
        text = ''.join(lines[start:end+1])
        return dict(start_line=start+1, end_line=end+1, text=text,
                    sha256=digest(text.encode()))

    bind('known-label-source', 'cryptanalysis', FORMAL,
         'docs/known-label-next-leads-20261028/Algebra.lean')
    project = 'experiments/hecke-432-formal-ci-20261025/'
    bind('lean-toolchain', 'cryptanalysis', FORMAL, project+'lean-toolchain')
    bind('lake-dependencies', 'cryptanalysis', FORMAL, project+'lake-manifest.json')
    packet = 'reports/known-label-formal-review-20261028/'
    for sid, path in [('native-log', 'native-ci/job-123003327508.log'),
                      ('native-receipt', 'native-ci/receipt.json'),
                      ('math-review', 'reviewers/TASK-20261028-32bc7d/report.md'),
                      ('fidelity-review', 'reviewers/TASK-20261028-a07ed4/report.md'),
                      ('gate-review', 'reviewers/TASK-20261028-68d1a5/report.md')]:
        bind(sid, 'cryptanalysis', ARCHIVE, packet+path)
    sources.append(dict(id='elaborated-types-missing', kind='unavailable',
                        locator='KnownLabelLeads four declarations at '+FORMAL,
                        reason='The archived packet lacks an explicit elaborated-type printout; source fidelity is narrower.'))
    claims = []
    for name in ('triangle_identity', 'signed_second_moment', 'signed_third_moment', 'positive_pair_product'):
        claims.append(dict(id='known-label/'+name, classification='mathematical',
            source_id='known-label-source', excerpt=excerpt('known-label-source', 'theorem '+name, ':= by ring'),
            statement='The named polynomial identity holds for arbitrary a, b, c in a commutative ring K.',
            assumptions=['K is a commutative ring; the exact displayed polynomial equality is the claim.',
                         'Native evidence trusts the pinned Lean/Mathlib/toolchain and auditor.'],
            evidence=dict(formal_source=['known-label-source'], toolchain=['lean-toolchain'],
                          dependencies=['lake-dependencies'], native_build=['native-log', 'native-receipt'],
                          axiom_audit=['native-log'], elaborated_types=['elaborated-types-missing'],
                          fidelity_review=['fidelity-review', 'math-review'], controls=['native-log', 'gate-review']),
            open_obligations=['Archive explicit elaborated types and review them against the intended source statements.',
                              'Native receipt covers the historical producer head, not the subsequent integration head.',
                              'Graph/group transfer, cancellation, probability, and cost claims require separate proofs.']))

    sheriff = 'research/sheriff/SHF-20261024-46b7da/'
    bind('sheriff-report', 'auto', AUTO, sheriff+'REPORT.md')
    bind('binstd-replay-code', 'auto', AUTO, sheriff+'scripts/binstd-per-target-replay.py')
    receipts = []
    for panel in ('ell89', 'ell89r1'):
        for ell in (8, 9):
            sid = f'binstd-{panel}-ell{ell}'
            bind(sid, 'auto', AUTO, sheriff+f'scripts/binstd-per-target-{panel}-ell{ell}.json')
            receipts.append(sid)
    claims.append(dict(id='binstd/four-cell-reconstruction', classification='computed',
        source_id='sheriff-report', excerpt=excerpt('sheriff-report', 'The PR branch also replayed the four amended BINSTD'),
        statement='The archived follow-up reports deterministic per-target reconstruction of four amended BINSTD cells.',
        assumptions=['Historical authority commits, freeze seeds and implementation hashes are named in each receipt.',
                     'Raw records linked here are reconstructed targets and witnesses, not original machine traces.'],
        evidence=dict(implementation=['binstd-replay-code'], raw_records=receipts, replay=receipts,
                      controls=receipts, context=['sheriff-report']),
        open_obligations=['Bind and independently inspect the original frozen protocol, full historical inputs and executable.',
                          'Independent execution review remains separate from integrity of the archived receipts.',
                          'No original host timing or semantic bridge to the conditional yield theorem is established.']))

    bind('cover-assessment', 'crypto', COVER, 'research/cover_transfer_assessment_20261013/README.md')
    claims.append(dict(id='cover/catalog-assessment-boundary', classification='interpretive',
        source_id='cover-assessment', excerpt=excerpt('cover-assessment', 'Every current cover map', 'Jacobian-transfer pipeline.'),
        statement='The frozen assessment distinguishes a completed catalog classification from incomplete Jacobian-transfer implementation.',
        assumptions=['This is the stated boundary at the frozen PR head, not an independently revalidated current catalog.'],
        evidence=dict(context=['cover-assessment']),
        open_obligations=['Bind catalog data, replay outputs and independent fidelity review before assessing underlying counts.',
                          'Resolve the current PR conflicts through source-aware regeneration; do not infer support for all-element transfer.']))
    result = dict(schema='historical-claim-evidence/v1',
        scope=dict(objective='Make exact historical claim/evidence bindings and missing obligations inspectable across all three repositories.',
                   coverage='partial', omissions=[
                       'Six selected rows only; the full individual-claim denominator remains unknown.',
                       'Other experiments, runs, proofs, dashboards and unresolved historical coverage obligations remain outside this seed.',
                       'Role assignments are curated pointers. The checker establishes byte and excerpt identity, not scientific content or execution proof.']),
        sources=sources, claims=claims)
    with args.output.open('x') as out:
        out.write(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
