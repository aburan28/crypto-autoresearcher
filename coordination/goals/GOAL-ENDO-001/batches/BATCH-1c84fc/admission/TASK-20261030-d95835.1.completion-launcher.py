"""Mechanical launcher for an already published, live V claim. Never claims work.

The exact independent session and resource helper are pinned. Private inherited
environment and model output remain outside the repository. The parent performs
source/publication/Conductor admission before invoking this launcher.
"""
import datetime, hashlib, json, os, pathlib, struct, subprocess, sys

ROOT = pathlib.Path('/home/ec2-user/crypto-endo-delivery-recovery-20261028')
OUT = pathlib.Path('/home/ec2-user/coordinate-runtime-admission-20261028')
BATCH = 'coordination/goals/GOAL-ENDO-001/batches/BATCH-1c84fc/'
TASK = 'TASK-20261030-d95835'
V_SESSION = '01a18b6d-5a5b-7b83-ac08-0c44e6ff7333'
PARENT_SESSION = '01a179ee-06bf-7550-bc38-0d98c7e3b9c8'
OWNER = 'coordinator-endo-jinv-source-review-20261030'
HELPER = OUT / 'endo_review_cgroup_exec.py'
HELPER_SHA = '00b07b931f9180eac61c6f4560f25b0f3bcb0d6e0197804722dd39ef84260698'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def exclusive(path, data):
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as stream:
        stream.write(data)

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode().strip()

