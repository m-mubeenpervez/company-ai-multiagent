from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DB = ROOT / "company_system" / "database" / "company.db"
SOURCE_QDRANT = ROOT / "company_system" / "qdrant_storage"


def prepare_runtime() -> dict[str, Path]:
    sys.path.insert(0, str(ROOT))
    from evaluations.runtime_isolation import prepare_isolated_runtime
    paths = prepare_isolated_runtime("existing_regressions")
    return {"root": paths["runtime_root"], "db": paths["database"], "qdrant": paths["qdrant"]}


def run_script(python: str, script: Path, env: dict[str, str]) -> None:
    print(f"\nRUN | {script.relative_to(ROOT)}")
    completed = subprocess.run(
        [python, str(script)],
        cwd=ROOT,
        env=env,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(f"FAILED | {script.relative_to(ROOT)} (exit {completed.returncode})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CompanyAI regression tests against copied local data.")
    parser.add_argument("--live", action="store_true", help="Also run Gemini API, live routing, and live RAG tests.")
    args = parser.parse_args()

    runtime = prepare_runtime()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    env["COMPANYAI_DB_PATH"] = str(runtime["db"])
    env["COMPANYAI_QDRANT_PATH"] = str(runtime["qdrant"])

    offline_tests = [
        "tests/test_database_sanity.py",
        "tests/test_routing_regression.py",
        "tests/test_security_regression.py",
        "tests/test_mcp_architecture.py",
        "tests/test_mcp_catalog.py",
        "tests/test_mcp_security_regression.py",
        "tests/test_gemini_configuration.py",
        "tests/test_rag.py",
        "tests/test_rag_chunker_quality.py",
        "tests/test_release_safety.py",
        "tests/test_secret_boundary.py",
    ]

    print("CompanyAI isolated regression suite")
    print(f"Test database: {runtime['db']}")
    print(f"Test Qdrant:   {runtime['qdrant']}")
    print("The active project database and Qdrant directory will not be modified.")

    for relative in offline_tests:
        run_script(sys.executable, ROOT / relative, env)

    if args.live:
        live_tests = [
            "verify_gemini.py",
            "tests/test_gemini_live.py",
            "tests/test_llm_routing_live.py",
            "tests/test_rag_live.py",
        ]
        for relative in live_tests:
            run_script(sys.executable, ROOT / relative, env)

    print("\nALL REQUESTED ISOLATED REGRESSION TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
