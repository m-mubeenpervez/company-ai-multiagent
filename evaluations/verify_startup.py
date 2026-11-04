"""Check authenticated local ADK application startup and denied development endpoints."""
from __future__ import annotations

import json
import argparse
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "evaluations/results/remediation_startup.json")
    args = parser.parse_args()
    report_path = args.output.resolve()
    if not report_path.is_relative_to(ROOT):
        parser.error("Startup evidence must stay inside this working tree.")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    log_path = report_path.with_suffix(".server.log")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    for previous in (report_path, log_path):
        if previous.exists():
            previous.with_name(previous.stem + "_previous_" + stamp + previous.suffix).write_bytes(previous.read_bytes())
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    env["OTEL_PROPAGATORS"] = "baggage"
    env["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"
    executable = Path(sys.executable)
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen([str(executable), "-m", "company_system.local_web", "--port", str(port)],
                                   cwd=ROOT, env=env, stdout=log, stderr=log,
                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            for _ in range(120):
                if process.poll() is not None:
                    raise RuntimeError("Local server stopped; inspect the output-specific server log")
                try:
                    base = f"http://127.0.0.1:{port}"
                    with urllib.request.urlopen(base + "/", timeout=2) as response:
                        assert response.status == 200
                        assert "CompanyAI" in response.read().decode()
                    denied = {}
                    for endpoint, expected in [("/api/me", 401), ("/list-apps", 404), ("/dev-ui/", 404), ("/debug/trace/x", 404)]:
                        try:
                            urllib.request.urlopen(base + endpoint, timeout=2)
                            raise AssertionError("Endpoint unexpectedly accessible: " + endpoint)
                        except urllib.error.HTTPError as exc:
                            assert exc.code == expected, (endpoint, exc.code)
                            denied[endpoint] = exc.code
                    request = urllib.request.Request(base + "/api/login", data=b'{}',
                        headers={"Content-Type": "application/json", "Origin": "https://evil.invalid"})
                    try:
                        urllib.request.urlopen(request, timeout=2)
                        raise AssertionError("Cross-origin login was accepted")
                    except urllib.error.HTTPError as exc:
                        assert exc.code == 403
                    probes = []
                    for address in sorted(set(socket.gethostbyname_ex(socket.gethostname())[2])):
                        if address.startswith("127."):
                            continue
                        try:
                            connection = socket.create_connection((address, port), timeout=1)
                        except OSError:
                            probes.append({"address": address, "reachable": False})
                        else:
                            connection.close()
                            raise AssertionError("Local app is reachable through a non-loopback interface")
                    from company_system.agent import root_agent
                    assert len(root_agent.sub_agents) == 18
                    report = {"created_at": datetime.now(timezone.utc).isoformat(), "server_log": str(log_path),
                              "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (ROOT / "company_system").rglob("*.py")}, "status": "PASS", "cwd": str(ROOT), "python": sys.executable,
                              "root_agent": root_agent.name, "agents": len(root_agent.sub_agents),
                              "bind": "127.0.0.1", "session_store": "host memory", "ui_http_status": 200,
                              "denied_endpoints": denied, "cross_origin_login": 403,
                              "non_loopback_interface_probes": probes,
                              "note": "Authenticated local UI; stock ADK development endpoints are not mounted."}
                    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
                    print(json.dumps(report, indent=2))
                    return
                except OSError:
                    time.sleep(0.5)
            raise TimeoutError("Local web did not start within 60 seconds")
        finally:
            if os.name == "nt" and process.poll() is None:
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                               capture_output=True, timeout=10, check=False)
            elif process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            with socket.socket() as probe:
                probe.settimeout(1)
                if probe.connect_ex(("127.0.0.1", port)) == 0:
                    raise RuntimeError("Local test server still listens after shutdown")
            if report_path.exists():
                saved = json.loads(report_path.read_text())
                saved["server_shutdown_verified"] = True
                report_path.write_text(json.dumps(saved, indent=2))


if __name__ == "__main__":
    main()
