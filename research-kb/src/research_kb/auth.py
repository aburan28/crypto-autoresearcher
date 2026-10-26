from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import time
from contextvars import ContextVar
from pathlib import Path

from starlette.responses import JSONResponse

principal: ContextVar[str] = ContextVar("research_kb_principal", default="local")


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class BearerAuth:
    """Opaque, revocable per-client tokens. The registry contains hashes only."""

    def __init__(self, app, *, auth_file: Path, per_minute=180, concurrent=16):
        self.app = app
        self.auth_file = auth_file
        self.per_minute = per_minute
        self.capacity = asyncio.Semaphore(concurrent)
        self.buckets = {}
        self.registry()  # HTTP startup fails closed without configured clients.

    def registry(self):
        raw = json.loads(self.auth_file.read_text())
        if raw.get("schema_version") != 1 or not raw.get("tokens"):
            raise ValueError("auth registry must contain at least one client token hash")
        for client, value in raw["tokens"].items():
            if not isinstance(client, str) or not isinstance(value, str) or len(value) != 64:
                raise ValueError("invalid auth registry")
            int(value, 16)
        return raw["tokens"]

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        if scope["path"] == "/healthz" and scope["method"] in {"GET", "HEAD"}:
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))
        auth = headers.get(b"authorization", b"").decode("latin1")
        if not auth.startswith("Bearer ") or len(auth) > 1024:
            return await JSONResponse({"error": "unauthorized"}, 401, headers={"WWW-Authenticate": "Bearer"})(
                scope, receive, send
            )
        try:
            registry = self.registry()
        except (OSError, ValueError, TypeError):
            return await JSONResponse({"error": "authentication unavailable"}, 503)(scope, receive, send)
        received = token_digest(auth[7:])
        client = None
        for name, expected in registry.items():
            if hmac.compare_digest(received, expected):
                client = name
        if client is None:
            return await JSONResponse({"error": "unauthorized"}, 401)(scope, receive, send)
        now = time.monotonic()
        # One fixed-size bucket per registered client, including after rotations.
        self.buckets = {k: v for k, v in self.buckets.items() if k in registry}
        count, start = self.buckets.get(client, (0, now))
        if now - start >= 60:
            count, start = 0, now
        if count >= self.per_minute:
            return await JSONResponse({"error": "rate limit exceeded"}, 429, headers={"Retry-After": "60"})(
                scope, receive, send
            )
        self.buckets[client] = (count + 1, start)
        try:
            length = int(headers.get(b"content-length", b"0"))
        except ValueError:
            return await JSONResponse({"error": "invalid content length"}, 400)(scope, receive, send)
        if length > 128 * 1024:
            return await JSONResponse({"error": "request too large"}, 413)(scope, receive, send)
        try:
            await asyncio.wait_for(self.capacity.acquire(), timeout=0.1)
        except TimeoutError:
            return await JSONResponse({"error": "service busy"}, 429)(scope, receive, send)
        reset = principal.set(client)
        try:
            if scope["method"] in {"POST", "PUT", "PATCH", "DELETE"}:
                body = bytearray()
                while True:
                    try:
                        message = await asyncio.wait_for(receive(), timeout=15)
                    except TimeoutError:
                        return await JSONResponse({"error": "request body timeout"}, 408)(
                            scope, receive, send
                        )
                    if message["type"] == "http.disconnect":
                        return
                    body.extend(message.get("body", b""))
                    if len(body) > 128 * 1024:
                        return await JSONResponse({"error": "request too large"}, 413)(scope, receive, send)
                    if not message.get("more_body", False):
                        break
                delivered = False

                async def bounded_receive():
                    nonlocal delivered
                    if not delivered:
                        delivered = True
                        return {"type": "http.request", "body": bytes(body), "more_body": False}
                    return await receive()

                return await self.app(scope, bounded_receive, send)
            return await self.app(scope, receive, send)
        finally:
            principal.reset(reset)
            self.capacity.release()
