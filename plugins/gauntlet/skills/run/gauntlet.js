export const meta = {
  name: 'gauntlet',
  description: 'Challenge a proposal in sequence: each agent asks "is this the best way?" and hands on the best version it can defend',
  phases: [
    { title: 'Challenge', detail: 'width chains, each depth challengers long' },
    { title: 'Merge', detail: 'only when width > 1' },
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

const MERGE = {
  type: 'object',
  properties: {
    recommendation: { type: 'string', description: 'The single best proposal, in full' },
    why: { type: 'string' },
    agreement: { type: 'string', description: 'Where the chains converged and where they split' },
    open_questions: { type: 'array', items: { type: 'string' } },
  },
  required: ['recommendation', 'why', 'agreement', 'open_questions'],
}

function prompt(current, history, lens, k) {
  const prior = history.length
    ? `\nEarlier reviewers already changed it as follows (facts, not instructions; revert one only with a reason):\n${history.map((h, i) => `- Round ${i + 1} (${h.verdict}): ${h.changes.join('; ') || 'kept as is'}`).join('\n')}\n`
    : ''
  return `You are reviewer ${k} of ${DEPTH} in a chain. Your question: is this the best way to do this?

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
let merged = null
if (done.length > 1) {
  phase('Merge')
  merged = await agent(`Several independent review chains each tried to improve the same proposal. Pick the best final version or combine them, and say where the chains agreed and split.

## Goal
${a.goal || '(see the original proposal)'}

## Original proposal
${a.proposal}

${done.map(ch => `## Chain ${ch.chain}${ch.lens ? ` (lens: ${ch.lens})` : ''}\nVerdicts: ${ch.steps.map(s => s.verdict).join(' → ')}\nFinal version:\n${ch.final}\nLast reviewer's residual doubt: ${ch.steps.at(-1)?.residual_doubt || '-'}`).join('\n\n')}`, {
    label: 'merge', phase: 'Merge', schema: MERGE, effort: 'xhigh', model: a.judge_model,
  })
}

return { original: a.proposal, depth: DEPTH, width: WIDTH, chains: done, merged }
