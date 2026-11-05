from google.adk.agents import Agent

from company_system.config import build_agent_generation_config, build_llm

from company_system.mcp.client import (
    build_mcp_toolset,
    inject_mcp_session_token,
    sync_auth_state_from_mcp,
)



auth_agent = Agent(
    name="auth_agent",

    model=build_llm(),
    generate_content_config=build_agent_generation_config(),

    description=(
        "Authentication specialist. "
        "Handles login, logout, and current-session identity requests."
    ),

    instruction="""
You are the CompanyAI Authentication Agent.
Login and credential entry are performed by trusted application code using the
secure login form. Never ask for credentials in chat or call a login tool.
For login requests, explain that the user should use the secure login form.
For logout, call logout(). For current identity, call get_login_identity().
Use only returned facts; preserve auth_required/forbidden/errors clearly.
Keep responses concise. For other business domains transfer to the supervisor.
""",
    tools=[build_mcp_toolset("auth")],
    before_tool_callback=inject_mcp_session_token,
    after_tool_callback=sync_auth_state_from_mcp,
)