from __future__ import annotations

import fnmatch
import io
import json
import os
import subprocess
import tarfile
import uuid
from contextlib import contextmanager
from pathlib import Path

import yaml

from crypto_kb.chunking import HierarchicalChunker
from crypto_kb.parsing import parse
from research_kb.catalog import digest
from research_kb.lean import discover, environment_info


@contextmanager
def writer_lock(home: Path):
    import fcntl

    home.mkdir(parents=True, exist_ok=True)
    with (home / "writer.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("another ingestion process is active") from exc
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def git_commit(root: Path):
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def source_files(source):
    seen = set()
    for pattern in source.include:
        for path in sorted(source.root.glob(pattern)):
            relative = path.relative_to(source.root).as_posix()
            if relative in seen or not path.is_file() or path.is_symlink():
                continue
            seen.add(relative)
            if not path.resolve().is_relative_to(source.root):
                continue
            if any(fnmatch.fnmatch(relative, p) or Path(relative).match(p) for p in source.exclude):
                continue
            if relative.endswith(".metadata.json"):
                continue
            yield path, relative


def frontmatter(data: bytes):
    text = data.decode("utf-8", errors="replace")
    if text.startswith("---\n"):
        try:
            obj = yaml.safe_load(text.split("---", 2)[1])
            return obj if isinstance(obj, dict) else {}
        except yaml.YAMLError:
            return {}
    if text.lstrip().startswith("{"):
        try:
            obj = json.loads(text)
            return obj if isinstance(obj, dict) else {}
        except ValueError:
            pass
    return {}


def pdf_text(data):
    try:
        import pymupdf
    except ImportError as exc:
        raise RuntimeError("PDF parsing requires the pdf extra: pip install 'research-kb[pdf]'") from exc
    parts, page_map, line = [], {}, 0
    with pymupdf.open(stream=data, filetype="pdf") as doc:
        for number, page in enumerate(doc, 1):
            text = page.get_text("text", sort=True)
            part = f"# PDF page {number}\n\n{text}\n\n"
            for i in range(len(part.splitlines())):
                page_map[line + i] = number
            line += len(part.splitlines())
            parts.append(part)
    text = "".join(parts)
    if len("".join(p.split("\n", 2)[-1] for p in parts).strip()) < 40:
        raise ValueError("PDF has no usable text layer; OCR is required")
    return text, page_map


def ingest_bytes(library, *, repo, path, data, commit=None, environment=None, scan_id=None):
    if len(data) > library.settings.max_file_bytes:
        raise ValueError("source exceeds configured maximum file size")
    suffix = Path(path).suffix.lower()
    sha = digest(data)
    # Deduplicate original PDF bytes globally. Notes retain their own identities.
    document_id = "paper:" + sha if suffix == ".pdf" else "source:" + digest(f"{repo}:{path}")[:32]
    front = frontmatter(data)
    title = str(front.get("title") or Path(path).stem)
    is_paper = (
        suffix in {".pdf", ".tex"}
        or Path(path).name == "paper_fulltext.md"
        or ("sources/originals/" in path and suffix == ".txt")
    )
    kind = "paper" if is_paper else "proof" if suffix == ".lean" else "internal-note"
    text_kind = (
        "original-full-text"
        if is_paper
        else "formal-source"
        if suffix == ".lean"
        else "literature-note"
        if "KN-LIT-" in path
        else "repository-record"
    )
    meta = {
        "text_kind": text_kind,
        "claim_status": "external-source" if kind == "paper" else "published",
        "authority": "primary-source" if kind == "paper" else "internal-analysis",
        "evidence_level": "none",
        "superseded": bool(front.get("superseded_by")),
        "superseded_by": front.get("superseded_by"),
        "topics": front.get("tags") if isinstance(front.get("tags"), list) else [],
        "extraction_quality": "unreviewed",
        "parser_revision": "research-kb-v2",
    }
    aliases = [Path(path).name]
    if isinstance(front.get("id"), str):
        aliases += [front["id"], f"{repo}:{front['id']}"]
    for name, value in (
        (front.get("identifiers") or {}).items() if isinstance(front.get("identifiers"), dict) else []
    ):
        if value:
            aliases.append(str(value))
    env = environment or {"digest": "unknown", "module": Path(path).stem, "pins": {}}
    if suffix == ".lean":
        meta["lean_environment"] = env
    version_id = "version:" + digest(document_id + sha + json.dumps(meta, sort_keys=True, default=str))
    with library.catalog.connect() as db:
        existing = db.execute(
            "SELECT metadata,original_key FROM versions WHERE id=?", (version_id,)
        ).fetchone()
    if existing:
        library.catalog.upsert(
            document_id=document_id,
            version_id=version_id,
            title=title,
            kind=kind,
            content_hash=sha,
            metadata=json.loads(existing["metadata"]),
            original_key=existing["original_key"],
            repo=repo,
            path=path,
            git_commit=commit,
            aliases=aliases,
            chunks=[],
            scan_id=scan_id,
        )
        return document_id
    page_map = None
    if suffix == ".pdf":
        markdown, page_map = pdf_text(data)
        meta["page_numbering"] = "PDF pages starting at 1; printed page labels not inferred"
    elif suffix in {".lean", ".tex"}:
        markdown = data.decode("utf-8", errors="replace")
    else:
        markdown = parse(data, path).markdown
    chunks = HierarchicalChunker().chunk(markdown, version_id, page_map=page_map)
    if not any(not c.is_parent for c in chunks):
        raise ValueError("source produced no searchable passages")
    key = f"objects/sha256/{sha[:2]}/{sha}"
    dest = library.settings.home / key
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        temp = dest.with_suffix(".tmp")
        temp.write_bytes(data)
        os.replace(temp, dest)
    declarations = discover(markdown, version_id, env["module"], env["digest"]) if suffix == ".lean" else []
    library.catalog.upsert(
        document_id=document_id,
        version_id=version_id,
        title=title,
        kind=kind,
        content_hash=sha,
        metadata=meta,
        original_key=key,
        repo=repo,
        path=path,
        git_commit=commit,
        aliases=aliases,
        chunks=chunks,
        declarations=declarations,
        scan_id=scan_id,
    )
    return document_id


def refresh(library):
    report = {"indexed": 0, "failed": 0, "missing_roots": [], "errors": []}
    library.catalog.initialize()
    with writer_lock(library.settings.home):
        for source in library.settings.sources():
            if not source.root.is_dir():
                report["missing_roots"].append({"repo": source.name, "root": str(source.root)})
                continue
            scan_id = uuid.uuid4().hex
            commit = git_commit(source.root)
            for path, relative in source_files(source):
                try:
                    if path.stat().st_size > library.settings.max_file_bytes:
                        raise ValueError("source exceeds configured maximum file size")
                    env = environment_info(path, source.root) if path.suffix == ".lean" else None
                    ingest_bytes(
                        library,
                        repo=source.name,
                        path=relative,
                        data=path.read_bytes(),
                        commit=commit,
                        environment=env,
                        scan_id=scan_id,
                    )
                    report["indexed"] += 1
                except Exception as exc:
                    library.catalog.record(source.name, relative, "failed", str(exc), scan_id)
                    report["failed"] += 1
                    report["errors"].append({"repo": source.name, "path": relative, "error": str(exc)})
            library.catalog.finish_scan(source.name, scan_id)
    return report


def bundle(settings, destination: Path):
    records, objects = [], {}
    for source in settings.sources():
        if not source.root.is_dir():
            raise ValueError(f"source root is unavailable: {source.name}")
        commit = git_commit(source.root)
        for path, relative in source_files(source):
            data = path.read_bytes()
            if len(data) > settings.max_file_bytes:
                raise ValueError(f"source exceeds file limit: {source.name}/{relative}")
            sha = digest(data)
            objects.setdefault(sha, data)
            records.append(
                {
                    "repo": source.name,
                    "path": relative,
                    "sha256": sha,
                    "commit": commit,
                    "environment": environment_info(path, source.root) if path.suffix == ".lean" else None,
                }
            )
    total = sum(len(b) for b in objects.values())
    if total > settings.max_bundle_bytes:
        raise ValueError("bundle is too large; select fewer source patterns or increase the bundle limit")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(destination, "w:gz") as archive:
        manifest = json.dumps({"schema": 1, "sources": records}).encode()
        for name, data in [("manifest.json", manifest), *(("objects/" + h, b) for h, b in objects.items())]:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
    return {"sources": len(records), "unique_objects": len(objects), "bytes": destination.stat().st_size}


def import_bundle(library, filename: Path):
    library.catalog.initialize()
    count = 0
    with writer_lock(library.settings.home), tarfile.open(filename, "r:gz") as archive:
        members = archive.getmembers()
        if len({m.name for m in members}) != len(members):
            raise ValueError("bundle contains duplicate entries")
        if any(not m.isfile() or m.name.startswith("/") or ".." in Path(m.name).parts for m in members):
            raise ValueError("bundle contains unsafe entries")
        if sum(m.size for m in members) > library.settings.max_bundle_bytes:
            raise ValueError("bundle exceeds uncompressed size limit")
        manifest = json.load(archive.extractfile("manifest.json"))
        if manifest.get("schema") != 1:
            raise ValueError("unsupported bundle schema")
        validated = []
        for record in manifest["sources"]:
            relative = Path(record["path"])
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("unsafe source path in manifest")
            member = archive.getmember("objects/" + record["sha256"])
            if member.size > library.settings.max_file_bytes:
                raise ValueError("bundle source exceeds file size limit")
            data = archive.extractfile(member).read()
            if digest(data) != record["sha256"]:
                raise ValueError("source hash does not match bundle manifest")
            validated.append((record, data))
        scan_id = uuid.uuid4().hex
        for record, data in validated:
            ingest_bytes(
                library,
                repo=record["repo"],
                path=record["path"],
                data=data,
                commit=record.get("commit"),
                environment=record.get("environment"),
                scan_id=scan_id,
            )
            count += 1
    return {"indexed": count, "bundle_sha256": digest(filename.read_bytes())}
