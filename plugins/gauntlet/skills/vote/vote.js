export const meta = {
  name: 'gauntlet-vote',
  description: 'Pick among discrete options by blind vote: independent proposers (unless options are given), a deduped pool, voters who each see a different order, and a plurality / Borda / Condorcet tally with margins',
  phases: [
    { title: 'Propose', detail: 'independent proposers, no shared context' },
    { title: 'Pool', detail: 'merge duplicates into distinct options' },
    { title: 'Vote', detail: 'blind voters rank the pool in rotated orders' },
  ],
}

const a = args || {}
if (!a.question) throw new Error('args.question is required')
const nProp = a.proposers ?? 5
const nVote = a.voters ?? 5
const method = a.method ?? 'borda'
const effort = a.effort ?? 'high'
const brief = [
  `Question: ${a.question}`,
  a.goal && `Goal: ${a.goal}`,
  a.context && `Context:\n${a.context}`,
  a.constraints && `Hard constraints (an option that breaks one is out):\n${a.constraints}`,
  a.criteria && `Judge by: ${a.criteria}`,
].filter(Boolean).join('\n\n')

const CANDIDATE = {
  type: 'object',
  properties: {
    label: { type: 'string', description: 'a short name for the option, under 8 words' },
    option: { type: 'string', description: 'the option in full, standalone' },
    why: { type: 'string', description: 'its case, in one or two sentences' },
  },
  required: ['label', 'option', 'why'],
}
const PROPOSAL = {
  type: 'object',
  properties: {
    candidates: { type: 'array', items: CANDIDATE, minItems: 2, maxItems: 3, description: 'distinct options, your best first' },
  },
  required: ['candidates'],
}
const POOL = {
  type: 'object',
  properties: {
    options: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          label: { type: 'string' },
          option: { type: 'string', description: 'the strongest full statement among the merged proposals' },
          from: { type: 'array', items: { type: 'string' }, description: 'ids (like "2.1") of the candidates merged into this option' },
        },
        required: ['label', 'option', 'from'],
      },
    },
  },
  required: ['options'],
}
const BALLOT = {
  type: 'object',
  properties: {
    ranking: { type: 'array', items: { type: 'string' }, description: 'every letter, best first' },
    out: { type: 'array', items: { type: 'string' }, description: 'letters that break a hard constraint; empty if none' },
    why_first: { type: 'string', description: 'one or two sentences on why the first choice wins' },
    worry: { type: 'string', description: 'the biggest risk in the first choice' },
  },
  required: ['ranking', 'out', 'why_first', 'worry'],
}

// Stances vary where each proposer starts looking; they are leanings, not assignments.
const STANCES = [
  'what an experienced practitioner would pick first',
  'the simplest thing that could work',
  'existing tools, libraries or prior art',
  'robustness: what is hardest to get wrong later',
  'what a sharp skeptic of the obvious answer would push',
  'what is cheapest to try and to reverse',
  'the most ambitious option worth its cost',
]

let pool
if (a.options && a.options.length) {
  pool = a.options.map((o, i) => (typeof o === 'string'
    ? { label: o.length > 60 ? `option ${i + 1}` : o, option: o, from: [] }
    : { label: o.label ?? `option ${i + 1}`, option: o.option ?? o.text ?? JSON.stringify(o), from: [] }))
  log(`${pool.length} options given; skipping proposers`)
} else {
  phase('Propose')
  const props = (await parallel(Array.from({ length: nProp }, (_, i) => () => agent(
`${brief}

You are one of several independent proposers. Give your two or three best answers, best first, as genuinely different options (different choices, not variants of one), each complete and concrete. Start your search from ${STANCES[i % STANCES.length]}, but rank by your honest judgment. Voters will choose among everyone's candidates, so a strong alternative is useful even if you would not pick it.`,
    { label: `propose ${i + 1}`, phase: 'Propose', schema: PROPOSAL, effort, model: a.model })))).filter(Boolean)
  if (!props.length) throw new Error('no proposals came back')
  const cands = props.flatMap((p, i) => p.candidates.map((c, j) => ({ ...c, id: `${i}.${j}` })))

  phase('Pool')
  const merged = await agent(
`${brief}

Independent proposers gave these candidates (id = proposer.rank; rank 0 is that proposer's first choice):

${cands.map(c => `[${c.id}] ${c.label}\n${c.option}`).join('\n\n')}

Merge candidates that are the same option in substance (different wording, same choice) so that votes are not split between duplicates. Keep genuinely different options apart, even if similar. Return every distinct option with the ids it absorbed; every id appears exactly once. Do not judge or drop any.`,
    { label: 'pool', phase: 'Pool', schema: POOL, effort: 'medium', model: a.judge_model })
  pool = merged.options
  pool.forEach(o => {
    o.proposed_by = new Set(o.from.map(id => String(id).split('.')[0])).size
    o.first_choice_of = o.from.filter(id => String(id).endsWith('.0')).length
  })
  log(`${cands.length} candidates from ${props.length} proposers → ${pool.length} distinct options`)
}
if (pool.length < 2) {
  return { question: a.question, pool, winner: pool[0]?.label ?? null, note: 'only one distinct option; nothing to vote on' }
}

