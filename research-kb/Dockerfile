# syntax=docker/dockerfile:1
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.lock ./
# Optional secret is the combined CA bundle in a managed development environment.
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    python -m pip install -r requirements.lock
COPY pyproject.toml UPSTREAM.md ./
COPY src/ ./src/
RUN python -m pip install --no-deps --no-build-isolation .
RUN groupadd --gid 10001 research-kb && useradd --uid 10001 --gid 10001 --create-home research-kb
USER 10001:10001
ENV RESEARCH_KB_HOME=/data RESEARCH_KB_HOST=0.0.0.0 RESEARCH_KB_PORT=8080
EXPOSE 8080
ENTRYPOINT ["research-kb"]
CMD ["serve"]
