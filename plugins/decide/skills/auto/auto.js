export const meta = {
  name: 'gauntlet-auto',
  description: 'Route a question or proposal to the right challenge pattern (vote, gauntlet, vote then gauntlet, gauntlet then vote, or none) and run it',
  phases: [
    { title: 'Route', detail: 'one selector agent picks the pattern' },
    { title: 'Run', detail: 'the chosen pattern, as child workflows' },
  ],
}

// ---- SELECTOR PROMPT: refine this over time from the routing log (see SKILL.md) ----
const SELECTOR = `You route a question to the cheapest challenge pattern that will answer it well. The patterns:

- none: opinion is the wrong tool. A machine check answers it better (run the tests, benchmark it, look it up, compute it), or it is trivial enough to just answer. Say what to do instead.
- vote: the answer is one of a discrete set (which library, which name, which of these plans, yes or no, a number from a few candidates), and answers compare exactly. The main risk is picking the wrong one, not leaving rough edges. Options may be given or easy to enumerate.
- gauntlet: one proposal is in hand and the job is to improve it: a design, a plan, a fix, wording. The space is continuous; the risks are unpolished details, a missed better way ("actually there's a library for this"), or a flaw nobody listed.
- vote_then_gauntlet: no proposal yet, and the answer is something to be built (a design, a plan, an approach, prose) where both choosing the basin and refining the choice matter. Independent proposers and a blind vote pick the starting point, then a gauntlet refines the winner.
- gauntlet_then_vote: a proposal is in hand but could fail in several distinct ways, or its premise is in doubt. Parallel challenge chains, each through a different lens, each hand back a version; a blind vote among those versions and the original decides, including whether the challengers improved on it at all.

How to choose:
- Options given → vote, unless the question is really "improve one of these".
- A proposal given → gauntlet, or gauntlet_then_vote when stakes are high and the failure modes are several and distinct.
- Neither given → vote if the answer is a pick, vote_then_gauntlet if it is a built thing.
- Prefer the cheaper route when unsure: none < vote ≈ gauntlet < composed routes (about 2–3x the cost).
- Independence finds basins; a relay climbs within one. A wide space with a known-good answer shape wants a vote first.`
// ---- end selector prompt ----

const ROUTE = {
  type: 'object',
  properties: {
    route: { type: 'string', enum: ['none', 'vote', 'gauntlet', 'vote_then_gauntlet', 'gauntlet_then_vote'] },
    why: { type: 'string', description: 'two sentences at most' },
    vote_question: { type: 'string', description: 'for vote routes: the question phrased so its answer is one discrete pick, without listing candidates (independent proposers do that; listing them anchors the proposers); else empty' },
    lenses: { type: 'array', items: { type: 'string' }, description: 'for gauntlet_then_vote: 2–4 distinct lenses, one per chain (e.g. correctness, simplicity, cost, is-the-premise-right); else empty' },
    instead: { type: 'string', description: 'for none: what to do instead; else empty' },
  },
  required: ['route', 'why', 'vote_question', 'lenses', 'instead'],
}

const a = args || {}
if (!a.question && !a.proposal) throw new Error('args.question or args.proposal is required')
if (!a.scripts?.vote || !a.scripts?.gauntlet) throw new Error('args.scripts.vote and args.scripts.gauntlet must be scratchpad paths to vote.js and gauntlet.js')
const common = { context: a.context, constraints: a.constraints, effort: a.effort, model: a.model, judge_model: a.judge_model }
const goal = a.goal || a.question

phase('Route')
let r
if (a.route) {
  r = { route: a.route, why: 'route set by caller', vote_question: a.question || '', lenses: a.lenses || [], instead: '' }
} else {
  r = await agent(`${SELECTOR}

## The request
${a.question ? `Question: ${a.question}\n` : ''}${a.proposal ? `Proposal in hand:\n${a.proposal}\n` : 'No proposal in hand.\n'}${a.options?.length ? `Options given: ${a.options.map(o => typeof o === 'string' ? o : o.label).join(' | ')}\n` : 'No options given.\n'}${a.goal ? `Goal: ${a.goal}\n` : ''}${a.context ? `Context:\n${a.context}\n` : ''}${a.constraints ? `Hard constraints:\n${a.constraints}\n` : ''}
Pick the route. Do not answer the question itself.`,
    { label: 'route', phase: 'Route', schema: ROUTE, effort: 'high', model: a.judge_model })
}
log(`route: ${r.route} (${r.why})`)

