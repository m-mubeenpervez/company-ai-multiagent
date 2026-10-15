from company_system.routing.deterministic_router_agent import (
    DeterministicRouterAgent,
)

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

from company_system.agents.common import SPECIALIST_RESPONSE_RULES


# =========================================================
# COMPANY SPECIALIST AGENTS
# =========================================================

SPECIALIST_AGENTS = [
    hr_agent,
    employee_agent,
    intern_agent,
    attendance_agent,
    leave_agent,
    policy_agent,
    recruitment_agent,
    performance_agent,
    training_agent,
    project_agent,
    payroll_agent,
    finance_agent,
    it_agent,
    document_agent,
    analytics_agent,
    notification_agent,
    audit_agent,
]


# =========================================================
# SPECIALIST CONFIGURATION
# =========================================================

for specialist in SPECIALIST_AGENTS:
    # Specialists cannot directly jump to sibling specialists.
    specialist.disallow_transfer_to_peers = True

    # A specialist may return to the root router if necessary.
    specialist.disallow_transfer_to_parent = False

    # Keep the common grounding/security/response rules
    # that were already being applied to every specialist.
    current_instruction = specialist.instruction or ""

    if SPECIALIST_RESPONSE_RULES not in current_instruction:
        specialist.instruction = (
            f"{current_instruction.strip()}\n\n"
            f"{SPECIALIST_RESPONSE_RULES.strip()}"
        )


# =========================================================
# AUTH AGENT CONFIGURATION
# =========================================================

# Authentication is still handled by the existing auth_agent.
#
# Important difference:
# auth_agent no longer decides when it should receive a request.
# The Python deterministic router sends ONLY login/logout requests
# to auth_agent.
#
# Therefore:
#
# Login request
#     -> deterministic router
#     -> auth_agent
#
# Employee request
#     -> deterministic router
#     -> employee_agent
#
# Intern request
#     -> deterministic router
#     -> intern_agent
#
# etc.


# =========================================================
# DETERMINISTIC ROOT ROUTER
# =========================================================

root_agent = DeterministicRouterAgent(
    name="company_ai_supervisor",

    description=(
        "Deterministic CompanyAI root router. "
        "Uses Python routing rules to send each request "
        "to the correct specialist agent."
    ),

    sub_agents=[
        auth_agent,
        *SPECIALIST_AGENTS,
    ],
)