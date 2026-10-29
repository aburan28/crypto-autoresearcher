#!/usr/bin/env python3
"""Observe existing owners and publish completed evidence; never launch trials.

This helper has no authority to restart a computation. If an owner disappears
before its fixed plan is complete, retain an incomplete status and exit. All
publication goes through publish_certificates.py, including anonymous readback.
"""
import argparse
import datetime
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import time

from certificate_campaign import digest, save
from publish_certificates import public_readback


def held(path):
    if not path.exists():
        return False
    with open(path, 'r') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(lock, fcntl.LOCK_UN)
    return False


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--repo-root', type=Path, required=True)
    p.add_argument('--repo', required=True)
    p.add_argument('--tag', required=True)
    p.add_argument('--interval', type=int, default=60)
    args = p.parse_args()
    study = Path(__file__).resolve().parent
    args.data = args.data.resolve()
    journal = args.data / 'publication-journal.jsonl'
    last = None
    failures = 0
    def record(value):
        value['observed_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with open(journal, 'a') as out:
            out.write(json.dumps(value, sort_keys=True) + '\n')
            out.flush()
            os.fsync(out.fileno())
        print(json.dumps(value), flush=True)
    with open(args.data / 'publication-supervisor.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        record(dict(event='observer_started', pid=os.getpid(), authority='publish existing completed records only'))
        while True:
            replay = list((args.data / 'replay').glob('*/attempt-*/result.json'))
            panel = list((args.data / 'expansion').glob('*/attempt-*/result.json'))
            state = (len({p.parent.parent.name for p in replay}),
                     len({p.parent.parent.name for p in panel}),
                     len(list((args.data / 'expansion').glob('*/inference-*.json'))))
            owners = (held(args.data / 'replay/campaign.lock'), held(args.data / 'expansion/expansion.lock'))
            if state != last:
                command = [sys.executable, str(study / 'publish_certificates.py'),
                           '--run-roots', str(args.data / 'replay'), str(args.data / 'expansion'),
                           '--archive', str(study / 'archive'), '--repo-root', str(args.repo_root),
                           '--repo', args.repo, '--tag', args.tag]
                stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
                log = args.data / ('publication-' + stamp + '.log')
                with open(log, 'x') as output:
                    result = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT)
                if result.returncode:
                    failures += 1
                    record(dict(event='publication_failed', returncode=result.returncode, log=str(log), consecutive=failures))
                    if failures >= 3:
                        record(dict(event='observer_stopped', reason='three publication failures; manual reconciliation required'))
                        return 2
                else:
                    failures = 0
                    snapshot = args.data / 'snapshots' / stamp
                    result = subprocess.run([sys.executable, str(study / 'collect_progress.py'),
                         '--data', str(args.data), '--study', str(study), '--out', str(snapshot)],
                         capture_output=True, text=True)
                    if result.returncode:
                        record(dict(event='snapshot_failed', stderr=result.stderr, snapshot=str(snapshot)))
                    else:
                        record(dict(event='snapshot_complete', replay_terminal=state[0], panel_terminal=state[1],
                                    snapshot=str(snapshot), publication_log=str(log)))
                    last = state
            # Owners may have completed while publishing: recheck on next turn
            # before declaring terminal, so the last certificate is collected.
            if not any(owners):
                current = (len({p.parent.parent.name for p in (args.data / 'replay').glob('*/attempt-*/result.json')}),
                           len({p.parent.parent.name for p in (args.data / 'expansion').glob('*/attempt-*/result.json')}),
                           len(list((args.data / 'expansion').glob('*/inference-*.json'))))
                if current != state:
                    continue
                complete = state == (13, 240, 240)
                if complete and failures == 0:
                    # Publish the full terminal records, including capped and
                    # unsuccessful outcomes. Certificates have separate assets.
                    snapshot = args.data / 'snapshots' / ('final-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
                    subprocess.run([sys.executable, str(study / 'collect_progress.py'),
                         '--data', str(args.data), '--study', str(study), '--out', str(snapshot)], check=True)
                    archive = study / 'archive' / (snapshot.name + '.outcomes.tar.gz')
                    with tarfile.open(archive, 'x:gz') as out:
                        out.add(snapshot, arcname=snapshot.name)
                    sha = digest(archive)
                    subprocess.run([sys.executable, str(args.repo_root / 'tools/artifacts/artifacts.py'),
                         'push', str(archive)], cwd=args.repo_root,
                         env={**os.environ, 'AWS_DEFAULT_REGION': 'us-east-2'}, check=True)
                    subprocess.run(['gh', 'release', 'upload', args.tag, str(archive), '--repo', args.repo], check=True)
                    url = f'https://github.com/{args.repo}/releases/download/{args.tag}/{archive.name}'
                    uri = f's3://setec-astronomy-artifacts/store/sha256/{sha[:2]}/{sha}'
                    with tempfile.TemporaryDirectory(prefix='semaev-final-readback-') as temp:
                        download = Path(temp) / 'download'
                        public_readback(url, sha, download)
                        subprocess.run(['aws', 's3', 'cp', uri, str(download), '--region', 'us-east-2', '--only-show-errors'], check=True)
                        if digest(download) != sha:
                            raise ValueError('final outcomes store readback mismatch')
                    ack = archive.with_suffix('.publication.json')
                    save(ack, dict(schema='semaev.outcomes-publication/v1', anonymous_url=url,
                         store_uri=uri, sha256=sha, bytes=archive.stat().st_size,
                         all_requested_outcomes_retained=True, inference_records=state[2],
                         note='All requested outcomes retained does not mean all closures succeeded or degree six was certified.'))
                    subprocess.run(['gh', 'release', 'upload', args.tag, str(ack), '--repo', args.repo], check=True)
                    record(dict(event='final_outcomes_published', anonymous_url=url, sha256=sha))
                record(dict(event='owners_finished', all_requested_outcomes_retained=complete,
                            replay_terminal=state[0], panel_terminal=state[1]))
                return 0 if complete else 3
            time.sleep(max(10, args.interval))


if __name__ == '__main__':
    sys.exit(main())
