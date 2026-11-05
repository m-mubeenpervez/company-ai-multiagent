"""Non-secret evaluation provenance and API quota classification."""
from __future__ import annotations

import hashlib
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def daily_quota_exhausted(error) -> bool:
    from company_system.security.quota import daily_exhausted
    return daily_exhausted(error)


def provider_quota_blocked(error) -> bool:
    text = str(error).lower()
    return daily_quota_exhausted(error) or any(term in text for term in (
        "api_rate_quota_blocked", "429", "resource_exhausted",
    ))


def provenance(dataset: Path) -> dict:
    paths = [dataset, ROOT / "company_system/agent.py", ROOT / "company_system/agents/common.py",
             ROOT / "company_system/routing/semantic_router_agent.py", ROOT / "company_system/rag/chunker.py",
             ROOT / "company_system/rag/retriever.py", ROOT / "evaluations/adk_harness.py",
             ROOT / "evaluations/run_ragas_eval.py", ROOT / "evaluations/run_deepeval_eval.py"]
    paths.extend(ROOT.joinpath("company_system").rglob("*.py"))
    paths.extend(ROOT.joinpath("mcp_server").rglob("*.py"))
    paths.extend([ROOT / "evaluations/reporting.py", ROOT / "evaluations/checkpointing.py", ROOT / "evaluations/gemini_judge.py",
                  ROOT / "evaluations/runtime_isolation.py", ROOT / "requirements.txt", ROOT / "requirements-evaluation.txt",
                  ROOT / "requirements-runtime-lock.txt", ROOT / "requirements-evaluation-lock.txt"])
    paths.extend([ROOT / "evaluations/run_routing_eval.py", ROOT / "evaluations/run_agent_acceptance.py",
                  ROOT / "security/run_prompt_injection_eval.py"])
    paths.extend([ROOT / "company_system/documents/company_handbook.pdf",
                  ROOT / "company_system/database/company.db"])
    import os
    config = {key: os.getenv(key) for key in (
        "GEMINI_LLM_MODEL", "GEMINI_EVAL_MODEL", "GEMINI_ROUTER_MODEL",
        "GEMINI_ROUTER_FALLBACK_MODEL", "GEMINI_ROUTER_MIN_CONFIDENCE", "GEMINI_EMBED_MODEL",
        "GEMINI_EMBED_DIM", "RAG_TOP_K", "RAG_MIN_SCORE",
    )}
    index = ROOT / "company_system/qdrant_storage"
    qdrant_sha256 = {str(path.relative_to(index)): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in index.rglob("*") if path.is_file() and path.name != ".lock"}
    import platform
    from importlib.metadata import distributions
    installed = {dist.metadata["Name"].lower().replace("_", "-"): dist.version for dist in distributions()}
    return {"python_version": platform.python_version(), "configuration": config, "qdrant_sha256": qdrant_sha256,
            "provider_account_sha256": hashlib.sha256((os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "unconfigured").encode()).hexdigest(),
            "installed_versions": dict(sorted(installed.items())),
            "source_sha256": {(str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else "external_dataset/" + path.name):
                              hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
            "versions": {name: version(name) for name in ["google-adk", "google-genai", "ragas", "litellm", "instructor", "deepeval"]}}
