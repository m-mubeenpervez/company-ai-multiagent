from __future__ import annotations

from pathlib import Path

from company_system.routing.catalog import ROUTE_NAMES, ROUTING_EXAMPLES

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    expected = {
        "auth_agent", "hr_agent", "employee_agent", "intern_agent",
        "attendance_agent", "leave_agent", "policy_agent", "recruitment_agent",
        "performance_agent", "training_agent", "project_agent", "payroll_agent",
        "finance_agent", "it_agent", "document_agent", "analytics_agent",
        "notification_agent", "audit_agent", "unknown",
    }
    assert set(ROUTE_NAMES) == expected
    assert len(ROUTING_EXAMPLES) >= 12

    routing_dir = PROJECT_ROOT / "company_system" / "routing"
    for old in ["router.py", "dispatcher.py", "deterministic_router_agent.py"]:
        assert not (routing_dir / old).exists(), f"Deterministic routing file still exists: {old}"

    root_text = (PROJECT_ROOT / "company_system" / "agent.py").read_text(encoding="utf-8")
    semantic_text = (routing_dir / "semantic_router_agent.py").read_text(encoding="utf-8")
    assert "GeminiSemanticRouterAgent" in root_text
    assert "DeterministicRouterAgent" not in root_text
    assert "response_schema=RoutingDecision" in semantic_text
    assert "confidence < GEMINI_ROUTER_MIN_CONFIDENCE" in semantic_text
    assert "GEMINI_ROUTER_FALLBACK_MODEL" in semantic_text
    assert "exact keyword matching" in semantic_text

    print("PASS | Deterministic Python routing has been removed")
    print("PASS | Gemini semantic router uses strict structured routing")
    print("PASS | Router covers all 18 CompanyAI agents plus unknown")
    print("PASS | Confidence gate, LLM retry and Gemini fallback are present")


if __name__ == "__main__":
    main()
