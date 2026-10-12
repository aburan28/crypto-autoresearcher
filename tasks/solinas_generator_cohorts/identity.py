"""EC1-compatible hashing, matching tools/curve_identity.py's exact preimage."""
import hashlib
import json


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode()).hexdigest()


def model_identity(curve):
    return 'urn:weierstrass-model:sha256:' + digest({k: curve[k] for k in ('p', 'A', 'B')})


def generator_identity(curve, generator, tag='publicsample'):
    p = curve['p']
    field = {'characteristic': p, 'degree': 1, 'representation': 'prime field, canonical integer residues',
             'element_encoding': 'integers 0..p-1', 'modulus': p}
    metadata = {'model': 'short-Weierstrass', 'a4': curve['A'], 'a6': curve['B'],
                'subgroup_order': curve['N'], 'cofactor': 1, 'generator': generator,
                'target_group': 'prime-order cyclic subgroup of E(F_p)'}
    sha = digest({'field': field, 'curve': metadata})
    return {'curve_id': f'EC1P{p.bit_length()}C{tag}h{sha[:12]}',
            'curve_uid': 'urn:ec-record:1:sha256:' + sha,
            'curve_sha256': sha, 'field_sha256': digest(field)}