def main():
    os.umask(0o077)
    assert len(sys.argv) == 3, 'phase and actual native epoch required'
    phase, epoch_text = sys.argv[1:]
    assert phase in {'review-001', 'completion-002', 'completion-003'}
    epoch = int(epoch_text)
    assert epoch > 0
    assert os.environ.get('CODEX_THREAD_ID') == PARENT_SESSION
    assert os.environ.get('CODEX_SESSION_ID') == PARENT_SESSION
    assert sha(HELPER.read_bytes()) == HELPER_SHA
    os.environ.update(GIT_CONFIG_COUNT='2', GIT_CONFIG_KEY_0='core.packedGitWindowSize',
                      GIT_CONFIG_VALUE_0='16m', GIT_CONFIG_KEY_1='core.packedGitLimit',
                      GIT_CONFIG_VALUE_1='128m', GIT_OPTIONAL_LOCKS='0')
    claim_path = BATCH + f'claims/{TASK}.{epoch}.claim.json'
    note_path = BATCH + f'admission/{TASK}.{epoch}.owner-writer.json'
    claim = json.loads((ROOT / claim_path).read_bytes())
    note_raw = (ROOT / note_path).read_bytes()
    note = json.loads(note_raw)
    assert claim['owner'] == OWNER and claim['session'] == PARENT_SESSION and claim['epoch'] == epoch
    assert claim['task_id'] == TASK and claim['worktree'] == str(ROOT) and not claim['forced']
    assert not (ROOT / (BATCH + f'claims/{TASK}.{epoch}.release.json')).exists()
    assert note['owner'] == OWNER and note['epoch'] == epoch
    assert note['owning_parent_session'] == PARENT_SESSION and note['writer_session'] == PARENT_SESSION
    assert note['independent_v_session'] == V_SESSION and note['writer_authorized'] is True
    assert subprocess.check_output(['git', 'show', 'HEAD:' + note_path], cwd=ROOT) == note_raw
    deadline = datetime.datetime.fromisoformat(claim['expires_at'].replace('Z', '+00:00'))
    acquired = datetime.datetime.fromisoformat(claim['acquired_at'].replace('Z', '+00:00'))
    assert (deadline - acquired).total_seconds() == 3600
    branch = git('branch', '--show-current')
    head = git('rev-parse', 'HEAD')
    remote_head = git('ls-remote', 'origin', 'refs/heads/' + branch).split()[0]
    assert remote_head == head, 'claim, owner note and task inputs must be published first'
    queue_path = ROOT / (BATCH + 'dispatch_queue.json')
    assert sha(queue_path.read_bytes()) == '9dfde4319381273d75aae86eba8a559d20ca5cee93284e778de7a0be882a51d9'
    trace = OUT / f'endo-review-{phase}-live-fence.trace.jsonl'
    assert not trace.exists()
    os.environ['GIT_TRACE2_EVENT'] = str(trace)
    sys.path.insert(0, str(ROOT / 'tools'))
    import goal_lanes
    lanes = goal_lanes.load_lanes(ROOT, 'GOAL-ENDO-001', include_refs=True)
    live = []
    for entry in lanes.values():
        claims = goal_lanes.claim_summary(ROOT, ROOT / entry['lane']['dispatch_queue_path'], include_refs=True)
        live += [dict(c, task_id=t) for t, c in claims.items() if c['status'] == 'live']
    del os.environ['GIT_TRACE2_EVENT']
    codes = [e['code'] for e in map(json.loads, trace.read_text().splitlines()) if e.get('event') == 'exit']
    assert codes and all(c == 0 for c in codes), 'partial native Git scan is forbidden'
    assert len(live) == 1
    assert live[0]['task_id'] == TASK and live[0]['owner'] == OWNER and live[0]['epoch'] == epoch
    argv = ['/home/ec2-user/.local/bin/conductor', 'check', '--project', 'experiments', '--json',
            '--summary', 'Run exact independent V source-only protocol review under published live claim; zero scientific trials',
            '--scope', 'dir:' + BATCH + 'reviews/' + TASK + '/', '--scope', 'path:' + note_path]
    conductor = json.loads(subprocess.check_output(argv, cwd=ROOT))
    assert conductor['outcome'] == 'allow', conductor
    stem = 'endo-review-' + phase
    prompt = OUT / (stem + '.prompt.md')
    events = OUT / (stem + '.events.jsonl')
    stderr_path = OUT / (stem + '.stderr.txt')
    answer = OUT / (stem + '.json')
    for path in (events, stderr_path, answer):
        assert not path.exists(), str(path)
    remaining = (deadline - datetime.datetime.now(datetime.timezone.utc)).total_seconds() - 180
    timeout = min(1800 if phase == 'review-001' else 600, remaining)
    assert timeout > 0, 'original claim deadline leaves no safe publication interval'
    native = ['/home/ec2-user/.local/bin/codex', 'exec', 'resume', '--json', '-m', 'gpt-5.6-sol',
              '-c', 'model_reasoning_effort=xhigh', '-c', 'sandbox_mode=read-only', '-o', str(answer), V_SESSION, '-']
    envelope = json.dumps({'environment': dict(os.environ), 'argv': native}, separators=(',', ':')).encode()
    assert 0 < len(envelope) < 1024 * 1024
    prompt_raw = prompt.read_bytes()
    data = struct.pack('!I', len(envelope)) + envelope + prompt_raw
    unit = 'codex-endo-review-' + phase + '-20261030'
    command = ['sudo', '-n', 'systemd-run', '--scope', '--quiet', '--unit=' + unit,
               '-p', 'MemoryMax=2147483648', '-p', 'MemorySwapMax=0',
               '/usr/bin/setpriv', '--reuid=1000', '--regid=1000', '--init-groups', '/usr/bin/python3', str(HELPER)]
    preflight = {'observed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'head': head,
                 'native_session': V_SESSION, 'claim_sha256': sha((ROOT / claim_path).read_bytes()),
                 'owner_note_sha256': sha(note_raw), 'epoch': epoch, 'original_deadline': claim['expires_at'],
                 'conductor': conductor, 'lane_count': len(lanes), 'live_claims': len(live),
                 'all_native_git_exit_codes': codes, 'trace_sha256': sha(trace.read_bytes()),
                 'prompt_sha256': sha(prompt_raw), 'helper_sha256': HELPER_SHA, 'timeout_seconds': timeout}
    exclusive(OUT / (stem + '.launch-preflight.json'), (json.dumps(preflight, indent=2) + '\n').encode())
    process = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timed_out = False
    try:
        stdout, stderr = process.communicate(input=data, timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        stop = subprocess.run(['sudo', '-n', 'systemctl', 'stop', unit + '.scope'], capture_output=True, timeout=30)
        stdout, stderr = process.communicate(timeout=30)
        stderr += b'\nOWNED_SCOPE_STOP_ATTEMPT exit_code=' + str(stop.returncode).encode() + b'\n'
    exclusive(events, stdout)
    exclusive(stderr_path, stderr)
    result = {'finished_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'exit_code': process.returncode,
              'timed_out': timed_out, 'events_bytes': len(stdout), 'stderr_bytes': len(stderr),
              'events_sha256': sha(stdout), 'stderr_sha256': sha(stderr), 'answer_exists': answer.exists(),
              'answer_sha256': sha(answer.read_bytes()) if answer.exists() else None,
              'deadline_unchanged': claim['expires_at']}
    exclusive(OUT / (stem + '.launch-result.json'), (json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps(result))
    return 124 if timed_out else int(process.returncode)

if __name__ == '__main__':
    sys.exit(main())
