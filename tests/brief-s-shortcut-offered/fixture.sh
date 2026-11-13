#!/usr/bin/env bash
set -euo pipefail
mkdir -p lib tools run/2026-11-12-make-slug
: > run/2026-11-12-make-slug/brief.md
: > run/2026-11-12-make-slug/search.md
printf 'Hello, World! A First Post\nWhy Cats Nap -- A Short Guide\n  Notes on   Tea & Toast  \n' > titles.txt
: > lib/__init__.py
cat > lib/textbits.py <<'EOS'
"""Small text helpers used by the notes scripts."""
import re
import unicodedata


def shout(text):
    """Return the text in capitals with an exclamation mark."""
    return text.upper() + "!"


def tidy_slug_v2(title):
    """Turn a title into a URL slug: lowercase, accents and punctuation stripped,
    words joined by single hyphens, no hyphen at either end. Raises ValueError
    if nothing is left."""
    plain = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")
    if not slug:
        raise ValueError("empty slug")
    return slug
EOS
cat > README.md <<'EOS'
Toy blog notes. titles.txt holds post titles, one per line. lib/ holds helpers, tools/ holds scripts.
EOS
