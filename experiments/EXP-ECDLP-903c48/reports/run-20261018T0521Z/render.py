#!/usr/bin/env python3
"""Render published native observations only; never invoke a scientific driver."""
from datetime import datetime
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path
import yaml

ROOT = Path('/workspace/crypto-autoresearcher')
PAIRS = [('f34097', '62ec3d'), ('903c48', '4616a2')]

def tex(value):
    escaped = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    return ''.join(escaped.get(c, c) for c in str(value))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--experiment', choices=[e for e, _ in PAIRS])
    args = parser.parse_args()
    for eid, rid in PAIRS:
        if args.experiment and args.experiment != eid:
            continue
        exp, run_id = 'EXP-ECDLP-' + eid, 'RUN-ECDLP-' + rid
        run = ROOT / 'experiments' / exp / 'runs' / run_id
        receipt = json.loads((run / 'execution-receipt.json').read_text())
        archive = subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', str((run / 'execution-receipt.json').relative_to(ROOT))], cwd=ROOT, text=True).strip()
        if not archive:
            raise RuntimeError('Native raw records are not committed: ' + run_id)
        refs = subprocess.check_output(['git', 'for-each-ref', '--contains=' + archive, '--format=%(refname)', 'refs/remotes/origin/'], cwd=ROOT, text=True).splitlines()
        if not refs:
            raise RuntimeError('Native raw archive is not published: ' + run_id)
        stamp = datetime.fromisoformat(receipt['started_at']).strftime('%Y%m%dT%H%MZ')
        out = ROOT / 'experiments' / exp / 'reports' / ('run-' + stamp)
        out.mkdir(parents=True, exist_ok=False)
        plan = json.loads((ROOT / 'experiments' / exp / 'trial-plan.json').read_text())
        spec = yaml.safe_load((ROOT / 'experiments' / exp / 'specification.yaml').read_text())
        launch = json.loads((run / 'launch.json').read_text())
        raw = json.loads((run / 'raw-result.json').read_text())
        env = json.loads((run / 'environment.json').read_text())
        duration = (datetime.fromisoformat(receipt['finished_at']) - datetime.fromisoformat(receipt['started_at'])).total_seconds()
        command = {'supervisor_argv': ['python3', 'tools/experiment_execution.py', 'run', '--plan', 'experiments/' + exp + '/trial-plan.json', '--owner', receipt['authority']['owner'], '--epoch', str(receipt['authority']['epoch'])], 'outer_environment_prefix': {}, 'native_launch_argv': launch['argv'], 'native_check_argv': launch['check_argv']}
        data = {'experiment_id': exp, 'run_id': run_id, 'hypothesis_id': plan.get('hypothesis_id', spec.get('hypothesis_id')), 'goal_id': plan.get('goal_id', spec.get('goal_id')), 'run_path': str(run.relative_to(ROOT)), 'raw_archive_commit': archive, 'origin_tracking_refs': refs, 'execution_commit': receipt['authority']['commit'], 'dirty_state': None, 'environment': env, 'native_receipt': receipt, 'native_elapsed_seconds_derived': duration, 'elapsed_derivation': 'finished_at minus started_at; complete native run interval, not a solver benchmark', 'driver_and_checker_returncodes': [receipt['returncode'], receipt['check_returncode']], 'memory_ceiling_mb': plan['trials'][0]['memory_mb'], 'watchdog_seconds': plan['trials'][0]['watchdog_seconds'], 'cpu_seconds': None, 'peak_rss_bytes': None, 'certificate': None, 'metrics_and_parameters_unchanged': raw, 'seed_semantics': 'No new random draw; original deterministic fixtures unchanged. No seed is recorded by the original driver.', 'trials_requested': 1, 'trials_output_validated': 0, 'trials_invalid_output': 1, 'trials_timed_out': 0, 'scope': 'Descriptive operational observations only; no scientific verdict or attack claim.'}
        (out / 'report-data.json').write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
        (out / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
        (out / 'metrics.json').write_text(json.dumps(raw, indent=2, sort_keys=True) + '\n')
        dot = 'digraph run { graph[rankdir=LR,bgcolor=white,fontname="Helvetica"]; node[shape=box,style="rounded,filled",fillcolor="#edf2f7",fontname="Helvetica",fontsize=11]; a[label="Frozen stage-0 fixture\\nNative supervisor: 256 MiB"]; b[label="Unchanged original driver\\nThree artifacts emitted"]; c[label="Original checker: exit 0"]; d[label="Native manifest schema\\ninvalid_output",fillcolor="#fee8d5"]; a->b->c->d; label=' + json.dumps(exp + ' / ' + run_id) + '; labelloc=t; }\n'
        (out / 'pipeline.dot').write_text(dot)
        for fmt in ['svg', 'png']:
            subprocess.run(['dot', '-T' + fmt, 'pipeline.dot', '-o', 'pipeline.' + fmt], cwd=out, check=True)
        summary = f"Requested 1 trial; driver and original checker each exited 0. Native output_validated 0, invalid_output 1, timed out 0. Native elapsed {duration:.6f} seconds is derived as finished_at minus started_at. CPU seconds, peak RSS, dirty state, detailed CPU model and a canonical certificate were not recorded. The 256 MiB limit is a ceiling, not measured memory use."
        boundary = "The missing canonical fields are code, environment, inputs, timing and result; the exact native reason is retained in report-data.json. The original checker accepted the emitted worksheet shape, then the supervisor rejected the manifest envelope. The run remains immutable and cannot be rerun in this slot. This process outcome is not a mathematical refutation."
        limits = "One deterministic toy fixture was measured, with no uncertainty interval or sampled inference. Raw timings use the original driver's local boundaries and are not end-to-end performance comparisons. No scientific certificate, security-bit estimate, asymptotic claim or deployed-curve conclusion follows. A later approved successor would have its own identity and observations."
        graphs = "Canonical graph scope checked: knowledge/frontiers/ecdlp and this experiment's frozen specification. No scientific graph content changes follow from a legacy manifest rejection. The pipeline diagram shows the execution and stopping point because there is one fixture and no pair of comparable performance arms."
        text = f"# Native execution report: {exp}\n\n{data['scope']}\n\nRun `{run_id}`; hypothesis `{data['hypothesis_id']}`; goal `{data['goal_id']}`. Immutable records: `{data['run_path']}`. Raw publication commit `{archive}`.\n\n{summary}\n\n{boundary}\n\nExecution commit `{data['execution_commit']}`. Platform and Python are retained in [report-data.json](report-data.json). Exact [commands](command.json), source and specification hashes, raw parameters, local timing fields and controls are retained without changes. Seed: deterministic fixture, no recorded random draw.\n\nRecorded worksheet fields, unchanged:\n\n```json\n{json.dumps(raw, indent=2, sort_keys=True)}\n```\n\n{limits}\n\n{graphs}\n\n[Diagram](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Sources: the run's execution-receipt.json, launch.json, environment.json, manifest.yaml, raw-result.json and original RESULTS.md.\n"
        (out / 'report.md').write_text(text)
        doc = r'''\documentclass[10pt]{article}
\usepackage[margin=17mm]{geometry}
\usepackage{graphicx,listings}
\lstset{basicstyle=\ttfamily\scriptsize,breaklines=true,columns=fullflexible}
\begin{document}
\section*{''' + tex('Native execution report: ' + exp) + r'''}
''' + tex(data['scope']) + r'''\par\medskip
''' + tex('Run ' + run_id + '; hypothesis ' + str(data['hypothesis_id']) + '; goal ' + str(data['goal_id']) + '.') + r'''\par
''' + tex('Raw archive ' + archive + '; execution commit ' + data['execution_commit'] + '.') + r'''\par\medskip
''' + tex(summary) + r'''\par\medskip
''' + tex(boundary) + r'''\par\medskip
\begin{center}\includegraphics[width=\linewidth]{pipeline.png}\end{center}
''' + tex(limits) + r'''\par\medskip
''' + tex(graphs) + r'''\par\medskip
''' + tex('Exact supervisor/driver/checker commands, source/spec hashes, whitelisted environment and native rejection detail are retained in command.json and report-data.json. Seed: deterministic fixture; no random draw or seed recorded. Sources: ../../runs/' + run_id + '/execution-receipt.json, launch.json, environment.json, manifest.yaml, raw-result.json and RESULTS.md.') + r'''
\newpage
\section*{Recorded worksheet fields (unchanged)}
\lstinputlisting{metrics.json}
\end{document}
'''
        (out / 'report.tex').write_text(doc)
        shutil.copy2(__file__, out / 'render.py')
        (out / '.gitignore').write_text('build/\n')
        build = out / 'build'
        build.mkdir()
        result = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', '-output-directory=build', 'report.tex'], cwd=out, capture_output=True, text=True)
        (out / 'render.stdout.log').write_text(result.stdout)
        (out / 'render.stderr.log').write_text(result.stderr)
        result.check_returncode()
        shutil.copy2(build / 'report.pdf', out / 'report.pdf')
        subprocess.run(['pdftotext', 'report.pdf', 'extracted.txt'], cwd=out, check=True)
        subprocess.run(['pdftoppm', '-scale-to', '1600', '-png', 'report.pdf', 'build/page'], cwd=out, check=True, capture_output=True)
        print(out)

if __name__ == '__main__':
    main()
