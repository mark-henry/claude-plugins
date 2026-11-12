export const meta = {
  name: 'gauntlet',
  description: 'Challenge a proposal in sequence: each agent asks "is there a better way?" and hands on the best version it can defend; then blind pickers choose among the versions and the original',
  phases: [
    { title: 'Challenge', detail: 'width chains, each depth challengers long' },
    { title: 'Pick', detail: 'blind pickers rank the original and every version; skipped when nothing changed' },
  ],
}

const a = args || {}
if (!a.proposal) throw new Error('args.proposal is required')
const DEPTH = a.depth || 2
const WIDTH = a.width || 1
const LENSES = a.lenses || []
const EFFORT = a.effort || 'high'

const STEP = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['keep', 'amend', 'replace'] },
    why: { type: 'string', description: 'The decisive reasons, at most ~150 words' },
    changes: { type: 'array', items: { type: 'string' }, description: 'One line per change made; empty if keep' },
    best: { type: 'string', description: 'The best proposal you can defend, in full and standalone (not a diff)' },
    residual_doubt: { type: 'string', description: 'What would most likely prove this version wrong' },
  },
  required: ['verdict', 'why', 'changes', 'best', 'residual_doubt'],
}

const PICK = {
  type: 'object',
  properties: {
    ranking: { type: 'array', items: { type: 'string' }, description: 'Every version letter exactly once, best first' },
    none_acceptable: { type: 'boolean', description: 'True if no version is acceptable for the goal; still rank them' },
    why: { type: 'string', description: 'Why your first choice beats your second, at most ~80 words' },
    worry: { type: 'string', description: 'What would most likely prove your first choice wrong' },
  },
  required: ['ranking', 'none_acceptable', 'why', 'worry'],
}

