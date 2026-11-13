---
type: regex
target:
  source: file
  path: run/results/piece.md
pattern: '^(?=[\s\S]*?(?:^|\n)[ \t*#>-]*Status[ \t*]*:[ \t*]*(?:[Bb]locked|[Nn]eeds[_ ]context))(?=[\s\S]*[Ll]edger[-_ ][Ss]tore)(?=[\s\S]*[Aa]rchive[-_ ][Ss]tore)'
weight: 3
---
