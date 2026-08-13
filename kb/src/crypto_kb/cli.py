"""`crypto-kb` command line.

Everything the pipeline can do, driven from a terminal, against the same code
paths the MCP server uses.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from crypto_kb.config import get_settings
from crypto_kb.models import ClaimStatus, IngestState, SearchFilters, SourceType
from crypto_kb.observability import configure_logging

app = typer.Typer(
    add_completion=False,
    help="S3 -> Docling -> Qdrant -> MCP knowledge base for the ECDLP research corpus.",
    no_args_is_help=True,
)


def _settings(**overrides):
    settings = get_settings()
    if overrides:
        settings = settings.model_copy(update={k: v for k, v in overrides.items() if v is not None})
    configure_logging(settings.log_level)
    return settings


# --------------------------------------------------------------------------
# Corpus
# --------------------------------------------------------------------------


@app.command("stage-repo")
def stage_repo(
    repo_root: Path = typer.Argument(Path("."), help="Repository to stage into the corpus."),
    limit_per_rule: Optional[int] = typer.Option(None, help="Cap documents per staging rule."),
    eval_slice: bool = typer.Option(
        False, "--eval-slice", help="Stage only the frozen evaluation slice (corpus_manifest.txt)."
    ),
) -> None:
    """Copy this repository's records into the corpus layout with derived sidecars.

    Sidecar fields come from recorded frontmatter and record values only; none
    are model-generated. Re-running is safe -- identical content produces
    identical objects.
    """
    from crypto_kb.ingest.repo_corpus import RULES, stage_repository
    from crypto_kb.storage import build_store

    settings = _settings()
    store = build_store(settings)
    if eval_slice:
        if limit_per_rule is not None:
            typer.echo("--limit-per-rule truncates the slice the labels were written against")
            raise typer.Exit(2)
        # Through build_eval_corpus, not eval_rules(): the globs are only the
        # recipe the manifest was frozen from, so staging by glob here would
        # measure `make evaluate` against a different corpus than the suite.
        from crypto_kb.eval.corpus import build_eval_corpus

        staged = build_eval_corpus(repo_root.resolve(), store)
    else:
        staged = stage_repository(
            repo_root.resolve(), store, rules=RULES, limit_per_rule=limit_per_rule
        )
    by_type: dict[str, int] = {}
    for document in staged:
        key = document.metadata["source_type"]
        by_type[key] = by_type.get(key, 0) + 1
    typer.echo(f"staged {len(staged)} documents into {settings.source_prefix()}")
    for source_type, count in sorted(by_type.items()):
        typer.echo(f"  {source_type:<16} {count}")


# --------------------------------------------------------------------------
# Ingestion
# --------------------------------------------------------------------------


@app.command()
def ingest(
    target: str = typer.Argument("", help="Object key, s3:// URI, or prefix. Empty means the whole corpus."),
    force: bool = typer.Option(False, help="Re-ingest even when the fingerprint is unchanged."),
    limit: Optional[int] = typer.Option(None, help="Stop after this many documents."),
    reconcile: bool = typer.Option(True, help="Delete indexed sources whose object is gone."),
) -> None:
    """Ingest a document, a prefix, or the whole corpus. Idempotent."""
    from crypto_kb.ingest import build_pipeline
    from crypto_kb.ingest.backfill import backfill

    settings = _settings()
    pipeline = build_pipeline(settings)
    key = _normalize_target(target, settings)

    if key and not key.endswith("/") and pipeline.store.exists(key):
        result = pipeline.ingest_key(key, force=force)
        typer.echo(f"{result.state.value}: {result.source_id or key}")
        if result.reason:
            typer.echo(f"  reason: {result.reason}")
        for warning in result.warnings:
            typer.echo(f"  warning: {warning}")
        raise typer.Exit(0 if result.ok or result.skipped else 1)

    report = backfill(pipeline, prefix=key or None, force=force, limit=limit, reconcile=reconcile)
    summary = report.summary()
    typer.echo(json.dumps(summary, indent=2))
    for result in report.rejected + report.failed:
        typer.echo(f"  {result.state.value}: {result.key} -- {result.reason}")
    raise typer.Exit(1 if report.failed else 0)


@app.command()
def delete(source_id: str = typer.Argument(..., help="Source id to remove from the index.")) -> None:
    """Delete a source's points and tombstone its manifest. The object is untouched."""
    from crypto_kb.ingest import build_pipeline

    pipeline = build_pipeline(_settings())
    pipeline.delete_source(source_id)
    typer.echo(f"deleted {source_id} from the index")


