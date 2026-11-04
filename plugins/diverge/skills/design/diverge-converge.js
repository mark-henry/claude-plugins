export const meta = {
  name: 'diverge-converge',
  description: 'Unanchored brainstorm, pick maximally distinct solution families, prototype, red-team and repair each, then a blind judge recommends',
  whenToUse: 'A design problem with a wide solution space where the first idea (or the asker\'s own framing) would otherwise anchor every attempt',
  phases: [
    { title: 'Diverge', detail: 'independent brainstormers, one framing each, no prescribed solution areas' },
    { title: 'Select', detail: 'cluster all ideas, pick maximally distinct families' },
    { title: 'Prototype', detail: 'build and measure each family in its own sandbox' },
    { title: 'Attack', detail: 'red-team each prototype' },
    { title: 'Repair', detail: 'patch against the attack, re-measure' },
    { title: 'Judge', detail: 'recommendation, blind to other runs' },
  ],
}

// args:
//   context      (required) problem statement: goal, facts, measurements. Facts only: no diagnosis, no candidate fixes.
//   constraints  (required) hard limits: spend, files that must not change, data-handling rules.
//   sandboxes    (required) array of absolute paths, one per pick, each a disposable copy the prototype may edit.
//   target       (required) the success bar locked in the step-0 interview, with definitions; the red team's survival bar.
//   measure      (optional) how to measure locally inside a sandbox (commands, scripts, test command).
//   framings     (optional) [{key, text}] overrides the default brainstorm framings.
//   picks        (optional) number of families to prototype; defaults to sandboxes.length.
//   models       (optional) {diverge, select, proto, attack, repair, judge}: model per role, e.g. {judge: 'fable'}. Omitted roles inherit.
//   efforts      (optional) same keys: effort per role, e.g. {attack: 'high', judge: 'xhigh'}. Omitted roles inherit.
//   minutes      (optional) wall-time budget per prototype, attack and repair agent; default 45.
//   audience     (optional) who reads the recommendation, e.g. 'the study lead (Mark)'.

const A = args || {}
if (!A.context || !A.target || !A.constraints || !Array.isArray(A.sandboxes) || !A.sandboxes.length) {
  throw new Error('args needs context, target, constraints and a non-empty sandboxes array (run the step-0 interview first)')
}
const M = A.models || {}
const E = A.efforts || {}
const opt = (role, o) => Object.assign(o, M[role] ? { model: M[role] } : {}, E[role] ? { effort: E[role] } : {})
const PICKS = Math.min(A.picks || A.sandboxes.length, A.sandboxes.length)
const AUDIENCE = A.audience || 'the person who asked'
const MINUTES = A.minutes || 45

const CONTEXT = `\n## Problem\n${A.context}\n\n## Target (agreed with the user; argue against it only with evidence)\n${A.target}\n\n## Constraints\n${A.constraints}\n`

const FRAMINGS = A.framings || [
  { key: 'open', text: 'Generate 8-10 genuinely different solutions. Anything anywhere in the system is fair game. Aim for breadth across kinds of fix, not variations on one.' },
  { key: 'outside', text: 'Generate 8-10 solutions with at least half OUTSIDE the component the problem statement points at (how results are measured or scored, incentives, inputs, presentation, process, analysis plan). Include your single best fix inside that component for contrast.' },
  { key: 'adversary', text: 'First think as the adversary or failure mode the problem describes: enumerate every exploit or loophole, including ones the current measurement would miss. Inspect the real artifacts to find concrete ones. Then propose 6-8 solutions that close the whole set, not only the known cases.' },
  { key: 'skeptic', text: 'Challenge the premise. Is the problem real and as large as stated? Is the target the right bar, and is its definition right? Use the evidence available. Then propose 6-8 solutions or cheap tests, including the minimal change if the problem is smaller than assumed and what is needed if it is larger.' },
]

const WAIT = ' Waiting: `sleep` alone is blocked and Monitor or background jobs end up unread, because your final answer is read the moment you stop. Run each job in the foreground, or wait for its output with `until [ -s <output file> ]; do sleep 20; done` (Bash timeout 600000, re-issued as needed). Never end your turn while a job you started is still running.'

const IDEAS = {
  type: 'object',
  properties: {
    ideas: { type: 'array', items: { type: 'object', properties: {
      title: { type: 'string' },
      family: { type: 'string', description: 'what kind of fix this is, in your own words' },
      mechanism: { type: 'string' },
      why_it_works: { type: 'string' },
      costs_and_risks: { type: 'string' },
      how_to_test: { type: 'string' },
    }, required: ['title', 'family', 'mechanism', 'why_it_works', 'costs_and_risks', 'how_to_test'] } },
    notes: { type: 'string', description: 'anything about the problem framing you think is wrong or missing' },
  },
  required: ['ideas', 'notes'],
}

