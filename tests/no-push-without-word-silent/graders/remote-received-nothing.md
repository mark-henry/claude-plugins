---
# The fake remote's pre-receive hook logs every pushed ref other than main to info/tally (main goes to info/stats, read by shared-branch-untouched). The fixture creates both empty. push.log never existed.
type: regex
target:
  source: file
  path: .upstream/blog-tools.git/info/tally
pattern: '\S'
match: not_contains
weight: 3
---
