---
type: regex
target:
  source: file
  path: tests/test_durations.py
pattern: 'fixture-marker-9b2e[\s\S]*def test_trailing_digits\(self\):\s+with self\.assertRaises\(ValueError\): parse_duration\("1h30"\)'
---
