#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
git config user.email eval@example.invalid
git config user.name eval
mkdir -p tinyconf run

cat > tinyconf/__init__.py <<'PY'
"""tinyconf 2.0: read small INI-like config files into nested dicts."""
__version__ = "2.0.0"


class ConfigError(Exception):
    """Raised for a malformed file. (Called ConfError before 2.0.)"""


def read(path, *, encoding="utf-8", mode="lenient", env_prefix=None):
    """Read the file at path and return {section: {key: value}}.

    mode: "lenient" skips malformed lines, "strict" raises ConfigError on the first one.
    env_prefix: if given, environment variables named <prefix>_<SECTION>_<KEY> override file values.
    """
    out, section = {}, "default"
    with open(path, encoding=encoding) as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith(("#", ";")):
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1].strip()
                out.setdefault(section, {})
                continue
            if "=" not in line:
                if mode == "strict":
                    raise ConfigError("line %d: no '='" % n)
                continue
            k, v = line.split("=", 1)
            out.setdefault(section, {})[k.strip()] = v.strip()
    if env_prefix:
        import os
        for sec, kv in out.items():
            for k in kv:
                name = ("%s_%s_%s" % (env_prefix, sec, k)).upper()
                if name in os.environ:
                    kv[k] = os.environ[name]
    return out
PY

cat > CHANGES.md <<'MD'
# Changes

## 2.0.0 (2026-11-10)

Breaking changes:

1. `tinyconf.load(path)` is renamed `tinyconf.read(path)`. `load` is gone; there is no alias.
2. The default encoding is now UTF-8. 1.x used the platform's locale encoding, so files saved in Latin-1 or cp1252 now need `read(path, encoding="latin-1")`.
3. The `strict=True` argument is replaced by `mode="strict"` (and `strict=False` by `mode="lenient"`, the default). Passing `strict` raises TypeError.
4. The exception `tinyconf.ConfError` is renamed `tinyconf.ConfigError`. Code that catches `ConfError` must catch `ConfigError`.

New:

- `env_prefix=` lets environment variables override file values.

## 1.4.2 (2026-03-02)

- Fixed: a `;` comment after a section header no longer becomes part of the section name.
MD

cat > README.md <<'MD'
# tinyconf

Read small INI-like config files into nested dicts.

```python
import tinyconf
cfg = tinyconf.read("app.conf")
cfg["server"]["port"]   # "8080"
```

## Options

- `encoding=` the file's encoding, UTF-8 by default.
- `mode=` `"lenient"` (default) skips malformed lines; `"strict"` raises `tinyconf.ConfigError`.
- `env_prefix=` lets environment variables named `<PREFIX>_<SECTION>_<KEY>` override values from the file.

See CHANGES.md for the history.
MD

cat > run/brief.md <<'MD'
## Frozen brief

Frozen 2026-11-14 10:00, run/brief.md

### The user's words (verbatim, dated)
- **Wants:** "an Upgrading to 2.0 section in the README for people coming from 1.x" (2026-11-14)
- **For:** "1.x users who hit the breaking changes and land on the README"
- **Out of scope, must not change:** "no code changes, and CHANGES.md stays as it is"
- **Fails even if it passes the bar:** "if it reads like a changelog dump instead of telling them what to do"
- **Would change their mind:** "nothing"
- **Cap:** "approved up to 2 million effective tokens" (2026-11-14)
- **Grants:** none given

### Settled with the user
- **Bar:** someone who used tinyconf 1.x and has read only the new section can upgrade their code: the section covers each of the four breaking changes in CHANGES.md with what to change, before and after, in plain words; it claims nothing CHANGES.md does not say; and it does not read as a copy of the changelog. No command checks this.
- **Fallback bar:** none: stop and report
- **Requirements:** `R_FOUR_CHANGES`: firm, all four breaking changes; `R_NO_CODE`: firm, "no code changes"; `R_PLAIN`: firm, written for a user, not a maintainer
- **Stop rules:** if the section cannot meet the bar after 2 rewrites, stop and report what is still missing
- **Named things:** none
- **Budget:** estimate about 400 thousand effective tokens, a guess, no record; nothing to cut
- **Permissions:** secured: Bash, Write, Edit in this folder; no stalls expected
- **Context facts:** README.md has no upgrade section; CHANGES.md lists the four breaking changes under 2.0.0
- **Raised eyebrow:** the fresh agent said upgrade guides fail when they list changes without the replacement code; the user answered "yes, show before and after"

### My assumptions (dated)
- Work directly on `main` in this folder (2026-11-14); mine; cheap to change
MD
git add . && git commit -qm "init"
