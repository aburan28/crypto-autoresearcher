#!/usr/bin/env python3
"""Render a descriptive data snapshot; requires the optional typst package."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import shutil


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('snapshot', type=Path)
    args = p.parse_args()
    root = args.snapshot
    if (root / 'report.pdf').exists():
        raise FileExistsError('reports are write-once; collect a new snapshot')
    progress = json.loads((root / 'progress.json').read_text())
    historical = [json.loads(p.read_text()) for p in sorted((root / 'evidence/replay').glob('*/attempt-*/result.json'))]
    verified = [v for v in historical if v['status'] == 'certificate_verified']
    maximum = max([v['certified_codimension_lower_bound'] for v in verified] + [1])
    height = 90 + 28 * len(verified)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="{height}">',
           '<rect width="100%" height="100%" fill="white"/>',
           '<g font-family="sans-serif" fill="#182332">',
           '<text x="12" y="24" font-size="18">Checked codimension lower bounds (F2 dimensions)</text>',
           '<text x="12" y="46" font-size="12">Each row is one named historical certificate; bars show lower bounds, not equalities.</text>']
    for i, value in enumerate(verified):
        y = 62 + 28 * i
        label = f'{value["id"]}, n={value["parameters"]["record"]["n"]}'
        bound = value['certified_codimension_lower_bound']
        width = 480 * bound / maximum
        svg += [f'<text x="12" y="{y+15}" font-size="13">{html.escape(label)}</text>',
                f'<rect x="140" y="{y}" width="{width:.2f}" height="19" fill="#2469a8"/>',
                f'<text x="650" y="{y+15}" font-size="13">at least {bound}</text>']
    svg += ['</g></svg>']
    (root / 'historical-certificates.svg').write_text('\n'.join(svg) + '\n')
    def text(value):
        return json.dumps(str(value), ensure_ascii=False)
    cells = []
    for value in historical:
        r = value['parameters']['record']
        cells.extend([value['id'], r['n'], value['status'], value.get('certified_codimension_lower_bound', 'unknown')])
    table = ',\n'.join(text(v) for v in ['Instance', 'n', 'Observed status', 'codim bound', *cells])
    created = progress['created_at']
    source = f'''#set page(paper: "a4", margin: 17mm)
#set text(size: 10pt)
#set par(justify: false)
= Semaev certificate data: progress snapshot
{created}

This report records observations from an incomplete campaign. It makes no scientific promotion, asymptotic, population-frequency, or performance claim. Missing results remain missing.

Historical replay: *{len(verified)} of 13 certificates independently accepted*, each with its previously recorded SHA-256. Public certificate downloads with complete hash readback: *{progress['public_readback_verified']}*. Fresh solution counts completed: *{progress['completed_solution_counts']} of 190*.

#table(columns: (1fr, 0.5fr, 2fr, 1fr), inset: 5pt,
{table})

#image("historical-certificates.svg", width: 100%)

The independent checker proves that the bounded-degree closure is contained in the kernel of the supplied map. Its codimension is therefore at least the plotted value. Equality is not claimed. Historical solution counts are carried in the original input records and were not recomputed by this replay.

Source: the exact named replay records under `evidence/replay/`, their certificate digests, and public readback acknowledgements in `publication-index.json`. The displayed dimensions are exact checked lower bounds; no uncertainty interval or averaging applies.

#pagebreak()
= Prospective panel and remaining data
The frozen plan has 190 exact input presentations: ten per integer n from 33 to 45 and from 47 to 51, plus ten separately labelled trace-zero inputs at n=33. Ordinary strata have five polynomial and five random subspaces. Every draw is retained, including easy refutations and solvable inputs.

There are 190 degree-four closure requests and 50 additional degree-five requests on the frontier inputs. Degree-five closure is required to certify a lower bound of six. A prospective memory refusal remains unknown; it is not a degree-five ceiling.

#image("coverage.svg", width: 100%)

Fresh lower bounds require both an accepted certificate and an exact exhaustive solution count smaller than the checked codimension. Neither the 190 generated parameter records nor a producer's solver trace substitutes for that conjunction. The graph shows progress counts only.

Execution: two closure workers, each with a 40 GiB address-space ceiling and a six-hour command watchdog. The host is shared, so all wall-valid flags are false. Completed instance records are restartable; in-progress elimination has no process checkpoint. Source and binary hashes are pinned in the copied protocols. Active-run recovery details live in the S3 resume checkpoint.

Software controls: the native counter passed 188 small full enumerations and four batch-boundary comparisons with another counting algorithm. Four damaged-certificate copies were rejected by the independent checker. These are software checks, not a formal proof of the counter.

Known limitations: the separate pre-run S3 checkpoint gate was missed and corrected after launch. The generic unified export mapping remains incomplete. Human expert review is deferred by the owner. None of these is hidden by the certificate or software-check results.
'''
    (root / 'report.typ').write_text(source)
    shutil.copyfile(Path(__file__), root / 'render_snapshot.py')
    import typst
    typst.compile(str(root / 'report.typ'), output=str(root / 'report.pdf'))
    rendered = {name: {'sha256': hashlib.sha256((root / name).read_bytes()).hexdigest(),
                       'bytes': (root / name).stat().st_size}
                for name in ('historical-certificates.svg', 'report.typ', 'report.pdf', 'render_snapshot.py')}
    with open(root / 'rendered-manifest.json', 'x') as out:
        json.dump(rendered, out, indent=2, sort_keys=True)
        out.write('\n')
    print(root / 'report.pdf')


if __name__ == '__main__':
    main()
