import os

# This local application does not export request bodies, credentials or model
# content. Configure before ADK/GenAI imports in every supported entry point.
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"
os.environ["OTEL_PROPAGATORS"] = "baggage"
from company_system.security.secret_boundary import install_log_redaction
install_log_redaction()

# ADK imports company_system.agent when the app runs. Setup/database utilities
# may import this package before Google ADK/GenAI dependencies are installed.
try:
    from . import agent  # noqa: F401
except (ModuleNotFoundError, ImportError) as exc:
    missing = getattr(exc, "name", "") or ""
    message = str(exc)
    if not (missing.startswith("google") or "google" in message.lower() or "mcp" in message.lower()):
        raise
