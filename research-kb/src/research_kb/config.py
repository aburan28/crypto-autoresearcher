from __future__ import annotations

import os
import re
import tomllib
from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Source(BaseModel):
    name: str
    root: Path
    include: list[str] = Field(
        default_factory=lambda: ["**/*.md", "**/*.txt", "**/*.pdf", "**/*.lean", "**/*.yaml"]
    )
    exclude: list[str] = Field(
        default_factory=lambda: [
            ".git/**",
            ".lake/**",
            ".venv/**",
            "node_modules/**",
            "target/**",
            "build/**",
        ]
    )

    @field_validator("name")
    @classmethod
    def valid_name(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", value):
            raise ValueError("source name must contain only letters, numbers, hyphens and underscores")
        return value

    @field_validator("include", "exclude")
    @classmethod
    def relative_patterns(cls, values: list[str]) -> list[str]:
        if any(Path(v).is_absolute() or ".." in Path(v).parts for v in values):
            raise ValueError("source patterns must stay within the registered root")
        return values


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RESEARCH_KB_", extra="forbid")

    home: Path = Field(default_factory=lambda: Path.home() / ".local/share/research-kb")
    config: Path = Field(
        default_factory=lambda: (
            Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "research-kb/sources.toml"
        )
    )
    qdrant_url: str | None = None
    collection: str = "research_kb_v1"
    qdrant_api_key: str | None = None
    dense_backend: str = "hashing"
    dense_model: str = "hashing-ngram-v1"
    dense_dimension: int = 512
    auth_file: Path | None = None
    host: str = "127.0.0.1"
    port: int = 8080
    max_file_bytes: int = 64 * 1024 * 1024
    max_bundle_bytes: int = 512 * 1024 * 1024
    requests_per_minute: int = 180
    max_concurrent_requests: int = 16
    public_url: str | None = None
    allowed_hosts: list[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1", "[::1]"])

    def sources(self) -> list[Source]:
        if not self.config.exists():
            return []
        with self.config.open("rb") as handle:
            raw = tomllib.load(handle)
        sources = []
        for item in raw.get("sources", []):
            source = Source.model_validate(item)
            source.root = source.root.expanduser()
            if not source.root.is_absolute():
                source.root = self.config.parent / source.root
            source.root = source.root.resolve()
            sources.append(source)
        names = [s.name for s in sources]
        if len(names) != len(set(names)):
            raise ValueError("source names must be unique")
        return sources

    @property
    def database(self) -> Path:
        return self.home.expanduser().resolve() / "catalog.sqlite"
