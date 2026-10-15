from __future__ import annotations
from google.adk.tools import ToolContext
from company_system.security.authz import require_auth
from company_system.rag.retriever import search_policy

def search_company_policy(query: str, tool_context: ToolContext) -> dict:
    """Search the official company handbook/policy documents using Qdrant RAG. Login required."""
    user, error = require_auth(tool_context)
    if error: return error
    result = search_policy(query)
    if result.get("status") == "success":
        result["grounding_rule"] = "Answer only from these passages. Cite source filename and page number."
    return result
