export const meta = {
  name: 'diverge-lite',
  description: 'Five independent recommendations from different stances, each red-teamed, then a judge picks or combines the best',
  phases: [{ title: 'Propose' }, { title: 'Attack' }, { title: 'Judge' }, { title: 'Control' }],
}

const A = args || {}
if (!A.question || !A.context) throw new Error('args needs question and context')
if (A.control && !A.sealed) throw new Error('control: true needs sealed (the main thread\'s own single-pass answer)')

const JUDGE_MODELS = { fable: { model: 'fable', effort: 'high' }, opus: { model: 'opus', effort: 'xhigh' } }
const J = JUDGE_MODELS[A.judge || 'fable'] || { model: A.judge, effort: 'high' }
const M = Object.assign({ judge: J.model }, A.models || {})
const E = Object.assign({ propose: 'medium', attack: 'high', judge: J.effort, control: 'xhigh' }, A.efforts || {})
const opt = (role, extra) => {
  const o = Object.assign({}, extra)
  if (M[role]) o.model = M[role]
  if (E[role]) o.effort = E[role]
  return o
}

const STANCES = A.stances || [
  { key: 'direct', card: 'The seasoned practitioner. What would someone who has solved this kind of problem many times do first, and why is that enough?' },
  { key: 'outside', card: 'Look away from the part of the system the question points at. The fix may live somewhere else: in how it is measured, the incentives, the process, the surrounding system.' },
  { key: 'adversary', card: 'Think as whoever or whatever will defeat the fix: the user who misuses it, the optimizer that games it, the edge case that breaks it. Recommend what still works after they try.' },
  { key: 'skeptic', card: 'Question the premise. Maybe the problem is smaller than it looks, the goal is the wrong one, or the best move is to do less, or nothing.' },
  { key: 'minimal', card: 'The cheapest move that buys most of the value: the smallest change, fastest to test, easiest to undo.' },
]

const BRIEF = `## Question\n${A.question}\n\n## Context\n${A.context}` +
  (A.constraints ? `\n\n## Constraints\n${A.constraints}` : '') +
  (A.bar ? `\n\n## What a good answer achieves\n${A.bar}` : '')

const TOOLS = ' Where the context names files, open them rather than trusting its summary. You may read files and run quick local read-only checks. ' +
  'Run everything in the foreground: no background jobs, no Monitor. Skip any check that would take over about 2 minutes and say you skipped it. ' +
  'Do not edit files, spend money, or post anywhere.'

const PROPOSAL = {
  type: 'object',
  properties: {
    title: { type: 'string', description: 'Five to ten words naming the recommendation' },
    recommendation: { type: 'string', description: 'What to do, concretely enough to act on' },
    why: { type: 'string', description: 'Why this beats the alternatives you considered' },
    rejected: { type: 'string', description: 'One or two alternatives you considered and why you dropped them' },
    first_check: { type: 'string', description: 'The cheapest way to find out early whether this is right' },
    risks: { type: 'string' },
  },
  required: ['title', 'recommendation', 'why', 'first_check', 'risks'],
}

const ATTACK = {
  type: 'object',
  properties: {
    strongest_objection: { type: 'string' },
    failure_scenario: { type: 'string', description: 'Concrete situation in which following the recommendation goes wrong' },
    evidence: { type: 'string', description: 'What you actually checked (files opened, numbers computed) and what it showed; say so if you checked nothing' },
    repair: { type: 'string', description: 'The smallest change that would answer the objection, if any' },
    verdict: { type: 'string', enum: ['survives', 'wounded', 'broken'] },
  },
  required: ['strongest_objection', 'failure_scenario', 'evidence', 'verdict'],
}

const LETTERS = 'ABCDEFGHIJ'

phase('Propose')
const chains = await pipeline(
  STANCES,
  s => agent(
    `You are one of ${STANCES.length} independent advisers answering the same question. You will not see the others, and they will not see you.\n\n` +
    `Your vantage point, to interpret freely:\n> ${s.card}\n\n${BRIEF}\n\n` +
    `Give your ONE best recommendation, not a menu.` + TOOLS,
    opt('propose', { label: `propose:${s.key}`, phase: 'Propose', schema: PROPOSAL })),
  (p, s) => p && agent(
    `Red-team this recommendation. Find its strongest objection, the one that would make a careful person not follow it. ` +
    `Verify the claim it rests on against the files or with a quick computation; don't nitpick style. ` +
    `"broken" means following it would likely fail the question; "wounded" means it works only with the repair you name; "survives" means you found nothing serious.\n\n${BRIEF}\n\n` +
    `## Recommendation under attack\n${JSON.stringify(p, null, 1)}\n\n` + TOOLS,
    opt('attack', { label: `attack:${s.key}`, phase: 'Attack', schema: ATTACK })).then(a => ({ stance: s.key, proposal: p, attack: a })),
)

