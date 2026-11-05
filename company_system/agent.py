from company_system.routing.semantic_router_agent import GeminiSemanticRouterAgent

from company_system.agents.auth_agent import auth_agent
from company_system.agents.hr_agent import hr_agent
from company_system.agents.employee_agent import employee_agent
from company_system.agents.intern_agent import intern_agent
from company_system.agents.attendance_agent import attendance_agent
from company_system.agents.leave_agent import leave_agent
from company_system.agents.policy_agent import policy_agent
from company_system.agents.recruitment_agent import recruitment_agent
from company_system.agents.performance_agent import performance_agent
from company_system.agents.training_agent import training_agent
from company_system.agents.project_agent import project_agent
from company_system.agents.payroll_agent import payroll_agent
from company_system.agents.finance_agent import finance_agent
from company_system.agents.it_agent import it_agent
from company_system.agents.document_agent import document_agent
from company_system.agents.analytics_agent import analytics_agent
from company_system.agents.notification_agent import notification_agent
from company_system.agents.audit_agent import audit_agent

from company_system.agents.common import SPECIALIST_RESPONSE_RULES, with_session_context
from company_system.security.secret_boundary import guard_model_request


SPECIALIST_AGENTS = [
    hr_agent, employee_agent, intern_agent, attendance_agent, leave_agent,
    policy_agent, recruitment_agent, performance_agent, training_agent,
    project_agent, payroll_agent, finance_agent, it_agent, document_agent,
    analytics_agent, notification_agent, audit_agent,
]

for specialist in SPECIALIST_AGENTS:
    specialist.disallow_transfer_to_peers = True
    specialist.disallow_transfer_to_parent = False
    current_instruction = specialist.instruction or ""
    if SPECIALIST_RESPONSE_RULES not in current_instruction:
        specialist.instruction = (
            f"{current_instruction.strip()}\n\n"
            f"{SPECIALIST_RESPONSE_RULES.strip()}"
        )

for specialist in [auth_agent, *SPECIALIST_AGENTS]:
    specialist.instruction = with_session_context(specialist.instruction or "")
    specialist.before_model_callback = guard_model_request

root_agent = GeminiSemanticRouterAgent(
    name="company_ai_supervisor",
    description=(
        "Gemini semantic CompanyAI supervisor. Uses an LLM classifier with a "
        "strict route schema, confidence checking, retry, and Gemini fallback "
        "to route natural-language requests to the correct specialist."
    ),
    sub_agents=[auth_agent, *SPECIALIST_AGENTS],
)
