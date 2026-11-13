---
type: regex
target:
  source: file
  path: src/export/codec.py
pattern: '^"""Export codec \(part 2, owned by the export team\): rows <-> CSV text for the finance import\."""\n\nHEADER = "name,amount"\n\n\ndef encode\(rows\):\n    lines = \[HEADER\]\n    for name, amount in rows:\n        lines\.append\(f"\{name\},\{amount\}"\)\n    return "\\n"\.join\(lines\) \+ "\\n"\n\n\ndef decode\(text\):\n    lines = text\.splitlines\(\)\n    if not lines or lines\[0\] != HEADER:\n        raise ValueError\("missing header"\)\n    return \[tuple\(line\.split\(","\)\) for line in lines\[1:\]\]\n$'
weight: 2
---