const done = chains.filter(Boolean)
if (done.length < STANCES.length) log(`${STANCES.length - done.length} adviser chain(s) returned nothing and are not judged`)
if (!done.length) throw new Error('no proposals came back')
const letters = done.map((_, i) => LETTERS[i])

phase('Judge')
const VERDICT = {
  type: 'object',
  properties: {
    pick: { type: 'array', items: { type: 'string', enum: letters }, minItems: 1, description: 'The chosen option, or several letters for a combination' },
    recommendation: { type: 'string', minLength: 300, maxLength: 4000, description: 'What to do, in plain words the asker can act on; for a combination, say which part comes from which option' },
    per_option: { type: 'array', items: { type: 'string' }, description: 'One line per option, in letter order: why it won or lost' },
    first_check: { type: 'string' },
    confidence: { type: 'string', description: 'How sure, and on which parts' },
    would_change_mind: { type: 'string' },
    none_good_enough: { type: 'boolean', description: 'True if no option meets the bar; then say in recommendation what would' },
  },
  required: ['pick', 'recommendation', 'per_option', 'first_check', 'confidence', 'would_change_mind'],
}
const dossier = done.map((c, i) =>
  `## Option ${LETTERS[i]}: ${c.proposal.title}\n### Proposal\n${JSON.stringify(c.proposal, null, 1)}\n### Red team\n${JSON.stringify(c.attack, null, 1)}`).join('\n\n')
const judgePrompt =
  `You are the judge. ${done.length} independent advisers answered the question below, and each answer was red-teamed. ` +
  `Pick the best option, or a combination if grafting part of a runner-up clearly helps. ` +
  `Weigh the red team's evidence fields, not its verdict labels, and discount a red team that checked nothing. ` +
  `Re-check only the claims your pick depends on. Length is not merit. If no option meets the bar, say so and what would.\n\n${BRIEF}\n\n${dossier}`
let judge = await agent(judgePrompt, opt('judge', { label: 'judge', phase: 'Judge', schema: VERDICT })).catch(e => { log(`judge failed: ${e.message}`); return null })
if (!judge || !judge.pick || !judge.pick.length) {
  log('judge returned nothing usable; rerunning once')
  judge = await agent(judgePrompt + '\n\n(Second attempt: the first returned nothing usable. Return the full object.)', opt('judge', { label: 'judge-retry', phase: 'Judge', schema: VERDICT }))
}
if (!judge) throw new Error('judge failed twice')

const titleOf = l => done[LETTERS.indexOf(l)].proposal.title
const verdict = [
  `**Pick: ${judge.pick.map(l => `${l} (${titleOf(l)})`).join(' + ')}**${judge.none_good_enough ? ' — the judge says no option meets the bar' : ''}`,
  judge.recommendation,
  `**Why, per option**\n${judge.per_option.map(x => `- ${x}`).join('\n')}`,
  `**First check.** ${judge.first_check}`,
  `**Confidence.** ${judge.confidence} **Would change my mind:** ${judge.would_change_mind}`,
].join('\n\n')

let control
if (A.control) {
  phase('Control')
  // Fixed order from the question's length, so reruns replay from cache and neither side is always first.
  const sealedFirst = A.question.length % 2 === 0
  const X = sealedFirst ? A.sealed : judge.recommendation
  const Y = sealedFirst ? judge.recommendation : A.sealed
  const c = await agent(
    `Two answers to the same question follow, in arbitrary order. Judge which one the asker would be better off following: correctness, actionability, and whether it addresses what was actually asked. Length is not merit. Ties are allowed.\n\n${BRIEF}\n\n## Answer X\n${X}\n\n## Answer Y\n${Y}`,
    opt('control', { label: 'control', phase: 'Control', schema: {
      type: 'object',
      properties: { better: { type: 'string', enum: ['X', 'Y', 'tie'] }, reason: { type: 'string' } },
      required: ['better', 'reason'],
    } }))
  if (c) control = { workflow_vs_sealed: c.better === 'tie' ? 'tie' : ((c.better === 'X') === !sealedFirst ? 'better' : 'worse'), reason: c.reason }
}

return {
  verdict,
  judge,
  control,
  options: done.map((c, i) => ({ letter: LETTERS[i], stance: c.stance, title: c.proposal.title, attack_verdict: c.attack && c.attack.verdict })),
  chains: done,
}
