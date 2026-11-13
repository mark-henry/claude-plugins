// Tests for vote.js with mocked agents. Run: node test_vote.mjs
import fs from 'node:fs'
import assert from 'node:assert/strict'
import { fileURLToPath } from 'node:url'

const src = fs.readFileSync(fileURLToPath(new URL('./vote.js', import.meta.url)), 'utf8').replace('export const meta', 'const meta')
const script = new (async () => {}).constructor('args', 'agent', 'parallel', 'pipeline', 'phase', 'log', src)

// voter(options, label, opts) gets [{letter, label}] in the order shown and returns a ballot.
async function run(args, { voter }) {
  const logs = [], seats = []
  const agent = async (prompt, opts = {}) => {
    if (/^(vote|tiebreak)/.test(opts.label)) {
      seats.push(opts)
      const options = [...prompt.matchAll(/^([A-Z])\. (.+)$/gm)].map(m => ({ letter: m[1], label: m[2] }))
      return voter(options, opts.label, opts)
    }
    throw new Error(`unexpected agent: ${opts.label}`)
  }
  const parallel = thunks => Promise.all(thunks.map(t => t()))
  return { result: await script(args, agent, parallel, null, () => {}, m => logs.push(m)), logs, seats }
}
// A voter that ranks labels in a fixed preference order and marks some out.
const prefer = (order, { out = [], none = false } = {}) => options => ({
  ranking: [...options].sort((x, y) => order.indexOf(x.label) - order.indexOf(y.label)).map(o => o.letter),
  out: options.filter(o => out.includes(o.label)).map(o => o.letter),
  none_acceptable: none, why_first: 'because', worry: 'a worry',
})
const tests = []
const test = (name, fn) => tests.push([name, fn])

const Q = { question: 'q', options: ['red', 'green', 'blue'] }
// byLabel({ 'vote 1': ballotFn, ... }) picks a ballot function per seat.
const byLabel = map => (options, label) => map[label](options)

test('two voters who agree settle it, and no tiebreaker runs', async () => {
  const { result, seats } = await run(Q, { voter: prefer(['green', 'red', 'blue']) })
  assert.equal(result.winner, 'green')
  assert.equal(result.voters, 2)
  assert.equal(seats.length, 2)
  assert.equal(result.split, false)
})

test('when the two disagree, one tiebreaker votes and its side wins', async () => {
  const voter = byLabel({ 'vote 1': prefer(['green', 'red', 'blue']), 'vote 2': prefer(['red', 'green', 'blue']), 'tiebreak 1': prefer(['red', 'blue', 'green']) })
  const { result, seats } = await run(Q, { voter })
  assert.equal(result.voters, 3)
  assert.equal(seats.length, 3)
  assert.equal(result.winner, 'red')
  assert.equal(result.split, false)
})

test('three different first choices and no tiebreakers left is a split with no winner', async () => {
  const voter = byLabel({ 'vote 1': prefer(['green', 'red', 'blue']), 'vote 2': prefer(['red', 'green', 'blue']), 'tiebreak 1': prefer(['blue', 'red', 'green']) })
  const { result } = await run(Q, { voter })
  assert.equal(result.winner, null)
  assert.equal(result.split, true)
  assert.equal(result.leader, 'red', 'the Borda leader is named, as a leader only')
})

test('each seat runs on the model or agent type it was given', async () => {
  const voter = byLabel({ 'vote 1': prefer(['green', 'red', 'blue']), 'vote 2': prefer(['red', 'green', 'blue']), 'tiebreak 1': prefer(['red', 'blue', 'green']) })
  const { seats, result } = await run({ ...Q, voters: [{ model: 'm-one' }, { agentType: 'other-family' }], tiebreakers: [{ model: 'm-strong', effort: 'xhigh' }] }, { voter })
  assert.deepEqual(seats.map(s => s.model ?? s.agentType), ['m-one', 'other-family', 'm-strong'])
  assert.equal(seats[2].effort, 'xhigh')
  assert.deepEqual(result.seats.map(s => s.seat), ['m-one', 'other-family', 'm-strong'])
})

test('a second tiebreaker runs only if the first left it open', async () => {
  const base = { 'vote 1': prefer(['green', 'red', 'blue']), 'vote 2': prefer(['red', 'green', 'blue']) }
  // The first tiebreaker's seat returns nothing (an errored agent), so the second is needed.
  const open = await run({ ...Q, tiebreakers: [{}, {}] }, { voter: byLabel({ ...base, 'tiebreak 1': () => null, 'tiebreak 2': prefer(['red', 'green', 'blue']) }) })
  assert.equal(open.seats.length, 4)
  assert.equal(open.result.winner, 'red')
  assert.equal(open.result.seats.find(s => s.label === 'tiebreak 1').returned, false, 'a seat that returned nothing is recorded')
  const closed = await run({ ...Q, tiebreakers: [{}, {}] }, { voter: byLabel({ ...base, 'tiebreak 1': prefer(['red', 'blue', 'green']) }) })
  assert.equal(closed.seats.length, 3)
})

test('one voter saying none of these sends it to the tiebreaker', async () => {
  const voter = byLabel({ 'vote 1': prefer(['green', 'red', 'blue']), 'vote 2': prefer(['green', 'red', 'blue'], { none: true }), 'tiebreak 1': prefer(['green', 'red', 'blue']) })
  const { result, seats } = await run(Q, { voter })
  assert.equal(seats.length, 3)
  assert.equal(result.winner, 'green')
})

test('when a majority rules every option out, nothing wins', async () => {
  const { result } = await run(Q, { voter: prefer(['green', 'red', 'blue'], { out: ['red', 'green', 'blue'] }) })
  assert.equal(result.winner, null)
  assert.equal(result.winner_option, null)
  assert.equal(result.none_eligible, true)
})

test('a majority can say none of these', async () => {
  const { result } = await run(Q, { voter: prefer(['green', 'red', 'blue'], { none: true }) })
  assert.equal(result.winner, null)
  assert.equal(result.none_acceptable, true)
})

test('an option ruled out by a majority cannot win, and votes pass to the next choice', async () => {
  const { result } = await run(Q, { voter: prefer(['green', 'red', 'blue'], { out: ['green'] }) })
  assert.equal(result.winner, 'red')
  const row = l => result.table.find(t => t.label === l)
  assert.equal(row('green').eligible, false)
  assert.equal(row('red').first, 2, 'first choices among eligible options')
})

test('options are required: the vote does not write its own', async () => {
  await assert.rejects(() => run({ question: 'q' }, { voter: prefer([]) }), /options/)
})

let failed = 0
for (const [name, fn] of tests) {
  try { await fn(); console.log(`ok    ${name}`) } catch (e) { failed++; console.log(`FAIL  ${name}\n      ${String(e.message).split('\n')[0]}`) }
}
console.log(failed ? `${failed} of ${tests.length} failed` : `all ${tests.length} passed`)
process.exit(failed ? 1 : 0)
