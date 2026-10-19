"""The generated root module of the Lean workspace.

Lake builds `CryptoResearch.lean` and whatever it imports.  A theorem file the
formalizer stages is a new file nobody imports, so without regenerating the
root it is never built, never audited, and silently absent from the evidence —
the proof artifact would report a PASS for a build that never touched it.

The root is derived from the directory, so it is gitignored and rebuilt on
demand (like `knowledge/INDEX.md`).  Deriving it also means staging a file
requires no edit to a shared file, which is what many concurrent worktrees
need.
"""
from __future__ import annotations

from pathlib import Path

DEFAULT_LIBRARY = "CryptoResearch"

_HEADER = """\
/-
GENERATED FILE -- do not edit, and do not commit.

Rebuild with `python3 tools/rebuild_formal_root.py`.  It lists every module
under {library}/ so that `lake build` compiles them and AxiomAudit.lean can
see their theorems.
-/
"""


def modules(workspace: Path, library: str = DEFAULT_LIBRARY) -> list[str]:
    """Every Lean module under the library directory, in import order."""

    root = workspace / library
    if not root.is_dir():
        return []
    return sorted(
        ".".join((library, *path.relative_to(root).with_suffix("").parts))
        for path in root.rglob("*.lean")
        if path.is_file()
    )


def render_root(workspace: Path, library: str = DEFAULT_LIBRARY) -> str:
    found = modules(workspace, library)
    body = (
        "\n" + "".join(f"import {module}\n" for module in found)
        if found
        else "\n-- no theorem modules staged yet\n"
    )
    return _HEADER.format(library=library) + body


def rebuild_root(workspace: Path, library: str = DEFAULT_LIBRARY) -> Path | None:
    """Write the root module if it is missing or stale; return it if it changed.

    A no-op when the workspace has no library directory and no root, so calling
    this against a workspace that is not laid out this way costs nothing.
    """

    target = workspace / f"{library}.lean"
    if not (workspace / library).is_dir() and not target.is_file():
        return None
    wanted = render_root(workspace, library)
    if target.is_file() and target.read_text(encoding="utf-8") == wanted:
        return None
    target.write_text(wanted, encoding="utf-8")
    return target


__all__ = ["DEFAULT_LIBRARY", "modules", "rebuild_root", "render_root"]
