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

- Goal: `count_words(text)` in `./wordcount.py` takes a string and returns the number of words in it as an int: user "yes to 1 and 2", 2026-11-12
- Purpose: a small notes tool will call it to show a word count under each note: user "yes to 1 and 2", 2026-11-12
- Out of scope, must not change: no command line, no file reading, no other module: user "yes to 1 and 2. for 3 also don't touch test_wordcount.py, it's mine", 2026-11-12
- Fails even if it passes: special-casing the test strings, or any edit to `test_wordcount.py`: user "yes to 1", 2026-11-12
- Simpler route: use `len(text.split())` but skip tokens with no letter or digit in them: user "for 2 use split but ignore tokens with no letter or digit", 2026-11-12
- Cap: user "cap: approved up to 3% of this week's quota", 2026-11-12
- Permissions: read and edit `./wordcount.py` only, run `python -m unittest` if a shell is available; nothing posted, pushed, deleted, installed or sent: user "yes to both", 2026-11-12
- Stop rule: after three honest failed attempts, stop and report which cases fail and why; never edit the test file: user "yes to both", 2026-11-12
- Would change their mind: user "1 yes, if the notes tool already counts words I'd drop this.", 2026-11-12
- Grants: user "2 right, no grants.", 2026-11-12
- Raised eyebrow, answered: user "keep it as is. the notes tool has no word count, I checked. my notes are all English, so text without spaces is out of scope.", 2026-11-12
EOF
cat > run/2026-11-12-word-counter/brief.md <<'EOF'
## Draft brief (not frozen)

Drafted 2026-11-12 20:23, ./run/2026-11-12-word-counter/brief.md    Builder: ./run/2026-11-12-word-counter/brief.builder.md

### The user's words (dated; in quotation marks only what the user typed; an accepted proposal as `<your proposal>: user "approved"`)
- **Wants:** `count_words(text)` in ./wordcount.py takes a string and returns the number of words in it as an int: user "yes to 1 and 2" (2026-11-12)
- **For:** a small notes tool will call it to show a word count under each note: user "yes to 1 and 2" (2026-11-12)
- **Out of scope, must not change:** no command line, no file reading, no other module: user "yes to 1 and 2. for 3 also don't touch test_wordcount.py, it's mine" (2026-11-12)
- **Fails even if it passes the bar:** special-casing the test strings, or any edit to test_wordcount.py: user "yes to 1" (2026-11-12)
- **Would change their mind:** "1 yes, if the notes tool already counts words I'd drop this." (2026-11-12)
- **Cap:** "cap: approved up to 3% of this week's quota" (2026-11-12)
- **Grants:** "2 right, no grants." (2026-11-12)

### Settled with the user
- **Bar:** `python -m unittest test_wordcount` passes all five tests, and test_wordcount.py is byte-for-byte unchanged (hash taken before the run)
- **Fallback bar:** none; after three honest failed attempts, stop and report which cases fail and why
- **Requirements:** firm: use `len(text.split())` but skip tokens with no letter or digit: user "for 2 use split but ignore tokens with no letter or digit"; firm: English only: user "my notes are all English, so text without spaces is out of scope."
- **Stop rules:** three honest failed attempts: stop and report; never edit test_wordcount.py
- **Named things:** ./wordcount.py, ./test_wordcount.py, `str.split`; no substitute: stop
- **Budget:** about 1% of this week's quota, a guess, no record; cap 3% of this week's quota; nothing to cut first, the job is one function
- **Permissions:** read and edit ./wordcount.py only; run `python -m unittest` in the workspace; stall to expect: a prompt for the test command if the shell is not allowed, in which case the run says the tests were not run
- **Context facts:** ./wordcount.py is a stub that raises NotImplementedError; ./test_wordcount.py holds five tests
- **Raised eyebrow:** a fresh agent on the strongest model: the method is standard; the trap is text with no spaces between words; the likeliest reason it is unnecessary is a count the notes tool already shows. The search for the case against found nothing against the method, and the notes tool's code is not here. User: "keep it as is. the notes tool has no word count, I checked. my notes are all English, so text without spaces is out of scope."

### My assumptions (dated)
- none
EOF
cat > run/2026-11-12-word-counter/brief.builder.md <<'EOF'
# Builder's reply: word counter, 2026-11-12

Seat: a fresh agent on the general-use model, given only ./run/2026-11-12-word-counter/brief.md, asked to plan the build from it alone and run what can be run.

Ran: `python -m unittest test_wordcount` on the untouched stub: 5 tests, 5 errors, each NotImplementedError. The check can fail.

Plan from the brief: replace the stub in ./wordcount.py with a count of the tokens from `text.split()` that hold at least one letter or digit, run the tests, report.

Questions where a wrong guess changes what gets built:
1. A token made only of underscores, such as `__`, has no letter or digit. Is it a word? The rule as written says no.

Recommendations:
2. The brief does not say where the result is reported. Recommend `report.md` in the run folder, with the test output.

Permissions the plan needs: edit ./wordcount.py; run `python -m unittest` in the workspace. Both are in the brief.
EOF
