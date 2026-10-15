from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from company_system.database.db import get_connection


def cleanup():
    conn = get_connection()

    try:
        print("Cleaning CompanyAI test data...")

        # ==========================================
        # 1. TEST CREDENTIALS
        # ==========================================

        cur = conn.execute(
            """
            DELETE FROM users
            WHERE username IN ('test.employee', 'sec.test')
               OR employee_id = 11
            """
        )

        print(f"Test users removed: {cur.rowcount}")


        # ==========================================
        # 2. TEST EXPENSE CLAIMS
        # ==========================================

        cur = conn.execute(
            """
            DELETE FROM expense_claims
            WHERE id IN (3, 4)
              AND employee_id = 3
              AND category = 'Test'
            """
        )

        print(f"Test expense claims removed: {cur.rowcount}")


        # ==========================================
        # 3. TEST NOTIFICATION
        # ==========================================

        cur = conn.execute(
            """
            DELETE FROM notifications
            WHERE id = 4
              AND employee_id = 5
              AND title = 'Test'
              AND message = 'Notification send test.'
            """
        )

        print(f"Test notifications removed: {cur.rowcount}")


        # ==========================================
        # 4. TEST EMPLOYEE
        # ==========================================

        cur = conn.execute(
            """
            DELETE FROM employees
            WHERE id = 11
              AND employee_code = 'EMP-011'
              AND full_name = 'Test Employee'
            """
        )

        print(f"Test employees removed: {cur.rowcount}")


        # ==========================================
        # 5. AUDIT LOGS CREATED BY THESE TESTS
        # ==========================================

        cur = conn.execute(
            """
            DELETE FROM audit_logs
            WHERE
                (
                    target_type = 'employee'
                    AND target_id = '11'
                )
                OR
                (
                    target_type = 'expense_claim'
                    AND target_id IN ('3', '4')
                )
                OR
                (
                    target_type = 'notification'
                    AND target_id = '4'
                )
                OR
                (
                    target_type = 'user'
                    AND details LIKE '%test.employee%'
                )
                OR
                (
                    target_type = 'user'
                    AND target_id = 'test.employee'
                )
            """
        )

        print(f"Related audit logs removed: {cur.rowcount}")


        conn.commit()

        print()
        print("==============================")
        print("TEST DATA CLEANUP COMPLETE")
        print("==============================")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    cleanup()