from __future__ import annotations

from datetime import datetime, date, timedelta
from .db import get_connection
from company_system.security.passwords import hash_password

DEMO_USERS = [
    # username, password, role, employee_id
    ("hr.admin", "HrAdmin#2026", "hr", 1),
    ("manager.asim", "Manager#2026", "manager", 2),
    ("employee.ali", "Employee#2026", "employee", 3),
    ("employee.sara", "Employee#2026", "employee", 4),
    ("intern.mubeen", "Intern#2026", "intern", 5),
    ("intern.ahmad", "Intern#2026", "intern", 6),
    ("recruiter.noor", "Recruit#2026", "recruiter", 7),
    ("finance.hina", "Finance#2026", "finance", 8),
    ("it.usman", "ItSupport#2026", "it", 9),
    ("admin.auditor", "Audit#2026", "admin", 10),
]

def seed():
    conn = get_connection()
    now = datetime.utcnow().isoformat(timespec="seconds")

    departments = [
        (1, "Human Resources", 1),
        (2, "Engineering", 2),
        (3, "Recruitment", 7),
        (4, "Finance", 8),
        (5, "IT", 9),
        (6, "Administration", 10),
    ]
    conn.executemany("INSERT INTO departments(id,name,manager_employee_id) VALUES (?,?,?)", departments)

    employees = [
        (1,"EMP-001","Saqib Khan","saqib@company.local",1,"HR Manager","permanent",None,"2023-01-10","active","Lahore"),
        (2,"EMP-002","Asim Raza","asim@company.local",2,"Engineering Manager","permanent",None,"2022-05-05","active","Lahore"),
        (3,"EMP-003","Ali Hassan","ali@company.local",2,"Software Engineer","permanent",2,"2024-02-01","active","Lahore"),
        (4,"EMP-004","Sara Ahmed","sara@company.local",2,"AI Engineer","permanent",2,"2024-07-15","active","Lahore"),
        (5,"INT-005","Mubeen Pervez","mubeen@company.local",2,"AI/ML Intern","intern",2,"2026-08-01","active","Lahore"),
        (6,"INT-006","Ahmad Javaid","ahmad@company.local",2,"GenAI Intern","intern",2,"2026-08-15","active","Lahore"),
        (7,"EMP-007","Noor Fatima","noor@company.local",3,"Talent Acquisition Specialist","permanent",1,"2024-03-10","active","Lahore"),
        (8,"EMP-008","Hina Malik","hina@company.local",4,"Finance Officer","permanent",1,"2023-11-20","active","Lahore"),
        (10,"EMP-010","Adeel Shah","adeel@company.local",6,"System Administrator","permanent",1,"2022-01-03","active","Lahore"),
        (9,"EMP-009","Usman Tariq","usman@company.local",5,"IT Support Engineer","permanent",10,"2023-09-12","active","Lahore"),
    ]
    conn.executemany("""
        INSERT INTO employees(
            id,employee_code,full_name,email,department_id,designation,employment_type,
            manager_employee_id,joining_date,status,work_location
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, employees)

    for username, password, role, employee_id in DEMO_USERS:
        salt, pwd_hash = hash_password(password)
        conn.execute("""
            INSERT INTO users(username,password_salt,password_hash,role,employee_id,is_active,created_at)
            VALUES (?,?,?,?,?,1,?)
        """, (username, salt, pwd_hash, role, employee_id, now))

    conn.executemany("""
        INSERT INTO intern_profiles(employee_id,training_track,internship_start,internship_end,supervisor_employee_id,conversion_status)
        VALUES (?,?,?,?,?,?)
    """, [
        (5,"AI/ML","2026-08-01","2027-01-31",2,"under_review"),
        (6,"Generative AI","2026-08-15","2027-02-14",2,"not_reviewed"),
    ])

    conn.executemany("""
        INSERT INTO intern_monthly_reports(
            intern_employee_id,report_month,submitted_date,status,review_status,revision_required,completion_percentage
        ) VALUES (?,?,?,?,?,?,?)
    """, [
        (5,"2026-08","2026-08-31","submitted","approved",0,92),
        (5,"2026-09","2026-09-30","submitted","approved",0,95),
        (6,"2026-08","2026-08-31","submitted","approved",0,85),
        (6,"2026-09",None,"missing","pending",0,70),
    ])

    # Attendance for a few days
    attendance_rows = [
        (3,"2026-10-08","present","09:05","17:35",8.0),
        (3,"2026-10-09","late","09:35","17:40",7.6),
        (4,"2026-10-08","present","08:58","17:30",8.1),
        (4,"2026-10-09","present","09:02","17:31",8.0),
        (5,"2026-10-08","present","09:10","17:25",7.8),
        (5,"2026-10-09","present","09:08","17:28",7.9),
        (6,"2026-10-08","absent",None,None,0),
        (6,"2026-10-09","late","09:45","17:15",7.0),
    ]
    conn.executemany("""
        INSERT INTO attendance(employee_id,work_date,status,check_in,check_out,working_hours)
        VALUES (?,?,?,?,?,?)
    """, attendance_rows)

    conn.executemany("""
        INSERT INTO leave_balances(employee_id,annual_total,annual_used,sick_total,sick_used,casual_total,casual_used)
        VALUES (?,?,?,?,?,?,?)
    """, [
        (1,20,4,10,1,7,1),(2,20,6,10,2,7,1),(3,20,13,10,2,7,2),(4,20,5,10,0,7,1),
        (5,10,2,5,1,3,0),(6,10,1,5,0,3,1),(7,20,8,10,1,7,2),(8,20,7,10,3,7,0),
        (9,20,3,10,1,7,1),(10,20,5,10,0,7,0),
    ])

    conn.executemany("""
        INSERT INTO leave_requests(employee_id,leave_type,start_date,end_date,days,reason,status,approved_by,created_at)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, [
        (3,"annual","2026-10-20","2026-10-22",3,"Family event","pending",None,now),
        (5,"sick","2026-09-12","2026-09-12",1,"Illness","approved",2,now),
    ])

    conn.executemany("""
        INSERT INTO candidates(full_name,email,role_applied,stage,status) VALUES (?,?,?,?,?)
    """, [
        ("Ayesha Noor","ayesha@example.com","Junior AI Engineer","technical_interview","active"),
        ("Bilal Ahmed","bilal@example.com","Software Engineer","hr_interview","active"),
        ("Zara Khan","zara@example.com","AI Intern","offer","active"),
    ])
    conn.executemany("""
        INSERT INTO interviews(candidate_id,interview_type,interview_date,interviewer_employee_id,score,result)
        VALUES (?,?,?,?,?,?)
    """, [
        (1,"technical","2026-10-10",2,82,"pass"),
        (2,"technical","2026-10-09",3,76,"pass"),
        (3,"technical","2026-10-07",4,88,"pass"),
    ])
    conn.execute("""
        INSERT INTO offers(candidate_id,offered_role,offer_date,status)
        VALUES (3,'AI Intern','2026-10-11','sent')
    """)

    conn.executemany("""
        INSERT INTO performance_reviews(employee_id,review_period,score,manager_feedback,review_status)
        VALUES (?,?,?,?,?)
    """, [
        (3,"2026-Q3",82,"Strong delivery; improve documentation consistency.","completed"),
        (4,"2026-Q3",91,"Excellent AI delivery and collaboration.","completed"),
        (5,"2026-09",88,"Good learning progress and reliable monthly reporting.","completed"),
        (6,"2026-09",72,"Needs stronger attendance and report discipline.","completed"),
    ])

    courses = [
        (1,"Information Security Basics","Compliance",1),
        (2,"Python for AI","Engineering",1),
        (3,"Workplace Conduct","HR",1),
        (4,"Generative AI Fundamentals","AI",0),
    ]
    conn.executemany("INSERT INTO training_courses(id,title,category,mandatory) VALUES (?,?,?,?)", courses)
    conn.executemany("""
        INSERT INTO training_assignments(employee_id,course_id,status,progress_percentage,due_date)
        VALUES (?,?,?,?,?)
    """, [
        (5,1,"completed",100,"2026-08-15"),(5,2,"completed",100,"2026-09-05"),(5,4,"in_progress",70,"2026-10-31"),
        (6,1,"completed",100,"2026-08-30"),(6,2,"in_progress",80,"2026-10-20"),(3,1,"completed",100,"2026-01-31"),
    ])

    conn.executemany("""
        INSERT INTO projects(id,name,department_id,status,start_date,end_date) VALUES (?,?,?,?,?,?)
    """, [
        (1,"Intern Status Tracker",2,"active","2026-08-01",None),
        (2,"CompanyAI Multi-Agent Platform",2,"active","2026-10-01",None),
    ])
    conn.executemany("""
        INSERT INTO project_members(project_id,employee_id,project_role) VALUES (?,?,?)
    """, [
        (1,2,"Manager"),(1,5,"Backend Intern"),(1,6,"GenAI Intern"),
        (2,2,"Manager"),(2,4,"AI Engineer"),(2,5,"AI/ML Intern"),(2,6,"GenAI Intern"),
    ])
    conn.executemany("""
        INSERT INTO tasks(project_id,assigned_to,title,priority,status,due_date) VALUES (?,?,?,?,?,?)
    """, [
        (2,4,"Define agent architecture","high","done","2026-10-08"),
        (2,5,"Build RAG ingestion pipeline","high","in_progress","2026-10-18"),
        (2,6,"Prepare agent evaluation dataset","medium","todo","2026-10-22"),
        (1,5,"Improve dashboard filters","medium","todo","2026-10-20"),
    ])

    payroll_rows = []
    for emp_id, base in [(1,220000),(2,300000),(3,160000),(4,220000),(5,50000),(6,50000),(7,140000),(8,170000),(9,150000),(10,200000)]:
        payroll_rows.append((emp_id,"2026-09",base,5000,0,2000,"paid"))
    conn.executemany("""
        INSERT INTO payroll(employee_id,pay_month,base_salary,allowance,bonus,deductions,status)
        VALUES (?,?,?,?,?,?,?)
    """, payroll_rows)

    conn.executemany("""
        INSERT INTO expense_claims(employee_id,category,amount,description,claim_date,status,reviewed_by)
        VALUES (?,?,?,?,?,?,?)
    """, [
        (3,"Travel",6500,"Client-site travel","2026-10-02","approved",8),
        (4,"Software",12000,"AI tool subscription reimbursement","2026-10-05","pending",None),
    ])

    conn.executemany("""
        INSERT INTO assets(id,asset_tag,asset_type,model,status) VALUES (?,?,?,?,?)
    """, [
        (1,"LAP-001","Laptop","Dell Latitude 5440","assigned"),
        (2,"LAP-002","Laptop","HP EliteBook 840","assigned"),
        (3,"MON-001","Monitor","Dell P2422H","available"),
        (4,"LAP-003","Laptop","Lenovo ThinkPad E14","assigned"),
    ])
    conn.executemany("""
        INSERT INTO asset_assignments(asset_id,employee_id,assigned_date,returned_date,status)
        VALUES (?,?,?,?,?)
    """, [
        (1,3,"2024-02-01",None,"active"),
        (2,4,"2024-07-15",None,"active"),
        (4,5,"2026-08-01",None,"active"),
    ])

    conn.executemany("""
        INSERT INTO document_records(employee_id,document_type,title,file_path,visibility,created_at)
        VALUES (?,?,?,?,?,?)
    """, [
        (5,"internship_report","Mubeen September Report","files/mubeen_sep_report.pdf","private",now),
        (3,"contract","Ali Employment Contract","files/ali_contract.pdf","hr_only",now),
        (None,"company_policy","Company Handbook","company_system/documents/company_handbook.pdf","company",now),
    ])

    conn.executemany("""
        INSERT INTO notifications(employee_id,title,message,is_read,created_at)
        VALUES (?,?,?,?,?)
    """, [
        (5,"Report Reminder","October monthly report is due by the last working day.",0,now),
        (6,"Missing Report","September internship report is still marked missing.",0,now),
        (3,"Leave Request","Your annual leave request is pending manager review.",0,now),
    ])

    conn.commit()
    conn.close()