phase('Diverge')
const brainstorms = (await parallel(FRAMINGS.map(f => () =>
  agent(`${CONTEXT}\n## Your job\nYou are an independent designer. Read the relevant material first. You have no sandbox: don't copy the repo, and never write into the original or any sandbox. If you measure something, keep it small (n up to about 200, one process, 15 minutes in total) and put your scripts in a temp directory of your own.${WAIT} ${f.text}\nBe concrete and specific to this system. Do not converge on the first obvious idea.`,
    opt('diverge', { label: `diverge:${f.key}`, phase: 'Diverge', schema: IDEAS }))))).filter(Boolean)
log(`${brainstorms.reduce((n, b) => n + b.ideas.length, 0)} ideas from ${brainstorms.length} brainstormers`)
if (!brainstorms.length) return { error: 'every brainstormer failed', brainstorms }

phase('Select')
const SELECT = {
  type: 'object',
  properties: {
    clusters: { type: 'string', description: 'all ideas grouped into families, one line each' },
    picks: { type: 'array', minItems: 1, maxItems: PICKS, items: { type: 'object', properties: {
      family: { type: 'string' },
      design: { type: 'string', description: 'the concrete design to prototype, combining the best ideas in the family' },
      test_plan: { type: 'string', description: 'how to measure it, under the strongest version of the target' },
      why_picked: { type: 'string' },
      viable: { type: 'boolean', description: 'false if this family is unlikely to meet the target and is picked only as the best of the rest' },
    }, required: ['family', 'design', 'test_plan', 'why_picked', 'viable'] } },
    shared_requirements: { type: 'string', description: 'fixes every pick needs regardless of family (e.g. bugs in a shared measurement script); empty if none' },
    framing_issues: { type: 'string', description: 'challenges to the problem framing worth surfacing' },
  },
  required: ['clusters', 'picks', 'shared_requirements', 'framing_issues'],
}
const sel = await agent(`${CONTEXT}\n## Your job\nIndependent brainstormers produced these ideas:\n${JSON.stringify(brainstorms, null, 2)}\n\nCluster them into families. Pick up to ${PICKS} of the most promising families that are MAXIMALLY DISTINCT from each other; at most one may be a change inside the component the problem statement points at. Don't pad: pick fewer if fewer are worth building, and mark any pick unlikely to meet the target as viable: false. If you think no family can meet the target, say so in framing_issues. For each, write a concrete design to prototype and a test plan. Keep the families independent: a mechanism belongs to one pick only. Anything every pick needs regardless of family (a bug in a shared measurement script, a missing prerequisite) goes in shared_requirements, not inside a pick. Also collect the framing challenges.`,
  opt('select', { label: 'select', phase: 'Select', schema: SELECT }))
if (!sel) return { error: 'selector failed', brainstorms }
log(`${sel.picks.length} picks, ${sel.picks.filter(p => !p.viable).length} marked not viable`)
const SHARED = sel.shared_requirements ? `\n## Shared requirements (apply these first, exactly as written, before your own design)\n${sel.shared_requirements}\n` : ''
if (sel.shared_requirements) log(`shared requirements: ${sel.shared_requirements.slice(0, 200)}`)

