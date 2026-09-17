"""Windowing for the database-load panel.

The LAST HOUR = 0 bug is a wall-clock window over a series whose newest
sample is older than an hour. That is a missing sample, not a stopped
database. These tests pin the fallback: show the hour ending at the latest
point, and never invent a rate of zero for an empty window.
"""

from __future__ import annotations

import io
import sys
import urllib.error
from pathlib import Path
from xml.etree.ElementTree import Element

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from ui.ops import (  # noqa: E402
    RDS_REGION, S3_METRIC_REGIONS, collect_payload, last_hour_bounds,
    summarize_rate, unavailable, window_mean,
)


def test_last_hour_uses_wall_clock_when_the_latest_point_is_fresh():
    now = 1_700_000_000
    start, end, basis = last_hour_bounds(now, now - 90)
    assert basis == "wall"
    assert end == now and start == now - 3600


def test_last_hour_falls_back_to_the_hour_ending_at_a_stale_point():
    now = 1_700_000_000
    latest = now - 3 * 3600
    start, end, basis = last_hour_bounds(now, latest)
    assert basis == "latest_sample"
    assert end == latest and start == latest - 3600


def test_last_hour_with_no_samples_stays_on_the_wall_clock():
    now = 1_700_000_000
    start, end, basis = last_hour_bounds(now, None)
    assert basis == "wall"
    assert (start, end) == (now - 3600, now)


def test_empty_window_is_none_not_zero():
    samples = [(100, 12.0), (160, 18.0)]
    mean, n = window_mean(samples, 1000, 2000)
    assert mean is None and n == 0
    summary = summarize_rate(samples, 1000, 2000, 60)
    assert summary["mean"] is None and summary["total"] is None and summary["samples"] == 0


def test_stale_hour_summary_uses_the_hour_that_has_points():
    now = 1_700_000_000
    latest = now - 3 * 3600
    start, end, basis = last_hour_bounds(now, latest)
    assert basis == "latest_sample"
    samples = [(latest - 120, 1700.0), (latest - 60, 1800.0), (latest, 1900.0)]
    summary = summarize_rate(samples, start, end, 60)
    assert summary["samples"] == 3
    assert summary["mean"] == pytest.approx(1800.0)
    wall = summarize_rate(samples, now - 3600, now, 60)
    assert wall["mean"] is None and wall["total"] is None


def test_integral_is_rate_times_period():
    samples = [(100, 10.0), (160, 20.0)]
    summary = summarize_rate(samples, 0, 200, 60)
    assert summary["mean"] == 15.0
    assert summary["total"] == 10.0 * 60 + 20.0 * 60


def test_collect_payload_does_not_invent_rates_without_credentials(monkeypatch):
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
    payload = collect_payload()
    assert payload == unavailable("no AWS credentials in this environment")
    assert "write_iops" not in payload
    assert "last_hour" not in payload


def test_rds_queries_stay_in_us_west_2_even_if_the_shell_region_differs(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIATEST")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "secret")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")
    seen: list[str] = []

    def fake_call(self, service, host, action, version, params):  # noqa: ARG001
        seen.append(host)
        raise RuntimeError("stop")

    monkeypatch.setattr("ui.ops.AwsQuery.call", fake_call)
    payload = collect_payload()
    assert payload["available"] is False
    assert seen == [f"rds.{RDS_REGION}.amazonaws.com"]
    assert "eu-west-1" not in seen[0]


