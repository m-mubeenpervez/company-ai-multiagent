from __future__ import annotations

ROUTE_DESCRIPTIONS = {
    "auth_agent": "Login, logout, sign-in/sign-out, current login identity, who-am-I requests.",
    "hr_agent": "Employee lifecycle/admin and HR credential administration: list/create/activate/deactivate employees, create/update/delete login credentials.",
    "employee_agent": "Individual employee profile/record lookup: code, name, email, department, designation, joining date, work location, manager.",
    "intern_agent": "Intern profile, internship progress/report status, conversion status, training track, missing intern records.",
    "attendance_agent": "Attendance records, check-in/check-out, lateness and working hours.",
    "leave_agent": "Personal/team leave balance, leave requests, leave history and leave approvals.",
    "policy_agent": "Company handbook, policies, rules, procedures and policy/deadline questions answered through RAG.",
    "recruitment_agent": "Candidates, interviews, offers, recruitment and hiring pipeline.",
    "performance_agent": "Performance reviews, evaluation records and performance ratings.",
    "training_agent": "Training assignments, courses, mandatory learning and learning progress.",
    "project_agent": "Projects, memberships, assigned tasks, task status and due dates.",
    "payroll_agent": "Salary, payroll and payslip records.",
    "finance_agent": "Expense claims, reimbursements, submitting/reviewing expenses.",
    "it_agent": "IT assets, laptops/devices, assigned assets and available assets.",
    "document_agent": "Employee/company document records and document metadata.",
    "analytics_agent": "Aggregated management analytics: headcount, counts by department/type, operational summary, pending leave counts, overdue task counts, missing intern-report counts.",
    "notification_agent": "Notifications, reminders and sending permitted notifications.",
    "audit_agent": "Audit logs, compliance trail and recent audited actions.",
    "unknown": "Request is genuinely outside CompanyAI domains or too ambiguous to route safely.",
}

ROUTE_NAMES = tuple(ROUTE_DESCRIPTIONS.keys())

ROUTING_COLLISION_RULES = """
Important collision guidance:
- Login/logout/who-am-I -> auth_agent. Managing another user's credentials -> hr_agent.
- Aggregated counts/summaries -> analytics_agent, even if they mention leave, tasks, interns or employees.
- Policy/rule/procedure/deadline questions -> policy_agent. Personal record/status questions -> the corresponding domain agent.
- Employee lifecycle/admin actions -> hr_agent. Read-only employee profile/details -> employee_agent.
- Internship report policy/deadline -> policy_agent; a specific intern's report status/progress -> intern_agent.
- Salary/payroll -> payroll_agent; expense/reimbursement -> finance_agent.
- Prefer the user's current explicit request over older conversation context.
""".strip()

ROUTING_EXAMPLES = [
    ("Log in with my company account", "auth_agent"),
    ("Who am I logged in as?", "auth_agent"),
    ("Create login credentials for employee 5", "hr_agent"),
    ("Create a new employee", "hr_agent"),
    ("What is my designation and department?", "employee_agent"),
    ("Show internship report status", "intern_agent"),
    ("What is the internship report deadline?", "policy_agent"),
    ("What does the leave policy say?", "policy_agent"),
    ("How many pending leave requests are there?", "analytics_agent"),
    ("Show my leave balance", "leave_agent"),
    ("How many overdue tasks are there?", "analytics_agent"),
    ("Show my assigned tasks", "project_agent"),
    ("How many missing intern reports are there?", "analytics_agent"),
    ("Show my payroll for September", "payroll_agent"),
    ("Show my expense claims", "finance_agent"),
]
