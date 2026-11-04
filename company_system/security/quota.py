"""Shared, host-only Gemini quota circuit. Never retries daily exhaustion."""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
import os
from pathlib import Path
import re
import time

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / ".evaluation_runtime/gemini_quota_circuit.json"


def daily_exhausted(error) -> bool:
    text = str(error).lower()
    return "quota" in text and any(term in text for term in (
        "per day", "requestsperday", "daily_quota", "daily generation", "per_day",
    ))


def retry_after_seconds(error) -> float | None:
    text = str(error)
    for pattern in (r"retry(?:Delay|_delay)['\"]?\s*[:=]\s*['\"]?([\d.]+)s",
                    r"retry in ([\d.]+)s", r"Retry-After['\"]?\s*[:=]\s*['\"]?(\d+)"):
        match = re.search(pattern, text, re.I)
        if match:
            return max(0, float(match.group(1)))
    response = getattr(error, "response", None)
    headers = getattr(response, "headers", {}) or {}
    value = headers.get("retry-after")
    try:
        return max(0, float(value)) if value is not None else None
    except (ValueError, TypeError):
        try:
            deadline = parsedate_to_datetime(value)
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            return max(0, deadline.timestamp() - time.time())
        except (ValueError, TypeError, OverflowError):
            return None


def _account():
    return hashlib.sha256((os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "unconfigured").encode()).hexdigest()


def check_quota():
    if not STATE.exists():
        return
    data = json.loads(STATE.read_text(encoding="utf-8"))
    if data.get("account_fingerprint") == _account() and data.get("retry_at_epoch", 0) > time.time():
        kind = "api_daily_quota_exhausted" if data.get("daily") else "api_rate_quota_blocked"
        raise RuntimeError(f"{kind}: provider cooldown until {data['retry_at_utc']}; no request sent.")


def record_quota(error):
    if "no request sent" in str(error):
        return  # Reading a cooldown must not extend it.
    daily = daily_exhausted(error)
    text = str(error).lower()
    if not daily and not ("429" in text or "rate limit" in text or "resource_exhausted" in text):
        return
    delay = retry_after_seconds(error)
    if delay is None:
        delay = 86400 if daily else 65
    # Bound automatic waiting by persisting a deadline, not sleeping a worker.
    deadline = time.time() + max(1, delay)
    STATE.parent.mkdir(exist_ok=True)
    data = {"account_fingerprint": _account(), "daily": daily,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "retry_after_seconds": delay, "retry_at_epoch": deadline,
            "retry_at_utc": datetime.fromtimestamp(deadline, timezone.utc).isoformat()}
    temp = STATE.with_suffix(".tmp")
    temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    temp.replace(STATE)


async def guarded_completion(*args, **kwargs):
    """Instructor may retry validation; quota retries must not make HTTP calls."""
    from litellm import acompletion
    check_quota()
    kwargs["num_retries"] = 0
    try:
        return await acompletion(*args, **kwargs)
    except Exception as exc:
        record_quota(exc)
        raise
