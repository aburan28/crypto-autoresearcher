"""CloudWatch snapshot of the rho distinguished-point database.

The research dashboard is static on GitHub Pages and live locally. Neither
host should show LAST HOUR as 0 merely because the wall-clock hour is empty
while the latest CloudWatch sample is a few hours old — that is a missing
sample, not a stopped database. This module:

  * reads RDS + CloudWatch when AWS credentials are in the environment;
  * reports LAST HOUR from wall-clock samples when they exist;
  * otherwise reports the hour ending at the latest sample, labelled as
    such, instead of a naked zero;
  * writes nothing to the repository.

Stdlib only. Missing credentials, a refused IAM call, or a timeout become
`available: false` with a reason — never fabricated rates.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any

# The distinguished-point store for the rho campaign. The dashboard names
# the instance, not the hostname.
RDS_INSTANCE = "rho-dp"
RDS_REGION = "us-west-2"
OBJECT_STORE_BUCKET = "crypto-autoresearcher"
# Daily S3 storage metrics usually land in us-east-1, but this bucket's
# series is published in the bucket region. Try the instance region first,
# then us-east-1, and keep whichever actually has datapoints.
S3_METRIC_REGIONS = (RDS_REGION, "us-east-1")

_S3_SIZE_TYPES = (
    "StandardStorage",
    "IntelligentTieringFAStorage",
    "StandardIAStorage",
    "GlacierInstantRetrievalStorage",
)

# Wall-clock last hour can be empty while samples from two hours ago are
# still the newest thing CloudWatch has. Fetch far enough back to fill the
# "hour ending at the latest point" fallback.
RECENT_SECONDS = 4 * 3600
DAY_SECONDS = 24 * 3600
STALE_AFTER_SECONDS = 15 * 60

_METRICS = (
    "WriteIOPS",
    "ReadIOPS",
    "WriteThroughput",
    "ReadThroughput",
    "FreeStorageSpace",
    "CPUUtilization",
    "DatabaseConnections",
)


def unavailable(reason: str) -> dict[str, Any]:
    return {"available": False, "reason": reason}


def _iso(ts: int | float | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _epoch(stamp: str) -> int:
    text = stamp.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return int(datetime.fromisoformat(text).timestamp())


def _local(elem: ET.Element, name: str) -> str:
    for child in elem:
        if child.tag.split("}", 1)[-1] == name:
            return (child.text or "").strip()
    return ""


def _members(elem: ET.Element, name: str) -> list[ET.Element]:
    found: list[ET.Element] = []
    for child in elem:
        tag = child.tag.split("}", 1)[-1]
        if tag == name:
            found.extend(
                grandchild for grandchild in child
                if grandchild.tag.split("}", 1)[-1] == "member")
            if not found and list(child):
                found.extend(list(child))
    return found


def window_mean(samples: list[tuple[int, float]], start: int, end: int) -> tuple[float | None, int]:
    picked = [value for ts, value in samples if start <= ts <= end]
    if not picked:
        return None, 0
    return sum(picked) / len(picked), len(picked)


def window_integral(samples: list[tuple[int, float]], start: int, end: int, period: int) -> float | None:
    picked = [value for ts, value in samples if start <= ts <= end]
    if not picked:
        return None
    return sum(value * period for value in picked)


def last_hour_bounds(now: int, latest: int | None) -> tuple[int, int, str]:
    """Prefer the wall-clock hour; fall back to the hour ending at `latest`."""
    if latest is not None and latest >= now - 3600:
        return now - 3600, now, "wall"
    if latest is not None:
        return latest - 3600, latest, "latest_sample"
    return now - 3600, now, "wall"


def summarize_rate(samples: list[tuple[int, float]], start: int, end: int, period: int) -> dict[str, Any]:
    mean, n = window_mean(samples, start, end)
    total = window_integral(samples, start, end, period)
    return {
        "mean": None if mean is None else round(mean, 4),
        "total": None if total is None else round(total, 3),
        "samples": n,
    }


class AwsQuery:
    """Minimal AWS query-protocol client. No boto3."""

    def __init__(self, access_key: str, secret: str, region: str, timeout: float = 12.0):
        self.access_key = access_key
        self.secret = secret
        self.region = region
        self.timeout = timeout

    def call(self, service: str, host: str, action: str, version: str,
             params: dict[str, str]) -> ET.Element:
        payload = urllib.parse.urlencode(
            {"Action": action, "Version": version, **params}).encode("utf-8")
        now = datetime.now(timezone.utc)
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = now.strftime("%Y%m%d")
        payload_hash = hashlib.sha256(payload).hexdigest()
        signed_headers = "content-type;host;x-amz-date"
        canonical = (
            f"POST\n/\n\n"
            f"content-type:application/x-www-form-urlencoded; charset=utf-8\n"
            f"host:{host}\n"
            f"x-amz-date:{amz_date}\n"
            f"\n{signed_headers}\n{payload_hash}"
        )
        scope = f"{date_stamp}/{self.region}/{service}/aws4_request"
        string_to_sign = (
            f"AWS4-HMAC-SHA256\n{amz_date}\n{scope}\n"
            f"{hashlib.sha256(canonical.encode()).hexdigest()}"
        )
        signing_key = _signing_key(self.secret, date_stamp, self.region, service)
        signature = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Host": host,
            "X-Amz-Date": amz_date,
            "Authorization": (
                f"AWS4-HMAC-SHA256 Credential={self.access_key}/{scope}, "
                f"SignedHeaders={signed_headers}, Signature={signature}"
            ),
        }
        req = urllib.request.Request(
            f"https://{host}/", data=payload, method="POST", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:400]
            raise RuntimeError(f"{action} {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(f"{action} failed: {exc}") from exc
        return ET.fromstring(body)


def _signing_key(secret: str, date_stamp: str, region: str, service: str) -> bytes:
    def _hmac(key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode(), hashlib.sha256).digest()
    k_date = _hmac(("AWS4" + secret).encode(), date_stamp)
    k_region = hmac.new(k_date, region.encode(), hashlib.sha256).digest()
    k_service = hmac.new(k_region, service.encode(), hashlib.sha256).digest()
    return hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()


def _metric_points(xml: ET.Element) -> list[tuple[int, float]]:
    result = None
    for child in xml:
        if child.tag.split("}", 1)[-1] == "GetMetricStatisticsResult":
            result = child
            break
    if result is None:
        return []
    points: list[tuple[int, float]] = []
    for member in _members(result, "Datapoints"):
        stamp = _local(member, "Timestamp")
        average = _local(member, "Average")
        if not stamp or not average:
            continue
        try:
            points.append((_epoch(stamp), float(average)))
        except ValueError:
            continue
    points.sort()
    return points


def _get_metric(client: AwsQuery, metric: str, start: int, end: int, period: int) -> list[tuple[int, float]]:
    params = {
        "Namespace": "AWS/RDS",
        "MetricName": metric,
        "StartTime": _iso(start) or "",
        "EndTime": _iso(end) or "",
        "Period": str(period),
        "Statistics.member.1": "Average",
        "Dimensions.member.1.Name": "DBInstanceIdentifier",
        "Dimensions.member.1.Value": RDS_INSTANCE,
    }
    xml = client.call("monitoring", f"monitoring.{client.region}.amazonaws.com",
                      "GetMetricStatistics", "2010-08-01", params)
    return _metric_points(xml)


def _describe_instance(client: AwsQuery) -> dict[str, Any]:
    xml = client.call(
        "rds", f"rds.{client.region}.amazonaws.com",
        "DescribeDBInstances", "2014-10-31",
        {"DBInstanceIdentifier": RDS_INSTANCE})
    fields: dict[str, str] = {}
    for node in xml.iter():
        tag = node.tag.split("}", 1)[-1]
        if tag in ("Engine", "EngineVersion", "DBInstanceClass", "DBInstanceStatus",
                   "AllocatedStorage", "MaxAllocatedStorage", "StorageType",
                   "PerformanceInsightsEnabled", "MonitoringInterval"):
            if node.text and tag not in fields:
                fields[tag] = node.text.strip()
    allocated = int(fields.get("AllocatedStorage") or 0)
    maximum = int(fields.get("MaxAllocatedStorage") or 0)
    return {
        "id": RDS_INSTANCE,
        "engine": fields.get("Engine") or "postgres",
        "engine_version": fields.get("EngineVersion"),
        "class": fields.get("DBInstanceClass"),
        "status": fields.get("DBInstanceStatus"),
        "region": client.region,
        "allocated_bytes": allocated * (1024 ** 3) if allocated else None,
        "max_bytes": maximum * (1024 ** 3) if maximum else None,
        "storage_type": fields.get("StorageType"),
        "performance_insights": fields.get("PerformanceInsightsEnabled", "").lower() == "true",
        "monitoring_interval": int(fields["MonitoringInterval"]) if fields.get("MonitoringInterval") else None,
    }


def _s3_size(access: str, secret: str, now: int) -> dict[str, Any] | None:
    for region in S3_METRIC_REGIONS:
        found = _s3_size_in(access, secret, now, region)
        if found:
            return found
    return None


def _s3_size_in(access: str, secret: str, now: int, region: str) -> dict[str, Any] | None:
    client = AwsQuery(access, secret, region)

    def one(metric: str, storage_type: str) -> list[tuple[int, float]]:
        params = {
            "Namespace": "AWS/S3",
            "MetricName": metric,
            "StartTime": _iso(now - 3 * DAY_SECONDS) or "",
            "EndTime": _iso(now) or "",
            "Period": str(DAY_SECONDS),
            "Statistics.member.1": "Average",
            "Dimensions.member.1.Name": "BucketName",
            "Dimensions.member.1.Value": OBJECT_STORE_BUCKET,
            "Dimensions.member.2.Name": "StorageType",
            "Dimensions.member.2.Value": storage_type,
        }
        xml = client.call("monitoring", f"monitoring.{client.region}.amazonaws.com",
                          "GetMetricStatistics", "2010-08-01", params)
        return _metric_points(xml)

    try:
        sizes = [one("BucketSizeBytes", kind) for kind in _S3_SIZE_TYPES]
        objects = one("NumberOfObjects", "AllStorageTypes")
    except RuntimeError:
        return None
    bytes_total = 0.0
    latest = None
    for series in sizes:
        if series:
            bytes_total += series[-1][1]
            latest = max(latest or 0, series[-1][0])
    if latest is None:
        return None
    return {
        "bucket": OBJECT_STORE_BUCKET,
        "bytes": round(bytes_total),
        "objects": None if not objects else round(objects[-1][1]),
        "as_of": _iso(latest),
    }


def collect_payload(*, now: int | None = None) -> dict[str, Any]:
    access = os.environ.get("AWS_ACCESS_KEY_ID") or ""
    secret = os.environ.get("AWS_SECRET_ACCESS_KEY") or ""
    if not access or not secret:
        return unavailable("no AWS credentials in this environment")
    # The instance lives in us-west-2. A stray AWS_DEFAULT_REGION must not
    # redirect DescribeDBInstances / RDS CloudWatch to another region.
    now = now or int(time.time())
    client = AwsQuery(access, secret, RDS_REGION)

    try:
        instance = _describe_instance(client)
    except RuntimeError as exc:
        return unavailable(str(exc))

    recent_start = now - RECENT_SECONDS
    day_start = now - DAY_SECONDS

    def fetch(metric: str, start: int, period: int) -> tuple[str, int, list[tuple[int, float]]]:
        return metric, period, _get_metric(client, metric, start, now + 60, period)

    series: dict[tuple[str, int], list[tuple[int, float]]] = {}
    try:
        jobs = [(m, recent_start, 60) for m in _METRICS] + [(m, day_start, 300) for m in _METRICS]
        with ThreadPoolExecutor(max_workers=8) as pool:
            for metric, period, points in pool.map(lambda job: fetch(*job), jobs):
                series[(metric, period)] = points
    except RuntimeError as exc:
        return unavailable(str(exc))

    latest = None
    for points in series.values():
        if points:
            latest = max(latest or 0, points[-1][0])
    hour_start, hour_end, hour_basis = last_hour_bounds(now, latest)

    def hour_of(metric: str) -> dict[str, Any]:
        recent = series.get((metric, 60)) or []
        if recent:
            return summarize_rate(recent, hour_start, hour_end, 60)
        return summarize_rate(series.get((metric, 300)) or [], hour_start, hour_end, 300)

    def day_of(metric: str) -> dict[str, Any]:
        return summarize_rate(series.get((metric, 300)) or [], day_start, now, 300)

    hour_write = hour_of("WriteIOPS")
    hour_read = hour_of("ReadIOPS")
    hour_wbytes = hour_of("WriteThroughput")
    hour_rbytes = hour_of("ReadThroughput")
    day_write = day_of("WriteIOPS")
    day_read = day_of("ReadIOPS")
    day_wbytes = day_of("WriteThroughput")
    day_rbytes = day_of("ReadThroughput")
    free = hour_of("FreeStorageSpace")
    if free["mean"] is None:
        free = day_of("FreeStorageSpace")
    cpu = hour_of("CPUUtilization")
    conn = hour_of("DatabaseConnections")

    allocated = instance.get("allocated_bytes")
    free_bytes = None if free["mean"] is None else round(free["mean"])
    used_bytes = None
    if allocated is not None and free_bytes is not None:
        used_bytes = max(0, allocated - free_bytes)

    age = None if latest is None else max(0, now - latest)
    object_store = _s3_size(access, secret, now)

    return {
        "available": True,
        "database": instance,
        "sampled_at": _iso(now),
        "latest_point": _iso(latest),
        "latest_point_age_seconds": age,
        "stale": bool(age is not None and age > STALE_AFTER_SECONDS),
        "last_hour": {
            "basis": hour_basis,
            "empty": hour_write["samples"] == 0 and hour_read["samples"] == 0,
            "start": _iso(hour_start),
            "end": _iso(hour_end),
            "write_iops": hour_write["mean"],
            "read_iops": hour_read["mean"],
            "write_bytes_per_sec": hour_wbytes["mean"],
            "read_bytes_per_sec": hour_rbytes["mean"],
            "samples": max(hour_write["samples"], hour_read["samples"]),
        },
        "last_24h": {
            "write_iops": day_write["mean"],
            "read_iops": day_read["mean"],
            "write_bytes_per_sec": day_wbytes["mean"],
            "read_bytes_per_sec": day_rbytes["mean"],
            "write_ops": None if day_write["total"] is None else round(day_write["total"]),
            "read_ops": None if day_read["total"] is None else round(day_read["total"]),
            "write_bytes": None if day_wbytes["total"] is None else round(day_wbytes["total"]),
            "read_bytes": None if day_rbytes["total"] is None else round(day_rbytes["total"]),
            "samples": max(day_write["samples"], day_read["samples"]),
        },
        "storage": {
            "allocated_bytes": allocated,
            "free_bytes": free_bytes,
            "used_bytes": used_bytes,
            "max_bytes": instance.get("max_bytes"),
        },
        "cpu_percent": cpu["mean"],
        "connections": conn["mean"],
        "object_store": object_store,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(
        prog="python3 -m ui.ops",
        description="Print the rho-dp CloudWatch snapshot as JSON. "
                    "Missing credentials print available:false, exit 1.")
    parser.parse_args(argv)
    payload = collect_payload()
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if payload.get("available") else 1


if __name__ == "__main__":
    raise SystemExit(main())
