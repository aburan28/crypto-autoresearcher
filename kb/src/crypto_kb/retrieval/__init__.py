"""Retrieval service. Deliberately independent of the MCP transport."""

from crypto_kb.retrieval.hybrid import KnowledgeRetriever, build_retriever

__all__ = ["KnowledgeRetriever", "build_retriever"]
