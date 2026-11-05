from __future__ import annotations

from company_system.routing.semantic_router_agent import classify_route

CASES = [
    ("Sign me out of my company account", "auth_agent"),
    ("Please make login credentials for employee number 5", "hr_agent"),
    ("Where does employee 3 work and what is their designation?", "employee_agent"),
    ("When exactly do interns have to submit the monthly report according to company rules?", "policy_agent"),
    ("Has my internship progress report been submitted?", "intern_agent"),
    ("How many leave requests are waiting for approval?", "analytics_agent"),
    ("How many vacation days do I have left?", "leave_agent"),
    ("Give me a summary of tasks that are overdue across the company", "analytics_agent"),
    ("What tasks have been assigned to me?", "project_agent"),
    ("Show the money I was paid in September", "payroll_agent"),
    ("I need to see my reimbursement claims", "finance_agent"),
    ("Which laptop is assigned to me?", "it_agent"),
]


def main() -> None:
    passed = 0
    for prompt, expected in CASES:
        result = classify_route(prompt)
        ok = result.route == expected
        print(("PASS" if ok else "FAIL"), "|", prompt, "->", result.route, f"({result.confidence:.2f})")
        if not ok:
            raise SystemExit(f"Expected {expected}, got {result.route}: {result.reason}")
        passed += 1
    print(f"\nLIVE LLM ROUTING SUMMARY: {passed}/{len(CASES)} PASS")


if __name__ == "__main__":
    main()
