from __future__ import annotations

from company_system.rag.retriever import search_policy


def main() -> None:
    result = search_policy("What is the deadline for submitting a monthly internship report?")
    assert result.get("status") == "success", result
    rows = result.get("results") or []
    assert rows, result
    combined = " ".join(str(row.get("text", "")) for row in rows).lower()
    assert "monthly" in combined
    assert "report" in combined
    print("PASS | Live Gemini embedding -> Qdrant policy retrieval works")
    print(f"PASS | Retrieved {len(rows)} grounded policy passages")


if __name__ == "__main__":
    main()
