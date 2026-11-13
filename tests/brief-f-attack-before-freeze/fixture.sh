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
cat > run/2026-11-12-word-counter/search.md <<'EOF'
# Search: word counter, 2026-11-12

Searched: this workspace (only wordcount.py, a stub, and test_wordcount.py); the Python standard library (str.split, re); no outside search needed for a one-function job.

Found: `len(text.split())` counts whitespace-separated tokens and passes four of the five test cases. It fails only the bare-punctuation case ("-- ... ! yes" gives 4, the test wants 1).

Changed: offered the simpler route to the user instead of writing a tokenizer; the user took it with one addition (see rulings.md, 2026-11-12).
EOF
cat > run/2026-11-12-word-counter/rulings.md <<'EOF'
# Rulings: word counter, 2026-11-12

- Goal: `count_words(text)` in `./wordcount.py` takes a string and returns the number of words in it as an int: user "yes to 1 and 2", 2026-11-12
- Purpose: a small notes tool will call it to show a word count under each note: user "yes to 1 and 2", 2026-11-12
- Out of scope, must not change: no command line, no file reading, no other module: user "yes to 1 and 2. for 3 also don't touch test_wordcount.py, it's mine", 2026-11-12
- Fails even if it passes: special-casing the test strings, or any edit to `test_wordcount.py`: user "yes to 1", 2026-11-12
- Simpler route: use `len(text.split())` but skip tokens with no letter or digit in them: user "for 2 use split but ignore tokens with no letter or digit", 2026-11-12
- Cap: user "cap: approved up to 3% of this week's quota", 2026-11-12
EOF
