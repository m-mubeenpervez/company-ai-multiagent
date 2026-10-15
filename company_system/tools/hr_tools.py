from __future__ import annotations

from datetime import datetime
from google.adk.tools import ToolContext
from company_system.database.db import get_connection, row_to_dict
from company_system.security.authz import require_roles, log_audit
from company_system.security.passwords import hash_password

VALID_ROLES = {"hr","manager","employee","intern","recruiter","finance","it","admin"}

def list_employees(tool_context: ToolContext) -> dict:
    """List company employees. HR and managers only."""
    user, error = require_roles(tool_context, {"hr","manager","admin"})
    if error: return error
    conn = get_connection()
    rows = conn.execute(
        """SELECT e.id,e.employee_code,e.full_name,e.email,d.name department,e.designation,
                  e.employment_type,e.status,e.manager_employee_id
           FROM employees e JOIN departments d ON d.id=e.department_id ORDER BY e.id"""
    ).fetchall()
    conn.close()
    if user["role"] == "manager":
        rows = [r for r in rows if r["manager_employee_id"] == user["employee_id"] or r["id"] == user["employee_id"]]
    return {"status":"success","employees":[dict(r) for r in rows]}

def create_employee(
    employee_code: str,
    full_name: str,
    email: str,
    department_id: int,
    designation: str,
    employment_type: str,
    manager_employee_id: int,
    joining_date: str,
    tool_context: ToolContext,
) -> dict:
    """Create an employee record. HR only."""
    user, error = require_roles(tool_context, {"hr"})
    if error: return error
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO employees(employee_code,full_name,email,department_id,designation,employment_type,
           manager_employee_id,joining_date,status,work_location)
           VALUES (?,?,?,?,?,?,?,?,'active','Lahore')""",
        (employee_code,full_name,email,department_id,designation,employment_type,manager_employee_id,joining_date),
    )
    conn.commit()
    employee_id = cur.lastrowid
    conn.close()
    log_audit(user["user_id"],"create_employee","employee",employee_id,full_name)
    return {"status":"success","employee_id":employee_id}

def update_employee_status(employee_id: int, status: str, tool_context: ToolContext) -> dict:
    """Update an employee lifecycle status. HR only."""
    user, error = require_roles(tool_context, {"hr"})
    if error: return error
    conn = get_connection()
    conn.execute("UPDATE employees SET status=? WHERE id=?", (status, employee_id))
    conn.commit()
    conn.close()
    log_audit(user["user_id"],"update_employee_status","employee",employee_id,status)
    return {"status":"success","employee_id":employee_id,"new_status":status}

def create_user_credentials(
    employee_id: int,
    username: str,
    password: str,
    role: str,
    tool_context: ToolContext,
) -> dict:
    """Create CompanyAI login credentials for an employee. ONLY HR can do this."""
    user, error = require_roles(tool_context, {"hr"})
    if error: return error
    role = role.strip().lower()
    if role not in VALID_ROLES:
        return {"status":"error","message":f"Invalid role. Allowed: {sorted(VALID_ROLES)}"}
    salt, pwd_hash = hash_password(password)
    conn = get_connection()
    employee = conn.execute("SELECT id,full_name FROM employees WHERE id=?", (employee_id,)).fetchone()
    if not employee:
        conn.close()
        return {"status":"error","message":"Employee does not exist."}
    try:
        conn.execute(
            """INSERT INTO users(username,password_salt,password_hash,role,employee_id,is_active,created_at)
               VALUES (?,?,?,?,?,1,?)""",
            (username.strip(),salt,pwd_hash,role,employee_id,datetime.utcnow().isoformat(timespec="seconds")),
        )
        conn.commit()
    except Exception as exc:
        conn.close()
        return {"status":"error","message":str(exc)}
    conn.close()
    log_audit(user["user_id"],"create_credentials","user",username,f"employee_id={employee_id}, role={role}")
    return {"status":"success","username":username,"role":role,"employee_id":employee_id}

def update_user_credentials(
    username: str,
    new_password: str,
    new_role: str,
    tool_context: ToolContext,
) -> dict:
    """Update a user's password and/or role. ONLY HR can do this. Use empty string for a field that should not change."""
    user, error = require_roles(tool_context, {"hr"})
    if error: return error
    conn = get_connection()
    target = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    if not target:
        conn.close()
        return {"status":"error","message":"User not found."}

    if new_role:
        new_role = new_role.strip().lower()
        if new_role not in VALID_ROLES:
            conn.close()
            return {"status":"error","message":"Invalid role."}
        conn.execute("UPDATE users SET role=? WHERE username=?", (new_role, username))

    if new_password:
        salt, pwd_hash = hash_password(new_password)
        conn.execute(
            "UPDATE users SET password_salt=?,password_hash=? WHERE username=?",
            (salt,pwd_hash,username),
        )

    conn.commit()
    conn.close()
    log_audit(user["user_id"],"update_credentials","user",username,f"role={new_role or 'unchanged'}")
    return {"status":"success","username":username}

def delete_user_credentials(username: str, tool_context: ToolContext) -> dict:
    """Delete CompanyAI login credentials. ONLY HR can do this. HR cannot delete the account currently logged into the session."""
    user, error = require_roles(tool_context, {"hr"})
    if error: return error
    if username == user["username"]:
        return {"status":"error","message":"HR cannot delete the credentials currently being used for this session."}
    conn = get_connection()
    target = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    if not target:
        conn.close()
        return {"status":"error","message":"User not found."}
    conn.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()
    log_audit(user["user_id"],"delete_credentials","user",username,"hard delete requested by HR")
    return {"status":"success","deleted_username":username}
