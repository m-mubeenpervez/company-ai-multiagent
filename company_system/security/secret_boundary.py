"""Host-only credentials and last-mile model protection.

No credential belongs in ADK state, messages or tool-call events. The context
variable is scoped to the trusted Runner invocation, not controlled by a model.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
import logging
import os
import re
from threading import RLock

_token: ContextVar[str] = ContextVar("companyai_host_token", default="")
_known: set[str] = set()
_lock = RLock()
_json_credential = re.compile(
    r'''(?i)(["'](?:password|new[_-]?password|api[_-]?key|session[_-]?(?:token|secret)|access[_-]?token|refresh[_-]?token|client[_-]?secret|authorization)["']\s*:\s*)["'][^"'\r\n]*["']'''
)
_credential_text = re.compile(
    r"(?i)(?:password|passwd|pwd|api[_ -]?key|access[_ -]?token|refresh[_ -]?token|"
    r"session[_ -]?(?:token|secret)|authorization)[ \t]*[:=][ \t]*[^\s\",;]{4,}|"
    r"\bbearer[ \t]+[A-Za-z0-9._~-]{16,}|AIza[A-Za-z0-9_-]{30,}|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----"
)


def remember_secret(value: str) -> None:
    # Values stay in host memory for redaction, never in reports or ADK state.
    if isinstance(value, str) and value:
        with _lock:
            if len(_known) >= 4096 and value not in _known:
                raise RuntimeError("Local redaction capacity reached; restart the local application.")
            _known.add(value)


def redact(value: str) -> str:
    with _lock:
        secrets = set(_known)
    secrets.update(os.getenv(key, "") for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY"))
    for secret in sorted(filter(None, secrets), key=len, reverse=True):
        value = value.replace(secret, "[REDACTED]")
    value = _json_credential.sub(r'\1"[REDACTED]"', value)
    return _credential_text.sub("[REDACTED CREDENTIAL]", value)


def reject_secret_text(text: str) -> None:
    if not isinstance(text, str) or redact(text) != text:
        raise ValueError("Sensitive input rejected. Use the secure credential form; never paste secrets into chat.")


def sanitize_payload(value):
    """Remove secret fields even in JSON text nested inside MCP content."""
    import json
    sensitive = {"password", "newpassword", "passwordhash", "passwordsalt", "apikey",
                 "sessiontoken", "sessionsecret", "accesstoken", "refreshtoken", "authorization", "clientsecret"}
    if isinstance(value, dict):
        return {key: sanitize_payload(child) for key, child in value.items()
                if str(key).casefold().replace("_", "").replace("-", "") not in sensitive}
    if isinstance(value, list):
        return [sanitize_payload(child) for child in value]
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except (ValueError, TypeError):
            return redact(value)
        if isinstance(parsed, (dict, list)):
            return json.dumps(sanitize_payload(parsed), ensure_ascii=False)
        return redact(value)
    return value


@contextmanager
def host_token(token: str):
    remember_secret(token)
    marker = _token.set(token)
    try:
        yield
    finally:
        _token.reset(marker)


def current_token() -> str:
    return _token.get()


def install_log_redaction() -> None:
    if getattr(logging.getLogRecordFactory(), "companyai_redacted", False):
        return
    previous = logging.getLogRecordFactory()

    def factory(*args, **kwargs):
        record = previous(*args, **kwargs)
        record.msg = redact(record.getMessage())
        record.args = ()
        if record.exc_info:
            # Exception repr/locals can contain passwords. Emit only the type.
            record.msg += " [exception: " + record.exc_info[0].__name__ + "]"
            record.exc_info = None
            record.exc_text = None
        return record

    factory.companyai_redacted = True
    logging.setLogRecordFactory(factory)


def guard_model_request(callback_context, llm_request):
    """Reject contaminated prompts at the final ADK callback before generation."""
    reject_secret_text(llm_request.model_dump_json(exclude_none=True))
    if not current_token():
        raise ValueError("Model execution requires an authenticated host invocation.")


def fingerprint_secret(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
