// Tests for vote.js with mocked agents. Run: node test_vote.mjs
import fs from 'node:fs'
import assert from 'node:assert/strict'
import { fileURLToPath } from 'node:url'

const src = fs.readFileSync(fileURLToPath(new URL('./vote.js', import.meta.url)), 'utf8').replace('export const meta', 'const meta')
const script = new (async () => {}).constructor('args', 'agent', 'parallel', 'pipeline', 'phase', 'log', src)

// voter(options, label) gets [{letter, label}] in the order shown and returns a ballot.
async function run(args, { voter, proposer, pooler }) {
  const logs = []
  const agent = async (prompt, opts = {}) => {
    if (/^propose/.test(opts.label)) return proposer(opts.label)
    if (opts.label === 'pool') return pooler(prompt)
    if (/^vote/.test(opts.label)) {
      const options = [...prompt.matchAll(/^([A-Z])\. (.+)$/gm)].map(m => ({ letter: m[1], label: m[2] }))
      return voter(options, opts.label)
    }
    throw new Error(`unexpected agent: ${opts.label}`)
  }
  const parallel = thunks => Promise.all(thunks.map(t => t()))
  return { result: await script(args, agent, parallel, null, () => {}, m => logs.push(m)), logs }
}
// A voter that ranks labels in a fixed preference order and marks some out.
const prefer = (order, { out = [], none = false } = {}) => options => ({
  ranking: [...options].sort((x, y) => order.indexOf(x.label) - order.indexOf(y.label)).map(o => o.letter),
  out: options.filter(o => out.includes(o.label)).map(o => o.letter),
  none_acceptable: none, why_first: 'because', worry: 'a worry',
})
const tests = []
const test = (name, fn) => tests.push([name, fn])

test('the best-ranked option wins, with a margin', async () => {
  const { result } = await run({ question: 'q', options: ['red', 'green', 'blue'] }, { voter: prefer(['green', 'red', 'blue']) })
  assert.equal(result.winner, 'green')
  assert.equal(result.tied, false)
})

test('when a majority rules every option out, nothing wins', async () => {
  const { result } = await run({ question: 'q', options: ['red', 'green', 'blue'] }, { voter: prefer(['green', 'red', 'blue'], { out: ['red', 'green', 'blue'] }) })
  assert.equal(result.winner, null)
  assert.equal(result.winner_option, null)
  assert.equal(result.none_eligible, true)
})

test('a majority can say none of these', async () => {
  const { result } = await run({ question: 'q', options: ['red', 'green', 'blue'] }, { voter: prefer(['green', 'red', 'blue'], { none: true }) })
  assert.equal(result.winner, null)
  assert.equal(result.none_acceptable, true)
})

test('an option ruled out by a majority cannot win, and votes pass to the next choice', async () => {
  const { result } = await run({ question: 'q', options: ['red', 'green', 'blue'] }, { voter: prefer(['green', 'red', 'blue'], { out: ['green'] }) })
  assert.equal(result.winner, 'red')
  const row = l => result.table.find(t => t.label === l)
  assert.equal(row('green').eligible, false)
  assert.equal(row('red').first, 5, 'first choices among eligible options')
})

test('a candidate the pooling agent dropped is put back', async () => {
  const proposer = label => ({ candidates: [{ label: `${label} a`, option: `${label} option a`, why: '' }, { label: `${label} b`, option: `${label} option b`, why: '' }] })
  const pooler = () => ({ options: [{ label: 'kept', option: 'kept option', from: ['0.0', '1.0'] }, { label: 'also', option: 'also option', from: ['0.1', '0.1'] }] })
  const { result } = await run({ question: 'q', proposers: 2 }, { proposer, pooler, voter: o => prefer(['kept'])(o) })
  const labels = result.pool.map(p => p.label)
  assert.ok(labels.includes('propose 2 b'), `1.1 was dropped by the pool and not restored: ${labels}`)
  assert.equal(result.pool.find(p => p.label === 'also').from.length, 1, 'a repeated id is counted once')
  assert.equal(result.pool_repairs.length > 0, true)
})

let failed = 0
for (const [name, fn] of tests) {
  try { await fn(); console.log(`ok    ${name}`) } catch (e) { failed++; console.log(`FAIL  ${name}\n      ${String(e.message).split('\n')[0]}`) }
}
console.log(failed ? `${failed} of ${tests.length} failed` : `all ${tests.length} passed`)
process.exit(failed ? 1 : 0)
