"""Authenticated local UI around the existing ADK Runner and agent tree.

Credentials never enter Runner.run_async. Stock ADK development/debug/session
endpoints are deliberately not mounted on this authenticated application.
"""
from __future__ import annotations

import os
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"
os.environ["OTEL_PROPAGATORS"] = "baggage"

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
import secrets
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from company_system.security.secret_boundary import (
    host_token, install_log_redaction, redact, reject_secret_text, remember_secret,
)

COOKIE = "companyai_local_session"
TTL = 3600


class StrictBody(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LoginBody(StrictBody):
    username: str = Field(min_length=1, max_length=128)
    password: SecretStr = Field(min_length=1, max_length=1024)


class ChatBody(StrictBody):
    message: str = Field(min_length=1, max_length=8000)


class CredentialBody(StrictBody):
    operation: str
    username: str = Field(min_length=1, max_length=128)
    password: SecretStr = SecretStr("")
    role: str = ""
    employee_id: int | None = None


@dataclass
class BrowserSession:
    token: str = field(repr=False)
    user_id: str
    session_id: str
    expires: float
    lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)


def create_app(port: int = 8000):
    install_log_redaction()
    from google.adk.runners import Runner
    from google.adk.agents.run_config import RunConfig
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    from company_system.agent import root_agent
    from company_system.tools import auth_tools, hr_tools
    from mcp_server.session_store import (
        SessionToolContext, context_from_session_token, create_mcp_session, revoke_mcp_session,
    )

    sessions: dict[str, BrowserSession] = {}
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, app_name="companyai_local", session_service=session_service)

    async def discard(key):
        item = sessions.pop(key, None)
        if item:
            await asyncio.to_thread(revoke_mcp_session, item.token)
            await session_service.delete_session(app_name="companyai_local", user_id=item.user_id, session_id=item.session_id)

    @asynccontextmanager
    async def lifespan(app):
        yield
        for key in list(sessions):
            await discard(key)
        await runner.close()

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    # Host-owned objects for offline verification, never HTTP serialization.
    app.state.browser_sessions = sessions
    app.state.runner = runner

    @app.exception_handler(RequestValidationError)
    async def invalid_body(request, exc):
        return JSONResponse({"detail": "Invalid request fields."}, status_code=400)

    @app.middleware("http")
    async def boundary(request: Request, call_next):
        expected_host = f"127.0.0.1:{port}"
        if request.client is None or request.client.host not in {"127.0.0.1", "::1"}:
            return JSONResponse({"detail": "Local access only."}, status_code=403)
        if request.headers.get("host") != expected_host:
            return JSONResponse({"detail": "Invalid host."}, status_code=403)
        if request.url.query:
            return JSONResponse({"detail": "Query parameters are not accepted."}, status_code=400)
        if request.method not in {"GET", "POST"}:
            return JSONResponse({"detail": "Method not allowed."}, status_code=405)
        if request.method == "POST":
            if request.headers.get("origin") != f"http://{expected_host}":
                return JSONResponse({"detail": "Same-origin request required."}, status_code=403)
            if request.headers.get("content-type", "").split(";")[0] != "application/json":
                return JSONResponse({"detail": "JSON required."}, status_code=415)
            size = 0
            chunks = []
            async for chunk in request.stream():
                size += len(chunk)
                if size > 16384:
                    return JSONResponse({"detail": "Request too large."}, status_code=413)
                chunks.append(chunk)
            request._body = b"".join(chunks)
        try:
            response = await call_next(request)
        except Exception as exc:
            from company_system.security.quota import record_quota
            record_quota(exc)
            quota_error = "quota" in str(exc).lower() or "429" in str(exc)
            import traceback
            app.state.last_error = {"type": type(exc).__name__, "frames": [
                {"function": frame.name, "line": frame.lineno, "file": Path(frame.filename).name}
                for frame in traceback.extract_tb(exc.__traceback__)[-6:]]}
            # No body, exception text or traceback is returned/logged.
            response = JSONResponse({"detail": "Provider temporarily unavailable." if quota_error else "Request failed."},
                                    status_code=503 if quota_error else 500)
        response.headers.update({
            "Cache-Control": "no-store", "Pragma": "no-cache",
            "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer",
            "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
        })
        return response

    async def authenticated(request):
        key = request.cookies.get(COOKIE, "")
        item = sessions.get(key)
        if not item or item.expires <= time.monotonic():
            await discard(key)
            raise HTTPException(401, "Authentication required.")
        context, error = await asyncio.to_thread(context_from_session_token, item.token)
        if error:
            await discard(key)
            raise HTTPException(401, "Authentication required.")
        return item, context

    @app.get("/", response_class=HTMLResponse)
    async def index():
        return (Path(__file__).with_name("local_ui.html")).read_text(encoding="utf-8")

    @app.get("/app.js")
    async def javascript():
        from fastapi.responses import Response
        return Response(Path(__file__).with_name("local_ui.js").read_text(encoding="utf-8"), media_type="text/javascript")

    @app.post("/api/login")
    async def login(body: LoginBody, request: Request):
        for key, item in list(sessions.items()):
            if item.expires <= time.monotonic():
                await discard(key)
        if len(sessions) >= 128:
            raise HTTPException(503, "Local session capacity reached.")
        password = body.password.get_secret_value()
        context = SessionToolContext({})
        result = await asyncio.to_thread(auth_tools.login, body.username, password, context)
        if result.get("status") != "success":
            raise HTTPException(401, "Invalid username or password.")
        remember_secret(password)
        await discard(request.cookies.get(COOKIE, ""))
        token = await asyncio.to_thread(create_mcp_session, context.state)
        remember_secret(token)
        try:
            user_id = secrets.token_urlsafe(24)
            session = await session_service.create_session(app_name="companyai_local", user_id=user_id, state=context.state)
            key = secrets.token_urlsafe(32)
            remember_secret(key)
            sessions[key] = BrowserSession(token, user_id, session.id, time.monotonic() + TTL)
        except BaseException:
            await asyncio.to_thread(revoke_mcp_session, token)
            raise
        response = JSONResponse({"status": "success", "identity": result})
        response.set_cookie(COOKIE, key, httponly=True, samesite="strict", max_age=TTL, path="/")
        return response

    @app.get("/api/me")
    async def me(request: Request):
        _, context = await authenticated(request)
        return {"status": "success", "identity": context.state}

    @app.post("/api/logout")
    async def logout(request: Request):
        await discard(request.cookies.get(COOKIE, ""))
        response = JSONResponse({"status": "success"})
        response.delete_cookie(COOKIE, path="/")
        return response

    @app.post("/api/credentials")
    async def credentials(body: CredentialBody, request: Request):
        _, context = await authenticated(request)
        if context.state.get("auth_role") != "hr":
            raise HTTPException(403, "Forbidden.")
        password = body.password.get_secret_value()
        if len(password) > 1024:
            raise HTTPException(400, "Invalid credential fields.")
        remember_secret(password)
        if body.operation == "create" and body.employee_id is not None:
            result = await asyncio.to_thread(hr_tools.create_user_credentials, body.employee_id, body.username, password, body.role, context)
        elif body.operation == "update":
            result = await asyncio.to_thread(hr_tools.update_user_credentials, body.username, password, body.role, context)
        elif body.operation == "delete":
            result = await asyncio.to_thread(hr_tools.delete_user_credentials, body.username, context)
        else:
            raise HTTPException(400, "Invalid credential operation.")
        import json
        return JSONResponse(json.loads(redact(json.dumps(result))))

    @app.post("/api/chat")
    async def chat(body: ChatBody, request: Request):
        item, context = await authenticated(request)
        try:
            reject_secret_text(body.message)
            # Conservative credential-intent screening before ADK history exists.
            import re
            if re.search(r"(?i)\b(?:password|passwd|pwd|secret|bearer|api.key|access.token|refresh.token)\b", body.message):
                raise ValueError()
        except ValueError:
            raise HTTPException(400, "Sensitive input rejected. Use the secure credential form.")
        async with item.lock:
            texts = []
            with host_token(item.token):
                async with asyncio.timeout(300):
                    async for event in runner.run_async(
                        user_id=item.user_id, session_id=item.session_id,
                        new_message=types.Content(role="user", parts=[types.Part.from_text(text=body.message)]),
                        state_delta=context.state,
                        run_config=RunConfig(max_llm_calls=12),
                    ):
                        if event.is_final_response() and event.content:
                            texts.extend(part.text for part in event.content.parts or [] if part.text)
            completed = await session_service.get_session(app_name="companyai_local", user_id=item.user_id,
                                                          session_id=item.session_id)
            if completed and completed.state.get("routing_error"):
                raise HTTPException(503, "Routing model temporarily unavailable. Check provider quota.")
            return {"answer": redact("\n".join(texts))}

    return app


def main():
    import argparse
    import uvicorn
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Invalid local port.")
    uvicorn.run(create_app(args.port), host="127.0.0.1", port=args.port,
                access_log=False, log_level="warning", proxy_headers=False)


if __name__ == "__main__":
    main()
