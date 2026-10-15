from __future__ import annotations

from company_system.routing.router import route_request


AGENT_ROUTE_MAP = {
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


def get_route(message: str) -> dict:
    """
    Return the deterministic routing decision for one user message.
    """

    route = route_request(message)

    if route in {"login", "logout"}:
        return {
            "status": "success",
            "route_type": "auth",
            "action": route,
            "agent_name": None,
        }

    if route in AGENT_ROUTE_MAP:
        return {
            "status": "success",
            "route_type": "specialist",
            "action": None,
            "agent_name": AGENT_ROUTE_MAP[route],
        }

    return {
        "status": "unknown",
        "route_type": "unknown",
        "action": None,
        "agent_name": None,
    }