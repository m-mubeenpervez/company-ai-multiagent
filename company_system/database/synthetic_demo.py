"""Synthetic-only demo records for new local databases.

These identities are fictional and deliberately use the reserved ``.invalid``
domain. Passwords are public demo credentials and are stored only as salted
PBKDF2 hashes by ``hash_password``.
"""
from __future__ import annotations

from datetime import datetime, timezone
import sqlite3

from company_system.security.passwords import hash_password


SYNTHETIC_USERS = (
    ("demo.hr", "DemoHr#2026", "hr", 1),
    ("demo.manager", "DemoManager#2026", "manager", 2),
    ("demo.employee", "DemoEmployee#2026", "employee", 3),
    ("demo.employee2", "DemoEmployee#2026", "employee", 4),
    ("demo.intern", "DemoIntern#2026", "intern", 5),
    ("demo.intern2", "DemoIntern#2026", "intern", 6),
    ("demo.recruiter", "DemoRecruit#2026", "recruiter", 7),
    ("demo.finance", "DemoFinance#2026", "finance", 8),
    ("demo.it", "DemoSupport#2026", "it", 9),
    ("demo.admin", "DemoAudit#2026", "admin", 10),
)


def seed_synthetic(connection: sqlite3.Connection) -> None:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    connection.executemany(
        "INSERT INTO departments(id,name,manager_employee_id) VALUES (?,?,NULL)",
        [(1, "People"), (2, "Product Lab"), (3, "Talent"),
         (4, "Accounts"), (5, "Technology"), (6, "Operations")],
    )
    employees = [
        (1, "DEMO-001", "Rowan Cedar", "rowan.cedar@example.invalid", 1, "People Lead", "permanent", None),
        (2, "DEMO-002", "Arden Vale", "arden.vale@example.invalid", 2, "Product Lead", "permanent", None),
        (3, "DEMO-003", "Jules Ember", "jules.ember@example.invalid", 2, "Software Engineer", "permanent", 2),
        (4, "DEMO-004", "Casey Harbor", "casey.harbor@example.invalid", 2, "AI Engineer", "permanent", 2),
        (5, "DEMO-005", "Riley Quartz", "riley.quartz@example.invalid", 2, "AI Intern", "intern", 2),
        (6, "DEMO-006", "Morgan Pine", "morgan.pine@example.invalid", 2, "Platform Intern", "intern", 2),
        (7, "DEMO-007", "Taylor Nimbus", "taylor.nimbus@example.invalid", 3, "Recruiter", "permanent", 1),
        (8, "DEMO-008", "Jordan Maple", "jordan.maple@example.invalid", 4, "Finance Analyst", "permanent", 1),
        (10, "DEMO-010", "Avery Lantern", "avery.lantern@example.invalid", 6, "Administrator", "permanent", 1),
        (9, "DEMO-009", "Quinn Solace", "quinn.solace@example.invalid", 5, "IT Specialist", "permanent", 10),
    ]
    connection.executemany(
        """INSERT INTO employees(
               id,employee_code,full_name,email,department_id,designation,
               employment_type,manager_employee_id,joining_date,status,work_location
           ) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        [row + ("2026-01-15", "active", "Demo Office") for row in employees],
    )
    connection.executemany(
        "UPDATE departments SET manager_employee_id=? WHERE id=?",
        [(1, 1), (2, 2), (7, 3), (8, 4), (9, 5), (10, 6)],
    )
    for username, password, role, employee_id in SYNTHETIC_USERS:
        salt, password_hash = hash_password(password)
        connection.execute(
            """INSERT INTO users(
                   username,password_salt,password_hash,role,employee_id,is_active,created_at
               ) VALUES (?,?,?,?,?,1,?)""",
            (username, salt, password_hash, role, employee_id, now),
        )
    connection.executemany(
        """INSERT INTO leave_balances(
               employee_id,annual_total,annual_used,sick_total,sick_used,casual_total,casual_used
           ) VALUES (?,20,0,10,0,5,0)""",
        [(employee_id,) for employee_id in range(1, 11)],
    )
    connection.executemany(
        """INSERT INTO intern_profiles(
               employee_id,training_track,internship_start,internship_end,
               supervisor_employee_id,conversion_status
           ) VALUES (?,?,?,?,?,?)""",
        [(5, "Applied AI", "2026-01-15", "2026-07-15", 2, "not_reviewed"),
         (6, "Platform Engineering", "2026-01-15", "2026-07-15", 2, "not_reviewed")],
    )
    connection.execute(
        """INSERT INTO projects(id,name,department_id,status,start_date,end_date)
           VALUES (1,'Synthetic Demo Workspace',2,'active','2026-01-15',NULL)"""
    )
    connection.execute(
        """INSERT INTO projects(id,name,department_id,status,start_date,end_date)
           VALUES (2,'Fictional Policy Portal',2,'planning','2026-02-01',NULL)"""
    )
    connection.executemany(
        "INSERT INTO project_members(project_id,employee_id,project_role) VALUES (1,?,?)",
        [(2, "Manager"), (3, "Engineer"), (4, "Engineer"), (5, "Intern"), (6, "Intern")],
    )
    connection.executemany(
        """INSERT INTO payroll(
               employee_id,pay_month,base_salary,allowance,bonus,deductions,status
           ) VALUES (?,'2026-09',1000,0,0,0,'paid')""",
        [(employee_id,) for employee_id in range(1, 11)],
    )
    connection.executemany(
        """INSERT INTO expense_claims(
               employee_id,category,amount,description,claim_date,status,reviewed_by
           ) VALUES (?,?,?,?,?,?,?)""",
        [(3, "Travel", 25, "Synthetic travel example", "2026-02-01", "approved", 8),
         (4, "Software", 40, "Synthetic software example", "2026-02-02", "pending", None)],
    )
    connection.executemany(
        "INSERT INTO notifications(employee_id,title,message,is_read,created_at) VALUES (?,?,?,?,?)",
        [(5, "Demo reminder", "Synthetic reminder", 0, now),
         (6, "Demo report", "Synthetic report notice", 0, now),
         (3, "Demo leave", "Synthetic leave notice", 0, now)],
    )
    connection.execute(
        """INSERT INTO document_records(
               employee_id,document_type,title,file_path,visibility,created_at
           ) VALUES (NULL,'company_policy','Company Handbook',
                     'company_system/documents/company_handbook.pdf','company',?)""",
        (now,),
    )
    connection.commit()
