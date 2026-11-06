# diverge:lite runs

Tune the lite defaults from this table (the full skill's log is [../design/runs.md](../design/runs.md)).

| # | date | question | version | judge | agents | tokens | wall | pick | attack verdicts | pick vs sealed | control | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-11-05 | how to design diverge:lite itself | v0 | Fable high | 11 | 0.63M | 3.9 min | A + B + C + E grafts on v0's shape | 5 wounded | no sealed draft (v0) | — | relay carried an unrelated question; harmless. Led to v1: judge schema + retry, sealed draft, opt-in pairwise control, no background jobs |
| 2 | 2026-11-05 | how to measure LOAD-BEARING-OFF on treated Qwen3.8 (no-think switch broken) | v1 | Fable high | 12 | 0.72M | 7.2 min | A + D + C | 5 wounded | different: same core, but found Qwen3.8's think-token ids differ from Qwen3's (248068/9, not 151667/8) and that enable_thinking=False drops a system line; sealed answer missed both | better | all 5 attackers opened files; the judge's schema worked first try |
