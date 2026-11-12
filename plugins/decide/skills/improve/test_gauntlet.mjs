// Tests for gauntlet.js with mocked agents. Run: node test_gauntlet.mjs
import fs from 'node:fs'
import assert from 'node:assert/strict'
import { fileURLToPath } from 'node:url'

const src = fs.readFileSync(fileURLToPath(new URL('./gauntlet.js', import.meta.url)), 'utf8').replace('export const meta', 'const meta')
const AsyncFunction = (async () => {}).constructor
const script = new AsyncFunction('args', 'agent', 'parallel', 'pipeline', 'phase', 'log', src)

// Run the workflow with a scripted agent. challenger(prompt, label) and picker(versions, label) return schema-shaped objects.
async function run(args, { challenger, picker }) {
  const calls = []
  const agent = async (prompt, opts = {}) => {
    calls.push({ label: opts.label, prompt })
    if (/challenge/.test(opts.label)) return challenger(prompt, opts.label)
    if (/pick/.test(opts.label)) {
      const versions = [...prompt.matchAll(/^## Version ([A-Z])\n([\s\S]*?)(?=\n## Version [A-Z]\n|\n## Your task)/gm)].map(m => ({ letter: m[1], text: m[2].trim() }))
      return picker(versions, opts.label)
    }
    throw new Error(`unexpected agent: ${opts.label}`)
  }
  const parallel = thunks => Promise.all(thunks.map(t => t().catch(e => { throw e })))
  const result = await script(args, agent, parallel, null, () => {}, () => {})
  return { result, calls }
}

const rankFirst = wanted => versions => ({
  ranking: [...versions].sort((x, y) => (y.text === wanted) - (x.text === wanted)).map(v => v.letter),
  none_acceptable: false, why: 'w', worry: 'a worry',
})
const step = (verdict, best) => ({ verdict, why: 'w', changes: verdict === 'keep' ? [] : ['changed'], best, residual_doubt: 'd' })
const tests = []
const test = (name, fn) => tests.push([name, fn])

test('the original wins when the challengers made it worse', async () => {
  let n = 0
  const { result, calls } = await run({ proposal: 'ORIGINAL' }, { challenger: () => step('amend', `WORSE ${++n}`), picker: rankFirst('ORIGINAL') })
  assert.equal(result.pick.original_won, true)
  assert.equal(result.answer, 'ORIGINAL')
  assert.equal(calls.filter(c => /pick/.test(c.label)).length, 3)
})

test('a better version wins and the original is still a candidate', async () => {
  let n = 0
  const { result } = await run({ proposal: 'ORIGINAL' }, { challenger: () => step('amend', `V${++n}`), picker: rankFirst('V2') })
  assert.equal(result.answer, 'V2')
  assert.equal(result.pick.original_won, false)
  assert.deepEqual(result.pick.candidates.map(c => c.from), ['original', 'chain 1 step 1', 'chain 1 step 2'])
})

test('when every challenger keeps it, nobody is asked to pick', async () => {
  const { result, calls } = await run({ proposal: 'ORIGINAL' }, { challenger: () => step('keep', 'ORIGINAL'), picker: () => { throw new Error('no pick expected') } })
  assert.equal(result.pick.survived, true)
  assert.equal(result.answer, 'ORIGINAL')
  assert.equal(calls.length, 2)
})

test('several chains end in a blind pick, never a merge agent', async () => {
  const { result, calls } = await run({ proposal: 'ORIGINAL', width: 2, depth: 1 },
    { challenger: (p, label) => step('replace', /chain 1/.test(label) ? 'FROM CHAIN 1' : 'FROM CHAIN 2'), picker: rankFirst('FROM CHAIN 2') })
  assert.equal(calls.some(c => /merge/i.test(c.label)), false)
  assert.equal(result.answer, 'FROM CHAIN 2')
  assert.equal(result.pick.candidates.length, 3)
})

test('pickers see the versions in different orders', async () => {
  let n = 0
  const firsts = new Set()
  await run({ proposal: 'ORIGINAL' }, { challenger: () => step('amend', `V${++n}`), picker: versions => { firsts.add(versions[0].text); return rankFirst('V2')(versions) } })
  assert.ok(firsts.size > 1, 'every picker saw the same version first')
})

test('with only two versions the original is still not always shown first', async () => {
  const firsts = new Set()
  await run({ proposal: 'ORIGINAL', depth: 1 }, { challenger: () => step('amend', 'V1'), picker: versions => { firsts.add(versions[0].text); return rankFirst('V1')(versions) } })
  assert.ok(firsts.size > 1, 'every picker saw the same version first')
})

test('a majority can say none is acceptable', async () => {
  let n = 0
  const { result } = await run({ proposal: 'ORIGINAL' }, { challenger: () => step('amend', `V${++n}`), picker: v => ({ ...rankFirst('V2')(v), none_acceptable: true }) })
  assert.equal(result.pick.none_acceptable, true)
  assert.equal(result.answer, null)
})

test('a malformed ballot is dropped, not guessed', async () => {
  let n = 0, p = 0
  const { result } = await run({ proposal: 'ORIGINAL' }, { challenger: () => step('amend', `V${++n}`),
    picker: v => (++p === 1 ? { ranking: ['A', 'A', 'Z'], none_acceptable: false, why: '', worry: '' } : rankFirst('V1')(v)) })
  assert.equal(result.pick.dropped, 1)
  assert.equal(result.answer, 'V1')
})

test('pick: false leaves the choice to the caller', async () => {
  let n = 0
  const { result, calls } = await run({ proposal: 'ORIGINAL', pick: false }, { challenger: () => step('amend', `V${++n}`), picker: () => { throw new Error('no pick expected') } })
  assert.equal(result.pick, null)
  assert.equal(calls.length, 2)
})

let failed = 0
for (const [name, fn] of tests) {
  try { await fn(); console.log(`ok    ${name}`) } catch (e) { failed++; console.log(`FAIL  ${name}\n      ${String(e.message).split('\n')[0]}`) }
}
console.log(failed ? `${failed} of ${tests.length} failed` : `all ${tests.length} passed`)
process.exit(failed ? 1 : 0)