def test_describe_does_not_publish_the_hostname(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIATEST")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "secret")
    describe = Element("DescribeDBInstancesResponse")
    # A real RDS response carries the hostname. The dashboard must not.
    for tag, text in (
        ("Engine", "postgres"),
        ("EngineVersion", "16.13"),
        ("DBInstanceClass", "db.r7g.xlarge"),
        ("DBInstanceStatus", "available"),
        ("AllocatedStorage", "400"),
        ("StorageType", "gp3"),
        ("Address", "rho-dp.internal.us-west-2.rds.amazonaws.com"),
        ("Endpoint", "rho-dp.internal.us-west-2.rds.amazonaws.com"),
    ):
        node = Element(tag)
        node.text = text
        describe.append(node)

    def fake_call(self, service, host, action, version, params):  # noqa: ARG001
        if action == "DescribeDBInstances":
            return describe
        if params.get("Namespace") == "AWS/S3":
            raise RuntimeError("s3-stop")
        return Element("GetMetricStatisticsResponse")

    monkeypatch.setattr("ui.ops.AwsQuery.call", fake_call)
    payload = collect_payload()
    assert payload["available"] is True
    assert payload["database"]["id"] == "rho-dp"
    assert payload["database"]["class"] == "db.r7g.xlarge"
    assert payload["database"]["allocated_bytes"] == 400 * (1024 ** 3)
    blob = str(payload)
    assert "rds.amazonaws.com" not in blob
    assert "internal" not in blob
    assert "Address" not in blob


def test_s3_storage_metrics_try_the_instance_region_then_us_east_1(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIATEST")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "secret")
    s3_hosts: list[str] = []
    rds_hosts: list[str] = []

    def fake_call(self, service, host, action, version, params):  # noqa: ARG001
        if action == "DescribeDBInstances":
            rds_hosts.append(host)
            return Element("DescribeDBInstancesResponse")
        if params.get("Namespace") == "AWS/S3":
            s3_hosts.append(host)
            raise RuntimeError("s3-stop")
        rds_hosts.append(host)
        return Element("GetMetricStatisticsResponse")

    monkeypatch.setattr("ui.ops.AwsQuery.call", fake_call)
    payload = collect_payload()
    assert payload["available"] is True
    assert payload["object_store"] is None
    assert s3_hosts
    expected = [f"monitoring.{region}.amazonaws.com" for region in S3_METRIC_REGIONS]
    assert s3_hosts[0] == expected[0]
    assert set(s3_hosts) <= set(expected)
    assert all(RDS_REGION in host for host in rds_hosts)
    dumped = str(payload).lower()
    assert "endpoint" not in dumped
    assert ".rds.amazonaws.com" not in dumped


def test_aws_http_error_body_is_not_published(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIATEST")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "secret")
    xml = (
        b"<ErrorResponse><Error><Code>AccessDenied</Code>"
        b"<Message>User: arn:aws:iam::123456789012:user/pages-deploy "
        b"is not authorized to perform: rds:DescribeDBInstances on "
        b"arn:aws:rds:us-west-2:123456789012:db:rho-dp</Message>"
        b"</Error></ErrorResponse>"
    )

    def fake_urlopen(req, timeout=None):  # noqa: ARG001
        raise urllib.error.HTTPError(
            "https://rds.us-west-2.amazonaws.com/",
            403,
            "Forbidden",
            hdrs=None,
            fp=io.BytesIO(xml),
        )

    monkeypatch.setattr("ui.ops.urllib.request.urlopen", fake_urlopen)
    payload = collect_payload()
    assert payload["available"] is False
    blob = str(payload)
    assert "arn:aws:iam" not in blob
    assert "123456789012" not in blob
    assert "pages-deploy" not in blob
    assert "AccessDenied" not in blob
    assert payload["reason"] == "DescribeDBInstances failed (403)"


def test_hour_falls_back_to_five_minute_when_one_minute_misses_the_window(monkeypatch):
    now = 1_700_000_000
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIATEST")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "secret")
    monkeypatch.setattr("ui.ops._describe_instance", lambda client: {  # noqa: ARG005
        "id": "rho-dp",
        "engine": "postgres",
        "engine_version": "16.13",
        "class": "db.r7g.xlarge",
        "status": "available",
        "region": RDS_REGION,
        "allocated_bytes": 400 * (1024 ** 3),
        "max_bytes": None,
        "storage_type": "gp3",
        "performance_insights": False,
        "monitoring_interval": None,
    })
    monkeypatch.setattr("ui.ops._s3_size", lambda *args, **kwargs: None)

    def fake_get_metric(client, metric, start, end, period):  # noqa: ARG001
        if metric == "WriteIOPS" and period == 60:
            return [(now - 2 * 3600, 10.0)]
        if metric == "WriteIOPS" and period == 300:
            return [(now - 2 * 3600, 10.0), (now - 300, 42.0)]
        if metric == "ReadIOPS" and period == 300:
            return [(now - 300, 1.0)]
        return []

    monkeypatch.setattr("ui.ops._get_metric", fake_get_metric)
    payload = collect_payload(now=now)
    assert payload["available"] is True
    assert payload["last_hour"]["basis"] == "wall"
    assert payload["last_hour"]["empty"] is False
    assert payload["last_hour"]["write_iops"] == 42.0
    assert payload["last_hour"]["read_iops"] == 1.0


def test_hour_prefers_in_window_one_minute_samples(monkeypatch):
    now = 1_700_000_000
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIATEST")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "secret")
    monkeypatch.setattr("ui.ops._describe_instance", lambda client: {  # noqa: ARG005
        "id": "rho-dp", "engine": "postgres", "engine_version": None,
        "class": None, "status": None, "region": RDS_REGION,
        "allocated_bytes": None, "max_bytes": None, "storage_type": None,
        "performance_insights": False, "monitoring_interval": None,
    })
    monkeypatch.setattr("ui.ops._s3_size", lambda *args, **kwargs: None)

    def fake_get_metric(client, metric, start, end, period):  # noqa: ARG001
        if metric == "WriteIOPS" and period == 60:
            return [(now - 60, 99.0)]
        if metric == "WriteIOPS" and period == 300:
            return [(now - 300, 42.0)]
        return []

    monkeypatch.setattr("ui.ops._get_metric", fake_get_metric)
    payload = collect_payload(now=now)
    assert payload["last_hour"]["write_iops"] == 99.0
    assert payload["last_hour"]["empty"] is False
