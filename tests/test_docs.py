"""Docs stay consistent: every feature page follows the template, and no relative link is broken."""
import re, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "docs/features/_template.md"
SKIP = {".git", ".claude", "node_modules"}


class TestDocs(unittest.TestCase):
    def test_feature_pages_follow_the_template(self):
        headings = re.findall(r"^## (.+)$", TEMPLATE.read_text(encoding="utf-8"), re.M)
        pages = [p for p in sorted((REPO / "docs/features").glob("*.md")) if p != TEMPLATE]
        self.assertGreaterEqual(len(pages), 9)
        for page in pages:
            with self.subTest(page=page.name):
                text = page.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("# Feature: "))
                self.assertIn("Status: ", text.split("\n## ", 1)[0])
                self.assertEqual(re.findall(r"^## (.+)$", text, re.M), headings)

    def test_every_feature_page_is_in_the_index(self):
        index = (REPO / "docs/README.md").read_text(encoding="utf-8")
        for page in (REPO / "docs/features").glob("*.md"):
            if page != TEMPLATE:
                self.assertIn(f"(features/{page.name})", index)

    def test_relative_markdown_links_resolve(self):
        broken = []
        for p in sorted(REPO.rglob("*.md")):
            if SKIP & set(p.relative_to(REPO).parts):
                continue
            for m in re.finditer(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", p.read_text(encoding="utf-8")):
                link = m.group(1)
                if not link.startswith(("http://", "https://", "mailto:")) and not (p.parent / link).exists():
                    broken.append(f"{p.relative_to(REPO).as_posix()} -> {link}")
        self.assertEqual(broken, [])


if __name__ == "__main__":
    unittest.main()
