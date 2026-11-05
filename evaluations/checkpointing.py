"""Atomic, provenance-checked evaluation resumption without repeated cases."""
from __future__ import annotations

import json
import math
from pathlib import Path
from datetime import datetime, timezone


def write_json_atomic(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False), encoding="utf-8")
    temporary.replace(path)


class CaseCheckpoint:
    def __init__(self, path: Path, provenance: dict, cases: list[dict], *, resume: bool = False):
        self.path, self.provenance = path, provenance
        self.ids = [case["id"] for case in cases]
        if len(set(self.ids)) != len(self.ids):
            raise ValueError("Duplicate evaluation case IDs are not allowed.")
        self.completed = {}
        if path.exists() and not resume:
            archive = path.with_name(path.stem + "_previous_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + path.suffix)
            archive.write_bytes(path.read_bytes())
        if resume:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("provenance") != provenance or data.get("case_ids") != self.ids:
                raise ValueError("Checkpoint provenance or selected cases changed; use a new output path.")
            results = data.get("results", [])
            seen = [row["id"] for row in results]
            if len(set(seen)) != len(seen) or set(seen) - set(self.ids):
                raise ValueError("Invalid checkpoint case IDs.")
            for row in results:
                if row.get("status") != "completed":
                    continue
                scores = [item.get("score") for item in row.get("metrics", [])]
                if "faithfulness" in row:
                    scores.extend(row.get(name) for name in ("faithfulness", "context_precision", "context_recall"))
                if any(not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 1 for score in scores):
                    raise ValueError("Completed checkpoint contains a missing or invalid metric score.")
            self.completed = {row["id"]: row for row in results if row.get("status") == "completed"}
            # Replaying a partially judged write can duplicate real effects.
            reads = {"login", "logout", "ping_companyai", "search_company_policy", "search_employee_by_name",
                     "attendance_summary", "company_people_summary", "company_operational_summary"}
            for row in results:
                if row.get("status") == "completed":
                    continue
                names = row.get("tool_names", [])
                if any(not name.startswith(("get_", "list_")) and name not in reads for name in names):
                    raise ValueError("Partial write-case checkpoint requires manual review before replay.")

    def save(self, results):
        write_json_atomic(self.path, {"created_at": datetime.now(timezone.utc).isoformat(),
                                     "provenance": self.provenance, "case_ids": self.ids, "results": results})