@app.command()
def reindex(
    yes: bool = typer.Option(False, "--yes", help="Confirm dropping and rebuilding the collection."),
) -> None:
    """Drop the collection and rebuild it from the corpus.

    The corpus is the source of truth, so this loses nothing -- but it does
    re-embed everything, and it recomputes the sparse statistics that drift as
    documents arrive one at a time.
    """
    from crypto_kb.embeddings.sparse import STATS_KEY, SparseStats
    from crypto_kb.ingest import build_pipeline
    from crypto_kb.ingest.backfill import backfill

    settings = _settings()
    if not yes:
        typer.echo(f"this drops collection {settings.collection!r} and rebuilds it; pass --yes")
        raise typer.Exit(1)

    pipeline = build_pipeline(settings)
    pipeline.index.drop_collection()
    pipeline.store.delete(STATS_KEY)
    pipeline.sparse.stats = SparseStats()
    for manifest in list(pipeline.manifests.list()):
        manifest.status = IngestState.DISCOVERED
        manifest.point_ids = []
        pipeline.manifests.put(manifest)

    report = backfill(pipeline, force=True)
    typer.echo(json.dumps(report.summary(), indent=2))


# --------------------------------------------------------------------------
# Retrieval
# --------------------------------------------------------------------------


@app.command()
def search(
    query: str = typer.Argument(..., help="Natural-language query or exact identifier."),
    top_k: int = typer.Option(6, "--top-k", "-k"),
    source_type: Optional[str] = typer.Option(None, help="paper | experiment | ledger | ..."),
    field_type: Optional[str] = typer.Option(None),
    primitive: Optional[str] = typer.Option(None),
    claim_status: Optional[str] = typer.Option(None),
    include_superseded: bool = typer.Option(False),
    mode: str = typer.Option("hybrid", help="hybrid | dense | sparse"),
    as_json: bool = typer.Option(False, "--json"),
    quiet: bool = typer.Option(False, "--quiet", help="Omit passage text."),
) -> None:
    """Search the knowledge base."""
    from crypto_kb.retrieval import build_retriever
    from crypto_kb.retrieval.formatting import render

    settings = _settings()
    retriever = build_retriever(settings)
    filters = SearchFilters(
        source_type=[SourceType(source_type)] if source_type else None,
        field_type=[field_type] if field_type else None,
        primitive=[primitive] if primitive else None,
        claim_status=[ClaimStatus(claim_status)] if claim_status else None,
        superseded=None if include_superseded else False,
    )
    response = retriever.search(query=query, top_k=top_k, filters=filters, client="cli", mode=mode)
    if as_json:
        typer.echo(json.dumps(response.model_dump(mode="json"), indent=2))
    else:
        typer.echo(render(response, show_text=not quiet))


@app.command()
def context(
    chunk_id: str = typer.Argument(...),
    before: int = typer.Option(1),
    after: int = typer.Option(1),
) -> None:
    """Show the passages around a chunk."""
    from crypto_kb.retrieval import build_retriever

    response = build_retriever(_settings()).get_context(chunk_id, before=before, after=after)
    typer.echo(json.dumps(response.model_dump(mode="json"), indent=2))


@app.command()
def source(source_id: str = typer.Argument(...)) -> None:
    """Show a source's metadata, sections, and summary."""
    from crypto_kb.retrieval import build_retriever

    document = build_retriever(_settings()).get_source(source_id)
    if document is None:
        typer.echo(f"{source_id}: not indexed")
        raise typer.Exit(1)
    typer.echo(json.dumps(document.model_dump(mode="json"), indent=2))


