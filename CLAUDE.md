# CLAUDE.md — agent-skills

## What This Repo Does

A Claude plugin marketplace (`jamf-identity-plugins`) of packaged skills that give AI agents
working knowledge of the Jamf/RapidIdentity platform. Each plugin under `plugins/` bundles exactly
one skill scoped to a single task or product area (Connect action set XML, portal workflows, or
IDHub MR Language) so it loads only when relevant, rather than acting as generic knowledge. The
marketplace manifest (`.claude-plugin/marketplace.json`) lists all three plugins; each plugin has
its own `.claude-plugin/plugin.json` plus a `skills/<name>/SKILL.md` and `references/` directory.

## How to Build / Run

There is no build step for using the skills — Claude Code, Desktop, Cowork, and claude.ai chat all
consume the source tree or the prebuilt `.plugin`/`.skill` bundle files directly (see README.md).

Building/refreshing the distributable bundles (after editing any plugin's `SKILL.md` or
references) requires PowerShell:

```bash
pwsh scripts/build.ps1
```

This regenerates all `.plugin` and `.skill` bundle zips for every plugin in one run — if only one
plugin changed, revert the untouched bundles before committing.

## Key Files

- `.claude-plugin/marketplace.json` — the marketplace manifest (plugin list, versions)
- `plugins/<name>/.claude-plugin/plugin.json` — per-plugin manifest (version, repository URL)
- `plugins/<name>/skills/<name>/SKILL.md` — the skill's entry point and instructions
- `plugins/<name>/skills/<name>/references/` — supporting reference docs the skill loads on demand
- `plugins/connect-action-sets/hooks/` — Claude Code hooks (XML read/grep guards, edit validator)
- `TODO.md` — skill-correction queue; see its header for the intended workflow

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
