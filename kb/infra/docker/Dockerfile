# Image for both roles. The command decides which one runs:
#   ingestion worker: crypto-kb worker
#   MCP service:      crypto-kb mcp
#
# They share an image but must not share an IAM role -- see infra/terraform.
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

# --------------------------------------------------------------------------
# Retrieval service: no Docling, no torch. This image serves queries; it has
# no reason to carry a PDF conversion stack, and a smaller image is a smaller
# attack surface on the one component agents talk to.
# --------------------------------------------------------------------------
FROM base AS mcp
RUN pip install ".[index,mcp]"
RUN useradd --create-home --uid 10001 crypto-kb
USER crypto-kb
EXPOSE 8080
CMD ["crypto-kb", "mcp"]

# --------------------------------------------------------------------------
# Ingestion worker: needs Docling for PDFs and boto3 for S3/SQS.
# --------------------------------------------------------------------------
FROM base AS worker
RUN pip install ".[index,aws,docling]"
RUN useradd --create-home --uid 10001 crypto-kb
USER crypto-kb
CMD ["crypto-kb", "worker"]