// Guard against routes the inputs can't support.
if ((r.route === 'gauntlet' || r.route === 'gauntlet_then_vote') && !a.proposal) {
  log('no proposal in hand; switching to vote_then_gauntlet')
  r.route = 'vote_then_gauntlet'
}

phase('Run')
const out = { route: r.route, why: r.why }

if (r.route === 'none') {
  return { ...out, instead: r.instead }
}

if (r.route === 'vote') {
  const v = await workflow({ scriptPath: a.scripts.vote }, {
    ...common, question: r.vote_question || a.question || `Which is best? ${goal}`, goal: a.goal, options: a.options,
    criteria: a.criteria, proposers: a.proposers, voters: a.voters,
  })
  return { ...out, answer: v.winner_option ?? v.winner, vote: v }
}

if (r.route === 'gauntlet') {
  const g = await workflow({ scriptPath: a.scripts.gauntlet }, {
    ...common, proposal: a.proposal, goal, depth: a.depth, width: a.width, lenses: a.lenses,
  })
  return { ...out, answer: g.answer, original_won: g.pick?.original_won, gauntlet: g }
}

if (r.route === 'vote_then_gauntlet') {
  const v = await workflow({ scriptPath: a.scripts.vote }, {
    ...common, question: r.vote_question || a.question, goal: a.goal, options: a.options,
    criteria: a.criteria, proposers: a.proposers ?? 4, voters: a.voters ?? 5,
  })
  if (!v.winner_option) return { ...out, answer: null, vote: v, note: v.note || 'the vote chose nothing, so there was nothing to refine' }
  const start = v.winner_option
  const others = (v.table || []).slice(1).map(t => t.label)
  const g = await workflow({ scriptPath: a.scripts.gauntlet }, {
    ...common,
    proposal: start,
    goal,
    context: [a.context,
      `This proposal won a blind vote among independent candidates${v.margin ? ` (${v.method} ${v.margin})` : ''}.`,
      others.length ? `Alternatives it beat: ${others.join('; ')}. Borrow from them only where they are better on a specific point.` : '',
      v.worries_about_winner?.length ? `Voters' worries about it: ${v.worries_about_winner.join(' | ')}` : '',
    ].filter(Boolean).join('\n'),
    depth: a.depth ?? 2,
  })
  return { ...out, answer: g.answer ?? start, original_won: g.pick?.original_won, vote: v, gauntlet: g }
}

if (r.route === 'gauntlet_then_vote') {
  const lenses = (r.lenses?.length ? r.lenses : a.lenses?.length ? a.lenses : ['correctness', 'simplicity', 'is the premise right']).slice(0, 4)
  const g = await workflow({ scriptPath: a.scripts.gauntlet }, {
    ...common, proposal: a.proposal, goal, depth: a.depth ?? 2, width: lenses.length, lenses, pick: false,
  })
  // The original goes last among neutral labels, so voters can't tell which version is unchallenged.
  const versions = [...g.chains.map(c => c.final), a.proposal]
  const v = await workflow({ scriptPath: a.scripts.vote }, {
    ...common, question: a.question || `Which version best achieves the goal: ${goal}`, goal: a.goal,
    options: versions.map((text, i) => ({ label: `Version ${i + 1}`, option: text })),
    criteria: a.criteria, voters: a.voters ?? 5,
  })
  const originalLabel = `Version ${versions.length}`
  return {
    ...out,
    answer: v.winner_option,
    original_won: v.winner === originalLabel,
    original_label: originalLabel,
    lenses,
    gauntlet: g,
    vote: v,
  }
}

throw new Error(`unknown route ${r.route}`)
