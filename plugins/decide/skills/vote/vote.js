export const meta = {
  name: 'decide-vote',
  description: 'Pick among given options by blind vote: two voters on different models rank them in different orders; if they disagree, heavier tiebreakers vote one at a time; code tallies plurality, Borda and Condorcet',
  phases: [
    { title: 'Vote', detail: 'two blind voters, different models, different orders' },
    { title: 'Tiebreak', detail: 'heavier seats, one at a time, only while undecided' },
  ],
}

const a = args || {}
if (!a.question) throw new Error('args.question is required')
if (!Array.isArray(a.options) || a.options.length < 2) throw new Error('args.options needs at least two options: this script picks, it does not propose')
const method = a.method ?? 'borda'
const effort = a.effort ?? 'high'
// A seat is {model?, agentType?, effort?}. Defaults inherit the session model; pass seats from different model families.
const voterSeats = Array.isArray(a.voters) && a.voters.length ? a.voters : [{}, {}]
const tieSeats = Array.isArray(a.tiebreakers) ? a.tiebreakers : [{}]
const seatName = s => s.model ?? s.agentType ?? 'session model'
const brief = [
  `Question: ${a.question}`,
  a.goal && `Goal: ${a.goal}`,
  a.context && `Context:\n${a.context}`,
  a.constraints && `Hard constraints (an option that breaks one is out):\n${a.constraints}`,
  a.criteria && `Judge by: ${a.criteria}`,
].filter(Boolean).join('\n\n')

const BALLOT = {
  type: 'object',
  properties: {
    ranking: { type: 'array', items: { type: 'string' }, description: 'every letter, best first' },
    out: { type: 'array', items: { type: 'string' }, description: 'letters that break a hard constraint; empty if none' },
    none_acceptable: { type: 'boolean', description: 'true if no option is an acceptable answer to the question, or the question is wrongly framed; still rank them' },
    why_first: { type: 'string', description: 'one or two sentences on why the first choice wins' },
    worry: { type: 'string', description: 'the biggest risk in the first choice' },
  },
  required: ['ranking', 'out', 'none_acceptable', 'why_first', 'worry'],
}

const pool = a.options.map((o, i) => (typeof o === 'string'
  ? { label: o.length > 60 ? `option ${i + 1}` : o, option: o }
  : { label: o.label ?? `option ${i + 1}`, option: o.option ?? o.text ?? JSON.stringify(o) }))

const L = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
const k = pool.length
// Seat i sees a rotation of the pool, reversed for odd i, so position bias spreads across options.
const orderFor = i => {
  const rot = Array.from({ length: k }, (_, j) => (j + i) % k)
  return i % 2 ? rot.reverse() : rot
}
const valid = [], seats = []
const cast = async (seat, i, label, ph) => {
  const order = orderFor(i)
  const b = await agent(
`${brief}

Options:

${order.map((p, j) => `${L[j]}. ${pool[p].label}\n${pool[p].option}`).join('\n\n')}

Rank every option, best first, by letter. You vote alone; judge each on its merits against the question${a.criteria ? ' and the criteria' : ''}. Mark any option that breaks a hard constraint as out (still rank it). If none of them is an acceptable answer, or the question itself is wrongly framed, rank them anyway and set none_acceptable: that is a valid result.`,
    { label, phase: ph, schema: BALLOT, effort: seat.effort ?? effort, ...(seat.model ? { model: seat.model } : {}), ...(seat.agentType ? { agentType: seat.agentType } : {}) })
  seats.push({ label, seat: seatName(seat), returned: !!b })
  if (!b) return
  // Map letters back to pool indices; drop a malformed ranking rather than guess.
  const idx = b.ranking.map(x => L.indexOf(String(x).trim().toUpperCase()[0])).filter(j => j >= 0 && j < k).map(j => order[j])
  const uniq = [...new Set(idx)]
  if (uniq.length !== k) { log(`dropped ${label}: it ranked ${uniq.length}/${k} options`); return }
  const out = b.out.map(x => L.indexOf(String(x).trim().toUpperCase()[0])).filter(j => j >= 0 && j < k).map(j => order[j])
  valid.push({ rank: uniq, out, none_acceptable: b.none_acceptable === true, why_first: b.why_first, worry: b.worry })
}
// Decided: at least two ballots, and a majority says none of these, or one eligible option holds a majority of
// first choices, or a majority has ruled every option out. Two ballots that differ on "none of these" are undecided.
const decided = () => {
  const n = valid.length
  if (n < 2) return false
  const none = valid.filter(v => v.none_acceptable).length
  if (none * 2 > n) return true
  if (none && n < 3) return false // one of two objecting is a disagreement; one of three is a minority
  const outs = Array(k).fill(0)
  for (const v of valid) v.out.forEach(p => outs[p]++)
  const ok = p => outs[p] * 2 <= n
  if (![...Array(k).keys()].some(ok)) return true
  const first = Array(k).fill(0)
  for (const v of valid) { const r = v.rank.filter(ok); if (r.length) first[r[0]]++ }
  return first.some(c => c * 2 > n)
}