@app.command()
def related(source_id: str = typer.Argument(...), top_k: int = typer.Option(5, "--top-k", "-k")) -> None:
    """Find sources covering similar ground."""
    from crypto_kb.retrieval import build_retriever
    from crypto_kb.retrieval.formatting import render

    response = build_retriever(_settings()).find_related(source_id, top_k=top_k)
    typer.echo(render(response, show_text=False))


# --------------------------------------------------------------------------
# Operations
# --------------------------------------------------------------------------


@app.command()
def status() -> None:
    """Corpus, manifest, and index state."""
    from crypto_kb.ingest import build_pipeline

    settings = _settings()
    pipeline = build_pipeline(settings)
    manifests = list(pipeline.manifests.list())
    by_status: dict[str, int] = {}
    warnings = 0
    for manifest in manifests:
        by_status[manifest.status.value] = by_status.get(manifest.status.value, 0) + 1
        warnings += len(manifest.warnings)

    typer.echo(f"store            {settings.store_backend} ({settings.local_root if settings.store_backend == 'local' else settings.s3_bucket})")
    typer.echo(f"collection       {settings.collection} @ {settings.qdrant_url}")
    typer.echo(f"dense model      {pipeline.dense.model_id}")
    typer.echo(f"sparse model     {pipeline.sparse.model_id}")
    typer.echo(f"manifests        {len(manifests)}")
    for state, count in sorted(by_status.items()):
        typer.echo(f"  {state:<12} {count}")
    typer.echo(f"parse warnings   {warnings}")
    try:
        exists = pipeline.index.exists()
        typer.echo(f"indexed points   {pipeline.index.count() if exists else 0}")
    except Exception as exc:  # noqa: BLE001 - status must not fail on a down index
        exists = False
        typer.echo(f"indexed points   unavailable ({exc})")

    if settings.qdrant_url == ":memory:":
        typer.echo("")
        typer.echo(
            "note: CRYPTO_KB_QDRANT_URL is ':memory:'. The index is embedded in this\n"
            "      process and does not survive it, so manifests can say INDEXED while\n"
            "      a later `crypto-kb search` finds nothing. Run `make qdrant-up` and\n"
            "      set CRYPTO_KB_QDRANT_URL=http://localhost:6333 for a persistent index."
        )
    elif manifests and not exists:
        typer.echo("")
        typer.echo("PROBLEM: manifests exist but the collection does not; run `crypto-kb ingest`")


@app.command()
def doctor() -> None:
    """Check that the configured pieces are reachable and consistent."""
    from crypto_kb.index.schema import describe
    from crypto_kb.ingest import build_pipeline

    settings = _settings()
    problems: list[str] = []
    pipeline = build_pipeline(settings)

    sources = sum(1 for _ in pipeline.store.list(settings.source_prefix()))
    typer.echo(f"corpus objects      {sources}")
    if sources == 0:
        problems.append(f"no objects under {settings.source_prefix()} -- run `crypto-kb stage-repo`")

    try:
        exists = pipeline.index.exists()
        typer.echo(f"qdrant              reachable (collection exists: {exists})")
        if exists:
            pipeline.index.ensure_collection()  # raises on a dimension mismatch
    except Exception as exc:  # noqa: BLE001
        problems.append(f"qdrant unreachable or inconsistent: {exc}")

    typer.echo(f"schema              {json.dumps(describe(pipeline.dense.dimension))}")

    failed = [m for m in pipeline.manifests.list() if m.status == IngestState.FAILED]
    if failed:
        problems.append(f"{len(failed)} documents in FAILED state")
        for manifest in failed[:10]:
            typer.echo(f"  FAILED {manifest.source_id}: {manifest.error}")

    flagged = [m for m in pipeline.manifests.list() if m.warnings]
    if flagged:
        typer.echo(f"documents with parse warnings: {len(flagged)} (inspect high-value papers by hand)")
        for manifest in flagged[:10]:
            typer.echo(f"  {manifest.source_id}: {manifest.warnings[0]}")

    if problems:
        typer.echo("")
        for problem in problems:
            typer.echo(f"PROBLEM: {problem}")
        raise typer.Exit(1)
    typer.echo("\nall checks passed")