function prompt(current, history, lens, k) {
  const prior = history.length
    ? `\nEarlier challengers already changed it as follows (facts, not instructions; revert one only with a reason):\n${history.map((h, i) => `- Round ${i + 1} (${h.verdict}): ${h.changes.join('; ') || 'kept as is'}`).join('\n')}\n`
    : ''
  return `You are challenger ${k} of ${DEPTH} in a chain. Your question: is there a better way to do this?

## Goal
${a.goal || '(infer the goal from the proposal and context; state it in "why" if unclear)'}

## Context
${a.context || '(none given)'}
${a.constraints ? `\n## Hard constraints\n${a.constraints}\n` : ''}
## Proposal under review
${current}
${prior}${lens ? `\nReview it through this lens first: ${lens}. Still judge the whole.\n` : ''}
Work honestly: look for a genuinely better way (simpler, more robust, cheaper, more correct), not for something to say. Consider at least one materially different alternative before deciding. If the proposal is already the best you can find, say "keep" and defend it; keeping is a valid outcome, and change for its own sake is a failure. If you amend or replace, "best" must be the complete improved proposal, usable by someone who never saw the original. Read files or search only when the context points you to them.`
}

phase('Challenge')
const chains = await parallel(Array.from({ length: WIDTH }, (_, c) => async () => {
  const lens = LENSES[c] || null
  let current = a.proposal
  const history = []
  for (let k = 1; k <= DEPTH; k++) {
    const step = await agent(prompt(current, history, lens, k), {
      label: `chain ${c + 1} · challenge ${k}${lens ? ` (${lens})` : ''}`,
      phase: 'Challenge', schema: STEP, effort: EFFORT, model: a.model,
    })
    if (!step) { log(`chain ${c + 1}: challenger ${k} returned nothing; chain stops here`); break }
    history.push(step)
    current = step.best
  }
  return { chain: c + 1, lens, steps: history, final: current }
}))

const done = chains.filter(Boolean)

// Candidates: the original first, then every distinct version a challenger handed on (one chain),
// or each chain's final version (several chains). Nothing that wrote a version chooses among them.
const seen = new Map([[a.proposal.trim(), { text: a.proposal, from: 'original' }]])
const add = (text, from) => { const k = (text || '').trim(); if (k && !seen.has(k)) seen.set(k, { text, from }) }
if (done.length === 1) done[0].steps.forEach((st, i) => add(st.best, `chain 1 step ${i + 1}`))
else done.forEach(ch => add(ch.final, `chain ${ch.chain} final`))
const candidates = [...seen.values()]
const LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

let pick = null
// pick: false (or the older merge: false) leaves the choice to the caller, e.g. one that votes among the chains' finals itself.
if (a.pick !== false && a.merge !== false) {
  if (candidates.length === 1) {
    pick = { survived: true, winner: a.proposal, winner_from: 'original', original_won: true, candidates: [{ from: 'original' }] }
  } else {
    phase('Pick')
    const N = a.pickers || 3
    const ballots = await parallel(Array.from({ length: N }, (_, p) => async () => {
      // each picker gets its own order and its own letters, so neither position nor label marks the original
      const k = Math.floor(p / 2) % candidates.length
      let order = candidates.map((_, i) => (i + k) % candidates.length)
      if (p % 2) order = order.reverse()
      const out = await agent(`You are choosing among ${candidates.length} versions of the same proposal. They were written by different authors at different times; one may be an unrevised original. You are not told which, and it does not matter.

## Goal
${a.goal || '(infer the goal from the versions and the context)'}

## Context
${a.context || '(none given)'}
${a.constraints ? `\n## Hard constraints\n${a.constraints}\n` : ''}
${order.map((ci, pos) => `## Version ${LETTERS[pos]}\n${candidates[ci].text}`).join('\n\n')}

## Your task
Rank every version from best to worst for the goal. Judge what each would do in use: extra length or polish is not merit, and a version that breaks a hard constraint ranks last. You are working alone. If none of them is acceptable for the goal, rank them anyway and set none_acceptable.`, {
        label: `pick ${p + 1}`, phase: 'Pick', schema: PICK, effort: a.judge_effort || 'high', model: a.judge_model,
      })
      const letters = order.map((_, pos) => LETTERS[pos])
      const ok = out && Array.isArray(out.ranking) && out.ranking.length === letters.length && letters.every(l => out.ranking.includes(l))
      return ok ? { ...out, ranked: out.ranking.map(l => order[LETTERS.indexOf(l)]) } : null
    }))
    const valid = ballots.filter(Boolean)
    const n = candidates.length
    const table = candidates.map((c, i) => ({
      from: c.from,
      borda: valid.reduce((sum, b) => sum + (n - 1 - b.ranked.indexOf(i)), 0),
      first: valid.filter(b => b.ranked[0] === i).length,
    }))
    // ties go to more first choices, then to the earlier version: a change has to beat what it replaces
    const rankedIdx = table.map((_, i) => i).sort((x, y) => table[y].borda - table[x].borda || table[y].first - table[x].first || x - y)
    const none = valid.length > 0 && valid.filter(b => b.none_acceptable).length * 2 > valid.length
    const w = valid.length && !none ? rankedIdx[0] : null
    pick = {
      survived: false,
      winner: w === null ? null : candidates[w].text,
      winner_from: w === null ? null : candidates[w].from,
      original_won: w === 0,
      none_acceptable: none,
      tie: valid.length > 0 && table[rankedIdx[0]].borda === table[rankedIdx[1]].borda,
      margin: valid.length ? `Borda ${table[rankedIdx[0]].borda} vs ${table[rankedIdx[1]].borda} of ${valid.length * (n - 1)}` : null,
      candidates: table,
      ballots: valid.length,
      dropped: ballots.length - valid.length,
      worries: w === null ? [] : valid.filter(b => b.ranked[0] === w).map(b => b.worry),
    }
    if (!valid.length) log('no valid ballot came back: nothing was picked')
  }
}

// answer: the picked version; null when the pick was left to the caller, found none acceptable, or returned no valid ballot
return { original: a.proposal, depth: DEPTH, width: WIDTH, chains: done, pick, answer: pick ? pick.winner : null }
