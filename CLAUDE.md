# CLAUDE.md — agent-skills

## What This Repo Does

<!-- Fill in: one paragraph describing the purpose, target users, and key outcome -->

## How to Build / Run

<!-- Fill in: install and run commands, e.g.:
```bash
npm install
npm run dev
```
-->

## Key Files

<!-- Fill in: point Claude to the files that matter most, e.g.:
- `src/main.ts` — entry point
- `config/` — configuration files
-->

## Where a New Skill Goes

Two packagings, two directories. Both hold agent skills; the difference is how a user installs one.

- `plugins/<plugin-name>/` — ships as a Claude Code plugin, follows the `.claude-plugin` structure, and must be registered in `.claude-plugin/marketplace.json`. Its skills are namespaced on invocation: `/plugin-name:skill-name`.
- `skills/<skill-name>/` — ships as a plain skill directory a user drops into their own skills directory or uploads to claude.ai. No registration; `SKILL.md` is the whole contract, and the skill is invoked by its own name. Include a `README.md` so the directory explains itself on GitHub.

Adding either one means updating the Available Skills table in `README.md` in the same PR.

## Branch Flow

`develop` → `main` via PR. Never commit directly to `main`.

All changes go through a PR — even small fixes.

## Org Safety Rule

Before any `git push`, confirm the remote is the expected org:

```bash
git remote get-url origin
```

Never push a Jamf-Concepts project to the `jamf` org (or any other org) without confirming first.

## Temp Files (Background Sessions)

Use `$CLAUDE_JOB_DIR/tmp` for all temp files in background Claude Code sessions. Never use `/tmp` — parallel jobs share it.
