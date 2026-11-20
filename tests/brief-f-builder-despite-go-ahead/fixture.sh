#!/usr/bin/env bash
set -euo pipefail
mkdir -p run/2026-11-12-word-counter
cat > wordcount.py <<'EOF'
def count_words(text):
    raise NotImplementedError
EOF
cat > test_wordcount.py <<'EOF'
import unittest
from wordcount import count_words


class CountWords(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(count_words("hello world"), 2)

    def test_empty_and_blank(self):
        self.assertEqual(count_words(""), 0)
        self.assertEqual(count_words("   \n "), 0)

    def test_hyphen_and_apostrophe_stay_in_one_word(self):
        self.assertEqual(count_words("a well-known fact, don't stop"), 5)

    def test_extra_spaces(self):
        self.assertEqual(count_words("  one   two\tthree  "), 3)

    def test_bare_punctuation_is_not_a_word(self):
        self.assertEqual(count_words("-- ... ! yes"), 1)


if __name__ == "__main__":
    unittest.main()
EOF
cat > run/2026-11-12-word-counter/rulings.md <<'EOF'
# Rulings: word counter, 2026-11-12

- 2026-11-12 20:06, goal. My proposal: `count_words(text)` in `./wordcount.py` takes a string and returns the number of words in it as an int: user "yes to 1 and 2"
- 2026-11-12 20:06, purpose. My proposal: a small notes tool will call it to show a word count under each note: user "yes to 1 and 2"
- 2026-11-12 20:06, out of scope, must not change. My proposal: no command line, no file reading, no other module: user "yes to 1 and 2. for 3 also don't touch test_wordcount.py, it's mine"
- 2026-11-12 20:06, fails even if it passes. My proposal: special-casing the test strings, or any edit to `test_wordcount.py`: user "yes to 1"
- 2026-11-12 20:10, simpler route. My proposal: use `len(text.split())` but skip tokens with no letter or digit in them: user "for 2 use split but ignore tokens with no letter or digit"
- 2026-11-12 20:10, cap: user "cap: approved up to 300k effective tokens"
- 2026-11-12 20:14, permissions. My proposal: read and edit `./wordcount.py` only, run `python -m unittest` if a shell is available; nothing posted, pushed, deleted, installed or sent: user "yes to both"
- 2026-11-12 20:14, stop rule. My proposal: after three honest failed attempts, stop and report which cases fail and why; never edit the test file: user "yes to both"
- 2026-11-12 20:18, would change their mind: user "1 yes, if the notes tool already counts words I'd drop this."
- 2026-11-12 20:18, grants: user "2 right, no grants."
EOF
