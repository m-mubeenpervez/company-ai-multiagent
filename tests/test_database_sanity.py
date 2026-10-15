from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from company_system.database.db import get_connection


def check(name: str, condition: bool, details: str = "") -> bool:
    if condition:
        print(f"PASS | {name}")
        return True

    print(f"FAIL | {name}")
    if details:
        print(f"       {details}")
    return False


def main():
    conn = get_connection()

    results = []

    try:
        # 1. Original employees should still be present
        employee_count = conn.execute(
            "SELECT COUNT(*) c FROM employees"
        ).fetchone()["c"]

        results.append(
            check(
                "Employee count is back to baseline",
                employee_count == 10,
                f"Actual employee count: {employee_count}",
            )
        )

        # 2. Test employee should be gone
        test_employee = conn.execute(
            "SELECT id FROM employees WHERE id = 11"
        ).fetchone()

        results.append(
            check(
                "Test employee 11 removed",
                test_employee is None,
            )
        )

        # 3. Test credentials should not exist
        test_users = conn.execute(
            """
            SELECT username
            FROM users
            WHERE username IN ('test.employee', 'sec.test')
            """
        ).fetchall()

        results.append(
            check(
                "Temporary test credentials removed",
                len(test_users) == 0,
                f"Found: {[r['username'] for r in test_users]}",
            )
        )

        # 4. All 10 demo users should still exist
        demo_user_count = conn.execute(
            """
            SELECT COUNT(*) c
            FROM users
            WHERE username IN (
                'hr.admin',
                'manager.asim',
                'employee.ali',
                'employee.sara',
                'intern.mubeen',
                'intern.ahmad',
                'recruiter.noor',
                'finance.hina',
                'it.usman',
                'admin.auditor'
            )
            """
        ).fetchone()["c"]

        results.append(
            check(
                "All demo users still exist",
                demo_user_count == 10,
                f"Actual demo user count: {demo_user_count}",
            )
        )

        # 5. Test expense claims should be gone
        test_expenses = conn.execute(
            """
            SELECT COUNT(*) c
            FROM expense_claims
            WHERE category = 'Test'
            """
        ).fetchone()["c"]

        results.append(
            check(
                "Test expense claims removed",
                test_expenses == 0,
                f"Remaining test claims: {test_expenses}",
            )
        )

        # 6. Original seeded expense claims should remain
        seeded_expenses = conn.execute(
            """
            SELECT COUNT(*) c
            FROM expense_claims
            WHERE id IN (1, 2)
            """
        ).fetchone()["c"]

        results.append(
            check(
                "Seed expense claims preserved",
                seeded_expenses == 2,
                f"Actual seeded claims: {seeded_expenses}",
            )
        )

        # 7. Test notification should be gone
        test_notification = conn.execute(
            """
            SELECT COUNT(*) c
            FROM notifications
            WHERE title = 'Test'
              AND message = 'Notification send test.'
            """
        ).fetchone()["c"]

        results.append(
            check(
                "Test notification removed",
                test_notification == 0,
            )
        )

        # 8. Original notifications should remain
        notification_count = conn.execute(
            "SELECT COUNT(*) c FROM notifications"
        ).fetchone()["c"]

        results.append(
            check(
                "Seed notifications preserved",
                notification_count == 3,
                f"Actual notifications: {notification_count}",
            )
        )

        # 9. Payroll data should still be intact
        payroll_count = conn.execute(
            """
            SELECT COUNT(*) c
            FROM payroll
            WHERE pay_month = '2026-09'
            """
        ).fetchone()["c"]

        results.append(
            check(
                "Payroll seed data preserved",
                payroll_count == 10,
                f"Actual payroll records: {payroll_count}",
            )
        )

        # 10. Core project data should still exist
        project_count = conn.execute(
            "SELECT COUNT(*) c FROM projects"
        ).fetchone()["c"]

        results.append(
            check(
                "Projects preserved",
                project_count == 2,
                f"Actual project count: {project_count}",
            )
        )

    finally:
        conn.close()

    passed = sum(results)
    total = len(results)
    failed = total - passed

    print()
    print("==============================")
    print("DATABASE SANITY SUMMARY")
    print("==============================")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {total}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()