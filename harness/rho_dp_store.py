"""Postgres distinguished-point store for parallel Pollard's rho.

Talks to the schema in `scripts/rho_dp/schema.sql` (`rho_campaigns`,
`distinguished_points`, `rho_collisions`, `report_dp()`). Credentials never
live in code: resolve `DATABASE_URL` / `RHO_DP_DSN`, or build a URL from
`./scripts/rho_rds.sh connstr` / Secrets Manager (`rho/dp-rds`).

Backends:
  * `psycopg` (v3) when installed — preferred for workers
  * `psql` subprocess fallback — enough for smoke tests on hosts that already
    have the client (e.g. CADO EC2) without installing Python packages

Point-key convention (toy Weierstrass): SEC1-style compressed
  `0x02|0x03 || x` (big-endian, width = ceil(log2(p)/8)). Infinity is rejected.
Walk coefficients `a`, `b` are unsigned big-endian integers mod n.

ECC2K-130 / Type-II quotient campaigns use a separate packing
(`point_key_ecc2k_limbs`); see `scripts/rho_dp/README.md`.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import quote_plus


# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------

def int_to_be_bytes(value: int, length: int | None = None) -> bytes:
    """Unsigned big-endian; length defaults to the minimal non-empty width."""
    if value < 0:
        raise ValueError("expected non-negative integer")
    if length is None:
        length = max(1, (value.bit_length() + 7) // 8)
    return value.to_bytes(length, "big")


def be_bytes_to_int(blob: bytes | memoryview | None) -> int | None:
    if blob is None:
        return None
    return int.from_bytes(bytes(blob), "big")


def point_key_sec1_compressed(x: int, y: int, field_bytes: int) -> bytes:
    """SEC1 compressed: 0x02 (even y) / 0x03 (odd y) || x big-endian."""
    if field_bytes < 1:
        raise ValueError("field_bytes must be >= 1")
    prefix = 0x02 if (y & 1) == 0 else 0x03
    return bytes([prefix]) + int_to_be_bytes(x, field_bytes)


def point_key_from_affine(R: tuple[int, int] | None, p: int) -> bytes:
    if R is None:
        raise ValueError("point at infinity is not a distinguished-point key")
    field_bytes = (p.bit_length() + 7) // 8
    return point_key_sec1_compressed(R[0] % p, R[1] % p, field_bytes)


def point_key_ecc2k_limbs(rep_x: int, rep_y: int) -> bytes:
    """Pack a GF(2^131) affine representative as 6×uint64 little-endian limbs.

    Matches the Type-II sidecar record layout used under
    `autolab/tasks/ecc2k130_pollard_rho/research/` (3 limbs x, 3 limbs y).
    """
    def limbs(v: int) -> bytes:
        out = bytearray()
        for i in range(3):
            out += ((v >> (64 * i)) & ((1 << 64) - 1)).to_bytes(8, "little")
        return bytes(out)

    return limbs(rep_x) + limbs(rep_y)


def coeff_bytes(value: int, n: int | None = None) -> bytes:
    """Big-endian a or b; width from n when given, else minimal."""
    value = int(value)
    if n is not None:
        value %= n
        length = max(1, (n.bit_length() + 7) // 8)
        return int_to_be_bytes(value, length)
    return int_to_be_bytes(value)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ReportOutcome:
    is_new: bool
    is_collision: bool
    prior_a: bytes | None
    prior_b: bytes | None
    prior_worker: str | None
    collision_id: int | None

    @property
    def prior_a_int(self) -> int | None:
        return be_bytes_to_int(self.prior_a)

    @property
    def prior_b_int(self) -> int | None:
        return be_bytes_to_int(self.prior_b)


class DPStore(Protocol):
    def register_campaign(
        self,
        campaign_id: str,
        curve_id: str,
        *,
        order_n: str | None = None,
        dp_mask_bits: int | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None: ...

    def report_dp(
        self,
        campaign_id: str,
        point_key: bytes,
        a: bytes,
        b: bytes,
        *,
        walk_seed: bytes | None = None,
        steps: int | None = None,
        worker_id: str | None = None,
    ) -> ReportOutcome: ...


# ---------------------------------------------------------------------------
# DSN resolution
# ---------------------------------------------------------------------------

def _repo_scripts_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "scripts"


def resolve_dsn(explicit: str | None = None) -> str:
    """Resolve a postgresql:// URL without printing it.

    Order: explicit arg → RHO_DP_DSN → DATABASE_URL → `rho_rds.sh connstr`
    → Secrets Manager `rho/dp-rds` + `.rho_rds_endpoint`.
    """
    for cand in (explicit, os.environ.get("RHO_DP_DSN"), os.environ.get("DATABASE_URL")):
        if cand:
            return cand.strip()

    scripts = _repo_scripts_dir()
    helper = scripts / "rho_rds.sh"
    if helper.is_file() and os.access(helper, os.X_OK):
        try:
            out = subprocess.check_output(
                [str(helper), "connstr"],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=60,
            )
            line = out.splitlines()[0].strip() if out else ""
            if line.startswith("postgresql://"):
                return line
        except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired):
            pass

    endpoint_file = scripts / ".rho_rds_endpoint"
    password_file = scripts / ".rho_rds_password"
    secret_name = os.environ.get("RHO_RDS_SECRET_NAME", "rho/dp-rds")
    region = os.environ.get("AWS_REGION", "us-west-2")
    user = os.environ.get("RHO_RDS_MASTER_USER", "rho")
    db = os.environ.get("RHO_RDS_DB_NAME", "rho_dp")

    endpoint = endpoint_file.read_text().strip() if endpoint_file.is_file() else ""
    if not endpoint:
        endpoint = os.environ.get(
            "RHO_RDS_ENDPOINT",
            "rho-dp.cxqyicswioh8.us-west-2.rds.amazonaws.com",
        )

    password = ""
    if password_file.is_file():
        password = password_file.read_text().strip()
    if not password:
        try:
            import json

            raw = subprocess.check_output(
                [
                    "aws", "secretsmanager", "get-secret-value",
                    "--region", region,
                    "--secret-id", secret_name,
                    "--query", "SecretString",
                    "--output", "text",
                ],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=30,
            )
            password = json.loads(raw).get("password") or ""
        except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired, ValueError):
            password = ""

    if not password:
        raise RuntimeError(
            "no DATABASE_URL / RHO_DP_DSN; set one, or ensure "
            f"{password_file} or Secrets Manager {secret_name} is reachable"
        )
    return (
        f"postgresql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{endpoint}:5432/{db}?sslmode=require"
    )


# ---------------------------------------------------------------------------
# psycopg backend
# ---------------------------------------------------------------------------

class PsycopgStore:
    def __init__(self, dsn: str):
        import psycopg  # type: ignore

        self._psycopg = psycopg
        self._conn = psycopg.connect(dsn, autocommit=True)

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> PsycopgStore:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def register_campaign(
        self,
        campaign_id: str,
        curve_id: str,
        *,
        order_n: str | None = None,
        dp_mask_bits: int | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        import json

        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO rho_campaigns (campaign_id, curve_id, order_n, dp_mask_bits, meta)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (campaign_id) DO UPDATE SET
                  curve_id = EXCLUDED.curve_id,
                  order_n = COALESCE(EXCLUDED.order_n, rho_campaigns.order_n),
                  dp_mask_bits = COALESCE(EXCLUDED.dp_mask_bits, rho_campaigns.dp_mask_bits),
                  meta = rho_campaigns.meta || EXCLUDED.meta
                """,
                (
                    campaign_id,
                    curve_id,
                    order_n,
                    dp_mask_bits,
                    json.dumps(meta or {}),
                ),
            )

    def report_dp(
        self,
        campaign_id: str,
        point_key: bytes,
        a: bytes,
        b: bytes,
        *,
        walk_seed: bytes | None = None,
        steps: int | None = None,
        worker_id: str | None = None,
    ) -> ReportOutcome:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT is_new, is_collision, prior_a, prior_b, prior_worker, collision_id
                FROM report_dp(%s, %s, %s, %s, %s, %s, %s)
                """,
                (campaign_id, point_key, a, b, walk_seed, steps, worker_id),
            )
            row = cur.fetchone()
        if row is None:
            raise RuntimeError("report_dp returned no row")
        return ReportOutcome(
            is_new=bool(row[0]),
            is_collision=bool(row[1]),
            prior_a=bytes(row[2]) if row[2] is not None else None,
            prior_b=bytes(row[3]) if row[3] is not None else None,
            prior_worker=row[4],
            collision_id=int(row[5]) if row[5] is not None else None,
        )


# ---------------------------------------------------------------------------
# psql subprocess backend (no Python driver required)
# ---------------------------------------------------------------------------

_SAFE_IDENT = re.compile(r"^[A-Za-z0-9_.:@+=/-]{1,200}$")


def _sql_str(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def _sql_bytea(blob: bytes | None) -> str:
    if blob is None:
        return "NULL"
    # E'\\xdeadbeef' form accepted by Postgres.
    return "E'\\\\x" + blob.hex() + "'"


def _sql_bigint(v: int | None) -> str:
    if v is None:
        return "NULL"
    return str(int(v))


class PsqlStore:
    """Drive report_dp / campaign insert through the `psql` CLI."""

    def __init__(self, dsn: str):
        if not shutil.which("psql"):
            raise RuntimeError("psql not found on PATH (and psycopg is not installed)")
        self._dsn = dsn

    def close(self) -> None:
        return

    def __enter__(self) -> PsqlStore:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _run(self, sql: str) -> str:
        # Pass DSN via env so it does not appear in argv.
        env = os.environ.copy()
        env["PGPASSWORD"] = env.get("PGPASSWORD", "")  # may already be in URL
        with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False) as fh:
            fh.write(sql)
            path = fh.name
        try:
            proc = subprocess.run(
                [
                    "psql", self._dsn,
                    "-v", "ON_ERROR_STOP=1",
                    "-A", "-t", "-F", "\t",
                    "-f", path,
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )
        finally:
            os.unlink(path)
        if proc.returncode != 0:
            raise RuntimeError(
                f"psql failed ({proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}"
            )
        return proc.stdout

    def register_campaign(
        self,
        campaign_id: str,
        curve_id: str,
        *,
        order_n: str | None = None,
        dp_mask_bits: int | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        import json

        if not _SAFE_IDENT.match(campaign_id):
            raise ValueError(f"unsafe campaign_id: {campaign_id!r}")
        if not _SAFE_IDENT.match(curve_id):
            raise ValueError(f"unsafe curve_id: {curve_id!r}")
        order_sql = "NULL" if order_n is None else _sql_str(order_n)
        bits_sql = "NULL" if dp_mask_bits is None else str(int(dp_mask_bits))
        meta_sql = _sql_str(json.dumps(meta or {}))
        self._run(
            f"""
            INSERT INTO rho_campaigns (campaign_id, curve_id, order_n, dp_mask_bits, meta)
            VALUES ({_sql_str(campaign_id)}, {_sql_str(curve_id)}, {order_sql},
                    {bits_sql}, {meta_sql}::jsonb)
            ON CONFLICT (campaign_id) DO UPDATE SET
              curve_id = EXCLUDED.curve_id,
              order_n = COALESCE(EXCLUDED.order_n, rho_campaigns.order_n),
              dp_mask_bits = COALESCE(EXCLUDED.dp_mask_bits, rho_campaigns.dp_mask_bits),
              meta = rho_campaigns.meta || EXCLUDED.meta;
            """
        )

    def report_dp(
        self,
        campaign_id: str,
        point_key: bytes,
        a: bytes,
        b: bytes,
        *,
        walk_seed: bytes | None = None,
        steps: int | None = None,
        worker_id: str | None = None,
    ) -> ReportOutcome:
        if not _SAFE_IDENT.match(campaign_id):
            raise ValueError(f"unsafe campaign_id: {campaign_id!r}")
        if worker_id is not None and not _SAFE_IDENT.match(worker_id):
            raise ValueError(f"unsafe worker_id: {worker_id!r}")
        worker_sql = "NULL" if worker_id is None else _sql_str(worker_id)
        out = self._run(
            f"""
            SELECT is_new::text, is_collision::text,
                   COALESCE(encode(prior_a, 'hex'), ''),
                   COALESCE(encode(prior_b, 'hex'), ''),
                   COALESCE(prior_worker, ''),
                   COALESCE(collision_id::text, '')
            FROM report_dp(
              {_sql_str(campaign_id)},
              {_sql_bytea(point_key)},
              {_sql_bytea(a)},
              {_sql_bytea(b)},
              {_sql_bytea(walk_seed)},
              {_sql_bigint(steps)},
              {worker_sql}
            );
            """
        )
        # psql -A -t may emit trailing tabs / blank lines; take the last
        # non-empty line and pad/truncate to the six SELECT columns.
        lines = [ln for ln in out.splitlines() if ln.strip()]
        if not lines:
            raise RuntimeError(f"report_dp returned empty psql output: {out!r}")
        parts = lines[-1].rstrip("\r").split("\t")
        if len(parts) < 2:
            raise RuntimeError(f"unexpected report_dp psql output: {out!r}")
        while len(parts) < 6:
            parts.append("")
        parts = parts[:6]

        def _bool(s: str) -> bool:
            return s.strip().lower() in ("t", "true", "1", "yes")

        prior_a = bytes.fromhex(parts[2]) if parts[2] else None
        prior_b = bytes.fromhex(parts[3]) if parts[3] else None
        return ReportOutcome(
            is_new=_bool(parts[0]),
            is_collision=_bool(parts[1]),
            prior_a=prior_a,
            prior_b=prior_b,
            prior_worker=parts[4] or None,
            collision_id=int(parts[5]) if parts[5] else None,
        )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def open_store(dsn: str | None = None) -> PsycopgStore | PsqlStore:
    url = resolve_dsn(dsn)
    try:
        import psycopg  # noqa: F401
        return PsycopgStore(url)
    except ImportError:
        return PsqlStore(url)
