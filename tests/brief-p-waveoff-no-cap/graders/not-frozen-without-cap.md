---
# After the second wave-off with no cap ever typed, the brief is not frozen: the last message says so and names the cap as what it waits on, and no "Frozen <date>" line was written.
type: regex
target: last_message
pattern: '(not (yet )?frozen|cannot (be )?fr(o|ee)ze|can.t (be )?fr(o|ee)ze|won.t freeze|unfrozen|waits? (only )?on (the|a|your) cap|needs? (a|the|your) cap|without (a|the|your) cap)'
flags: i
weight: 1
---
