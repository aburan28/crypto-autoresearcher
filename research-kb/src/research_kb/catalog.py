from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_version(version INTEGER PRIMARY KEY);
INSERT OR IGNORE INTO schema_version VALUES(1);
CREATE TABLE IF NOT EXISTS documents(
 id TEXT PRIMARY KEY, title TEXT NOT NULL, kind TEXT NOT NULL, active_version TEXT);
CREATE TABLE IF NOT EXISTS versions(
 id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(id),
 content_hash TEXT NOT NULL, metadata TEXT NOT NULL, original_key TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')));
CREATE TABLE IF NOT EXISTS locations(
 repo TEXT NOT NULL, path TEXT NOT NULL, document_id TEXT NOT NULL REFERENCES documents(id),
 version_id TEXT NOT NULL REFERENCES versions(id), git_commit TEXT, present INTEGER NOT NULL DEFAULT 1,
 scan_id TEXT, PRIMARY KEY(repo,path));
CREATE INDEX IF NOT EXISTS locations_doc ON locations(document_id,present,repo);
CREATE TABLE IF NOT EXISTS provenance(
 version_id TEXT NOT NULL REFERENCES versions(id),repo TEXT NOT NULL,path TEXT NOT NULL,git_commit TEXT,
 PRIMARY KEY(version_id,repo,path));
CREATE TABLE IF NOT EXISTS aliases(
 alias TEXT NOT NULL, repo TEXT NOT NULL, path TEXT NOT NULL, document_id TEXT NOT NULL,
 PRIMARY KEY(alias,repo,path));
CREATE INDEX IF NOT EXISTS aliases_lookup ON aliases(alias COLLATE NOCASE);
CREATE TABLE IF NOT EXISTS passages(
 id TEXT PRIMARY KEY, version_id TEXT NOT NULL REFERENCES versions(id), title TEXT NOT NULL,
 text TEXT NOT NULL, section_path TEXT NOT NULL, page_start INTEGER, page_end INTEGER,
 chunk_index INTEGER NOT NULL, parent_id TEXT, is_parent INTEGER NOT NULL, content_hash TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS passages_version ON passages(version_id,chunk_index);
CREATE VIRTUAL TABLE IF NOT EXISTS passage_fts USING fts5(title,text,content='passages',content_rowid='rowid',tokenize='unicode61');
CREATE TRIGGER IF NOT EXISTS passages_ai AFTER INSERT ON passages BEGIN
 INSERT INTO passage_fts(rowid,title,text) VALUES(new.rowid,new.title,new.text); END;
CREATE TRIGGER IF NOT EXISTS passages_ad AFTER DELETE ON passages BEGIN
 INSERT INTO passage_fts(passage_fts,rowid,title,text) VALUES('delete',old.rowid,old.title,old.text); END;
CREATE TABLE IF NOT EXISTS declarations(
 id TEXT PRIMARY KEY, version_id TEXT NOT NULL REFERENCES versions(id), name TEXT NOT NULL,
 module TEXT NOT NULL, kind TEXT NOT NULL, statement TEXT NOT NULL, line_start INTEGER NOT NULL,
 line_end INTEGER NOT NULL, environment TEXT NOT NULL, verification TEXT NOT NULL DEFAULT 'source-only',
 axioms TEXT NOT NULL DEFAULT '[]', receipt TEXT);
CREATE INDEX IF NOT EXISTS declarations_name ON declarations(name,environment);
CREATE VIRTUAL TABLE IF NOT EXISTS declaration_fts USING fts5(name,statement,content='declarations',content_rowid='rowid',tokenize='unicode61');
CREATE TRIGGER IF NOT EXISTS declaration_ai AFTER INSERT ON declarations BEGIN
 INSERT INTO declaration_fts(rowid,name,statement) VALUES(new.rowid,new.name,new.statement); END;
CREATE TRIGGER IF NOT EXISTS declaration_ad AFTER DELETE ON declarations BEGIN
 INSERT INTO declaration_fts(declaration_fts,rowid,name,statement) VALUES('delete',old.rowid,old.name,old.statement); END;
CREATE TABLE IF NOT EXISTS ingestion(
 repo TEXT NOT NULL,path TEXT NOT NULL,status TEXT NOT NULL,reason TEXT,scan_id TEXT,
 updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
 PRIMARY KEY(repo,path));
CREATE TABLE IF NOT EXISTS state(key TEXT PRIMARY KEY,value TEXT NOT NULL);
"""


def digest(value: bytes | str) -> str:
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()


def fts_query(query: str) -> str:
    # Quote tokens: agent text is never accepted as SQL or FTS syntax.
    terms = re.findall(r"[^\W_]+", query, re.UNICODE)[:24]
    return " OR ".join('"' + term.replace('"', '""') + '"' for term in terms)


class Catalog:
    def __init__(self, path: Path):
        self.path = path

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA foreign_keys=ON")
            db.executescript(SCHEMA)

    @contextmanager
    def connect(self, write=False):
        if not self.path.exists():
            raise RuntimeError("knowledge base is not initialized; run research-kb refresh")
        target = str(self.path) if write else self.path.as_uri() + "?mode=ro"
        with sqlite3.connect(target, uri=not write, timeout=30) as db:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("PRAGMA busy_timeout=30000")
            yield db

    def status(self):
        if not self.path.exists():
            return {"initialized": False, "documents": 0, "ready": False}
        with self.connect() as db:
            counts = {
                table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in ("documents", "versions", "locations", "passages", "declarations")
            }
            dispositions = dict(db.execute("SELECT status,COUNT(*) FROM ingestion GROUP BY status"))
            revision = db.execute("SELECT value FROM state WHERE key='revision'").fetchone()
            active = db.execute(
                "SELECT COUNT(DISTINCT document_id) FROM locations WHERE present=1"
            ).fetchone()[0]
        return {
            "initialized": True,
            **counts,
            "active_documents": active,
            "dispositions": dispositions,
            "revision": revision[0] if revision else None,
            "ready": active > 0,
        }

    def record(self, repo, path, status, reason=None, scan_id=None):
        with self.connect(True) as db:
            db.execute(
                """INSERT INTO ingestion(repo,path,status,reason,scan_id) VALUES(?,?,?,?,?)
                ON CONFLICT(repo,path) DO UPDATE SET status=excluded.status,reason=excluded.reason,
                scan_id=excluded.scan_id,updated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now')""",
                (repo, path, status, reason, scan_id),
            )

    def upsert(
        self,
        *,
        document_id,
        version_id,
        title,
        kind,
        content_hash,
        metadata,
        original_key,
        repo,
        path,
        git_commit,
        aliases,
        chunks,
        declarations=(),
        scan_id=None,
    ):
        with self.connect(True) as db:
            db.execute(
                "INSERT INTO documents VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,kind=excluded.kind,active_version=excluded.active_version",
                (document_id, title, kind, version_id),
            )
            db.execute(
                "INSERT OR IGNORE INTO versions(id,document_id,content_hash,metadata,original_key) VALUES(?,?,?,?,?)",
                (version_id, document_id, content_hash, json.dumps(metadata), original_key),
            )
            # Immutable versions are reused, including their passages and compiled receipts.
            if not db.execute("SELECT 1 FROM passages WHERE version_id=? LIMIT 1", (version_id,)).fetchone():
                for c in chunks:
                    db.execute(
                        "INSERT INTO passages VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                        (
                            c.chunk_id,
                            version_id,
                            title,
                            c.text,
                            json.dumps(c.section_path),
                            c.page_start,
                            c.page_end,
                            c.chunk_index,
                            c.parent_id,
                            int(c.is_parent),
                            c.content_hash,
                        ),
                    )
                for d in declarations:
                    db.execute(
                        "INSERT OR IGNORE INTO declarations(id,version_id,name,module,kind,statement,line_start,line_end,environment) VALUES(?,?,?,?,?,?,?,?,?)",
                        (
                            d["id"],
                            version_id,
                            d["name"],
                            d["module"],
                            d["kind"],
                            d["statement"],
                            d["line_start"],
                            d["line_end"],
                            d["environment"],
                        ),
                    )
            db.execute(
                "INSERT INTO locations VALUES(?,?,?,?,?,1,?) ON CONFLICT(repo,path) DO UPDATE SET document_id=excluded.document_id,version_id=excluded.version_id,git_commit=excluded.git_commit,present=1,scan_id=excluded.scan_id",
                (repo, path, document_id, version_id, git_commit, scan_id),
            )
            db.execute(
                "INSERT OR IGNORE INTO provenance VALUES(?,?,?,?)", (version_id, repo, path, git_commit)
            )
            db.execute("DELETE FROM aliases WHERE repo=? AND path=?", (repo, path))
            for alias in set([document_id, *aliases]):
                db.execute("INSERT OR IGNORE INTO aliases VALUES(?,?,?,?)", (alias, repo, path, document_id))
            db.execute(
                "INSERT INTO state VALUES('revision',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (scan_id or version_id,),
            )
        self.record(repo, path, "indexed", scan_id=scan_id)

    def enrich(self, row):
        r = dict(row)
        with self.connect() as db:
            if "source_content_hash" not in r:
                source = db.execute(
                    "SELECT content_hash FROM versions WHERE id=?", (r["version_id"],)
                ).fetchone()
                r["source_content_hash"] = source[0] if source else None
            origins = [
                dict(x)
                for x in db.execute(
                    "SELECT p.repo,p.path,p.git_commit,COALESCE(l.present,0) present FROM provenance p LEFT JOIN locations l ON l.version_id=p.version_id AND l.repo=p.repo AND l.path=p.path WHERE p.version_id=?",
                    (r["version_id"],),
                )
            ]
        meta = json.loads(r.pop("metadata"))
        if "lean_environment" in meta:
            env = dict(meta["lean_environment"])
            pins = env.pop("pins", {})
            env["pin_hashes"] = {name: digest(value) for name, value in pins.items()}
            env["toolchain"] = pins.get("lean-toolchain", "unknown").strip()
            meta["lean_environment"] = env
        result = {
            **r,
            **meta,
            "source_id": r["document_id"],
            "chunk_id": r.get("id"),
            "origins": origins,
            "origin_repositories": sorted({x["repo"] for x in origins}),
            "score": r.get("score", 1.0),
        }
        if "section_path" in result:
            result["section_path"] = json.loads(result["section_path"])
        if "text" in result:
            result["text"] = result["text"][:5000]
        if "axioms" in result:
            result["axioms"] = json.loads(result["axioms"])
        result.pop("original_key", None)
        if result.get("receipt"):
            result["receipt"] = json.loads(result["receipt"])
        return result

    def _where(self, repo=None, kind=None, include_superseded=False):
        clauses = [
            "v.id=d.active_version",
            "EXISTS(SELECT 1 FROM locations l WHERE l.document_id=d.id AND l.version_id=v.id AND l.present=1"
            + (" AND l.repo=?" if repo else "")
            + ")",
        ]
        args = [repo] if repo else []
        if kind:
            clauses.append("d.kind=?")
            args.append(kind)
        if not include_superseded:
            clauses.append("COALESCE(json_extract(v.metadata,'$.superseded'),0)=0")
        return " AND ".join(clauses), args

    def search(self, query, top_k=6, repo=None, kind=None, include_superseded=False):
        query = query.strip()[:4000]
        if not query:
            raise ValueError("query cannot be empty")
        limit = max(1, min(top_k, 10))
        where, args = self._where(repo, kind, include_superseded)
        select = "SELECT p.*,d.id document_id,d.kind,v.metadata,v.content_hash source_content_hash FROM passages p JOIN versions v ON p.version_id=v.id JOIN documents d ON v.document_id=d.id "
        with self.connect() as db:
            exact_ids = [
                r[0]
                for r in db.execute(
                    "SELECT DISTINCT a.document_id FROM aliases a JOIN locations l ON l.repo=a.repo AND l.path=a.path WHERE a.alias=? COLLATE NOCASE AND l.present=1"
                    + (" AND a.repo=?" if repo else ""),
                    [query, *([repo] if repo else [])],
                )
            ]
            if exact_ids:
                placeholders = ",".join("?" for _ in exact_ids)
                rows = db.execute(
                    select
                    + f"WHERE {where} AND p.is_parent=0 AND d.id IN ({placeholders}) ORDER BY p.chunk_index LIMIT ?",
                    [*args, *exact_ids, limit * 3],
                ).fetchall()
            else:
                fts = fts_query(query)
                if not fts:
                    return []
                rows = db.execute(
                    select
                    + "JOIN passage_fts ON passage_fts.rowid=p.rowid "
                    + f"WHERE passage_fts MATCH ? AND {where} AND p.is_parent=0 ORDER BY bm25(passage_fts,3.0,1.0) LIMIT ?",
                    [fts, *args, limit * 6],
                ).fetchall()
        kept, per_source = [], {}
        for row in rows:
            key = row["document_id"]
            if per_source.get(key, 0) >= 2:
                continue
            per_source[key] = per_source.get(key, 0) + 1
            kept.append(self.enrich(row))
            if len(kept) >= limit:
                break
        return kept

    def source(self, source_id):
        with self.connect() as db:
            rows = db.execute(
                "SELECT DISTINCT document_id FROM aliases WHERE alias=? COLLATE NOCASE", (source_id,)
            ).fetchall()
            if len(rows) > 1:
                return {"found": False, "ambiguous": True, "candidates": [r[0] for r in rows]}
            key = rows[0][0] if rows else source_id
            row = db.execute(
                "SELECT d.id document_id,v.id version_id,d.title,d.kind,v.metadata,v.content_hash source_content_hash FROM documents d JOIN versions v ON v.id=d.active_version WHERE d.id=?",
                (key,),
            ).fetchone()
            if row is None:
                return {"found": False, "source_id": source_id}
            sections = db.execute(
                "SELECT section_path FROM passages WHERE version_id=? AND is_parent=0 ORDER BY chunk_index LIMIT 100",
                (row["version_id"],),
            ).fetchall()
        result = self.enrich(row)
        result.update(
            found=True, table_of_contents=list(dict.fromkeys(" / ".join(json.loads(x[0])) for x in sections))
        )
        return result

    def context(self, chunk_id, before=1, after=1):
        with self.connect() as db:
            row = db.execute(
                "SELECT p.*,d.id document_id,d.kind,v.metadata FROM passages p JOIN versions v ON p.version_id=v.id JOIN documents d ON v.document_id=d.id WHERE p.id=?",
                (chunk_id,),
            ).fetchone()
            if row is None:
                return {"found": False, "chunk_id": chunk_id}
            rows = db.execute(
                "SELECT p.*,d.id document_id,d.kind,v.metadata FROM passages p JOIN versions v ON p.version_id=v.id JOIN documents d ON v.document_id=d.id WHERE p.version_id=? AND p.is_parent=0 AND p.chunk_index BETWEEN ? AND ? ORDER BY p.chunk_index",
                (
                    row["version_id"],
                    row["chunk_index"] - max(0, min(before, 3)),
                    row["chunk_index"] + max(0, min(after, 3)),
                ),
            ).fetchall()
        return {"found": True, "chunk": self.enrich(row), "context": [self.enrich(r) for r in rows]}

    def search_theorems(self, query, top_k=6, repo=None, environment=None):
        where, args = self._where(repo, "proof")
        if environment:
            where += " AND t.environment=?"
            args.append(environment)
        base = "SELECT t.*,d.id document_id,t.version_id,v.metadata,v.content_hash source_content_hash FROM declarations t JOIN versions v ON t.version_id=v.id JOIN documents d ON d.id=v.document_id "
        with self.connect() as db:
            rows = db.execute(
                base + f"WHERE {where} AND (t.name=? OR t.id=?) LIMIT ?",
                [*args, query, query, max(1, min(top_k, 10))],
            ).fetchall()
            if not rows and (fts := fts_query(query)):
                rows = db.execute(
                    base
                    + "JOIN declaration_fts ON declaration_fts.rowid=t.rowid "
                    + f"WHERE {where} AND declaration_fts MATCH ? ORDER BY bm25(declaration_fts) LIMIT ?",
                    [*args, fts, max(1, min(top_k, 10))],
                ).fetchall()
        return [self.enrich(r) for r in rows]

    def finish_scan(self, repo, scan_id):
        with self.connect(True) as db:
            # Excluded or failed entries keep their last successful source but are not presented as current.
            db.execute(
                "UPDATE locations SET present=0 WHERE repo=? AND COALESCE(scan_id,'')<>?", (repo, scan_id)
            )
            db.execute(
                "UPDATE ingestion SET status='missing' WHERE repo=? AND COALESCE(scan_id,'')<>?",
                (repo, scan_id),
            )
            db.execute(
                "INSERT INTO state VALUES('revision',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (scan_id,),
            )

    def backup(self, destination: Path):
        destination.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db, sqlite3.connect(destination) as target:
            db.backup(target)
