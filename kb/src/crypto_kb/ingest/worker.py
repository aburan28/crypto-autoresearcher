"""SQS ingestion worker.

S3 -> EventBridge -> SQS -> this worker, rather than S3 -> Lambda. Parsing a
mathematical PDF with Docling is minutes of CPU and hundreds of megabytes of
model; a queue with a long visibility timeout and a dead-letter queue is the
right shape for that, and a 15-minute function ceiling is not.

Delivery is at-least-once, so correctness rests on the pipeline being
idempotent (deterministic point ids, fingerprint skip) rather than on the
queue never redelivering. A message is deleted only after Qdrant *and* the
manifest have been updated; anything else is left for redelivery, and after
``max_receive_count`` attempts the queue's redrive policy moves it to the DLQ.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable

from crypto_kb.models import IngestState
from crypto_kb.observability import Metrics, get_logger
from crypto_kb.ingest.pipeline import IngestionPipeline, IngestResult

log = get_logger("crypto_kb.worker")

_CREATED = ("ObjectCreated", "Object Created")
_REMOVED = ("ObjectRemoved", "Object Deleted")


@dataclass(frozen=True)
class S3Event:
    bucket: str
    key: str
    kind: str  # "created" | "removed"
    version_id: str | None = None
    etag: str | None = None


def parse_event(body: str | dict[str, Any]) -> list[S3Event]:
    """Extract S3 events from a message body.

    Handles the two shapes that reach this queue: EventBridge's
    ``detail-type``/``detail`` envelope, and a raw S3 notification's
    ``Records`` list. An SNS envelope around either is unwrapped.
    """
    payload = json.loads(body) if isinstance(body, str) else body
    if not isinstance(payload, dict):
        return []

    if payload.get("Type") == "Notification" and "Message" in payload:
        return parse_event(payload["Message"])

    events: list[S3Event] = []

    detail_type = payload.get("detail-type") or payload.get("detailType")
    if detail_type and "detail" in payload:
        detail = payload["detail"]
        kind = _classify(detail_type)
        if kind:
            events.append(
                S3Event(
                    bucket=detail.get("bucket", {}).get("name", ""),
                    key=_unquote(detail.get("object", {}).get("key", "")),
                    kind=kind,
                    version_id=detail.get("object", {}).get("version-id"),
                    etag=detail.get("object", {}).get("etag"),
                )
            )
        return events

    for record in payload.get("Records", []):
        kind = _classify(record.get("eventName", ""))
        if not kind:
            continue
        s3 = record.get("s3", {})
        events.append(
            S3Event(
                bucket=s3.get("bucket", {}).get("name", ""),
                key=_unquote(s3.get("object", {}).get("key", "")),
                kind=kind,
                version_id=s3.get("object", {}).get("versionId"),
                etag=s3.get("object", {}).get("eTag"),
            )
        )
    return events


def _classify(name: str) -> str | None:
    if any(name.startswith(prefix) or name == prefix for prefix in _CREATED):
        return "created"
    if any(name.startswith(prefix) or name == prefix for prefix in _REMOVED):
        return "removed"
    return None


def _unquote(key: str) -> str:
    from urllib.parse import unquote_plus

    return unquote_plus(key)


class IngestionWorker:
    def __init__(
        self,
        pipeline: IngestionPipeline,
        queue_url: str | None = None,
        sqs_client: Any | None = None,
        settings=None,
    ) -> None:
        self.pipeline = pipeline
        self.settings = settings or pipeline.settings
        self.queue_url = queue_url or self.settings.sqs_queue_url
        self._sqs = sqs_client

    @property
    def sqs(self) -> Any:
        if self._sqs is None:
            import boto3

            session = boto3.Session(
                profile_name=self.settings.aws_profile, region_name=self.settings.aws_region
            )
            self._sqs = session.client("sqs")
        return self._sqs

    # -- event handling ----------------------------------------------------

    def handle_event(self, event: S3Event) -> IngestResult:
        """Apply one S3 event. Bucket and prefix are validated first."""
        expected_bucket = self.settings.s3_bucket
        if event.bucket and expected_bucket and event.bucket != expected_bucket:
            return IngestResult(
                None, event.key, IngestState.REJECTED, skipped=True,
                reason=f"event for unexpected bucket {event.bucket!r}",
            )

        ingestible, reason = self.pipeline.should_ingest(event.key)
        if not ingestible:
            return IngestResult(None, event.key, IngestState.REJECTED, skipped=True, reason=reason)

        if event.kind == "removed":
            source_id = self.pipeline.source_id_for_key(event.key)
            if source_id is None:
                return IngestResult(
                    None, event.key, IngestState.REJECTED, skipped=True,
                    reason="delete event for an unknown key",
                )
            return self.pipeline.delete_source(source_id)

        return self.pipeline.ingest_key(event.key)

    def handle_message(self, body: str | dict[str, Any]) -> list[IngestResult]:
        results: list[IngestResult] = []
        for event in parse_event(body):
            result = self.handle_event(event)
            results.append(result)
            _count(result)
        return results

    # -- polling loop ------------------------------------------------------

    def poll_once(self) -> list[IngestResult]:
        """Receive one batch, process it, delete only what fully succeeded."""
        if not self.queue_url:
            raise ValueError("no SQS queue configured (set CRYPTO_KB_SQS_QUEUE_URL)")

        response = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=self.settings.sqs_max_messages,
            WaitTimeSeconds=self.settings.sqs_wait_seconds,
            VisibilityTimeout=self.settings.sqs_visibility_timeout,
            AttributeNames=["ApproximateReceiveCount", "SentTimestamp"],
        )
        results: list[IngestResult] = []
        for message in response.get("Messages", []):
            try:
                message_results = self.handle_message(message["Body"])
            except Exception as exc:  # noqa: BLE001 - redelivery is the recovery path
                log.error("message_failed", error=str(exc), message_id=message.get("MessageId"))
                continue

            results.extend(message_results)

            # Only FAILED is retried. REJECTED is a permanent verdict about
            # the document -- a missing sidecar, invalid JSON, an unsupported
            # format -- and redelivering it five times before parking it in
            # the DLQ neither fixes it nor makes it more visible. The fix is
            # to correct the object, which produces a fresh event. Rejections
            # are logged at warning level and recorded on the manifest so they
            # surface in `crypto-kb doctor`.
            retryable = [r for r in message_results if r.state == IngestState.FAILED]
            rejected = [r for r in message_results if r.state == IngestState.REJECTED and not r.skipped]
            for result in rejected:
                log.warning("permanently_rejected", key=result.key, reason=result.reason)

            if not retryable:
                self.sqs.delete_message(
                    QueueUrl=self.queue_url, ReceiptHandle=message["ReceiptHandle"]
                )
            else:
                # Left visible on purpose: the redrive policy counts the
                # attempts and moves it to the DLQ after max_receive_count.
                log.warning(
                    "message_retained_for_retry",
                    message_id=message.get("MessageId"),
                    receive_count=message.get("Attributes", {}).get("ApproximateReceiveCount"),
                    failures=[r.reason for r in retryable],
                )
        return results

    def run(self, max_batches: int | None = None) -> list[IngestResult]:  # pragma: no cover - loop
        results: list[IngestResult] = []
        batch = 0
        while max_batches is None or batch < max_batches:
            results.extend(self.poll_once())
            batch += 1
        return results


def _count(result: IngestResult) -> None:
    try:
        metrics = Metrics.instance()
    except Exception:  # pragma: no cover - prometheus optional at runtime
        return
    if result.state == IngestState.INDEXED and not result.skipped:
        metrics.chunks_indexed.inc(result.chunk_count)
    elif result.skipped:
        metrics.documents_skipped.inc()
    elif result.state in {IngestState.FAILED, IngestState.REJECTED}:
        metrics.documents_failed.labels(stage=result.state.value).inc()


def process_bodies(worker: IngestionWorker, bodies: Iterable[str | dict[str, Any]]) -> list[IngestResult]:
    """Process message bodies without a queue. Used by tests and replay."""
    results: list[IngestResult] = []
    for body in bodies:
        results.extend(worker.handle_message(body))
    return results