phase('Vote')
const L = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
const k = pool.length
// Voter i sees a rotation of the pool, reversed for odd i, so position bias spreads across options.
const orderFor = i => {
  const rot = Array.from({ length: k }, (_, j) => (j + i) % k)
  return i % 2 ? rot.reverse() : rot
}
const ballots = (await parallel(Array.from({ length: nVote }, (_, i) => () => {
  const order = orderFor(i)
  return agent(
`${brief}

Options:

${order.map((p, j) => `${L[j]}. ${pool[p].label}\n${pool[p].option}`).join('\n\n')}

Rank every option, best first, by letter. You vote alone and do not know who proposed what; judge each on its merits against the question${a.criteria ? ' and the criteria' : ''}. Mark any option that breaks a hard constraint as out (still rank it).`,
    { label: `vote ${i + 1}`, phase: 'Vote', schema: BALLOT, effort, model: a.judge_model ?? a.model })
    .then(b => b && { ...b, order })
}))).filter(Boolean)

// Map letters back to pool indices; drop malformed rankings rather than guess.
const valid = []
for (const b of ballots) {
  const idx = b.ranking.map(x => L.indexOf(String(x).trim().toUpperCase()[0])).filter(j => j >= 0 && j < k).map(j => b.order[j])
  const uniq = [...new Set(idx)]
  if (uniq.length !== k) { log(`dropped a ballot ranking ${uniq.length}/${k} options`); continue }
  const out = b.out.map(x => L.indexOf(String(x).trim().toUpperCase()[0])).filter(j => j >= 0 && j < k).map(j => b.order[j])
  valid.push({ rank: uniq, out, why_first: b.why_first, worry: b.worry })
}
const n = valid.length
if (!n) throw new Error('no valid ballots')

const first = Array(k).fill(0), borda = Array(k).fill(0), outs = Array(k).fill(0)
const beats = Array.from({ length: k }, () => Array(k).fill(0))
for (const v of valid) {
  first[v.rank[0]]++
  v.rank.forEach((p, pos) => { borda[p] += k - 1 - pos })
  v.out.forEach(p => outs[p]++)
  for (let x = 0; x < k; x++) for (let y = x + 1; y < k; y++) beats[v.rank[x]][v.rank[y]]++
}
// An option a majority of voters marks as breaking a hard constraint cannot win.
const eligible = p => outs[p] * 2 <= n
const byScore = s => [...Array(k).keys()].sort((x, y) => (eligible(y) - eligible(x)) || (s[y] - s[x]))
const pl = byScore(first), bo = byScore(borda)
const condorcetIdx = [...Array(k).keys()].find(p => eligible(p) && [...Array(k).keys()].every(q => q === p || !eligible(q) || beats[p][q] > beats[q][p]))
const ranked = method === 'plurality' ? pl : bo
const score = method === 'plurality' ? first : borda
const winner = ranked[0], runner = ranked[1]
const maxScore = method === 'plurality' ? n : n * (k - 1)

return {
  question: a.question,
  method,
  voters: n,
  winner: pool[winner].label,
  winner_option: pool[winner].option,
  margin: `${score[winner]} vs ${score[runner]} (${pool[runner].label}) of ${maxScore} possible`,
  agree: {
    plurality: pool[pl[0]].label,
    borda: pool[bo[0]].label,
    condorcet: condorcetIdx === undefined ? null : pool[condorcetIdx].label,
  },
  tied: score[winner] === score[runner],
  table: ranked.map(p => ({
    label: pool[p].label,
    first: first[p], borda: borda[p], out: outs[p], eligible: eligible(p),
    proposed_by: pool[p].proposed_by ?? null,
    first_choice_of: pool[p].first_choice_of ?? null,
  })),
  reasons_for_winner: valid.filter(v => v.rank[0] === winner).map(v => v.why_first),
  worries_about_winner: valid.filter(v => v.rank[0] === winner).map(v => v.worry),
  pool,
}
