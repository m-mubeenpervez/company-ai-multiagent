from company_system.routing.router import route_request


tests = [
    # AUTH
    ("Log in with username employee.ali and password Employee#2026", "login"),
    ("Log out", "logout"),

    # HR
    ("List all employees", "hr_agent"),
    ("Create a new employee", "hr_agent"),
    ("Change employee 11 status to inactive", "hr_agent"),
    ("Create login credentials for employee 5", "hr_agent"),

    # EMPLOYEE
    ("Show my employee profile", "employee_agent"),
    ("What is my designation and department?", "employee_agent"),

    # POLICY
    ("What is the internship report deadline?", "policy_agent"),
    ("What does the leave policy say?", "policy_agent"),

    # INTERN
    ("Show my intern profile", "intern_agent"),
    ("Show internship report status", "intern_agent"),

    # ATTENDANCE
    ("Show my attendance", "attendance_agent"),

    # LEAVE
    ("Show my leave balance", "leave_agent"),

    # RECRUITMENT
    ("List candidates in interview stage", "recruitment_agent"),

    # PERFORMANCE
    ("Show my performance reviews", "performance_agent"),

    # TRAINING
    ("Show my training assignments", "training_agent"),

    # PROJECT
    ("Show my projects", "project_agent"),
    ("Show my assigned tasks", "project_agent"),

    # PAYROLL
    ("Show my payroll for 2026-09", "payroll_agent"),

    # FINANCE
    ("Show my expense claims", "finance_agent"),

    # IT
    ("Show my assigned assets", "it_agent"),

    # DOCUMENT
    ("Show my documents", "document_agent"),

    # ANALYTICS
    ("Show company headcount summary", "analytics_agent"),
    ("Show the operational dashboard summary", "analytics_agent"),
    ("How many pending leave requests are there?", "analytics_agent"),
    ("How many overdue tasks are there?", "analytics_agent"),
    ("How many missing intern reports are there?", "analytics_agent"),

    # NOTIFICATION
    ("Show my notifications", "notification_agent"),

    # AUDIT
    ("Show the last 10 audit logs", "audit_agent"),
]


passed = 0
failed = 0

for prompt, expected in tests:
    actual = route_request(prompt)

    if actual == expected:
        print(f"PASS | {prompt} -> {actual}")
        passed += 1
    else:
        print(
            f"FAIL | {prompt}\n"
            f"     Expected: {expected}\n"
            f"     Actual:   {actual}"
        )
        failed += 1


print("\n==============================")
print("ROUTING REGRESSION SUMMARY")
print("==============================")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Total:  {passed + failed}")