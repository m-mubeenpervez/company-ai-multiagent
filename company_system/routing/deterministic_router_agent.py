from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import aclosing

from google.adk.agents import BaseAgent, InvocationContext
from google.adk.events import Event
from google.genai import types

from company_system.routing.router import route_request


# =========================================================
# ROUTE -> ADK AGENT NAME
# =========================================================

ROUTE_TO_AGENT = {
    # Authentication
    "login": "auth_agent",
    "logout": "auth_agent",

    # Company specialists
    "hr_agent": "hr_agent",
    "employee_agent": "employee_agent",
    "intern_agent": "intern_agent",
    "attendance_agent": "attendance_agent",
    "leave_agent": "leave_agent",
    "policy_agent": "policy_agent",
    "recruitment_agent": "recruitment_agent",
    "performance_agent": "performance_agent",
    "training_agent": "training_agent",
    "project_agent": "project_agent",
    "payroll_agent": "payroll_agent",
    "finance_agent": "finance_agent",
    "it_agent": "it_agent",
    "document_agent": "document_agent",
    "analytics_agent": "analytics_agent",
    "notification_agent": "notification_agent",
    "audit_agent": "audit_agent",
}


class DeterministicRouterAgent(BaseAgent):
    """
    Deterministic CompanyAI root router.

    The LLM does NOT choose which specialist handles the request.

    Flow:

    User message
        ↓
    Python route_request()
        ↓
    selected child agent
        ↓
    child agent handles tools / response
    """

    async def _run_async_impl(
        self,
        ctx: InvocationContext,
    ) -> AsyncGenerator[Event, None]:

        # =====================================================
        # 1. READ CURRENT USER MESSAGE
        # =====================================================

        text_parts: list[str] = []

        if ctx.user_content and ctx.user_content.parts:
            for part in ctx.user_content.parts:
                if part.text:
                    text_parts.append(part.text)

        user_text = " ".join(text_parts).strip()

        # =====================================================
        # 2. DETERMINE ROUTE IN PYTHON
        # =====================================================

        route = route_request(user_text)

        target_name = ROUTE_TO_AGENT.get(route)

        # =====================================================
        # 3. UNKNOWN REQUEST
        # =====================================================

        if target_name is None:
            yield Event(
                author=self.name,
                branch=ctx.branch,
                invocation_id=ctx.invocation_id,
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part.from_text(
                            text=(
                                "I could not determine which CompanyAI "
                                "specialist should handle this request."
                            )
                        )
                    ],
                ),
            )
            return

        # =====================================================
        # 4. FIND TARGET CHILD AGENT
        # =====================================================

        target_agent = self.find_agent(target_name)

        if target_agent is None:
            raise ValueError(
                f"Routing target '{target_name}' "
                "was not found in the CompanyAI agent tree."
            )

        # =====================================================
        # 5. RUN TARGET AGENT DIRECTLY
        # =====================================================

        async with aclosing(
            target_agent.run_async(ctx)
        ) as agent_events:

            async for event in agent_events:
                yield event