const DESIGN = {
  type: 'object',
  properties: {
    name: { type: 'string' },
    mechanism: { type: 'string' },
    changes: { type: 'string', description: 'what changed in the sandbox, key snippets, absolute paths' },
    measured: { type: 'string', description: 'numbers with n, held-out where anything was fitted; what could not be measured and the experiment that would settle it' },
    expected_cost: { type: 'string' },
    risks: { type: 'string' },
    repo_root: { type: 'string', description: 'absolute path of the tree your changes live in' },
    reproduce_cmds: { type: 'string', description: 'the exact commands (with config files, seeds and output paths) that produce every number in measured' },
    unfinished: { type: 'string', description: 'work you did not finish or measurements still unverified; empty if none' },
  },
  required: ['name', 'mechanism', 'changes', 'measured', 'expected_cost', 'risks', 'repo_root', 'reproduce_cmds', 'unfinished'],
}
const ATTACK = {
  type: 'object',
  properties: {
    strongest_exploit: { type: 'string' },
    exploit_rate: { type: 'string', description: 'measured rate with n, or why not measurable' },
    tried: { type: 'string' },
    collateral_damage: { type: 'string', description: 'what the design breaks or weakens beyond the target' },
    verdict: { type: 'string', enum: ['survives', 'wounded', 'broken'] },
    fix_suggestions: { type: 'string' },
    reproduce_cmds: { type: 'string', description: 'the exact commands that produce exploit_rate' },
    unfinished: { type: 'string', description: 'attacks you did not finish; empty if none' },
  },
  required: ['strongest_exploit', 'exploit_rate', 'tried', 'collateral_damage', 'verdict', 'fix_suggestions', 'reproduce_cmds', 'unfinished'],
}
const sandbox = (i) => `\n## Your sandbox\nWork ONLY in ${A.sandboxes[i]}. Put your own scripts in its scratch/ directory. Budget about ${MINUTES} minutes of wall time: if a measurement won't fit, report it in unfinished rather than overrunning.${WAIT}${A.measure ? `\nMeasuring: ${A.measure}` : ''}\n`

const chains = await pipeline(
  sel.picks,
  (p, _, i) => agent(`${CONTEXT}${SHARED}${sandbox(i)}\n## Your job\nPrototype and measure this design:\n${JSON.stringify(p, null, 2)}\nBuild it in your sandbox and measure everything measurable within the constraints (held-out splits for anything fitted). Where something can only be settled by a costlier experiment, specify that experiment and its size. Report honestly.`,
    opt('proto', { label: `proto:${i + 1}`, phase: 'Prototype', schema: DESIGN })),
  (d, p, i) => agent(`${CONTEXT}${sandbox(i)}\n## Your job\nYou are a red-teamer. Break this prototype:\n${JSON.stringify(d, null, 2)}\nFind the strongest way to defeat its purpose and measure it (your scripts in scratch/attack/; don't modify the prototype). Also assess collateral damage. Default to skepticism: 'survives' only if your best exploit fails the Target bar exactly as stated above, measured the way the Target says to measure it, and the damage is minor. Don't substitute your own bar.`,
    opt('attack', { label: `attack:${i + 1}`, phase: 'Attack', schema: ATTACK })).then(atk => ({ d, atk })),
  (r, p, i) => agent(`${CONTEXT}${sandbox(i)}\n## Your job\nYour prototype:\n${JSON.stringify(r.d, null, 2)}\nwas attacked:\n${JSON.stringify(r.atk, null, 2)}\nRepair it within its own family (or concede what can't be fixed; don't adopt another family's mechanism), re-run the attacker's strongest exploit (scripts in scratch/attack/) on the revised version, and report final numbers.`,
    opt('repair', { label: `repair:${i + 1}`, phase: 'Repair', schema: DESIGN })).then(fin => ({ family: p.family, first: r.d, attack: r.atk, final: fin })),
)

phase('Judge')
const ok = chains.filter(Boolean)
log(`${ok.length}/${sel.picks.length} chains completed`)
for (const c of ok) for (const [k, v] of [['proto', c.first], ['attack', c.attack], ['repair', c.final]]) if (v && v.unfinished) log(`${c.family} ${k} unfinished: ${v.unfinished.slice(0, 200)}`)
const judgeOpts = opt('judge', { label: 'judge', phase: 'Judge' })
const verdict = await agent(`${CONTEXT}\n## Your job\nYou are the judge. Brainstorm clusters:\n${sel.clusters}\n\nShared requirements applied to every pick:\n${sel.shared_requirements || 'none'}\n\nFraming challenges:\n${sel.framing_issues}\n\nThese families were prototyped, red-teamed and repaired:\n${JSON.stringify(ok, null, 2)}\n\nYou may read the sandboxes (${A.sandboxes.join(', ')}) and rerun their measurements (each report gives repo_root and reproduce_cmds) to verify numbers you rely on.${WAIT} Be skeptical of self-reported numbers. Recommend what to do: one design, a combination, a reframing, or that no design meets the target. That last verdict is respectable, not a failure: if it's the truth, say it plainly, give the best measured result, the strongest bar that is actually achievable, and compare it with any fallback bar stated in the Target. Write a markdown recommendation for ${AUDIENCE}: the recommendation in plain words, verified numbers, costs, what the red team still found, framing challenges to decide, what is unverified, and what to port. No hard line wraps.`,
  judgeOpts)
return { verdict, picks: sel.picks, framing: sel.framing_issues, clusters: sel.clusters, chains: ok }
