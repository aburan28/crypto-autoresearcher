"""J4(i): run the snapshot-committed pipeline (copied to src/pipeline_perm; instrument.py patched ONLY
in the walk, run_generic.py and analysis.py byte-identical to the snapshot) on a keyed BIJECTION of
[0, 2^20) at T = 64, W = 64, cap 8W, a = 1/4, seeds 1..3, all arms (U = 16T; eps_ss(8T) reported),
then the pipeline's own analysis (S1/S3/G1 verdicts).  Review control, not an experiment run.
Resource measurement: wall clock + RUSAGE_CHILDREN max RSS (no /usr/bin/time on this host)."""
import os, subprocess, resource, time, datetime, sys, json
TD = '/home/user/crypto-autoresearcher/coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-289698/tasks/TASK-20260906-90e7cf'
PIPE = f'{TD}/src/pipeline_perm'
REPO = '/home/user/crypto-autoresearcher'
ENV = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONHASHSEED='0')
kinds = sys.argv[1:] or ['permutation', 'affine_xorshift']
for kind in kinds:
    rd = f'{TD}/results/j4_perm/{kind}'
    os.makedirs(rd, exist_ok=True)
    for s in (1, 2, 3):
        out = f'{rd}/RUN-RT-90e7cf-{kind}-s{s}'
        os.makedirs(out, exist_ok=True)
        cmd = [sys.executable, f'{PIPE}/run_generic.py', '--n-bits', '20', '--a', '1/4', '--seed', str(s), '--outdir', out]
        open(f'{out}/command.txt', 'w').write(f'cd {REPO}\nRT_WALK_KIND={kind} OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0 timeout 600s ' + ' '.join(cmd) + '\n')
        r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
        t0 = time.monotonic(); start = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with open(f'{out}/stdout.log', 'w') as so, open(f'{out}/stderr.log', 'w') as se:
            try:
                rc = subprocess.run(cmd, cwd=REPO, env=dict(ENV, RT_WALK_KIND=kind), stdout=so, stderr=se, timeout=600).returncode
            except subprocess.TimeoutExpired:
                rc = -1
        wall = time.monotonic() - t0; end = datetime.datetime.now(datetime.timezone.utc).isoformat()
        r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = (r1.ru_utime + r1.ru_stime) - (r0.ru_utime + r0.ru_stime)
        rss = r1.ru_maxrss * 1024  # cumulative max over children; upper bound for this child
        man = {'run': {'id': f'RUN-RT-90e7cf-{kind}-s{s}',
                       'kind_note': 'RED TEAM review control (proves-too-much object, J4(i)); NOT an experiment run of EXP-ECDLP-612fb1',
                       'status': 'completed_valid' if rc == 0 else 'failed_infrastructure', 'exit_code': rc, 'walk_kind': kind,
                       'code': {'pipeline_copy': PIPE, 'snapshot_commit': '840df8a5b51bff046007d1c12b3a45553d76dc11', 'diff_applied': f'{PIPE}/instrument.py.diff'},
                       'inputs': {'parameters': {'kind': 'generic', 'n_bits': 20, 'a': 0.25, 'seed': s, 'stage': 'G'}, 'seed': s},
                       'timing': {'started_at': start, 'finished_at': end, 'wall_seconds': round(wall, 2), 'cpu_seconds': round(cpu, 2)},
                       'resources': {'peak_rss_bytes': rss, 'note': 'RUSAGE_CHILDREN ru_maxrss (max over all children so far)'},
                       'result': {'valid': rc == 0, 'invalid_reason': None if rc == 0 else f'exit code {rc}'}}}
        import yaml
        open(f'{out}/manifest.yaml', 'w').write(yaml.safe_dump(man, sort_keys=False))
        print(f'[{kind} seed {s}] rc={rc} wall={wall:.2f}s cpu={cpu:.2f}s maxrss_children={rss/2**20:.0f} MiB', flush=True)
    an = f'{rd}/analysis'; os.makedirs(an, exist_ok=True)
    cmd = [sys.executable, f'{PIPE}/analysis.py', '--runs-dir', rd, '--stages', 'G', '--outdir', an, '--resamples', '2000']
    open(f'{an}/command.txt', 'w').write(' '.join(cmd) + '\n')
    t0 = time.monotonic()
    with open(f'{an}/stdout.log', 'w') as so, open(f'{an}/stderr.log', 'w') as se:
        rc = subprocess.run(cmd, cwd=REPO, env=ENV, stdout=so, stderr=se, timeout=900).returncode
    print(f'[{kind} analysis] rc={rc} wall={time.monotonic() - t0:.1f}s', flush=True)
