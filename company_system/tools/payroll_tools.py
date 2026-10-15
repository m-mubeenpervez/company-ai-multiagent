from __future__ import annotations
from google.adk.tools import ToolContext
from company_system.database.db import get_connection
from company_system.security.authz import require_auth

def get_payroll(employee_id: int, pay_month: str, tool_context: ToolContext) -> dict:
    """Get payroll. Employees/interns can see only their own; HR and Finance can see any employee payroll."""
    user, error = require_auth(tool_context)
    if error: return error
    if user["role"] not in {"hr","finance"} and user["employee_id"] != employee_id:
        return {"status":"forbidden","message":"You can only view your own payroll."}
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM payroll WHERE employee_id=? AND pay_month=?",
        (employee_id,pay_month),
    ).fetchone()
    conn.close()
    if not row: return {"status":"not_found"}
    data = dict(row)
    data["net_pay"] = data["base_salary"] + data["allowance"] + data["bonus"] - data["deductions"]
    return {"status":"success","payroll":data}
