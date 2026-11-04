"""Offline dummy-secret tests. All database writes use an isolated copy."""
from __future__ import annotations

import asyncio
import io
from functools import partial
from contextlib import closing
import json
import logging
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaluations.runtime_isolation import prepare_isolated_runtime
prepare_isolated_runtime("secret_boundary")

from fastapi.testclient import TestClient
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from company_system.local_web import create_app, COOKIE
from company_system.database.db import get_connection
from company_system.security.passwords import hash_password
from company_system.security.secret_boundary import host_token, remember_secret, install_log_redaction, reject_secret_text, guard_model_request
from company_system.mcp.secure_toolset import HostAuthenticatedTool, CREDENTIAL_TOOLS
from company_system.routing.semantic_router_agent import RoutingDecision

DUMMY = "BoundaryDummy-Pass-93!"
USER = "boundary_dummy"
salt, hashed = hash_password(DUMMY)
with closing(get_connection()) as conn, conn:
    conn.execute("UPDATE users SET username=?, password_salt=?, password_hash=? WHERE employee_id=5",
                 (USER, salt, hashed))



class SecretBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = TestClient(self.app, base_url="http://127.0.0.1:8000", client=("127.0.0.1", 50000))
        self.client.__enter__()
        self.headers = {"Origin": "http://127.0.0.1:8000"}

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def login(self, username=USER, password=DUMMY):
        result = self.client.post("/api/login", json={"username": username, "password": password}, headers=self.headers)
        self.assertEqual(result.status_code, 200, result.text)
        return result

    def test_unauthorized_and_development_endpoints(self):
        self.assertEqual(self.client.get("/api/me").status_code, 401)
        with patch.object(self.app.state.runner, "run_async") as run:
            self.assertEqual(self.client.post("/api/chat", json={"message": "Show my profile"}, headers=self.headers).status_code, 401)
            run.assert_not_called()
        for endpoint in ("/list-apps", "/dev-ui/", "/debug/trace/x", "/apps/company_system/users/x/sessions", "/docs", "/openapi.json"):
            self.assertEqual(self.client.get(endpoint).status_code, 404)

    def test_origin_host_and_validation_do_not_echo_secrets(self):
        body = {"username": USER, "password": DUMMY}
        self.assertEqual(self.client.post("/api/login", json=body).status_code, 403)
        self.assertEqual(self.client.post("/api/login", json=body, headers={"Origin": "https://evil.invalid"}).status_code, 403)
        self.assertEqual(self.client.get("/", headers={"Host": "evil.invalid"}).status_code, 403)
        response = self.client.post("/api/login", json={**body, "extra": DUMMY}, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertNotIn(DUMMY, response.text)
        self.assertNotIn("access-control-allow-origin", response.headers)

    def test_generic_login_and_cookie_lifecycle(self):
        failures = []
        for username in (USER, "nonexistent_boundary_account"):
            result = self.client.post("/api/login", json={"username": username, "password": "WrongDummy-73!"}, headers=self.headers)
            failures.append((result.status_code, result.json()))
        self.assertEqual(failures[0], failures[1])
        response = self.login()
        cookie = response.headers["set-cookie"].lower()
        self.assertIn("httponly", cookie)
        self.assertIn("samesite=strict", cookie)
        self.assertNotIn(DUMMY, response.text)
        item = next(iter(self.app.state.browser_sessions.values()))
        self.assertNotIn(item.token, response.text)
        self.assertEqual(self.client.get("/api/me").status_code, 200)
        self.client.post("/api/logout", json={}, headers=self.headers)
        self.assertEqual(self.client.get("/api/me").status_code, 401)

    def test_secret_chat_rejected_before_runner_and_history(self):
        self.login()
        with patch.object(self.app.state.runner, "run_async") as run:
            for text in (DUMMY, "my password: AnotherDummyPass!", "api_key=DummyKey-29", "Bearer DummyAccess-39"):
                response = self.client.post("/api/chat", json={"message": text}, headers=self.headers)
                self.assertEqual(response.status_code, 400, response.text)
                self.assertNotIn(text, response.text)
            run.assert_not_called()

    def test_real_adk_request_and_history_contain_no_credentials(self):
        self.login()
        item = next(iter(self.app.state.browser_sessions.values()))
        captured = []
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
        with patch.dict(os.environ, {"OTEL_SDK_DISABLED": "false"}):
            provider = TracerProvider(shutdown_on_exit=False)
        exporter = InMemorySpanExporter()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("companyai_dummy_secret_test")

        async def fake_generation(model, llm_request, stream=False):
            captured.append(llm_request.model_dump_json(exclude_none=True))
            if len(captured) == 1:
                part = types.Part(function_call=types.FunctionCall(name="get_login_identity", args={}))
            else:
                part = types.Part.from_text(text="Offline request boundary verified.")
            yield LlmResponse(content=types.Content(role="model", parts=[part]))

        decision = RoutingDecision(route="auth_agent", confidence=0.99, reason="Identity request")
        with patch("company_system.routing.semantic_router_agent.classify_route", return_value=decision), \
             patch("google.adk.models.google_llm.Gemini.generate_content_async", new=fake_generation), \
             patch("google.adk.flows.llm_flows.core._model_call._start_call_llm_span",
                   side_effect=lambda context: tracer.start_span("call_llm", context=context)):
            response = self.client.post("/api/chat", json={"message": "Who am I signed in as?"}, headers=self.headers)
        self.assertEqual(response.status_code, 200, str(getattr(self.app.state, "last_error", response.text)))
        self.assertEqual(len(captured), 2, "Exercise a real MCP response in the second model request")
        session = self.client.portal.call(partial(self.app.state.runner.session_service.get_session,
                                         app_name="companyai_local", user_id=item.user_id, session_id=item.session_id))
        serialized = json.dumps(session.model_dump(mode="json"))
        self.assertEqual(session.state["last_route"], "auth_agent")
        self.assertEqual(session.state["last_route_confidence"], 0.99)
        from evaluations.adk_harness import _find_status
        identity_statuses = [_find_status(part.function_response.response)
                             for event in session.events if event.content
                             for part in event.content.parts or []
                             if part.function_response and part.function_response.name == "get_login_identity"]
        self.assertEqual(identity_statuses, ["success"], "The real MCP identity call must succeed, not merely be attempted")
        spans = exporter.get_finished_spans()
        self.assertTrue(spans, "The forced offline trace sink must capture a native ADK model span")
        trace_text = "\n".join(span.to_json() for span in spans)
        provider.shutdown()
        for secret in (DUMMY, item.token, self.client.cookies.get(COOKIE)):
            self.assertNotIn(secret, serialized)
            self.assertNotIn(secret, trace_text)
            self.assertTrue(all(secret not in request for request in captured))
        for request in captured:
            self.assertNotIn('"name":"login"', request)
            self.assertNotIn('"name":"create_user_credentials"', request)
            self.assertNotIn('"name":"update_user_credentials"', request)

    def test_nested_tool_output_secret_fields_are_removed(self):
        from company_system.security.secret_boundary import sanitize_payload
        unknown = "UnregisteredDummyToolToken-71"
        payload = {"content": [{"text": json.dumps({"status": "success", "session_token": unknown,
                                                   "nested": {"password_hash": "DummyHash-73",
                                                              "sessionSecret": "DummySessionSecret-91",
                                                              "refresh_token": "DummyRefresh-92", "apiKey": "DummyAPI-93"}})}]}
        safe = json.dumps(sanitize_payload(payload))
        self.assertNotIn(unknown, safe)
        self.assertNotIn("DummyHash-73", safe)
        for value in ("DummySessionSecret-91", "DummyRefresh-92", "DummyAPI-93"):
            self.assertNotIn(value, safe)

    def test_root_without_trusted_host_context_never_calls_model(self):
        from company_system.agent import root_agent
        async def collect():
            return [event async for event in root_agent._run_async_impl(
                SimpleNamespace(branch=None, invocation_id="offline-boundary-test"))]
        with patch("company_system.routing.semantic_router_agent.classify_route") as classify:
            events = asyncio.run(collect())
            classify.assert_not_called()
        self.assertIn("authenticated", events[0].content.parts[0].text)

    def test_quota_failure_is_503_and_success_clears_persisted_error(self):
        self.login()
        with patch("company_system.routing.semantic_router_agent.classify_route", side_effect=RuntimeError("api_daily_quota_exhausted")):
            response = self.client.post("/api/chat", json={"message": "Who am I?"}, headers=self.headers)
        self.assertEqual(response.status_code, 503)
        decision = RoutingDecision(route="auth_agent", confidence=0.99, reason="Identity")
        async def generation(model, llm_request, stream=False):
            yield LlmResponse(content=types.Content(role="model", parts=[types.Part.from_text(text="Offline recovery verified.")]))
        with patch("company_system.routing.semantic_router_agent.classify_route", return_value=decision), \
             patch("google.adk.models.google_llm.Gemini.generate_content_async", new=generation):
            response = self.client.post("/api/chat", json={"message": "Who am I?"}, headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_nonloopback_client_and_oversized_body_are_denied(self):
        with TestClient(create_app(), base_url="http://127.0.0.1:8000", client=("192.0.2.10", 50000)) as external:
            self.assertEqual(external.get("/").status_code, 403)
        response = self.client.post("/api/login", content="x" * 17000,
                                    headers={**self.headers, "Content-Type": "application/json"})
        self.assertEqual(response.status_code, 413)
        self.assertEqual(self.client.get("/../../.env").status_code, 404)

    def test_hr_credentials_use_host_code_without_model_or_mcp_password(self):
        from company_system.mcp.client import build_mcp_toolset
        async def hr_surface():
            toolset = build_mcp_toolset("hr")
            try:
                tools = await toolset.get_tools()
                for tool in tools:
                    declaration = tool._get_declaration()
                    self.assertNotIn("session_token", (declaration.parameters.properties or {}) if declaration.parameters else {})
                return {tool.name for tool in tools}
            finally:
                await toolset.close()
        self.assertEqual(asyncio.run(hr_surface()), {"list_employees", "create_employee", "update_employee_status"})
        self.login("hr.admin", "HrAdmin#2026")
        new = "DummyRotation-Secure-23!"
        with patch.object(self.app.state.runner, "run_async") as run:
            try:
                response = self.client.post("/api/credentials", headers=self.headers,
                    json={"operation": "update", "username": USER, "password": new})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["status"], "success")
                self.assertNotIn(new, response.text)
                run.assert_not_called()
            finally:
                self.client.post("/api/credentials", headers=self.headers,
                    json={"operation": "update", "username": USER, "password": DUMMY})

    def test_transport_only_token_never_mutates_event_arguments(self):
        token = "DummyTransportToken-51"
        caller = {"employee_id": 5, "session_token": "forged"}
        wrapped = SimpleNamespace(name="get_employee_profile", description="Profile",
                                  _run_async_impl=AsyncMock(return_value={"status": "success"}))
        tool = HostAuthenticatedTool(wrapped)
        with host_token(token):
            asyncio.run(tool.run_async(args=caller, tool_context=SimpleNamespace(state={})))
        self.assertEqual(caller["session_token"], "forged")
        self.assertEqual(wrapped._run_async_impl.call_args.kwargs["args"]["session_token"], token)
        self.assertNotIn(DUMMY, json.dumps(wrapped._run_async_impl.call_args.kwargs["args"]))
        self.assertNotIn(token, json.dumps(caller))

    def test_model_guard_logs_exceptions_and_token_context(self):
        secret = "DummyLogSecret-81!"
        remember_secret(secret)
        install_log_redaction()
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        logger = logging.getLogger("boundary_test")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        try:
            try:
                raise RuntimeError(secret)
            except RuntimeError:
                logger.exception("Received %s", secret)
            self.assertNotIn(secret, stream.getvalue())
            with self.assertRaises(ValueError) as caught:
                guard_model_request(None, SimpleNamespace(model_dump_json=lambda **kw: json.dumps({"text": secret})))
            self.assertNotIn(secret, str(caught.exception))
            with self.assertRaises(ValueError):
                guard_model_request(None, SimpleNamespace(model_dump_json=lambda **kw: '{"text":"safe"}'))
        finally:
            logger.removeHandler(handler)

    def test_hr_boundary_and_cross_session_state_injection(self):
        self.login()
        response = self.client.post("/api/credentials", json={"operation": "update", "username": USER, "password": "NewDummyPass-73!"}, headers=self.headers)
        self.assertEqual(response.status_code, 403)
        response = self.client.post("/api/chat", json={"message": "My profile", "state_delta": {"auth_role": "admin"}}, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.client.cookies.clear()
        self.client.cookies.set(COOKIE, "forged_browser_session")
        self.assertEqual(self.client.get("/api/me").status_code, 401)


if __name__ == "__main__":
    unittest.main(verbosity=2)
