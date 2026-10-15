PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS document_records;
DROP TABLE IF EXISTS asset_assignments;
DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS expense_claims;
DROP TABLE IF EXISTS payroll;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS project_members;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS training_assignments;
DROP TABLE IF EXISTS training_courses;
DROP TABLE IF EXISTS performance_reviews;
DROP TABLE IF EXISTS offers;
DROP TABLE IF EXISTS interviews;
DROP TABLE IF EXISTS candidates;
DROP TABLE IF EXISTS leave_requests;
DROP TABLE IF EXISTS leave_balances;
DROP TABLE IF EXISTS remote_work_requests;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS intern_monthly_reports;
DROP TABLE IF EXISTS intern_profiles;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    manager_employee_id INTEGER
);

CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    employee_code TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    department_id INTEGER NOT NULL,
    designation TEXT NOT NULL,
    employment_type TEXT NOT NULL CHECK(employment_type IN ('intern','probation','permanent','contract','part_time')),
    manager_employee_id INTEGER,
    joining_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    work_location TEXT NOT NULL DEFAULT 'Lahore',
    FOREIGN KEY(department_id) REFERENCES departments(id),
    FOREIGN KEY(manager_employee_id) REFERENCES employees(id)
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_salt TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('hr','manager','employee','intern','recruiter','finance','it','admin')),
    employee_id INTEGER UNIQUE,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY(employee_id) REFERENCES employees(id)
);

CREATE TABLE intern_profiles (
    employee_id INTEGER PRIMARY KEY,
    training_track TEXT NOT NULL,
    internship_start TEXT NOT NULL,
    internship_end TEXT NOT NULL,
    supervisor_employee_id INTEGER NOT NULL,
    conversion_status TEXT NOT NULL DEFAULT 'not_reviewed',
    FOREIGN KEY(employee_id) REFERENCES employees(id),
    FOREIGN KEY(supervisor_employee_id) REFERENCES employees(id)
);

CREATE TABLE intern_monthly_reports (
    id INTEGER PRIMARY KEY,
    intern_employee_id INTEGER NOT NULL,
    report_month TEXT NOT NULL,
    submitted_date TEXT,
    status TEXT NOT NULL,
    review_status TEXT NOT NULL,
    revision_required INTEGER NOT NULL DEFAULT 0,
    completion_percentage REAL NOT NULL DEFAULT 0,
    UNIQUE(intern_employee_id, report_month),
    FOREIGN KEY(intern_employee_id) REFERENCES employees(id)
);

CREATE TABLE attendance (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    work_date TEXT NOT NULL,
    status TEXT NOT NULL,
    check_in TEXT,
    check_out TEXT,
    working_hours REAL NOT NULL DEFAULT 0,
    UNIQUE(employee_id, work_date),
    FOREIGN KEY(employee_id) REFERENCES employees(id)
);

CREATE TABLE remote_work_requests (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    work_date TEXT NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    approved_by INTEGER,
    FOREIGN KEY(employee_id) REFERENCES employees(id),
    FOREIGN KEY(approved_by) REFERENCES employees(id)
);

CREATE TABLE leave_balances (
    employee_id INTEGER PRIMARY KEY,
    annual_total REAL NOT NULL,
    annual_used REAL NOT NULL DEFAULT 0,
    sick_total REAL NOT NULL,
    sick_used REAL NOT NULL DEFAULT 0,
    casual_total REAL NOT NULL,
    casual_used REAL NOT NULL DEFAULT 0,
    FOREIGN KEY(employee_id) REFERENCES employees(id)
);

CREATE TABLE leave_requests (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    leave_type TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    days REAL NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    approved_by INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY(employee_id) REFERENCES employees(id),
    FOREIGN KEY(approved_by) REFERENCES employees(id)
);

CREATE TABLE candidates (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role_applied TEXT NOT NULL,
    stage TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE interviews (
    id INTEGER PRIMARY KEY,
    candidate_id INTEGER NOT NULL,
    interview_type TEXT NOT NULL,
    interview_date TEXT NOT NULL,
    interviewer_employee_id INTEGER NOT NULL,
    score REAL,
    result TEXT NOT NULL,
    FOREIGN KEY(candidate_id) REFERENCES candidates(id),
    FOREIGN KEY(interviewer_employee_id) REFERENCES employees(id)
);

CREATE TABLE offers (
    id INTEGER PRIMARY KEY,
    candidate_id INTEGER NOT NULL,
    offered_role TEXT NOT NULL,
    offer_date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY(candidate_id) REFERENCES candidates(id)
);

CREATE TABLE performance_reviews (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    review_period TEXT NOT NULL,
    score REAL NOT NULL,
    manager_feedback TEXT NOT NULL,
    review_status TEXT NOT NULL,
    FOREIGN KEY(employee_id) REFERENCES employees(id)
);

CREATE TABLE training_courses (
    id INTEGER PRIMARY KEY,
    title TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    mandatory INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE training_assignments (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    progress_percentage REAL NOT NULL DEFAULT 0,
    due_date TEXT,
    UNIQUE(employee_id, course_id),
    FOREIGN KEY(employee_id) REFERENCES employees(id),
    FOREIGN KEY(course_id) REFERENCES training_courses(id)
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    department_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT,
    FOREIGN KEY(department_id) REFERENCES departments(id)
);

CREATE TABLE project_members (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    project_role TEXT NOT NULL,
    UNIQUE(project_id, employee_id),
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(employee_id) REFERENCES employees(id)
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    assigned_to INTEGER NOT NULL,
    title TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    due_date TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(assigned_to) REFERENCES employees(id)
);

CREATE TABLE payroll (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    pay_month TEXT NOT NULL,
    base_salary REAL NOT NULL,
    allowance REAL NOT NULL DEFAULT 0,
    bonus REAL NOT NULL DEFAULT 0,
    deductions REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    UNIQUE(employee_id, pay_month),
    FOREIGN KEY(employee_id) REFERENCES employees(id)
);

CREATE TABLE expense_claims (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT NOT NULL,
    claim_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    reviewed_by INTEGER,
    FOREIGN KEY(employee_id) REFERENCES employees(id),
    FOREIGN KEY(reviewed_by) REFERENCES employees(id)
);

CREATE TABLE assets (
    id INTEGER PRIMARY KEY,
    asset_tag TEXT UNIQUE NOT NULL,
    asset_type TEXT NOT NULL,
    model TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE asset_assignments (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    assigned_date TEXT NOT NULL,
    returned_date TEXT,
    status TEXT NOT NULL,
    FOREIGN KEY(asset_id) REFERENCES assets(id),
    FOREIGN KEY(employee_id) REFERENCES employees(id)
);

CREATE TABLE document_records (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER,
    document_type TEXT NOT NULL,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    visibility TEXT NOT NULL DEFAULT 'private',
    created_at TEXT NOT NULL,
    FOREIGN KEY(employee_id) REFERENCES employees(id)
);

CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY(employee_id) REFERENCES employees(id)
);

CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY,
    actor_user_id INTEGER,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT,
    details TEXT,
    created_at TEXT NOT NULL
);
