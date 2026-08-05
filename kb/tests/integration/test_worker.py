"""Event-driven ingestion: event parsing, deletion, and at-least-once safety."""

from __future__ import annotations

import json

import pytest

from crypto_kb.ingest.worker import IngestionWorker, parse_event, process_bodies
from crypto_kb.models import IngestState


def eventbridge(key: str, kind: str = "Object Created", bucket: str = "crypto-autoresearcher"):
    return json.dumps(
        {
            "detail-type": kind,
            "detail": {
                "bucket": {"name": bucket},
                "object": {"key": key, "etag": "abc", "version-id": "v1"},
            },
        }
    )


def s3_notification(key: str, event_name: str = "ObjectCreated:Put"):
    return json.dumps(
        {
            "Records": [
                {
                    "eventName": event_name,
                    "s3": {
                        "bucket": {"name": "crypto-autoresearcher"},
                        "object": {"key": key, "eTag": "abc", "versionId": "v1"},
                    },
                }
            ]
        }
    )


# -- event parsing ---------------------------------------------------------


def test_parses_eventbridge_envelope():
    events = parse_event(eventbridge("knowledge/source/papers/a.md"))
    assert len(events) == 1
    assert events[0].key == "knowledge/source/papers/a.md"
    assert events[0].kind == "created"


def test_parses_raw_s3_notification():
    events = parse_event(s3_notification("knowledge/source/papers/a.md"))
    assert events[0].kind == "created"


def test_parses_removal_events():
    assert parse_event(eventbridge("k/a.md", kind="Object Deleted"))[0].kind == "removed"
    assert parse_event(s3_notification("k/a.md", "ObjectRemoved:Delete"))[0].kind == "removed"


def test_unwraps_an_sns_envelope():
    wrapped = json.dumps({"Type": "Notification", "Message": eventbridge("k/a.md")})
    assert parse_event(wrapped)[0].key == "k/a.md"


def test_url_encoded_keys_are_decoded():
    events = parse_event(eventbridge("knowledge/source/papers/a+b%3Ac.md"))
    assert events[0].key == "knowledge/source/papers/a b:c.md"


def test_unrelated_event_types_are_ignored():
    assert parse_event(eventbridge("k/a.md", kind="Object Restore Completed")) == []


# -- handling --------------------------------------------------------------


@pytest.fixture
def worker(pipeline):
    return IngestionWorker(pipeline, queue_url="https://example/queue")


def test_event_for_another_bucket_is_ignored(worker):
    results = worker.handle_message(eventbridge("knowledge/source/papers/a.md", bucket="other"))
    assert results[0].skipped
    assert "unexpected bucket" in results[0].reason


def test_event_outside_the_source_prefix_is_ignored(worker):
    results = worker.handle_message(eventbridge("knowledge/normalized/markdown/a.md"))
    assert results[0].skipped


def test_metadata_sidecar_events_are_ignored(worker):
    results = worker.handle_message(eventbridge("knowledge/source/papers/a.md.metadata.json"))
    assert results[0].skipped
    assert results[0].reason == "metadata sidecar"


def test_create_event_indexes_the_document(worker, store, sample_document, sample_metadata):
    key = "knowledge/source/papers/a.md"
    store.put(key, sample_document.encode("utf-8"))
    store.put(key + ".metadata.json", json.dumps(sample_metadata).encode("utf-8"))

    results = worker.handle_message(eventbridge(key))

    assert results[0].state == IngestState.INDEXED
    assert worker.pipeline.index.by_source(sample_metadata["source_id"])


def test_redelivery_creates_no_duplicates(worker, store, sample_document, sample_metadata):
    key = "knowledge/source/papers/a.md"
    store.put(key, sample_document.encode("utf-8"))
    store.put(key + ".metadata.json", json.dumps(sample_metadata).encode("utf-8"))

    body = eventbridge(key)
    process_bodies(worker, [body, body, body])

    assert worker.pipeline.index.count() == len(
        worker.pipeline.manifests.get(sample_metadata["source_id"]).point_ids
    )


