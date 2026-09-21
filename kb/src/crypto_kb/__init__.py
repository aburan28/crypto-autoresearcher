"""Crypto knowledge base: S3 -> Docling -> Qdrant -> MCP.

The corpus in object storage is the source of truth. Everything this package
builds -- normalized markdown, chunks, vectors, the Qdrant collection -- is
derived and can be deleted and rebuilt from the sources without loss.
"""

__version__ = "0.1.0"

# Version tags that participate in the document fingerprint. Bumping any of
# them invalidates every affected document on the next ingest pass, which is
# the intended way to force a re-index after a behaviour change.
CHUNKER_VERSION = "crypto-hierarchical-v1"
SCHEMA_VERSION = 1

__all__ = ["__version__", "CHUNKER_VERSION", "SCHEMA_VERSION"]
