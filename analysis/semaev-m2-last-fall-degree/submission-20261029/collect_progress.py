#!/usr/bin/env python3
"""Write a new, evidence-linked progress snapshot; never fill in missing data."""
import argparse
import collections
import datetime
import html
import json
from pathlib import Path
import shutil

from certificate_campaign import digest, save


def terminal_rows(root):
    result = {}
    for path in sorted(root.glob('*/attempt-*/result.json')):
        value = json.loads(path.read_text())
        result[value['id']] = (value, path)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--study', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    plan = json.loads((args.data / 'expansion/plan.json').read_text())
    replay = terminal_rows(args.data / 'replay')
    expansion = terminal_rows(args.data / 'expansion')
    counts = {}
    for path in sorted((args.data / 'expansion/counts').glob('*/attempt-*/result.json')):
        value = json.loads(path.read_text())
        counts[value['parameters']['name']] = (value, path)
    publications = {p.stem.removesuffix('.publication'): json.loads(p.read_text())
                    for p in (args.study / 'archive').glob('*.publication.json')}
    rows = []
    for item in plan['items']:
        name = item['id']
        record = item['record']
        value, source = expansion.get(name, ({}, None))
        count, count_path = counts.get(record['name'], ({}, None))
        inferences = sorted((args.data / 'expansion' / name).glob('inference-*.json'))
        inference = json.loads(inferences[-1].read_text()) if inferences else {}
        rows.append(dict(id=name, n=record['n'], k=record['k'], family=record['basis'],
             degree=item['degree'], status=value.get('status', 'pending'),
             exact_solutions=count.get('ordered_solutions') if count.get('status') == 'completed' else None,
             certified_codimension_lower_bound=value.get('certified_codimension_lower_bound'),
             last_fall_degree_lower_bound=inference.get('last_fall_degree_lower_bound'),
             public_readback_verified=name in publications,
             result_sha256=digest(source) if source else None))
    # Preserve the completed records used in this snapshot, not partial log
    # tails from still-running processes. Large certificates remain in archive/.
    sources = [path for _, path in replay.values()] + [path for _, path in expansion.values()]
    sources += [path for _, path in counts.values()]
    sources += list((args.data / 'expansion').glob('*/inference-*.json'))
    completed_sources = list(sources)
    for source in completed_sources:
        if source.name == 'result.json':
            sources += [path for path in source.parent.iterdir()
                        if path.is_file() and path.name not in ('certificate.bin', 'result.json')]
    for source in set(sources):
        target = args.out / 'evidence' / source.relative_to(args.data)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for name in ('replay-protocol.json', 'expansion-protocol.json'):
        shutil.copyfile(args.study / name, args.out / name)
    shutil.copyfile(args.data / 'expansion/plan.json', args.out / 'planned-inputs.json')
    progress = dict(schema='semaev.data-progress/v1', created_at=now,
         historical_planned=13, historical_terminal=len(replay),
         historical_statuses=dict(collections.Counter(v['status'] for v, _ in replay.values())),
         prospective_inputs=190, prospective_closure_requests=240,
         completed_solution_counts=sum(v['status'] == 'completed' for v, _ in counts.values()),
         prospective_statuses=dict(collections.Counter(r['status'] for r in rows)),
         public_readback_verified=len(publications),
         plan_sha256=digest(args.data / 'expansion/plan.json'),
         notes=['A planned input is not a completed count or a certificate.',
                'Publication requires anonymous download/hash and S3 download/hash.',
                'Only count < certified codimension supports the recorded LFD lower bound.',
                'No asymptotic, population-frequency or runtime claim.'])
    save(args.out / 'progress.json', progress)
    save(args.out / 'rows.json', rows)
    save(args.out / 'publication-index.json', publications)
    lines = ['# Certificate data progress', '', now, '',
             f'Historical certificates: **{progress["historical_statuses"].get("certificate_verified",0)}/13** independently checked with historical hash identity.',
             f'Public certificates with complete download/hash readback: **{len(publications)}**.',
             f'Fresh exact solution counts completed: **{progress["completed_solution_counts"]}/190**.', '',
             'The 190 input records and 240 closure requests are a fixed plan. Pending cells carry no measured result.', '',
             '| n | Inputs | D4 terminal | D4 certificates | LFD ≥ 5 inferred | D5 terminal | LFD ≥ 6 inferred |',
             '|---:|---:|---:|---:|---:|---:|---:|']
    groups = []
    for n in sorted({r['n'] for r in rows}):
        d4 = [r for r in rows if r['n'] == n and r['degree'] == 4]
        d5 = [r for r in rows if r['n'] == n and r['degree'] == 5]
        values = [n, len(d4), sum(r['status'] != 'pending' for r in d4),
                  sum(r['status'] == 'certificate_verified' for r in d4),
                  sum((r['last_fall_degree_lower_bound'] or 0) >= 5 for r in d4),
                  sum(r['status'] != 'pending' for r in d5),
                  sum((r['last_fall_degree_lower_bound'] or 0) >= 6 for r in d5)]
        lines.append('| ' + ' | '.join(map(str, values)) + ' |')
        groups.append(values)
    lines += ['', 'The n=33 total includes ten separately labelled trace-zero inputs. Every other n has five polynomial and five random-subspace inputs.', '',
              'A certificate proves W_D ⊆ ker(π), hence a codimension lower bound. The fresh-panel inference additionally uses the exhaustive solution count. A producer report that 1 belongs to W_D is retained without upgrading it to an independently checked certificate.', '',
              '![Completed degree-four certificate checks](coverage.svg)', '',
              'Sources: `rows.json`, the copied completed records under `evidence/`, the frozen protocols, and `planned-inputs.json`. No pending result has been imputed.']
    (args.out / 'report.md').write_text('\n'.join(lines) + '\n')
    height = 110 + 26 * len(groups)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="820" height="{height}" viewBox="0 0 820 {height}">',
           '<rect width="100%" height="100%" fill="white"/>',
           '<g font-family="sans-serif" fill="#182332">',
           '<text x="24" y="28" font-size="19">Fresh-panel degree-four certificate checks</text>',
           '<text x="24" y="52" font-size="12">Blue: independently checked certificates. Gray: fixed input count. Missing checks remain unknown.</text>']
    for i, values in enumerate(groups):
        n, planned, terminal, certified, inferred, _, _ = values
        y = 76 + 26 * i
        svg += [f'<text x="24" y="{y+14}" font-size="13">n = {n}</text>',
                f'<rect x="95" y="{y}" width="{planned*24}" height="18" fill="#e5e9ee"/>',
                f'<rect x="95" y="{y}" width="{certified*24}" height="18" fill="#2469a8"/>',
                f'<text x="600" y="{y+14}" font-size="13">{certified}/{planned} checked; {terminal} terminal</text>']
    svg += [f'<text x="24" y="{height-14}" font-size="11">Snapshot {html.escape(now)} — exact named inputs; no timing or growth inference.</text>', '</g></svg>']
    (args.out / 'coverage.svg').write_text('\n'.join(svg) + '\n')
    save(args.out / 'manifest.json', {str(path.relative_to(args.out)): {'bytes': path.stat().st_size, 'sha256': digest(path)}
                                     for path in sorted(args.out.rglob('*')) if path.is_file()})
    print(json.dumps(progress))


if __name__ == '__main__':
    main()
