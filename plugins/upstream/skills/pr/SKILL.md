---
name: pr
description: "Send a pull request to a repository someone else owns: read the project's agent instructions (CLAUDE.md, AGENTS.md), README and contributing guide before writing any commit, check its AI policy and existing issues, fork and branch, match its commit and PR conventions, run its checks, then show the user the draft before opening it. Use for \"send a PR\", \"open a PR upstream\", \"contribute this fix\", \"submit this to <owner>/<repo>\", \"file a PR against\", or any change bound for a GitHub repo the user doesn't own. Not for the user's own repos or branches."
---

# Sending a PR upstream

A PR to someone else's repo is a request for a stranger's time. The maintainer owes you nothing, and an agent-written PR that ignores their rules costs them more than it gives. The job is to make the PR easy to say yes to: it follows their conventions, solves a problem they want solved, and is small enough to review in one sitting.

The most common failure is writing the change first and reading the rules afterward, then finding out the project wanted a different commit format, a sign-off, an issue first, a changeset file, or no AI-written code at all. So the reading comes first.

## 1. Read the project's instructions before authoring any commit

Do this before you write code, not just before you commit. Read these files in full, from the upstream default branch, not a stale fork:

- **Agent instructions:** `CLAUDE.md` and `AGENTS.md` at the root, plus any in the directories you will touch (they nest, and the nearest one wins). Also look for `.github/copilot-instructions.md`, `.cursorrules`, `.cursor/rules/`, `GEMINI.md` and `.windsurfrules`. Whatever tool they were written for, they are the maintainer telling agents what they want.
- **`README.md`:** what the project is for, how it is built and tested, and what is out of scope.
- **`CONTRIBUTING.md`** (at the root, in `.github/` or in `docs/`), `.github/PULL_REQUEST_TEMPLATE.md` or `.github/PULL_REQUEST_TEMPLATE/`, and `CODE_OF_CONDUCT.md`.
- **Tooling that enforces conventions:** commitlint config, `.pre-commit-config.yaml`, `.editorconfig`, linter and formatter configs, `.changeset/`, `CHANGELOG.md` (do entries go in with the PR?), and the CI workflows in `.github/workflows/` (these show which checks your PR must pass).

```bash
gh repo view OWNER/REPO --json defaultBranchRef,description,isArchived,visibility
gh api repos/OWNER/REPO/contents/ --jq '.[].name'          # root listing, without cloning
gh api repos/OWNER/REPO/contents/AGENTS.md --jq .content | base64 -d
```

Write down the rules that apply to this change: commit format, sign-off, branch naming, test command, PR template fields, anything it says about AI. You will check the finished PR against this list in step 6.

If the files say "no AI-generated contributions", stop and tell the user. Don't route around it. If they ask for disclosure, plan to disclose.

## 2. Check that the PR is wanted

- **Is the repo alive?** Archived, or no merges in a year: tell the user before investing in it.
- **Search for duplicates:** `gh issue list -R OWNER/REPO --search "KEYWORDS" --state all` and `gh pr list -R OWNER/REPO --search "KEYWORDS" --state all`. A closed PR that was rejected tells you what the maintainer doesn't want. An open one may mean you should comment there instead.
- **Issue first?** If CONTRIBUTING asks for an issue before non-trivial PRs, or the change is a feature, a design choice or a breaking change, propose an issue first and let the user decide. Typo fixes, clear bug fixes and doc fixes usually don't need one.

## 3. Fork and branch

```bash
gh repo fork OWNER/REPO --clone --remote    # origin = your fork, upstream = theirs
git fetch upstream
git switch -c fix/short-description upstream/DEFAULT_BRANCH
```

Branch from fresh upstream, never from your fork's possibly stale default branch. Use their branch-naming convention if they have one.

## 4. Make the change their way

- **Keep it small and on one topic.** One problem per PR. No drive-by refactors, no reformatting lines you didn't otherwise change, no dependency bumps, no "while I was here". If you find a second problem, it is a second PR, or a note to the user.
- **Match the surrounding code**, not your preferences: naming, error handling, comment density, test style.
- **Add or update tests** the way the project already tests. For a bug fix, the test should fail without the fix.
- **Run their checks locally**, using the commands from the README, CONTRIBUTING or CI workflows: tests, linter, formatter, type checker. Don't open a PR you know is red.

## 5. Commit their way

- **Message format:** read `git log --oneline -20 upstream/DEFAULT_BRANCH` and match it (Conventional Commits, `area: summary`, imperative mood, ticket prefix, line lengths).
- **Sign-off:** if they use a DCO (a `Signed-off-by` check in CI, or DCO named in CONTRIBUTING), commit with `git commit -s`. A sign-off certifies something about the user, so it uses the user's name, and you tell the user you added it. If they need a CLA signed, tell the user; only they can sign it.
- **Attribution trailers:** use your usual `Co-Authored-By` trailer for the agent unless the project's rules say otherwise. Their rules win.
- **History:** a few clean commits, or one, as their history suggests. Squash fixups before opening.
- **No secrets, local paths or private context** in the diff, commit messages or PR text: no home-directory paths, no internal hostnames, no names of the user's other projects.

## 6. Write the PR, and show it to the user before opening it

Opening a PR is public and pings real people, so draft it and get the user's go-ahead first. Show the title, the body and `git diff --stat upstream/DEFAULT_BRANCH`.

- **Fill in their template** if they have one, every section. Don't replace it with your own format.
- **Body:** what problem this solves (link the issue: `Fixes #123`), what changed, and how it was tested (the commands run and their results). Keep it short. Maintainers skim.
- **Disclose agent authorship** in the body, at least in one line, even if the project doesn't ask. If they ask for a specific form of disclosure, use that.
- **Mentions:** only `@` a real login you mean to notify. Put code like `@types/node` in backticks.
- **Check against your step-1 list:** commit format, sign-off, template, changelog entry, tests, checks passing.

```bash
git push -u origin HEAD
gh pr create -R OWNER/REPO --base DEFAULT_BRANCH --head YOUR_LOGIN:BRANCH \
  --title "..." --body-file pr-body.md
```

Leave "Allow edits from maintainers" on (the `gh` default), so they can make small fixes themselves rather than ask you. Open as a draft (`--draft`) only if the project uses drafts or the user wants early feedback.

## 7. After opening

- **Watch CI:** `gh pr checks NUMBER -R OWNER/REPO --watch`. If something fails that you caused, fix it with a new commit, or with a force-push if their history rules want that. If the failure isn't yours (a flaky test, or a check that is broken upstream too), say so in a comment rather than touching unrelated code.
- **Review comments:** address each one, or explain why not. Don't argue style; it's their project. Before replying for the user, show them the reply.
- **Silence:** one polite ping after a week or two is fine. More is not.

## Done means

The PR is open, it follows every rule from step 1, its checks pass (or failures are explained), and the user has the link.
