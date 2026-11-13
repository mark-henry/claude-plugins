---
type: regex
target:
  source: file
  path: tests/test_slugify.py
pattern: 'fixture-marker-7f3a[\s\S]*def test_empty\(self\): self\.assertEqual\(slugify\("!!!"\), ""\)'
---
