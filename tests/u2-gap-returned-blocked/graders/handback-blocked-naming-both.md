---
# piece.md says blocked (labeled "Status:" anywhere, or as its unlabeled first line, which is how go's Done step 1 writes the status) and names both stores.
type: regex
target:
  source: file
  path: run/results/piece.md
pattern: '^(?=\s*[ \t*#>-]*(?:Status[ \t*]*:[ \t*]*)?(?:[Bb]locked|[Nn]eeds[_ ]context)|[\s\S]*?(?:^|\n)[ \t*#>-]*Status[ \t*]*:[ \t*]*(?:[Bb]locked|[Nn]eeds[_ ]context))(?=[\s\S]*[Ll]edger[-_ ][Ss]tore)(?=[\s\S]*[Aa]rchive[-_ ][Ss]tore)'
weight: 3
---
