"""Content-preservation regressions for policy chunking; no API calls."""
from __future__ import annotations

import re
import sys
import unittest
from collections import Counter
from pathlib import Path

from company_system.rag.chunker import chunk_pages
from company_system.rag.loader import load_pdf_pages


class PolicyChunkQualityTests(unittest.TestCase):
    def test_heading_stays_with_rule_and_wrapped_exception(self):
        chunks = chunk_pages([{
            "source": "rules.pdf", "page": 7,
            "text": "1. Expenses\nExpenses need receipts.\n2. Travel\nTravel requires approval unless a written\nstanding authorization applies.",
        }])
        self.assertEqual(len(chunks), 2)
        self.assertIn("2. Travel\nTravel requires approval unless a written standing authorization applies.", chunks[1]["text"])
        self.assertNotIn("Travel", chunks[0]["text"])
        self.assertEqual((chunks[1]["source"], chunks[1]["page"]), ("rules.pdf", 7))

    def test_oversized_sentence_is_not_cut_or_lost(self):
        sentence = "An authorization remains valid unless " + "a documented condition " * 12 + "applies."
        chunks = chunk_pages([{"source": "rules.pdf", "page": 1, "text": sentence}], chunk_size=80, overlap=10)
        self.assertEqual([chunk["text"] for chunk in chunks], [sentence])

    def test_overlap_uses_complete_sentences_within_the_same_section(self):
        sentences = [f"Rule {i} has a distinct documented condition." for i in range(6)]
        chunks = chunk_pages([{"source": "rules.pdf", "page": 1, "text": "1. Rules\n" + " ".join(sentences)}], chunk_size=140, overlap=50)
        found = []
        for chunk in chunks:
            self.assertTrue(chunk["text"].startswith("1. Rules\n"))
            units = re.split(r"(?<=\.) ", chunk["text"].split("\n", 1)[1])
            self.assertTrue(all(unit in sentences for unit in units))
            found.extend(units)
            self.assertLessEqual(len(chunk["text"]), 140)
        self.assertEqual(set(found), set(sentences))

    def test_continued_heading_keeps_original_pages_and_resets_for_new_title(self):
        pages = [
            {"source": "rules.pdf", "page": 1, "text": "1. Travel\nApproval is required."},
            {"source": "rules.pdf", "page": 2, "text": "A standing authorization can apply."},
            {"source": "rules.pdf", "page": 3, "text": "Safety Overview\nWear protective equipment."},
            {"source": "other.pdf", "page": 1, "text": "A different document has its own rule."},
        ]
        chunks = chunk_pages(pages)
        self.assertTrue(chunks[1]["text"].startswith("1. Travel\n"))
        self.assertEqual(chunks[1]["page"], 2)
        self.assertTrue(chunks[2]["text"].startswith("Safety Overview\n"))
        self.assertNotIn("Travel", chunks[3]["text"])
        self.assertEqual(len(set(chunk["chunk_id"] for chunk in chunks)), len(chunks))

    def test_handbook_content_is_preserved_on_each_original_page(self):
        root = Path(__file__).resolve().parents[1]
        pages = load_pdf_pages(root / "company_system/documents/company_handbook.pdf")
        chunks = chunk_pages(pages)
        for page in pages:
            original = Counter(page["text"].split())
            output = Counter(" ".join(chunk["text"] for chunk in chunks if
                                      (chunk["source"], chunk["page"]) == (page["source"], page["page"])).split())
            self.assertFalse(original - output, f"Missing words on page {page['page']}")

    def test_invalid_parameters_and_empty_pages(self):
        self.assertEqual(chunk_pages([]), [])
        self.assertEqual(chunk_pages([{"source": "empty.pdf", "page": 1, "text": " \n"}]), [])
        for size, overlap in ((0, 0), (100, -1), (100, 100)):
            with self.subTest(size=size, overlap=overlap), self.assertRaises(ValueError):
                chunk_pages([], size, overlap)


if __name__ == "__main__":
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout, verbosity=2))
