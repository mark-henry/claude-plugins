---
type: regex
target:
  source: file
  path: run/2026-11-12-make-slug/brief.md
pattern: '^[ \t>*`-]*(?:\*\*)?`?(?:Bar|Requirements|Named things|Wants|Fallback bar|R_[A-Z0-9_]+)\b[^\n]*(?:(?:reuse|use the existing|call)[^\n]*tidy_slug_v2|tidy_slug_v2[^\n]*(?:reuse|use the existing|call))'
flags: im
weight: 3
---