phase('Vote')
await parallel(voterSeats.map((s, i) => () => cast(s, i, `vote ${i + 1}`, 'Vote')))
for (let t = 0; t < tieSeats.length && !decided(); t++) {
  if (t === 0) phase('Tiebreak')
  log(`undecided after ${valid.length} ballot(s); tiebreak ${t + 1} on ${seatName(tieSeats[t])}`)
  await cast(tieSeats[t], voterSeats.length + t, `tiebreak ${t + 1}`, 'Tiebreak')
}
const split = !decided()

const n = valid.length
if (!n) throw new Error('no valid ballots')

// An option a majority of voters marks as breaking a hard constraint cannot win, and is left out of every tally:
// each ballot is read as its ranking of the eligible options only.
const outs = Array(k).fill(0)
for (const v of valid) v.out.forEach(p => outs[p]++)
const eligible = p => outs[p] * 2 <= n
const ke = [...Array(k).keys()].filter(eligible).length
const first = Array(k).fill(0), borda = Array(k).fill(0)
const beats = Array.from({ length: k }, () => Array(k).fill(0))
for (const v of valid) {
  const r = v.rank.filter(eligible)
  if (r.length) first[r[0]]++
  r.forEach((p, pos) => { borda[p] += ke - 1 - pos })
  for (let x = 0; x < r.length; x++) for (let y = x + 1; y < r.length; y++) beats[r[x]][r[y]]++
}
const byScore = sc => [...Array(k).keys()].sort((x, y) => (eligible(y) - eligible(x)) || (sc[y] - sc[x]))
const pl = byScore(first), bo = byScore(borda)
const condorcetIdx = [...Array(k).keys()].find(p => eligible(p) && [...Array(k).keys()].every(q => q === p || !eligible(q) || beats[p][q] > beats[q][p]))
const ranked = method === 'plurality' ? pl : bo
const score = method === 'plurality' ? first : borda
const maxScore = method === 'plurality' ? n : n * Math.max(ke - 1, 0)
const table = ranked.map(p => ({
  label: pool[p].label,
  first: first[p], borda: borda[p], out: outs[p], eligible: eligible(p),
}))
// "None of these" is a result: every option ruled out, or a majority saying no option is acceptable.
const noneAcceptable = valid.filter(v => v.none_acceptable).length * 2 > n
if (ke === 0 || noneAcceptable) {
  return {
    question: a.question, method, voters: n, winner: null, winner_option: null,
    none_eligible: ke === 0, none_acceptable: noneAcceptable,
    note: ke === 0 ? 'a majority of voters ruled out every option' : 'a majority of voters found no option acceptable',
    split: false, seats, table, reasons: valid.filter(v => v.none_acceptable).map(v => v.why_first), pool,
  }
}
const winner = ranked[0], runner = ke > 1 ? ranked[1] : null

return {
  question: a.question,
  method,
  voters: n,
  // A split is not a win: the leader is named, and the caller reports the split.
  winner: split ? null : pool[winner].label,
  winner_option: split ? null : pool[winner].option,
  leader: pool[winner].label,
  split,
  seats,
  margin: runner === null ? 'the only eligible option' : `${score[winner]} vs ${score[runner]} (${pool[runner].label}) of ${maxScore} possible`,
  agree: {
    plurality: pool[pl[0]].label,
    borda: pool[bo[0]].label,
    condorcet: condorcetIdx === undefined ? null : pool[condorcetIdx].label,
  },
  tied: runner !== null && score[winner] === score[runner],
  none_eligible: false,
  none_acceptable: false,
  table,
  reasons_for_winner: valid.filter(v => v.rank[0] === winner).map(v => v.why_first),
  worries_about_winner: valid.filter(v => v.rank[0] === winner).map(v => v.worry),
  pool,
}
