"""Own and supervise the admitted paired Prym CLI; never bypass its gate."""
import argparse
from datetime import datetime, timezone
import fcntl
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
from time import monotonic

from common import HERE, ROOT, NATIVE, INPUTS, PARAMETERS, bindings, digest, git, write_once


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('protocol', 'release', 'out'):
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--owner', required=True)
    args = p.parse_args()
    release = json.loads(args.release.read_text())
    if release.get('owner') != args.owner or release.get('parameters') != PARAMETERS:
        raise ValueError('owner/parameters differ from explicit root release')
    if release.get('execution_authorized') is not True:
        raise ValueError('root execution release is absent')
    if args.out.exists():
        raise ValueError('fresh output directory required')
    bindings(release['source_commit'])
    for package, version in release['package_versions'].items():
        if importlib.metadata.version(package) != version:
            raise ValueError('package version differs from release: '+package)
    lock_path = ROOT/'.resume/b1-continuation-owner.lock'
    lock_path.parent.mkdir(exist_ok=True)
    with lock_path.open('a+') as lease:
        fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
        args.out.mkdir(parents=True)
        started, start = now(), monotonic()
        ownership = dict(owner=args.owner, supervisor_pid=os.getpid(), started_at=started,
                         protocol=str(args.protocol), protocol_sha256=release['protocol_sha256'],
                         release_sha256=digest(args.release), output=str(args.out.resolve()))
        lease.seek(0); lease.truncate(); lease.write(json.dumps(ownership)+'\n'); lease.flush()
        write_once(args.out/'ownership.json', ownership)
        cpu = Path('/proc/cpuinfo').read_text() if Path('/proc/cpuinfo').exists() else ''
        mem = Path('/proc/meminfo').read_text() if Path('/proc/meminfo').exists() else ''
        cpu_model = next((line.split(':', 1)[1].strip() for line in cpu.splitlines() if line.startswith('model name')), None)
        memory_bytes = next((int(line.split()[1])*1024 for line in mem.splitlines() if line.startswith('MemTotal:')), None)
        host = dict(cpu_model=cpu_model, logical_cpus=os.cpu_count(), memory_bytes=memory_bytes,
                    kernel=platform.release(), hypervisor=None, isolation_tier_max=None,
                    python=sys.version, executable_sha256=digest(Path(sys.executable).resolve()),
                    packages=release['package_versions'], observed_git_head=git('rev-parse', 'HEAD'),
                    git_dirty=bool(git('status', '--porcelain')), source_commit=release['source_commit'])
        write_once(args.out/'host.json', host)
        argv = [sys.executable, '-B', str(NATIVE/'run_prym.py'), '--inputs', str(INPUTS),
                '--protocol', str(args.protocol.resolve()), '--release', str(args.release.resolve()),
                '--out', str((args.out/'raw').resolve())]
        env = os.environ.copy()
        env.update(PYTHONPATH=str(ROOT/'src')+':'+str(ROOT), OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
        timeout = release['watchdog_seconds']
        def constrain():
            resource.setrlimit(resource.RLIMIT_AS, (release['memory_bytes'], release['memory_bytes']))
            resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout+5))
        timed_out, returncode, exception = False, None, None
        with (args.out/'stdout.txt').open('x') as stdout, (args.out/'stderr.txt').open('x') as stderr:
            child = None
            try:
                child = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=stdout, stderr=stderr,
                                         start_new_session=True, preexec_fn=constrain)
                write_once(args.out/'child.json', dict(supervisor_pid=os.getpid(), child_pid=child.pid,
                                                      child_process_group=child.pid, argv=argv, started_at=now()))
                returncode = child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    returncode = child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    returncode = child.wait()
            except BaseException as error:
                exception = dict(type=type(error).__name__, reason=str(error))
                if child is not None:
                    os.killpg(child.pid, signal.SIGTERM)
                    child.wait()
        unchanged = True
        try:
            bindings(release['source_commit'])
        except Exception as error:
            unchanged = False
            exception = dict(type=type(error).__name__, reason=str(error))
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        write_once(args.out/'execution.json', dict(schema='b1-supervised-execution/v1', owner=args.owner,
            argv=argv, source_commit=release['source_commit'], source_unchanged_after=unchanged,
            protocol=str(args.protocol.resolve()), protocol_sha256=release['protocol_sha256'],
            release_sha256=digest(args.release), observed_git_head=host['observed_git_head'],
            started_at=started, finished_at=now(), diagnostic_wall_seconds=monotonic()-start,
            cpu_user_seconds=usage.ru_utime, cpu_sys_seconds=usage.ru_stime,
            max_rss_bytes=usage.ru_maxrss*1024, wall_valid=False,
            returncode=returncode, timeout=timed_out, exception=exception,
            model_verified=False, model_identity=None, scientific_promotion=False))
        print(json.dumps(dict(output=str(args.out), returncode=returncode, timeout=timed_out)))
        return 0 if returncode == 0 and unchanged and not timed_out else 1


if __name__ == '__main__':
    sys.exit(main())
