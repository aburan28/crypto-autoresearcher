#!/usr/bin/env python3
"""Known saved serial transcripts and corrupted completion/error controls."""
import json
from pathlib import Path
from guest_framing import valid_frame

HERE = Path(__file__).resolve().parent
out = HERE / 'attempts/framing-v1'
out.mkdir(exist_ok=False)
rows = []
source = HERE / 'attempts/qemu-v3'
for p in sorted(source.glob('*/serial.raw')):
    result = json.loads((p.parent / 'result.json').read_text())
    assert valid_frame(result['qemu_exit'], p.read_bytes(), result['reason'])
    rows.append({'name': p.parent.name, 'expected_frame': True, 'observed_frame': True})
raw = (source / 'prime101/serial.raw').read_bytes().replace(b'\r\n', b'\n')
cases = [('missing-completion', 33, raw.replace(b'__ECPP_GUEST_COMPLETE__\n', b''), None),
         ('missing-begin', 33, raw.replace(b'__ECPP_GUEST_BEGIN__\n', b''), None),
         ('missing-child-exit', 33, raw.replace(b'__ECPP_CHILD_EXIT__', b'NO_CHILD'), None),
         ('duplicate-transcript', 33, raw + raw, None),
         ('wrong-ABI', 33, raw.replace(b'__ECPP_INIT_ABI__ 4 4 4', b'__ECPP_INIT_ABI__ 4 8 8'), None),
         ('guest-watchdog', 33, raw.replace(b'timeout=0', b'timeout=1'), None),
         ('host-watchdog', None, raw, 'host_watchdog'),
         ('qemu-exception', 1, raw, None),
         ('empty-output', 33, b'', None)]
for name, code, serial, reason in cases:
    observed = valid_frame(code, serial, reason)
    rows.append({'name': name, 'expected_frame': False, 'observed_frame': observed})
    assert not observed, name
(out / 'COMPLETE.json').write_text(json.dumps({'status': 'passed', 'cases': len(rows),
    'unaltered_saved_transcripts': 17, 'synthetic_negative_controls': 9, 'rows': rows}, indent=2, sort_keys=True) + '\n')
print(json.dumps({'status': 'passed', 'cases': len(rows)}))
