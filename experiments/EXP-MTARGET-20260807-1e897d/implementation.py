#!/usr/bin/env python3
"""Multi-target Baby-step Giant-step with BKK structure.

For |F|^q targets {y_i}, find P such that O_D([2^i]P) = y_i for all i in 0..r-1
given oracle access to O_D([2^{-1}]Q) = x(Q).

The attack uses r-1 = 1 giant babysteps per target, then meet-in-the-middle
with |F|^m entries per table, where m = floor(q * log_b(q)) + 1.

For multi-target with |F|^q targets, the complexity is O(|F|^{m * (r-1)}),
yielding BFK runtime O(p^{3*r-2+eps}).
"""
import json
import os
import time
import hashlib
import shutil
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import resource

# Constants
P_VALUE = 103
Q_VALUE = 32
R_VALUE = 2
M_VALUE = 6
DEFAULT_BABYSTEPS = 6
DEFAULT_GIANTSTEPS = 6
MEMORY_GB_LIMIT = 4.0
WALL_CLOCK_LIMIT = 3600


@dataclass
class ResultMetadata:
    """Result metadata."""
    p: int
    q: int
    r: int
    b: int
    m: int
    b_minus_1: int
    target_count: int
    run_name: str
    memory_gb: float
    wall_time_seconds: float
    babystep_table_memory: int
    giantstep_table_memory: int
    table_size: int
    run_start: float
    run_end: Optional[float] = None
    success_count: int = 0
    failed_count: int = 0
    early_terminated: bool = False
    early_termination_reason: str = ""
    total_field_ops: int = 0
    config_dict: Dict[str, int] = field(default_factory=dict)


def get_baby_steps(b: int, seed: int = 0) -> List[Tuple[int, int]]:
    """Generate baby-step pairs: (i, i * generator) mod p for i in [0, b-1]."""
    random.seed(seed)
    steps = []
    generator = 2  # Fixed generator for simulation
    for i in range(b):
        step_val = (i * generator) % P_VALUE
        steps.append((i, step_val))
    return steps


def get_giant_steps(m: int, b: int) -> List[Tuple[int, int]]:
    """Generate giant-step pairs: (j*b, (j*b)*generator) mod p for j in [0, m-1]."""
    steps = []
    generator = 2
    for j in range(m):
        gp = (j * b) % P_VALUE
        steps.append((j * b, gp))
    return steps


def hash_pair(pair: Tuple[int, int]) -> str:
    """Hash a pair for lookup table using SHA256."""
    pair_str = f"{pair[0]}:{pair[1]}"
    hash_obj = hashlib.sha256(pair_str.encode())
    return hash_obj.hexdigest()[:16]


def build_lookup_table(steps: List[Tuple[int, int]]) -> Dict[int, str]:
    """Build lookup table from baby-step pairs. Key = value mod |F|^r."""
    lookup = {}
    for step_pair in steps:
        key_val = (step_pair[1] * Q_VALUE) % (Q_VALUE ** R_VALUE)
        hash_val = hash_pair(step_pair)
        lookup[key_val] = hash_val
    return lookup


def find_match(giant_pair: Tuple[int, int], lookup: Dict[int, str], seed: int = 0) -> Optional[Tuple[int, int]]:
    """Find match in lookup table for given giant-step pair with collision."""
    key_val = (giant_pair[1] * Q_VALUE) % (Q_VALUE ** R_VALUE)
    hash_val = hash_pair(giant_pair)
    
    if key_val in lookup:
        for stored_key, stored_hash in lookup.items():
            if stored_hash == hash_val:
                # Found collision
                return (giant_pair[0] % P_VALUE, giant_pair[1])
    return None


def check_memory_usage() -> bool:
    """Check if memory usage is within limits."""
    try:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        current_maxrss_mb = usage.ru_maxrss / 1024  # Convert to MB
        current_maxrss_gb = current_maxrss_mb / 1024  # Convert to GB
        return current_maxrss_gb <= MEMORY_GB_LIMIT
    except (MemoryError, OSError):
        return False


def run_batch(run_id: int, seed: int = 0) -> Dict:
    """Execute a single BKK run.

    For p=103, |F|=32, r=2:
    - Baby-step table size: |F|^b = 32^b entries
    - Giant-step table size: m entries per table
    - Total tables: q^r targets
    
    Returns:
        Dict containing run result metadata
    """
    run_start = time.time()
    babystep_table_memory = 0
    giantstep_table_memory = 0
    table_size = 0
    
    try:
        # Generate baby steps
        baby_steps = get_baby_steps(DEFAULT_BABYSTEPS, seed)
        
        # Build lookup table
        lookup_table = build_lookup_table(baby_steps)
        babystep_table_memory = len(lookup_table) * 16  # bytes per entry
        table_size = len(lookup_table)
        
        # Generate giant steps
        giant_steps = get_giant_steps(M_VALUE, DEFAULT_BABYSTEPS)
        
        # Find matches (simulated)
        for giant_pair in giant_steps:
            match = find_match(giant_pair, lookup_table, seed)
            if match:
                # In real implementation: increment success counter for collisions
        
    except Exception as e:
        return {
            'run_id': run_id,
            'babystep_table_memory': 0,
            'giantstep_table_memory': 0,
            'table_size': 0,
            'field_ops': 0,
            'run_time': 0,
            'error': str(e)
        }
    
    run_end = time.time()
    
    # Calculate field operations (BFK estimate)
    # BFK complexity: O(p^{3*r-2+eps}) = O(103^4) = O(112550881)
    field_ops = int(P_VALUE**(3 * R_VALUE - 2 + 0.5))
    if table_size:
        field_ops *= table_size
    
    return {
        'run_id': run_id,
        'babystep_table_memory': babystep_table_memory,
        'giantstep_table_memory': giantstep_table_memory,
        'table_size': table_size,
        'field_ops': field_ops,
        'run_time': run_end - run_start
    }


def main():
    """Main function to execute experiment runs."""
    results = []
    
    print(f"Running multi-target BKK experiment")
    print(f"Parameters: p={P_VALUE}, q={Q_VALUE}, r={R_VALUE}, b={DEFAULT_BABYSTEPS}, m={M_VALUE}")
    print(f"Target count: {Q_VALUE ** R_VALUE}")
    
    for run_id in range(1, DEFAULT_GIANTSTEPS + 1):
        try:
            result = run_batch(run_id)
            results.append(result)
            print(f"Run {run_id}: completed in {result['run_time']}s")
        except Exception as e:
            print(f"Error in run {run_id}: {e}")
            print(f"Early termination")
            break
    
    # Print summary
    print("\n--- Summary ---")
    for result in results:
        print(f"Run {result['run_id']}: {result}")
    
    return results


if __name__ == "__main__":
    main()
