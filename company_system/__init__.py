# ADK imports this package and exposes root_agent through company_system.agent.
# The guarded import also lets standalone database/setup utilities run before
# google-adk is installed in a brand-new virtual environment.
try:
    from . import agent  # noqa: F401
except ModuleNotFoundError as exc:
    if not (exc.name or '').startswith('google.adk'):
        raise
