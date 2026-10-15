from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from company_system.tools.payroll_tools import get_payroll
from company_system.tools.document_tools import list_documents
from company_system.tools.analytics_tools import company_people_summary
from company_system.tools.audit_tools import get_recent_audit_logs
from company_system.tools.it_tools import list_available_assets
from company_system.tools.finance_tools import review_expense
from company_system.tools.performance_tools import get_performance_reviews
from company_system.tools.training_tools import get_training_assignments
from company_system.tools.hr_tools import create_user_credentials


class FakeToolContext:
    def __init__(self, *, user_id, username, role, employee_id, full_name):
        self.state = {
            "auth_user_id": user_id,
            "auth_username": username,
            "auth_role": role,
            "auth_employee_id": employee_id,
            "auth_full_name": full_name,
        }


USERS = {
    "employee_ali": FakeToolContext(user_id=3, username="employee.ali", role="employee", employee_id=3, full_name="Ali Hassan"),
    "intern_mubeen": FakeToolContext(user_id=5, username="intern.mubeen", role="intern", employee_id=5, full_name="Mubeen Pervez"),
    "manager_asim": FakeToolContext(user_id=2, username="manager.asim", role="manager", employee_id=2, full_name="Asim Raza"),
    "finance_hina": FakeToolContext(user_id=8, username="finance.hina", role="finance", employee_id=8, full_name="Hina Malik"),
    "hr_admin": FakeToolContext(user_id=1, username="hr.admin", role="hr", employee_id=1, full_name="Saqib Khan"),
    "it_usman": FakeToolContext(user_id=9, username="it.usman", role="it", employee_id=9, full_name="Usman Tariq"),
}


def check_status(name, result, expected_status):
    actual = result.get("status")
    if actual == expected_status:
        print(f"PASS | {name} -> {actual}")
        return True
    print(f"FAIL | {name}\n     Expected status: {expected_status}\n     Actual result:   {result}")
    return False


def main():
    results = []

    results.append(check_status(
        "Employee cannot view another employee payroll",
        get_payroll(employee_id=5, pay_month="2026-09", tool_context=USERS["employee_ali"]),
        "forbidden",
    ))

    results.append(check_status(
        "Employee cannot view another employee documents",
        list_documents(employee_id=5, tool_context=USERS["employee_ali"]),
        "forbidden",
    ))

    results.append(check_status(
        "Employee cannot view company analytics",
        company_people_summary(tool_context=USERS["employee_ali"]),
        "forbidden",
    ))

    results.append(check_status(
        "Employee cannot view audit logs",
        get_recent_audit_logs(limit=10, tool_context=USERS["employee_ali"]),
        "forbidden",
    ))

    results.append(check_status(
        "Employee cannot view available IT assets",
        list_available_assets(tool_context=USERS["employee_ali"]),
        "forbidden",
    ))

    results.append(check_status(
        "Employee cannot approve expense",
        review_expense(claim_id=3, decision="approved", tool_context=USERS["employee_ali"]),
        "forbidden",
    ))

    results.append(check_status(
        "Intern cannot view employee performance",
        get_performance_reviews(employee_id=3, tool_context=USERS["intern_mubeen"]),
        "forbidden",
    ))

    results.append(check_status(
        "Intern cannot view employee training",
        get_training_assignments(employee_id=3, tool_context=USERS["intern_mubeen"]),
        "forbidden",
    ))

    results.append(check_status(
        "Manager cannot create credentials",
        create_user_credentials(employee_id=5, username="sec.test", password="Test#2026", role="intern", tool_context=USERS["manager_asim"]),
        "forbidden",
    ))

    results.append(check_status(
        "Finance can view employee payroll",
        get_payroll(employee_id=5, pay_month="2026-09", tool_context=USERS["finance_hina"]),
        "success",
    ))

    results.append(check_status(
        "HR can view employee documents",
        list_documents(employee_id=3, tool_context=USERS["hr_admin"]),
        "success",
    ))

    results.append(check_status(
        "IT can view available assets",
        list_available_assets(tool_context=USERS["it_usman"]),
        "success",
    ))

    passed = sum(results)
    total = len(results)
    failed = total - passed

    print("\n==============================")
    print("SECURITY REGRESSION SUMMARY")
    print("==============================")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {total}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