def test_delete_event_removes_the_document(worker, store, sample_document, sample_metadata):
    key = "knowledge/source/papers/a.md"
    store.put(key, sample_document.encode("utf-8"))
    store.put(key + ".metadata.json", json.dumps(sample_metadata).encode("utf-8"))
    worker.handle_message(eventbridge(key))

    store.delete(key)
    store.delete(key + ".metadata.json")
    results = worker.handle_message(eventbridge(key, kind="Object Deleted"))

    assert results[0].state == IngestState.DELETED
    assert worker.pipeline.index.by_source(sample_metadata["source_id"]) == []
    assert worker.pipeline.manifests.get(sample_metadata["source_id"]).status == IngestState.DELETED


def test_delete_event_for_an_unknown_key_is_skipped(worker):
    results = worker.handle_message(eventbridge("knowledge/source/papers/never.md", kind="Object Deleted"))
    assert results[0].skipped


# -- queue semantics -------------------------------------------------------


class FakeSqs:
    """Records deletes so the test can assert what was acknowledged."""

    def __init__(self, messages):
        self.messages = messages
        self.deleted: list[str] = []

    def receive_message(self, **kwargs):
        return {"Messages": self.messages}

    def delete_message(self, QueueUrl, ReceiptHandle):  # noqa: N803 - boto3 signature
        self.deleted.append(ReceiptHandle)


def test_successful_message_is_acknowledged(pipeline, store, sample_document, sample_metadata):
    key = "knowledge/source/papers/a.md"
    store.put(key, sample_document.encode("utf-8"))
    store.put(key + ".metadata.json", json.dumps(sample_metadata).encode("utf-8"))

    sqs = FakeSqs([{"MessageId": "1", "ReceiptHandle": "rh-1", "Body": eventbridge(key)}])
    worker = IngestionWorker(pipeline, queue_url="q", sqs_client=sqs)
    worker.poll_once()

    assert sqs.deleted == ["rh-1"]


def test_permanent_rejection_is_acknowledged_not_retried(pipeline, store):
    """A bad sidecar cannot be fixed by redelivering the message."""
    key = "knowledge/source/papers/a.md"
    store.put(key, b"# body")
    store.put(key + ".metadata.json", b"{ broken json")

    sqs = FakeSqs([{"MessageId": "1", "ReceiptHandle": "rh-1", "Body": eventbridge(key)}])
    worker = IngestionWorker(pipeline, queue_url="q", sqs_client=sqs)
    results = worker.poll_once()

    assert results[0].state == IngestState.REJECTED
    assert sqs.deleted == ["rh-1"], "a permanent rejection was queued for retry"


def test_transient_failure_is_left_for_redelivery(pipeline, store, sample_document, sample_metadata, monkeypatch):
    """An infrastructure error must not be acknowledged -- the work is unfinished."""
    key = "knowledge/source/papers/a.md"
    store.put(key, sample_document.encode("utf-8"))
    store.put(key + ".metadata.json", json.dumps(sample_metadata).encode("utf-8"))

    def explode(*args, **kwargs):
        raise ConnectionError("qdrant is unreachable")

    monkeypatch.setattr(pipeline.index, "upsert", explode)

    sqs = FakeSqs([{"MessageId": "1", "ReceiptHandle": "rh-1", "Body": eventbridge(key)}])
    worker = IngestionWorker(pipeline, queue_url="q", sqs_client=sqs)
    results = worker.poll_once()

    assert results[0].state == IngestState.FAILED
    assert sqs.deleted == [], "a failed message was acknowledged and its work lost"
    assert pipeline.manifests.get(sample_metadata["source_id"]).status == IngestState.FAILED


def test_polling_without_a_queue_is_an_error(pipeline):
    worker = IngestionWorker(pipeline, queue_url=None)
    with pytest.raises(ValueError, match="no SQS queue configured"):
        worker.poll_once()
