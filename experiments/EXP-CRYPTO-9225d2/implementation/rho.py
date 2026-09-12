"""rho.py -- two-worker distinguished-point rho walk SOURCE, coefficient
tracking, table structure, and restart/IPC/checkpoint accounting interfaces
for EXP-CRYPTO-9225d2.

STATUS: source only. No walk, transition, or IPC round is executed by this
task (maximum_runs=0). The `run_worker` / `run_coordinator` entry points
below raise a guard rather than run, matching fixture_generator.py's
pattern, so the schedule/logic is reviewable without being launchable here.

Preserves exactly, without narrowing or scalar-GOE substitution:
  - three actual processes (one coordinator + two workers), one transition
    per lane per barrier round (spec.rho.schedule, spec.controlled_variables
    .rho_processes_per_job=3, rho_lanes=2);
  - the common partition law (mod 3 via rejection-sampled hash) and the
    per-branch coefficient recurrence (spec.rho.transition);
  - the distinguished-point law with d = 12/16/20 for k = 40/48/56
    (spec.rho.transition.dp);
  - the canonical endpoint table (open addressing, linear probing, 256-byte
    slots, capacity growth to 2 GiB) (spec.rho.table);
  - restart-on-useless-collision and long-trail (20 * 2**d transitions)
    handling (spec.rho.endpoint_collision, spec.rho.long_trails);
  - checkpoint/IPC accounting fields.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants exactly per specification
# ---------------------------------------------------------------------------

RHO_PROCESSES_PER_JOB = 3  # coordinator + two workers
RHO_LANES = 2
DP_BITS_BY_K = {40: 12, 48: 16, 56: 20}
LONG_TRAIL_MULTIPLIER = 20  # 20 * 2**d transitions before forced restart

TABLE_SLOT_BYTES = 256
TABLE_INITIAL_CAPACITY = 1024
TABLE_MAX_CAPACITY = 8_388_608  # 2 GiB at 256 bytes/slot


# ---------------------------------------------------------------------------
# Partition and transition law (spec.rho.transition)
# ---------------------------------------------------------------------------


def partition_branch(walk_key: bytes, point_encoding: bytes,
                      record_rejections: Optional[List[int]] = None) -> Tuple[int, int]:
    """Hash encode(GOE9225/rho/partition) || walk_key || point_encoding || u64(j)
    with j from zero; accept the first integer h < floor(2**256/3)*3 and use
    h mod 3. Every rejection hash is charged (caller's hash_calls counter,
    not tracked here directly). Returns (branch, final_j)."""
    domain = "GOE9225/rho/partition"
    domain_bytes = len(domain).to_bytes(4, "big") + domain.encode("utf-8")
    threshold = (2 ** 256 // 3) * 3
    j = 0
    while True:
        h_bytes = hashlib.sha256(
            domain_bytes + walk_key + point_encoding + j.to_bytes(8, "big")
        ).digest()
        h = int.from_bytes(h_bytes, "big")
        if h >= threshold:
            if record_rejections is not None:
                record_rejections.append(j)
            j += 1
            continue
        return h % 3, j


def dp_bit_for_k(k_bits: int) -> int:
    if k_bits not in DP_BITS_BY_K:
        raise ValueError("spec.rho fixes k in {40, 48, 56} with d in {12, 16, 20}")
    return DP_BITS_BY_K[k_bits]


def is_distinguished_point(walk_key: bytes, point_encoding: bytes, d_bits: int) -> bool:
    """First d bits of SHA256(encode(GOE9225/rho/DP) || walk_key ||
    point_encoding) are zero. Checked only after transitions, never on
    newly drawn starts (spec.rho.transition.dp)."""
    domain = "GOE9225/rho/DP"
    domain_bytes = len(domain).to_bytes(4, "big") + domain.encode("utf-8")
    digest = hashlib.sha256(domain_bytes + walk_key + point_encoding).digest()
    h = int.from_bytes(digest, "big")
    top_bits = h >> (256 - d_bits)
    return top_bits == 0


@dataclass
class WalkState:
    """A single lane's current (X, a, b) tuple in affine + coefficient form,
    with N-modular coefficient reduction."""

    x: Optional[int]
    y: Optional[int]
    a: int
    b: int
    n_order: int

    def coefficients_reduced(self) -> Tuple[int, int]:
        return self.a % self.n_order, self.b % self.n_order


def apply_branch(branch: int, state: WalkState, q_point: Tuple[Optional[int], Optional[int]],
                  g_point: Tuple[Optional[int], Optional[int]],
                  point_add_fn, point_double_fn) -> WalkState:
    """Branch semantics exactly per spec.rho.transition.branches:
        0 -> (X + Q, a, b + 1)
        1 -> (2X,    2a, 2b)
        2 -> (X + G, a + 1, b)
    coefficients reduced mod N. `point_add_fn`/`point_double_fn` are
    injected callables implementing the fixed ADD/DOUBLE formulas at Z=1
    with the appropriate curve `a` parameter, normalizing after every
    transition (spec.rho.transition.point_step). Not called against real
    walk data in this task.
    """
    n = state.n_order
    if branch == 0:
        new_point = point_add_fn((state.x, state.y), q_point)
        return WalkState(new_point[0], new_point[1], state.a % n, (state.b + 1) % n, n)
    elif branch == 1:
        new_point = point_double_fn((state.x, state.y))
        return WalkState(new_point[0], new_point[1], (2 * state.a) % n, (2 * state.b) % n, n)
    elif branch == 2:
        new_point = point_add_fn((state.x, state.y), g_point)
        return WalkState(new_point[0], new_point[1], (state.a + 1) % n, state.b % n, n)
    else:
        raise ValueError("branch must be 0, 1, or 2")


# ---------------------------------------------------------------------------
# Endpoint table (spec.rho.table)
# ---------------------------------------------------------------------------


@dataclass
class TableSlot:
    x: bytes  # 32 bytes
    y: bytes  # 32 bytes
    a: bytes  # 32 bytes
    b: bytes  # 32 bytes
    trail_id: bytes  # 16 bytes
    transition_count: int  # 8-byte big-endian on serialization
    lane: int  # 4-byte big-endian on serialization
    status: int  # 4-byte big-endian; identity uses this, not unused coords
    endpoint_hash: bytes  # 32 bytes, SHA-256 table hash
    zero_padding: bytes = field(default_factory=lambda: b"\x00" * 64)

    def serialize(self) -> bytes:
        out = (
            self.x + self.y + self.a + self.b + self.trail_id
            + self.transition_count.to_bytes(8, "big")
            + self.lane.to_bytes(4, "big")
            + self.status.to_bytes(4, "big")
            + self.endpoint_hash
            + self.zero_padding
        )
        if len(out) != TABLE_SLOT_BYTES:
            raise ValueError(f"slot must serialize to exactly {TABLE_SLOT_BYTES} bytes, got {len(out)}")
        return out


class EndpointTable:
    """Deterministic open-addressing table with linear probing, keyed by the
    full canonical affine endpoint, retaining the earliest endpoint on
    equality (spec.rho.table). Capacity starts at 1024 slots, doubles
    before load would exceed one half, capped at 8388608 slots (2 GiB);
    both old and new arrays during a resize count toward the 8 GiB process
    memory protection (spec.rho.table.capacity)."""

    def __init__(self) -> None:
        self.capacity = TABLE_INITIAL_CAPACITY
        self.slots: Dict[int, TableSlot] = {}
        self.count = 0

    def _probe_index(self, key_hash: int) -> int:
        return key_hash % self.capacity

    def insert_if_absent(self, key_hash: int, slot: TableSlot) -> Tuple[bool, TableSlot]:
        """Return (inserted_new, resident_slot). Retains earliest endpoint on
        equality; never evicts or reseeds silently (spec.rho.table.cap_behavior).
        Growth/eviction beyond max capacity is a checkpoint-and-censor event,
        not performed automatically here -- this method raises if capacity
        would be exceeded rather than silently discarding data."""
        idx = self._probe_index(key_hash)
        probes = 0
        while idx in self.slots:
            occupant = self.slots[idx]
            # Same affine endpoint (spec.rho.table key): retain earliest slot.
            if occupant.x == slot.x and occupant.y == slot.y:
                return False, occupant
            if probes >= self.capacity:
                raise RuntimeError(
                    "endpoint table full without an explicit resize decision; "
                    "spec.rho.table.cap_behavior requires a checkpoint-and-"
                    "censor receipt here, not silent eviction"
                )
            idx = (idx + 1) % self.capacity
            probes += 1
        if self.count + 1 > self.capacity // 2 and self.capacity < TABLE_MAX_CAPACITY:
            raise RuntimeError(
                "table load would exceed one half capacity; a resize "
                "decision (doubling, retaining old+new arrays for the "
                "memory guard) must happen before this insert, per "
                "spec.rho.table.capacity -- not performed automatically here"
            )
        self.slots[idx] = slot
        self.count += 1
        return True, slot


# ---------------------------------------------------------------------------
# Endpoint collision resolution (spec.rho.endpoint_collision)
# ---------------------------------------------------------------------------


def resolve_endpoint_collision(stored_a: int, stored_b: int, arriving_c: int,
                                arriving_d: int, n_order: int) -> Optional[int]:
    """For stored (a, b) and new (c, d) at the same affine endpoint:
        if d - b != 0 mod N: return (a - c) / (d - b) mod N  (candidate h)
        if d == b mod N: useless collision -> return None (caller restarts
            the arriving lane and retains the earliest stored endpoint).
    The caller must independently verify [h]G = Q before accepting h as a
    recovery (spec.rho.endpoint_collision). Not invoked against real walk
    data in this task."""
    diff = (arriving_d - stored_b) % n_order
    if diff == 0:
        return None
    diff_inv = pow(diff, -1, n_order)
    h = ((stored_a - arriving_c) % n_order) * diff_inv % n_order
    return h


# ---------------------------------------------------------------------------
# Long-trail handling (spec.rho.long_trails)
# ---------------------------------------------------------------------------


def long_trail_threshold(d_bits: int) -> int:
    """After exactly 20 * 2**d transitions without a DP endpoint, the trail
    is recorded and ended, then the same lane restarts at its next trail
    index. A DP on that final step takes precedence over the threshold."""
    return LONG_TRAIL_MULTIPLIER * (2 ** d_bits)


# ---------------------------------------------------------------------------
# Three-process schedule: coordinator + two worker roles
# ---------------------------------------------------------------------------


@dataclass
class RoundMessage:
    """IPC message tagged with round/lane IDs, per spec.rho.schedule.
    Refuses a missing, repeated, or out-of-order round at the coordinator
    (checked by `CoordinatorBarrier.accept`, not enforced by this dataclass
    itself)."""

    round_id: int
    lane_id: int
    payload: bytes


class CoordinatorBarrier:
    """Barrier logic for one round: both lanes execute one transition, then
    endpoints are processed in lane order 0 then 1 (spec.rho.schedule).
    Refuses a missing, repeated, or out-of-order round."""

    def __init__(self) -> None:
        self.expected_round = 0
        self.received: Dict[int, RoundMessage] = {}

    def accept(self, msg: RoundMessage) -> None:
        if msg.round_id != self.expected_round:
            raise ValueError(
                f"out-of-order or repeated round: expected {self.expected_round}, "
                f"got {msg.round_id} (spec.rho.schedule refuses this)"
            )
        if msg.lane_id in self.received:
            raise ValueError(f"duplicate message for lane {msg.lane_id} in round {msg.round_id}")
        self.received[msg.lane_id] = msg

    def round_complete(self) -> bool:
        return set(self.received.keys()) == set(range(RHO_LANES))

    def advance(self) -> List[RoundMessage]:
        if not self.round_complete():
            raise RuntimeError("cannot advance an incomplete round")
        # process endpoints in lane order 0 then 1
        ordered = [self.received[lane] for lane in range(RHO_LANES)]
        self.received = {}
        self.expected_round += 1
        return ordered


def run_worker(lane_id: int) -> None:
    """Worker-process entry point (one of the two actual rho worker
    processes). Not launched or executed by this task."""
    raise RuntimeError(
        "run_worker is source-only in TASK-20260907-ecd3a2; this task "
        "authorizes zero scientific execution and must not spawn or run a "
        "rho worker process. A future scientific-execution task launches "
        "this under its own admitted three-process/cgroup contract."
    )


def run_coordinator(k_bits: int) -> None:
    """Coordinator-process entry point for one rho logical job. Not launched
    or executed by this task."""
    raise RuntimeError(
        "run_coordinator is source-only in TASK-20260907-ecd3a2; this task "
        "authorizes zero scientific execution and must not spawn or run a "
        "rho coordinator process. A future scientific-execution task "
        "launches this under its own admitted three-process/cgroup contract."
    )


# ---------------------------------------------------------------------------
# Checkpoint accounting (spec.runtime.continuation)
# ---------------------------------------------------------------------------


@dataclass
class RhoCheckpoint:
    """Binds RNG/draw counters, both lanes' full state, endpoint table
    contents, input and code hashes, accumulated counters, and timing, per
    spec.runtime.continuation. Resume of the same logical job requires a
    recorded remaining-work disposition and compatible lock; a checkpoint
    never restarts the sample from a favorable seed and never exhausts the
    campaign. Not populated with real data in this task."""

    logical_job_id: str
    lane_states: Tuple[WalkState, WalkState]
    table_snapshot_ref: str
    input_hash: bytes
    code_hash: bytes
    accumulated_counters_ref: str
    wall_ns_elapsed: int
    cpu_ns_elapsed: int
    remaining_work_disposition: str


__all__ = [
    "RHO_PROCESSES_PER_JOB",
    "RHO_LANES",
    "DP_BITS_BY_K",
    "LONG_TRAIL_MULTIPLIER",
    "TABLE_SLOT_BYTES",
    "TABLE_INITIAL_CAPACITY",
    "TABLE_MAX_CAPACITY",
    "partition_branch",
    "dp_bit_for_k",
    "is_distinguished_point",
    "WalkState",
    "apply_branch",
    "TableSlot",
    "EndpointTable",
    "resolve_endpoint_collision",
    "long_trail_threshold",
    "RoundMessage",
    "CoordinatorBarrier",
    "run_worker",
    "run_coordinator",
    "RhoCheckpoint",
]

# NOTE: run_worker/run_coordinator raise rather than execute. All other
# functions/classes here are pure and side-effect-free but are not invoked
# against real walk/seed data anywhere in this module or by importing it.
# Only `python3 -m py_compile` static syntax checking has been run against
# this file under TASK-20260907-ecd3a2.
