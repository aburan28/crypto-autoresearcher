#!/usr/bin/env python3
"""CLI for the Pollard-rho distinguished-point RDS store.

Examples:
  # Credentials (pick one):
  export DATABASE_URL=$(./scripts/rho_rds.sh connstr | head -1)
  # or: RHO_DP_DSN=...  /  Secrets Manager rho/dp-rds on EC2

  python3 scripts/rho_dp/worker.py register \\
      --campaign toy-ecc-12 --curve toy-weierstrass --order-n  ... --dp-bits 2

  python3 scripts/rho_dp/worker.py smoke --campaign smoke-$(date +%s)

  python3 scripts/rho_dp/worker.py run-toy \\
      --campaign toy-ecc-12 --seed 7 --field-bits 12 --dp-bits 2 --max-walks 256

  # ECC2K-130: register the shared campaign, then ingest or watch T2QBIN1 sidecars
  # written by autolab typeii_orbit_pmull_lut_worker.c:
  python3 scripts/rho_dp/worker.py register-ecc2k
  python3 scripts/rho_dp/worker.py ingest-ecc2k \\
      --campaign ecc2k-130 --files /path/to/shard*.t2qbin --limit 64
  python3 scripts/rho_dp/worker.py watch-ecc2k \\
      --campaign ecc2k-130 --dir /path/to/worker_runs --glob '*.t2qbin'
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.rho_dp_store import (  # noqa: E402
    ReportOutcome,
    coeff_bytes,
    open_store,
    point_key_ecc2k_limbs,
    resolve_dsn,
)

# Canonical campaign for live ECC2K-130 Type-II / rho DP sharing.
ECC2K_CAMPAIGN_ID = "ecc2k-130"
ECC2K_CURVE_ID = "certicom-ecc2k-130"
# Subgroup order from typeii_orbit_pmull_lut_worker.c SUBGROUP_ORDER (LE limbs):
#   0x4d4fdd5703a3f269 + 2 * 2^128
ECC2K_ORDER_N = str((2 << 128) + 0x4D4FDD5703A3F269)
# Coeff encoding width must stay fixed across all workers (bytea equality).
ECC2K_COEFF_MOD = 1 << 131


def cmd_register(args: argparse.Namespace) -> int:
    store = open_store(args.dsn)
    try:
        meta = json.loads(args.meta) if args.meta else {}
        store.register_campaign(
            args.campaign,
            args.curve,
            order_n=args.order_n,
            dp_mask_bits=args.dp_bits,
            meta=meta,
        )
    finally:
        store.close()
    print(json.dumps({"ok": True, "campaign_id": args.campaign, "curve_id": args.curve}))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    store = open_store(args.dsn)
    try:
        outcome = store.report_dp(
            args.campaign,
            bytes.fromhex(args.point_key_hex),
            bytes.fromhex(args.a_hex),
            bytes.fromhex(args.b_hex),
            walk_seed=bytes.fromhex(args.walk_seed_hex) if args.walk_seed_hex else None,
            steps=args.steps,
            worker_id=args.worker,
        )
    finally:
        store.close()
    print(json.dumps({
        "is_new": outcome.is_new,
        "is_collision": outcome.is_collision,
        "prior_a_hex": outcome.prior_a.hex() if outcome.prior_a else None,
        "prior_b_hex": outcome.prior_b.hex() if outcome.prior_b else None,
        "prior_worker": outcome.prior_worker,
        "collision_id": outcome.collision_id,
    }))
    return 0


def cmd_smoke(args: argparse.Namespace) -> int:
    """Insert two walks on one point_key; expect is_new then is_collision."""
    # Touch resolve early so missing creds fail before any write.
    _ = resolve_dsn(args.dsn)
    campaign = args.campaign
    store = open_store(args.dsn)
    try:
        store.register_campaign(
            campaign,
            "smoke-curve",
            order_n="17",
            dp_mask_bits=1,
            meta={"purpose": "smoke", "ts": time.time()},
        )
        pk = bytes.fromhex("020102")
        a1, b1 = bytes.fromhex("01"), bytes.fromhex("02")
        a2, b2 = bytes.fromhex("03"), bytes.fromhex("04")
        r1 = store.report_dp(campaign, pk, a1, b1, worker_id="smoke-w1", steps=1)
        r2 = store.report_dp(campaign, pk, a2, b2, worker_id="smoke-w2", steps=2)
        # Duplicate of first walk: not a collision.
        r3 = store.report_dp(campaign, pk, a1, b1, worker_id="smoke-w1", steps=1)
    finally:
        store.close()
    ok = (
        r1.is_new and not r1.is_collision
        and (not r2.is_new) and r2.is_collision
        and (not r3.is_new) and (not r3.is_collision)
    )
    print(json.dumps({
        "ok": ok,
        "campaign_id": campaign,
        "first": {"is_new": r1.is_new, "is_collision": r1.is_collision},
        "second": {
            "is_new": r2.is_new,
            "is_collision": r2.is_collision,
            "collision_id": r2.collision_id,
            "prior_worker": r2.prior_worker,
        },
        "duplicate": {"is_new": r3.is_new, "is_collision": r3.is_collision},
    }))
    return 0 if ok else 1


def cmd_run_toy(args: argparse.Namespace) -> int:
    from harness.toycurve import generate_instance
    from harness.walk import solve_dp

    inst = generate_instance(seed=args.seed, field_bits=args.field_bits)
    store = open_store(args.dsn)
    worker = args.worker or f"toy-{os.getpid()}"
    try:
        store.register_campaign(
            args.campaign,
            f"toy-weierstrass-p{inst.p}",
            order_n=str(inst.n),
            dp_mask_bits=args.dp_bits,
            meta={
                "field_bits": inst.field_bits,
                "seed": inst.seed,
                "p": str(inst.p),
                "note": "toy ECDLP; k never sent to the store",
            },
        )
        result = solve_dp(
            inst,
            dp_bits=args.dp_bits,
            branches=args.branches,
            max_walks=args.max_walks,
            store=store,
            campaign_id=args.campaign,
            worker_id=worker,
        )
    finally:
        store.close()

    out = {
        "solved": result.solved,
        "k": result.k,
        "verified": False,
        "group_operations": result.group_operations,
        "steps": result.steps,
        "distinguished_points": result.distinguished_points,
        "walks": len(result.walks),
        "reason": result.reason,
        "campaign_id": args.campaign,
        "worker_id": worker,
        "n": inst.n,
        "field_bits": inst.field_bits,
        "seed": inst.seed,
    }
    if result.solved and result.k is not None:
        # Independent verify: never trust the store for the scalar claim.
        out["verified"] = inst.curve().mul(result.k, inst.P) == inst.Q
    print(json.dumps(out))
    return 0 if (result.solved and out["verified"]) else 1


# Type-II binary sidecar record (autolab typeii_orbit_pmull_lut_worker.c /
# typeii_binary_quotient_merge.py). Magic + fixed 128-byte LE records.
_SIDECAR_MAGIC = b"T2QBIN1\n"
_RECORD = struct.Struct("<15QIHBx")
assert _RECORD.size == 128


def _limbs_to_int(limbs: tuple[int, int, int]) -> int:
    return limbs[0] | (limbs[1] << 64) | (limbs[2] << 128)


def _register_ecc2k_campaign(
    store: Any,
    campaign_id: str,
    *,
    curve: str | None = None,
    order_n: str | None = None,
    dp_bits: int | None = None,
    meta: dict[str, Any] | None = None,
) -> None:
    base_meta = {
        "format": "T2QBIN1",
        "point_key": "6xuint64-le-limbs (3x + 3y)",
        "coeff_encoding": "17-byte big-endian mod 2^131",
        "walker": "autolab/tasks/ecc2k130_pollard_rho/research/typeii_orbit_pmull_lut_worker.c",
        "ingest": "typeii-binary-sidecar",
    }
    if meta:
        base_meta.update(meta)
    store.register_campaign(
        campaign_id,
        curve or ECC2K_CURVE_ID,
        order_n=order_n or ECC2K_ORDER_N,
        dp_mask_bits=dp_bits,
        meta=base_meta,
    )


def _report_t2qbin_record(
    store: Any,
    campaign_id: str,
    blob: bytes,
    *,
    worker_id: str,
) -> ReportOutcome:
    values = _RECORD.unpack(blob)
    rep_x = _limbs_to_int(values[0:3])
    rep_y = _limbs_to_int(values[3:6])
    a = _limbs_to_int(values[6:9])
    b = _limbs_to_int(values[9:12])
    pk = point_key_ecc2k_limbs(rep_x, rep_y)
    return store.report_dp(
        campaign_id,
        pk,
        coeff_bytes(a, ECC2K_COEFF_MOD),
        coeff_bytes(b, ECC2K_COEFF_MOD),
        walk_seed=coeff_bytes(int(values[14])),
        steps=int(values[13]),
        worker_id=worker_id,
    )


def _iter_new_t2qbin_records(
    path: Path,
    start_offset: int,
) -> tuple[list[bytes], int, bool]:
    """Read complete new T2QBIN1 records starting at start_offset.

    Returns (record_blobs, new_offset, truncated_tail).
    start_offset 0 means "begin of file" (magic still unread).
    """
    size = path.stat().st_size
    if size < len(_SIDECAR_MAGIC):
        return [], start_offset, False

    with path.open("rb") as fh:
        magic = fh.read(len(_SIDECAR_MAGIC))
        if magic != _SIDECAR_MAGIC:
            raise SystemExit(f"{path}: bad magic {magic!r}")
        if start_offset <= 0:
            offset = len(_SIDECAR_MAGIC)
        else:
            offset = start_offset
            if offset < len(_SIDECAR_MAGIC):
                offset = len(_SIDECAR_MAGIC)
            fh.seek(offset)

        records: list[bytes] = []
        while True:
            blob = fh.read(_RECORD.size)
            if not blob:
                return records, offset, False
            if len(blob) != _RECORD.size:
                # Growing file: wait for a full record.
                return records, offset, True
            records.append(blob)
            offset += _RECORD.size


def _load_watch_state(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {"files": {}}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {"files": {}}
    if not isinstance(data, dict):
        return {"files": {}}
    files = data.get("files")
    if not isinstance(files, dict):
        data["files"] = {}
    return data


def _save_watch_state(path: Path | None, state: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def cmd_register_ecc2k(args: argparse.Namespace) -> int:
    store = open_store(args.dsn)
    try:
        meta = json.loads(args.meta) if args.meta else {}
        _register_ecc2k_campaign(
            store,
            args.campaign,
            curve=args.curve,
            order_n=args.order_n,
            dp_bits=args.dp_bits,
            meta=meta,
        )
    finally:
        store.close()
    print(json.dumps({
        "ok": True,
        "campaign_id": args.campaign,
        "curve_id": args.curve or ECC2K_CURVE_ID,
        "order_n": args.order_n or ECC2K_ORDER_N,
    }))
    return 0


def cmd_ingest_ecc2k(args: argparse.Namespace) -> int:
    """Report Type-II binary quotient records into RDS (collision surface only).

    Does not run the ECC2K walk; it only uploads already-produced sidecars so
    remote workers share one collision table. Sidecar format is exactly what
    `typeii_orbit_pmull_lut_worker.c --worker-run-detect-sidecar-neg-bin` writes.
    """
    store = open_store(args.dsn)
    reported = 0
    collisions = 0
    stopped = False
    try:
        _register_ecc2k_campaign(
            store,
            args.campaign,
            curve=args.curve,
            order_n=args.order_n,
            dp_bits=args.dp_bits,
            meta={"mode": "ingest"},
        )
        for path_s in args.files:
            path = Path(path_s)
            records, _offset, truncated = _iter_new_t2qbin_records(path, 0)
            if truncated and not records:
                raise SystemExit(f"{path}: truncated after magic (no full records)")
            for blob in records:
                outcome = _report_t2qbin_record(
                    store,
                    args.campaign,
                    blob,
                    worker_id=args.worker or path.name,
                )
                reported += 1
                if outcome.is_collision:
                    collisions += 1
                    if args.stop_on_collision:
                        stopped = True
                        print(json.dumps({
                            "ok": True,
                            "reported": reported,
                            "collisions": collisions,
                            "collision_id": outcome.collision_id,
                            "prior_worker": outcome.prior_worker,
                            "stopped": True,
                            "campaign_id": args.campaign,
                        }))
                        return 0
                if args.limit is not None and reported >= args.limit:
                    stopped = True
                    break
            if stopped:
                break
    finally:
        store.close()
    print(json.dumps({
        "ok": True,
        "reported": reported,
        "collisions": collisions,
        "campaign_id": args.campaign,
        "limit_reached": bool(args.limit is not None and reported >= args.limit),
    }))
    return 0


def _discover_t2qbin(directory: Path, pattern: str) -> list[Path]:
    paths = sorted(directory.glob(pattern))
    return [p for p in paths if p.is_file()]


def cmd_watch_ecc2k(args: argparse.Namespace) -> int:
    """Continuously ingest growing/new T2QBIN1 files from a directory.

    Parallel C walkers keep writing `*.t2qbin`; one or more watchers share the
    same `--campaign` and let `report_dp()` detect cross-worker collisions.
    Byte offsets are checkpointed so restarts skip already-reported records
    (duplicates are still safe — same (a,b) is a no-op).
    """
    directory = Path(args.dir)
    if not directory.is_dir():
        raise SystemExit(f"not a directory: {directory}")
    state_path = Path(args.state) if args.state else (directory / ".rho_dp_watch_state.json")
    state = _load_watch_state(state_path)
    files_state: dict[str, Any] = state.setdefault("files", {})

    store = open_store(args.dsn)
    total_reported = 0
    total_collisions = 0
    try:
        _register_ecc2k_campaign(
            store,
            args.campaign,
            curve=args.curve,
            order_n=args.order_n,
            dp_bits=args.dp_bits,
            meta={"mode": "watch", "dir": str(directory)},
        )
        deadline = None if args.seconds is None else (time.time() + args.seconds)
        idle_rounds = 0
        while True:
            batch_reported = 0
            for path in _discover_t2qbin(directory, args.glob):
                key = str(path.resolve())
                entry = files_state.setdefault(key, {"offset": 0, "reported": 0})
                start = int(entry.get("offset") or 0)
                try:
                    records, new_offset, _truncated = _iter_new_t2qbin_records(path, start)
                except SystemExit as exc:
                    print(json.dumps({"ok": False, "error": str(exc)}), flush=True)
                    continue
                for blob in records:
                    outcome = _report_t2qbin_record(
                        store,
                        args.campaign,
                        blob,
                        worker_id=args.worker or path.name,
                    )
                    batch_reported += 1
                    total_reported += 1
                    entry["reported"] = int(entry.get("reported") or 0) + 1
                    if outcome.is_collision:
                        total_collisions += 1
                        print(json.dumps({
                            "event": "collision",
                            "path": str(path),
                            "collision_id": outcome.collision_id,
                            "prior_worker": outcome.prior_worker,
                            "worker_id": args.worker or path.name,
                            "campaign_id": args.campaign,
                        }), flush=True)
                        if args.stop_on_collision:
                            entry["offset"] = new_offset
                            files_state[key] = entry
                            _save_watch_state(state_path, state)
                            print(json.dumps({
                                "ok": True,
                                "reported": total_reported,
                                "collisions": total_collisions,
                                "stopped": True,
                                "campaign_id": args.campaign,
                            }))
                            return 0
                entry["offset"] = new_offset
                files_state[key] = entry

            if batch_reported:
                idle_rounds = 0
                _save_watch_state(state_path, state)
                print(json.dumps({
                    "event": "progress",
                    "reported": total_reported,
                    "collisions": total_collisions,
                    "batch": batch_reported,
                    "campaign_id": args.campaign,
                }), flush=True)
            else:
                idle_rounds += 1
                if args.once:
                    break
                if args.max_idle_rounds is not None and idle_rounds >= args.max_idle_rounds:
                    break

            if deadline is not None and time.time() >= deadline:
                break
            if args.once:
                break
            time.sleep(max(0.05, float(args.poll_seconds)))
    finally:
        _save_watch_state(state_path, state)
        store.close()

    print(json.dumps({
        "ok": True,
        "reported": total_reported,
        "collisions": total_collisions,
        "campaign_id": args.campaign,
        "state": str(state_path),
    }))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dsn", default=None, help="postgresql:// URL (else RHO_DP_DSN / DATABASE_URL / rho_rds.sh)")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("register", help="create/update a rho_campaigns row")
    r.add_argument("--campaign", required=True)
    r.add_argument("--curve", required=True)
    r.add_argument("--order-n", default=None)
    r.add_argument("--dp-bits", type=int, default=None)
    r.add_argument("--meta", default=None, help="JSON object")
    r.set_defaults(func=cmd_register)

    re2 = sub.add_parser("register-ecc2k", help=f"register canonical {ECC2K_CAMPAIGN_ID} campaign")
    re2.add_argument("--campaign", default=ECC2K_CAMPAIGN_ID)
    re2.add_argument("--curve", default=ECC2K_CURVE_ID)
    re2.add_argument("--order-n", default=ECC2K_ORDER_N)
    re2.add_argument("--dp-bits", type=int, default=None)
    re2.add_argument("--meta", default=None, help="JSON object")
    re2.set_defaults(func=cmd_register_ecc2k)

    rep = sub.add_parser("report", help="call report_dp() once")
    rep.add_argument("--campaign", required=True)
    rep.add_argument("--point-key-hex", required=True)
    rep.add_argument("--a-hex", required=True)
    rep.add_argument("--b-hex", required=True)
    rep.add_argument("--walk-seed-hex", default=None)
    rep.add_argument("--steps", type=int, default=None)
    rep.add_argument("--worker", default=None)
    rep.set_defaults(func=cmd_report)

    s = sub.add_parser("smoke", help="insert-or-collide self-test against RDS")
    s.add_argument("--campaign", default=f"smoke-{int(time.time())}")
    s.set_defaults(func=cmd_smoke)

    t = sub.add_parser("run-toy", help="toy Weierstrass DP rho worker writing to RDS")
    t.add_argument("--campaign", required=True)
    t.add_argument("--seed", type=int, default=7)
    t.add_argument("--field-bits", type=int, default=12)
    t.add_argument("--dp-bits", type=int, default=2)
    t.add_argument("--branches", type=int, default=16)
    t.add_argument("--max-walks", type=int, default=512)
    t.add_argument("--worker", default=None)
    t.set_defaults(func=cmd_run_toy)

    e = sub.add_parser("ingest-ecc2k", help="upload Type-II T2QBIN1 sidecars to RDS")
    e.add_argument("--campaign", default=ECC2K_CAMPAIGN_ID)
    e.add_argument("--files", nargs="+", required=True)
    e.add_argument("--curve", default=None)
    e.add_argument("--order-n", default=None)
    e.add_argument("--dp-bits", type=int, default=None)
    e.add_argument("--worker", default=None)
    e.add_argument("--limit", type=int, default=None, help="stop after N records (smoke)")
    e.add_argument("--stop-on-collision", action="store_true")
    e.set_defaults(func=cmd_ingest_ecc2k)

    w = sub.add_parser("watch-ecc2k", help="continuously ingest T2QBIN1 files from a directory")
    w.add_argument("--campaign", default=ECC2K_CAMPAIGN_ID)
    w.add_argument("--dir", required=True, help="directory containing *.t2qbin worker outputs")
    w.add_argument("--glob", default="*.t2qbin", help="glob under --dir (default: *.t2qbin)")
    w.add_argument("--state", default=None, help="offset checkpoint JSON (default: DIR/.rho_dp_watch_state.json)")
    w.add_argument("--poll-seconds", type=float, default=2.0)
    w.add_argument("--seconds", type=float, default=None, help="exit after this many seconds")
    w.add_argument("--once", action="store_true", help="single scan then exit")
    w.add_argument("--max-idle-rounds", type=int, default=None, help="exit after N idle polls")
    w.add_argument("--curve", default=None)
    w.add_argument("--order-n", default=None)
    w.add_argument("--dp-bits", type=int, default=None)
    w.add_argument("--worker", default=None)
    w.add_argument("--stop-on-collision", action="store_true")
    w.set_defaults(func=cmd_watch_ecc2k)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
