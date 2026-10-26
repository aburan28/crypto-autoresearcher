"""Frozen descriptive analysis of retained F3 rows; never runs arithmetic cases."""
import argparse
from hashlib import sha256
from html import escape
import json
from pathlib import Path


def write_once(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def diagram(cases):
    width, height = 1000, 155+46*len(cases)
    maximum = max([1]+[len(c['assessments']) for c in cases])
    scale = 480/maximum
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<g font-family="Liberation Sans, sans-serif" fill="#18283b">',
             '<text x="24" y="30" font-size="21">F3: recorded four-partition dependencies</text>',
             '<text x="24" y="56" font-size="14">Exact finite-domain counts; controls are deliberately constructed. No confidence interval or yield estimate.</text>',
             '<text x="300" y="82" font-size="13">Dependencies (blue) and verified useful dependencies (green); unit: rows</text>']
    for index, case in enumerate(cases):
        y = 105+46*index
        count = len(case['assessments'])
        useful = sum(a['classification'] == 'useful' for a in case['assessments'])
        parts += [f'<text x="24" y="{y+14}" font-size="14">{escape(case["case"])}</text>',
                  f'<rect x="300" y="{y}" width="{scale*count:.2f}" height="15" fill="#357ba5"/>',
                  f'<rect x="300" y="{y+17}" width="{scale*useful:.2f}" height="10" fill="#278358"/>',
                  f'<text x="810" y="{y+17}" font-size="14">{count} / {useful}</text>']
    parts += [f'<text x="24" y="{height-20}" font-size="13">Source: this report\'s retained run/case files. Zero means an observed empty complete domain only when the case completed.</text>',
              '</g>', '</svg>']
    return '\n'.join(parts)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit('Refusing to overwrite an earlier analysis')
    execution = json.loads((args.run/'execution.json').read_text())
    rows = [json.loads(line) for line in (args.run/'rows.jsonl').read_text().splitlines() if line]
    by_arm = {row['arm']: row for row in rows}
    if len(rows) != 2 or set(by_arm) != {'mitm', 'exhaustive'}:
        raise ValueError('frozen export grid is two algorithms over one full fixed panel each')
    row = by_arm['mitm']
    cases = []
    for entry in execution['case_artifacts']:
        path = args.run/entry['path']
        data = path.read_bytes()
        if sha256(data).hexdigest() != entry['sha256'] or len(data) != entry['bytes']:
            raise ValueError('retained case artifact changed: '+entry['path'])
        case = json.loads(data)
        if case['solver']['relations'] != case['oracle']['relations']:
            raise ValueError('retained relation lists disagree: '+entry['path'])
        cases.append(case)
    natural = [case for case in cases if case['mode'] == 'natural']
    case_rows = [{'case': c['case'], 'mode': c['mode'], 'seed': c['seed'],
                  'dependencies': len(c['assessments']),
                  'useful': sum(a['classification'] == 'useful' for a in c['assessments']),
                  'zero_Q': sum(a['classification'] == 'zero_Q_dependency' for a in c['assessments']),
                  'oracle_signed_quadruples': c['oracle']['signed_quadruples_visited'],
                  'oracle_trace_sha256': c['oracle']['enumeration_trace_sha256'],
                  'label_checks': c['label_verification']['passed'],
                  'target_rejections': len(c['target_rejections']),
                  'base_draws': len(c['base_draws']),
                  'base_rejections': sum(not d['accepted'] for d in c['base_draws'])} for c in cases]
    derived = {'natural_dependencies': sum(c['dependencies'] for c in case_rows if c['mode'] == 'natural'),
               'natural_useful': sum(c['useful'] for c in case_rows if c['mode'] == 'natural'),
               'oracle_signed_quadruples': sum(c['oracle_signed_quadruples'] for c in case_rows)}
    observed = {**row, 'oracle_signed_quadruples': by_arm['exhaustive']['oracle_signed_quadruples']}
    if any(observed[key] != value for key, value in derived.items()):
        raise ValueError('native summary does not match retained case counts')
    args.out.mkdir(parents=True, exist_ok=False)
    result = {'schema': 'f3-pass2-descriptive-analysis/v1', 'task': 'TASK-20261026-821d10',
              'run_id': row['run_id'], 'native_status': row['status'],
              'scope': 'descriptive exact finite-domain arithmetic only',
              'source': row['source'], 'protocol_sha256': execution['protocol_sha256'],
              'planned_cases': 10, 'completed_cases': len(cases), 'natural_cases_completed': len(natural),
              'cases': case_rows, 'derived': derived, 'native_metrics': execution['metrics'],
              'failure': execution['failure'], 'native_flow': execution['flow'],
              'performance_advantage_claim': False, 'official_state_transition': False,
              'model_verified': False,
              'limitations': ['Deterministic SHA fixtures do not establish an independent-uniform law.',
                              'Constructed useful witness was already known to generation.',
                              'The complete oracle is a separate implementation, not independent-session scientific review.',
                              'No general large-base yield, impossibility, comparative speed or end-to-end ECDLP result.']}
    write_once(args.out/'result.json', result)
    (args.out/'diagram.svg').write_text(diagram(cases))
    write_once(args.out/'diagram-source.json', {'source': 'result.json', 'rows': case_rows,
                                             'unit': 'dependencies', 'uncertainty': 'none_exact'})
    table = '\n'.join(f'| {c["case"]} | {c["dependencies"]} | {c["useful"]} | {c["zero_Q"]} | {c["oracle_signed_quadruples"]} |'
                      for c in case_rows)
    report = f'''# F3 second pass: retained m=4 P-256 observations

Observations only. Task `TASK-20261026-821d10`; run `{row['run_id']}`.
The native panel status is **{row['status']}**. {len(cases)} of 10 declared
cases completed, including {len(natural)} of eight unplanted cases. A missing
or stopped case is unknown, not an observed empty relation set.

| Case | Dependencies | Verified useful | Zero-Q | Complete signed quadruples |
| --- | ---: | ---: | ---: | ---: |
{table}

![Recorded finite-domain dependency counts](diagram.svg)

Each completed case uses four disjoint P-256 partitions of eight points.
The point-only shared-coordinate pair join is compared with a separate
Jacobian exhaustive oracle. Both full relation lists are retained. Every
target and label is checked independently with Jacobian arithmetic.
{derived['oracle_signed_quadruples']} signed quadruple visits are recorded
across completed cases. This is an enumeration count, not a cost comparison.

The unplanted cases contain {derived['natural_dependencies']} recorded
dependencies, of which {derived['natural_useful']} have a nonzero target
coefficient and a point-verified scalar. No target scalar was generated for
these cases. The separate useful control deliberately uses a public known
generation witness, while the zero-Q control deliberately creates a label
dependency with A=B=0. Their outcomes are correctness checks and are not
unknown-log recoveries. All base/target rejection attempts and control
planting attempts are retained in case files and flushed event journals.

The native panel records {row['refusal_and_premise_checks']} refusal/premise
checks. These cover forged labels, off-curve inputs, inverse coordinates,
overlapping partitions, wrong signs, repeated-index cancellation and the
nonzero-modulo-r condition. The adaptivity controls audit declared premises;
they cannot detect an undisclosed label-dependent sampling algorithm.

Protocol hash: `{execution['protocol_sha256']}`. Runtime HEAD:
`{row['source']['observed_git_head']}`. The implementation-commit identity and
its checked source-byte equivalence are in the execution receipt. Native
construction, solver, oracle, assessment and refusal counters are kept
separate in `rows.jsonl`; scalar multiplication and group-addition counts are
not interchanged. Host metadata and diagnostic wall/CPU/RSS values are
retained, with `wall_valid=false` on the shared managed host.

The exported unit is one algorithm over the full fixed panel: two arm rows,
MITM and exhaustive. They share inputs, setup/postprocessing and the diagnostic
process interval; those clocks are not separate algorithm measurements.
Per-case flow is native metadata, not a change in the export unit. See `result.json` for the recorded
failure, native flow and exact case digests. Raw files and command/source
receipts are under `{args.run}`. Execution interval: {row['started_at']} to
{row['finished_at']}.

APS (2018), sections 3--3.3, supplies the labelled construction, partition
formulation and shared-S3-coordinate method. The exact source review and
primary-source access gaps are in the track's `literature.md`. The m=4
completeness argument and model-only counting boundary are in `derivation.md`.
The conditional-usefulness lemma requires independent uniform labels,
point-only relation selection and an aggregated vector nonzero modulo r;
our deterministic fixtures do not estimate that probability law.

No comparative performance trial, generic ECDLP advantage, large-base yield
law, impossibility theorem, formal proof certificate, canonical model or
scientific-review admission, or official hypothesis transition is claimed.
The missing interface is a naturally productive structured labelled solver
with complete setup/search/recovery and memory costs. These bounded exact
observations preserve that question.
'''
    (args.out/'report.md').write_text(report)
    print(json.dumps({'status': 'analysis_written', 'out': str(args.out), 'completed_cases': len(cases)}))


if __name__ == '__main__':
    main()
