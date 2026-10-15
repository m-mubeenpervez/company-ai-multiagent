from __future__ import annotations


def route_request(message: str) -> str:
    """
    Deterministically decide which CompanyAI specialist
    should handle the current user request.

    Returns one of:
    - login
    - logout
    - hr_agent
    - employee_agent
    - intern_agent
    - attendance_agent
    - leave_agent
    - policy_agent
    - recruitment_agent
    - performance_agent
    - training_agent
    - project_agent
    - payroll_agent
    - finance_agent
    - it_agent
    - document_agent
    - analytics_agent
    - notification_agent
    - audit_agent
    - unknown
    """

    text = message.lower().strip()


    # =====================================================
    # HR CREDENTIAL ADMINISTRATION
    # =====================================================
    #
    # IMPORTANT:
    # Check credential-management intent BEFORE normal login/logout.
    #
    # Example:
    # "Create login credentials for employee 5"
    # must go to hr_agent,
    # NOT auth_agent.
    # =====================================================

    if (
        any(
            phrase in text
            for phrase in [
                "create login credentials",
                "update login credentials",
                "delete login credentials",
                "create credentials",
                "update credentials",
                "delete credentials",
                "create user credentials",
                "update user credentials",
                "delete user credentials",
            ]
        )

        # Password change such as:
        # "Change user test.employee password ..."
        or (
            "change user" in text
            and "password" in text
        )

        # Role change such as:
        # "Change user test.employee role to manager"
        or (
            "change user" in text
            and "role" in text
        )

        # Login password change
        or (
            "change login" in text
            and "password" in text
        )
    ):
        return "hr_agent"


    # =====================================================
    # AUTHENTICATION
    # =====================================================

    if any(
        phrase in text
        for phrase in [
            "log in",
            "login",
            "sign in",
            "signin",
        ]
    ):
        return "login"

    if any(
        phrase in text
        for phrase in [
            "log out",
            "logout",
            "sign out",
            "signout",
        ]
    ):
        return "logout"


    # =====================================================
    # HR EMPLOYEE LIFECYCLE / ADMINISTRATION
    # =====================================================
    #
    # IMPORTANT:
    # HR action intent must be checked BEFORE employee-record
    # lookup intent.
    #
    # Example:
    # "Create a new employee with employee code EMP-011..."
    # must go to hr_agent, not employee_agent.
    # =====================================================

    if (
        any(
            phrase in text
            for phrase in [
                # Employee listing
                "list employees",
                "list all employees",
                "show all employees",
                "show employees",
                "company employees",
                "employees i manage",
                "my employees",

                # Employee creation
                "create employee",
                "create a new employee",
                "create new employee",
                "add employee",
                "add a new employee",
                "add new employee",

                # Employee lifecycle
                "update employee status",
                "deactivate employee",
                "activate employee",
                "employee lifecycle",

                # HR records
                "hr record",
                "hr records",
            ]
        )

        # Handles:
        # "Change employee 11 status to inactive"
        # "Change employee 5 status to active"
        or (
            "change employee" in text
            and "status" in text
        )

        # Handles:
        # "Mark employee 11 inactive"
        # "Mark employee 5 active"
        or (
            "mark employee" in text
            and (
                "active" in text
                or "inactive" in text
            )
        )
    ):
        return "hr_agent"


    # =====================================================
    # ANALYTICS / MANAGEMENT REPORTING
    # =====================================================
    #
    # IMPORTANT:
    # Check specific aggregated-management intents BEFORE
    # employee/intern/leave/project domain lookups.
    #
    # This prevents:
    # - "employee count by department" -> employee_agent
    # - "pending leave requests" -> leave_agent
    # - "overdue tasks" -> project_agent
    # - "missing intern reports" -> intern_agent
    # =====================================================

    if (
        any(
            phrase in text
            for phrase in [
                "analytics",
                "management report",
                "management reporting",
                "company headcount",
                "headcount summary",
                "company headcount summary",
                "employee count by department",
                "employees by department",
                "employee count by employment type",
                "employees by employment type",
                "people summary",
                "company people summary",
                "operational summary",
                "operational dashboard",
                "operational dashboard summary",
                "pending leave requests",
                "overdue tasks",
                "missing intern reports",
            ]
        )
        or (
            ("how many" in text or "count" in text)
            and ("employee" in text or "employees" in text)
            and ("department" in text or "employment type" in text)
        )
    ):
        return "analytics_agent"


    # =====================================================
    # EMPLOYEE RECORDS
    # =====================================================

    if (
        any(
            phrase in text
            for phrase in [
                "employee profile",
                "employee code",
                "employee email",
                "designation",
                "department",
                "employment type",
                "joining date",
                "work location",
                "manager employee",
                "employee lookup",
                "search employee",
                "find employee",
            ]
        )

        # Handles:
        # "Show employee 11 profile"
        # "Show employee 5 details"
        or (
            "employee" in text
            and (
                "profile" in text
                or "details" in text
            )
        )
    ):
        return "employee_agent"

    # =====================================================
    # POLICY / RAG
    # =====================================================
    #
    # IMPORTANT:
    # Policy intent is checked BEFORE intern/attendance/leave.
    #
    # This prevents questions such as:
    #
    # "What is the deadline for submitting a monthly
    # internship report?"
    #
    # from incorrectly routing to intern_agent.
    #
    # Policy/rule/deadline questions should go to policy_agent.
    # Record/status/profile questions should go to domain agents.
    # =====================================================

    if any(
        phrase in text
        for phrase in [
            "policy",
            "handbook",
            "company rule",
            "company rules",
            "procedure",
            "procedures",
            "what does the handbook say",
            "what does policy say",
            "according to policy",
            "allowed by policy",
            "policy says",
            "report deadline",
            "internship report deadline",
            "intern report deadline",
            "monthly internship report deadline",
            "deadline for submitting",
            "deadline for submission",
            "submission deadline",
            "remote work policy",
            "leave policy",
            "attendance policy",
            "internship policy",
            "working time policy",
            "working-time policy",
        ]
    ):
        return "policy_agent"

    # =====================================================
    # INTERN MANAGEMENT
    # =====================================================

    if any(
        phrase in text
        for phrase in [
            "intern profile",
            "internship report",
            "intern report",
            "internship progress",
            "missing intern report",
            "conversion status",
            "training track",
        ]
    ):
        return "intern_agent"

    # =====================================================
    # ATTENDANCE
    # =====================================================

    if any(
        phrase in text
        for phrase in [
            "attendance",
            "working hours",
            "late",
            "lateness",
            "check in",
            "check-in",
            "check out",
            "check-out",
        ]
    ):
        return "attendance_agent"

    # =====================================================
    # LEAVE
    # =====================================================

    if any(
        phrase in text
        for phrase in [
            "leave balance",
            "leave request",
            "leave history",
            "annual leave",
            "sick leave",
            "casual leave",
            "approve leave",
            "leave approval",
        ]
    ):
        return "leave_agent"

    
    # =====================================================
    # RECRUITMENT
    # =====================================================

    if any(
        phrase in text
        for phrase in [
            "candidate",
            "interview",
            "offer",
            "recruitment",
            "hiring pipeline",
        ]
    ):
        return "recruitment_agent"

    # =====================================================
    # PERFORMANCE
    # =====================================================

    if any(
        phrase in text
        for phrase in [
            "performance review",
            "evaluation",
            "performance rating",
        ]
    ):
        return "performance_agent"

    # =====================================================
    # TRAINING
    # =====================================================

    if any(
        phrase in text
        for phrase in [
            "training",
            "course",
            "learning progress",
            "mandatory course",
        ]
    ):
        return "training_agent"

    # =====================================================
    # PROJECTS / TASKS
    # =====================================================

    if any(
        phrase in text
        for phrase in [
            "project",
            "task",
            "assigned task",
            "project membership",
        ]
    ):
        return "project_agent"

    # =====================================================
    # PAYROLL
    # =====================================================

    if any(
        phrase in text
        for phrase in [
            "salary",
            "payroll",
            "payslip",
            "pay slip",
        ]
    ):
        return "payroll_agent"

    # =====================================================
    # FINANCE / EXPENSE
    # =====================================================

    if any(
        phrase in text
        for phrase in [
            "expense",
            "reimbursement",
            "expense claim",
        ]
    ):
        return "finance_agent"

    # =====================================================
    # IT
    # =====================================================

    if any(
        phrase in text
        for phrase in [
            "laptop",
            "device",
            "asset",
            "it asset",
            "asset assignment",
        ]
    ):
        return "it_agent"

    # =====================================================
    # DOCUMENTS
    # =====================================================

    if any(
        phrase in text
        for phrase in [
            "document",
            "document metadata",
        ]
    ):
        return "document_agent"

    # =====================================================
    # NOTIFICATIONS
    # =====================================================

    if any(
        phrase in text
        for phrase in [
            "notification",
            "reminder",
        ]
    ):
        return "notification_agent"

    # =====================================================
    # AUDIT
    # =====================================================

    if any(
        phrase in text
        for phrase in [
            "audit",
            "audit log",
            "compliance",
        ]
    ):
        return "audit_agent"

    return "unknown"