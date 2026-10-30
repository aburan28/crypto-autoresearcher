#!/usr/bin/env python3
"""Planning arithmetic for the frozen dense D5 requests, not trial results."""
import json
import math


def estimate(n):
    variables = 2 * ((n + 1) // 2)
    columns = sum(math.comb(variables, d) for d in range(6))
    low = sum(math.comb(variables, d) for d in range(5))
    stride = 8 * ((columns + 63) // 64)
    # This term alone occurs in the frozen admission formula regardless of
    # the initial row count. It lower-bounds that formula, not actual RSS.
    admission_floor = math.ceil(stride * (2 * (columns + 60000) + low) * 1.35) + 2**30
    return dict(n=n, boolean_variables=variables, degree=5, columns=columns,
                admission_formula_floor_bytes=admission_floor,
                exceeds_current_40_GiB_gate=admission_floor > 40 * 2**30,
                exceeds_128_GiB_pool_limit=admission_floor > 128 * 2**30)


if __name__ == '__main__':
    print(json.dumps(dict(schema='semaev.frontier-capacity-planning/v1',
        basis='certificate_campaign.memory_admission, chunk=60000, D=5',
        scope='Derived floor on the existing conservative admission formula; not measured RSS or a universal algorithmic memory lower bound.',
        rows=[estimate(n) for n in range(47, 52)]), indent=2, sort_keys=True))
