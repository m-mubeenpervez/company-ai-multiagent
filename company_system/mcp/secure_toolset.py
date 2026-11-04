"""Keep bearer injection below ADK's model/event/trace boundary.

The wire MCP schemas stay unchanged. Only model-facing declarations omit secrets.
Credential operations remain available to trusted application code, not models.
"""
from __future__ import annotations

import copy
import json

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.mcp_tool import McpToolset
from company_system.security.secret_boundary import current_token, sanitize_payload, reject_secret_text

CREDENTIAL_TOOLS = {"login", "create_user_credentials", "update_user_credentials", "delete_user_credentials"}


class HostAuthenticatedTool(BaseTool):
    def __init__(self, wrapped):
        super().__init__(name=wrapped.name, description=wrapped.description)
        self.wrapped = wrapped

    def _get_declaration(self):
        declaration = copy.deepcopy(self.wrapped._get_declaration())
        schema = declaration.parameters
        if schema:
            if schema.properties:
                schema.properties.pop("session_token", None)
            if schema.required:
                schema.required = [key for key in schema.required if key != "session_token"]
        if declaration.parameters_json_schema:
            declaration.parameters_json_schema.get("properties", {}).pop("session_token", None)
            required = declaration.parameters_json_schema.get("required", [])
            declaration.parameters_json_schema["required"] = [key for key in required if key != "session_token"]
        return declaration

    async def run_async(self, *, args, tool_context):
        # Never mutate the function-call arguments that ADK stores/traces.
        if self.name in CREDENTIAL_TOOLS:
            return {"status": "forbidden", "message": "Use the secure credential form."}
        wire_args = {key: value for key, value in args.items() if key != "session_token"}
        reject_secret_text(json.dumps(wire_args, ensure_ascii=False))
        wire_args["session_token"] = current_token()
        if not wire_args["session_token"]:
            return {"status": "auth_required", "message": "Sign in using the secure login form."}
        try:
            # Keep the pinned SDK's session leases, termination recovery and
            # no-replay behavior. Skip only its outer debug/auth wrapper, which
            # can retain credential-bearing wire arguments in ADK metadata.
            payload = await self.wrapped._run_async_impl(
                args=wire_args, tool_context=tool_context, credential=None,
            )
            return sanitize_payload(payload)
        except Exception:
            return {"status": "error", "message": "Tool transport failed; execution may be incomplete. Do not blindly retry writes."}


class HostAuthenticatedToolset(McpToolset):
    async def get_tools(self, readonly_context=None):
        tools = await super().get_tools(readonly_context)
        return [HostAuthenticatedTool(tool) for tool in tools if tool.name not in CREDENTIAL_TOOLS]
