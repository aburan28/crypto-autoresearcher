# Commands and access record

All shell commands were executed through the tool runtime. All authored files were confined to `/home/ec2-user/crypto-autoresearcher-frob-c5-review-20261027/research/frob_c5_direct_trace_review_20261027/reports/TASK-20261027-fc5-j2/`. Patch-tool writes created the independent script, report, command record, and attestation. No repository source was read.

## First filesystem source read

```sh
sha256sum /var/tmp/frob-c5-blind-20261027/statement.json && cat /var/tmp/frob-c5-blind-20261027/statement.json
```

The digest matched `17ba164feb8a59ba91346448befaf8ca56e8318de2cc53d6f950a377cbff45e2`. This was the only filesystem source read before coordination and writing the independent implementation.

## Coordination and output-directory creation

```sh
/home/ec2-user/.local/bin/conductor --help
/home/ec2-user/.local/bin/conductor task --help
```

From working directory `/home/ec2-user/crypto-autoresearcher-frob-c5-review-20261027`:

```sh
/home/ec2-user/.local/bin/conductor task claim T-629
```

The claim succeeded with lease `5788c260-c6e7-47c3-81c7-9213910c47d5`, epoch 1. Output identified only the assigned task and this review's write territory. The parent then supplied only the required attestation keys/types and designated joint name.

```sh
mkdir -p /home/ec2-user/crypto-autoresearcher-frob-c5-review-20261027/research/frob_c5_direct_trace_review_20261027/reports/TASK-20261027-fc5-j2
```

## Exact calculation

Working directory: `/home/ec2-user/crypto-autoresearcher-frob-c5-review-20261027`.

```sh
python3 research/frob_c5_direct_trace_review_20261027/reports/TASK-20261027-fc5-j2/exact_trace.py --statement /var/tmp/frob-c5-blind-20261027/statement.json --results research/frob_c5_direct_trace_review_20261027/reports/TASK-20261027-fc5-j2/results.json --runtime research/frob_c5_direct_trace_review_20261027/reports/TASK-20261027-fc5-j2/runtime.json > research/frob_c5_direct_trace_review_20261027/reports/TASK-20261027-fc5-j2/raw_output.json
```

Exit code 0. Runtime details are in `runtime.json`. The source script reads only the isolated statement as mathematical input. Standard-library interpreter dependencies are runtime dependencies, and their source text was not inspected as review material.

## Output inspection

```sh
python3 - <<'PY'
import json
from pathlib import Path
root=Path('/home/ec2-user/crypto-autoresearcher-frob-c5-review-20261027/research/frob_c5_direct_trace_review_20261027/reports/TASK-20261027-fc5-j2')
data=json.loads((root/'results.json').read_text())
for cell in data['cells']:
    print(cell['id'], 'q=', cell['q'])
    for label in ('frobenius', 'five_term_direct', 'wrong_length_four_term_control'):
        if label in cell:
            obj=cell[label]
            print(label)
            for row in obj['matrix_rows']:
                print(row)
            print('rank',obj['rank'],'nullity',obj['nullity'],'base_field_image',obj['image_in_base_field_line'])
    print('equal:',cell['direct_equals_matrix_sum'],'irreducibility:',cell['rabin_irreducibility'])
print((root/'runtime.json').read_text())
PY
```

This read only the reviewer's own `results.json` and `runtime.json`.

## Sealing

The sealing command below reads only the isolated statement and explicitly named files from this review directory. It writes `SHA256SUMS`, then checks the new manifest against all sealed bytes and prints the manifest's own hash. The manifest is an integrity record, not a cryptographic signature or external timestamp. No file is changed after sealing.

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib
root=Path('/home/ec2-user/crypto-autoresearcher-frob-c5-review-20261027/research/frob_c5_direct_trace_review_20261027/reports/TASK-20261027-fc5-j2')
paths=[Path('/var/tmp/frob-c5-blind-20261027/statement.json')]
paths += [root/name for name in ['exact_trace.py','report.md','raw_output.json','results.json','runtime.json','commands.md','review_attestation.yaml']]
manifest=root/'SHA256SUMS'
manifest.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p)+'\n' for p in paths))
for line in manifest.read_text().splitlines():
    expected,path=line.split('  ',1)
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected
print(manifest.read_text(),end='')
print('MANIFEST_SHA256',hashlib.sha256(manifest.read_bytes()).hexdigest())
print('SEAL_VERIFIED',len(paths),'files')
PY
```

After the seal, the only coordination operation is help for release syntax followed by release of T-629 with a note that J2 was sealed and delivered. The release occurs outside the sealed filesystem artifact set and is reported in the delivery message.
