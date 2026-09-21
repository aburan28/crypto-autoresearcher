"""Logging, metrics, and the query log.

The query log is the artifact that makes retrieval improvable: without a
record of what was asked, what came back, and how long it took, tuning is
guesswork. It records query text, filters, returned chunk ids and scores, and
the calling client -- never response bodies, which would duplicate the corpus
into a log file.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import structlog

_configured = False


def configure_logging(level: str = "info") -> None:
    global _configured
    if _configured:
        return
    import logging

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer(colors=False),
        ],
        cache_logger_on_first_use=True,
    )
    _configured = True


def get_logger(name: str = "crypto_kb"):
    configure_logging()
    return structlog.get_logger(name)


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------


class Metrics:
    """Prometheus counters/histograms, created once per process."""

    _instance: "Metrics | None" = None

    def __init__(self) -> None:
        from prometheus_client import Counter, Gauge, Histogram

        self.documents_ingested = Counter(
            "crypto_kb_documents_ingested_total", "Documents that reached INDEXED", ["source_type"]
        )
        self.documents_skipped = Counter(
            "crypto_kb_documents_skipped_total", "Documents skipped on an unchanged fingerprint"
        )
        self.documents_failed = Counter(
            "crypto_kb_documents_failed_total", "Documents that failed ingestion", ["stage"]
        )
        self.chunks_indexed = Counter(
            "crypto_kb_chunks_indexed_total", "Chunks written to the index"
        )
        self.queries = Counter("crypto_kb_queries_total", "Retrieval queries", ["client", "tool"])
        self.query_latency = Histogram(
            "crypto_kb_query_latency_seconds", "Retrieval latency", ["tool"]
        )
        self.empty_results = Counter(
            "crypto_kb_empty_results_total", "Queries that returned nothing"
        )
        self.queue_age = Gauge(
            "crypto_kb_queue_oldest_message_seconds", "Age of the oldest SQS message"
        )

    @classmethod
    def instance(cls) -> "Metrics":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def start_metrics_server(port: int) -> None:  # pragma: no cover - side effect only
    from prometheus_client import start_http_server

    start_http_server(port)


# --------------------------------------------------------------------------
# Query log
# --------------------------------------------------------------------------


class QueryLog:
    """Append-only JSONL query log. A missing path disables it."""

    def __init__(self, path: str | Path | None) -> None:
        self.path = Path(path) if path else None
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def new_query_id() -> str:
        return uuid.uuid4().hex

    def record(
        self,
        *,
        query_id: str,
        query: str,
        filters: dict[str, Any],
        retrieved_chunk_ids: list[str],
        scores: list[float],
        client: str | None,
        agent: str | None,
        task_id: str | None,
        latency_ms: int,
        tool: str = "search_knowledge",
        notes: list[str] | None = None,
    ) -> None:
        if not self.path:
            return
        entry = {
            "query_id": query_id,
            "tool": tool,
            "query": query,
            "filters": filters,
            "retrieved_chunk_ids": retrieved_chunk_ids,
            "scores": [round(s, 6) for s in scores],
            "client": client,
            "agent": agent,
            "task_id": task_id,
            "latency_ms": latency_ms,
            "notes": notes or [],
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
