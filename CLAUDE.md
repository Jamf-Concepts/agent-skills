# CLAUDE.md — \<repo_name\>

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