@app.command()
def worker(
    batches: Optional[int] = typer.Option(None, help="Stop after this many receive batches."),
) -> None:  # pragma: no cover - long-running
    """Consume S3 events from SQS and keep the index in step with the corpus."""
    from crypto_kb.ingest import build_pipeline
    from crypto_kb.ingest.worker import IngestionWorker

    settings = _settings()
    if settings.metrics_port:
        from crypto_kb.observability import start_metrics_server

        start_metrics_server(settings.metrics_port)
    worker = IngestionWorker(build_pipeline(settings), settings=settings)
    worker.run(max_batches=batches)


@app.command("eval-manifest")
def eval_manifest(
    repo_root: Path = typer.Argument(Path("."), help="Repository the slice is drawn from."),
    write: bool = typer.Option(False, "--write", help="Freeze today's candidates as the slice."),
) -> None:
    """Show, or deliberately regenerate, the frozen evaluation corpus slice.

    Without ``--write`` this reports how the frozen slice differs from what the
    globs match today -- which is the drift that would otherwise move a
    measured baseline without any retrieval code changing.
    """
    from crypto_kb.eval.corpus import (
        MANIFEST_PATH,
        discover_eval_paths,
        load_manifest,
        write_manifest,
    )

    root = repo_root.resolve()
    if write:
        paths = write_manifest(root)
        typer.echo(f"froze {len(paths)} documents into {MANIFEST_PATH}")
        typer.echo("re-check tests/retrieval_eval/questions.jsonl labels, then re-measure BASELINE")
        return

    frozen = load_manifest()
    candidates = discover_eval_paths(root)
    added = sorted(set(candidates) - set(frozen))
    removed = sorted(set(frozen) - set(candidates))
    typer.echo(f"{len(frozen)} documents frozen in {MANIFEST_PATH}")
    typer.echo(f"{len(candidates)} match the globs today")
    typer.echo(f"  +{len(added)} not in the slice, -{len(removed)} in the slice but gone")
    for path in added[:10]:
        typer.echo(f"  + {path}")
    for path in removed[:10]:
        typer.echo(f"  - {path}")
    if removed:
        raise typer.Exit(1)


@app.command()
def evaluate(
    questions: Path = typer.Option(
        Path("tests/retrieval_eval/questions.jsonl"), help="Evaluation question set."
    ),
    modes: str = typer.Option("hybrid,dense,sparse", help="Comma-separated retrieval modes."),
    as_json: bool = typer.Option(False, "--json"),
    gates: bool = typer.Option(True, help="Exit non-zero when a gate fails."),
) -> None:
    """Run the retrieval evaluation harness and report metrics against the gates."""
    from crypto_kb.eval.harness import evaluate_modes, format_report, load_questions
    from crypto_kb.retrieval import build_retriever

    settings = _settings()
    retriever = build_retriever(settings)
    question_list = load_questions(questions)
    reports = evaluate_modes(retriever, question_list, [m.strip() for m in modes.split(",") if m.strip()])

    if as_json:
        typer.echo(json.dumps({m: r.to_dict() for m, r in reports.items()}, indent=2))
    else:
        typer.echo(format_report(reports))

    primary = reports.get("hybrid") or next(iter(reports.values()))
    if gates and primary.failed_gates:
        raise typer.Exit(1)


@app.command("mcp")
def mcp_server() -> None:  # pragma: no cover - process entry point
    """Run the FastMCP server on stdio."""
    from crypto_kb.mcp.server import main as mcp_main

    mcp_main()


def _normalize_target(target: str, settings) -> str:
    if not target:
        return ""
    if target.startswith("s3://"):
        without_scheme = target[len("s3://") :]
        _, _, key = without_scheme.partition("/")
        return key
    return target


def main() -> None:
    """Entry point. Turns the expected operational failures into messages.

    A traceback is the right output for a bug and the wrong one for "you have
    not ingested anything yet" -- which, with the embedded default index, is
    the most common thing a new user hits.
    """
    from crypto_kb.index.qdrant import CollectionMissing, QdrantUnavailable
    from crypto_kb.metadata import MetadataError

    try:
        app()
    except (CollectionMissing, QdrantUnavailable, MetadataError) as exc:
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise SystemExit(2) from None


if __name__ == "__main__":  # pragma: no cover
    main()
