# AGENTS.md

**Single source of truth for coding agents** (Claude Code, Cursor, Copilot, Aider, etc.).  
Takes precedence over `README.md`, `CLAUDE.md`, and similar instruction files.  
Claude Code loads this file through the one-line `@AGENTS.md` reference in `CLAUDE.md`.

## Orchestration Contract
This file codifies project rules, boundaries, workflows, and repeatable skills. If the same correction repeats, formalize it here instead of re-prompting it.

## Project Overview
Jamf Platform agent skills. Each skill is a focused body of knowledge about one Jamf product area — its APIs, file formats, conventions, and mistakes worth avoiding. Upstream: `Jamf-Concepts/agent-skills`.

Two packagings, same content type:
- **Skill directory** (`skills/<skill-name>/`): `SKILL.md` plus reference files; installed by `curl`/upload; invoked as `/<skill-name>`; portable to Claude Code, claude.ai, the Claude API, and any Agent Skills–standard tool.
- **Plugin** (`plugins/<plugin-name>/`): Claude Code plugin carrying one or more skills plus optional hooks, subagents, MCP or LSP servers; installed from marketplace `jamf-agent-skills`; invoked as `/<plugin-name>:<skill-name>`.

Repo is Markdown-first. No build step, no runtime, no package manager. CI only validates JSON and lints plugin Python.

## Key Commands
- Validate JSON (mirrors CI): `find . -name "*.json" -not -path "*/.git/*" | xargs -I {} python3 -m json.tool {} > /dev/null`
- Lint plugin Python (only when `plugins/**/*.py` exists): `pip install ruff==0.16.7 --only-binary :all: && ruff check plugins/`
- Read a skill's version: `sed -n '1,12p' skills/<skill-name>/SKILL.md` → `metadata.version`
- Confirm remote before any push: `git remote get-url origin`

## Agent Workflow
- Start non-trivial changes in Plan mode or equivalent.
- In Plan mode, make no changes and propose no code until confidence is at least 95%; ask follow-up questions until then.
- Treat context like a scalpel, not a net; provide only files, lines, and examples needed. `SKILL.md` and its reference files are long — read the sections the task touches.
- Use surgical edits; reference exact headings or line ranges instead of pasting large sections.
- Check `git status` before editing so unrelated local work is not overwritten.
- In background Claude Code sessions, put temp files in `$CLAUDE_JOB_DIR/tmp`. Never use `/tmp` — parallel jobs share it.
- Confirm this file is loaded before starting a session.
- Use codified Skills below when they fit instead of re-describing the workflow.

## Skills
Invoke relevant skill name during planning.

### Add New Skill Directory Skill
1. Create `skills/<skill-name>/`; directory name equals frontmatter `name`.
2. Write `SKILL.md` with portable frontmatter only: `name`, `description` (what it does + when to use it, with trigger phrases), `compatibility`, `metadata.version`, `allowed-tools`. Nothing surface-specific.
3. Put reference material in sibling files one level deep, linked from `SKILL.md` with relative links.
4. Add `README.md` for people: install, what it needs, what it never does, layout table, versioning, changelog. State that `SKILL.md` is what the harness reads.
5. Add a row to the Available Skills table in root `README.md` in the same PR.

### Add New Plugin Skill
1. Create `plugins/<plugin-name>/` following `.claude-plugin` structure.
2. Register it in `.claude-plugin/marketplace.json` (marketplace name `jamf-agent-skills`). File does not exist yet; first plugin creates it.
3. Hooks: executable, referenced correctly from `hooks.json`, Python passes `ruff check plugins/` (`ruff.toml`: py311, rules `E4,E7,E9,F`).
4. All JSON must pass `python3 -m json.tool`.
5. Add a row to the Available Skills table in root `README.md` in the same PR.

### Update Existing Skill / Release Skill
1. Classify change with the skill's own semver rules (see its `README.md` → Versioning). For `jamf-platform-api-migration`: patch = bundled data refresh or wording; minor = conversion rule added or changed; major = report structure changed.
2. Bump `metadata.version` in `SKILL.md` frontmatter.
3. Sync every hardcoded copy of the version: `SKILL.md` Output contract examples, README version badge, README Versioning section.
4. When bundled permissions-map data is refreshed, update its date everywhere that permissions-map date appears: frontmatter `metadata.bundled-permissions-map`, `capability-grants.md`, README badge, README Versioning section, and README audit notes. Update the `conversion-rules.md` known-version table date only when that table is independently re-verified.
5. Add a changelog entry in the skill's `README.md` with date.

## Boundaries
**Always allowed without asking**
- Read any repository file.
- Run JSON validation, `ruff`, link checks, and `git status`/`git diff`.
- Make small targeted doc or skill edits that follow rules below.

**Ask before doing**
- Add a new skill or plugin, or create `.claude-plugin/marketplace.json`.
- Bump a skill's version or prepare a release.
- Change a skill's output contract, report structure, file-naming rules, or stop conditions.
- Edit `.github/` (CI, templates, CODEOWNERS, dependabot) or `ruff.toml`.
- Add dependencies or tooling.
- `git push`, or open a PR.

**Never do**
- Commit directly to `main`.
- Push without confirming the remote with `git remote get-url origin`; never push a Jamf-Concepts project to the `jamf` org (or any other org) without confirming first.
- Commit secrets, client IDs, tenant hostnames, or organization-specific data — including in skill examples.
- Commit audit output (`*-concept-audit-report-*`, `codeql-results-*.sarif`, `gitleaks-results-*.txt`) or `.claude/settings.local.json`.
- Modify files outside current task scope without approval.

## Source of Truth
When files disagree, prefer:
1. `skills/<skill-name>/SKILL.md` and its reference files for skill behavior; its frontmatter for version and bundled-data dates.
2. Live `developer.jamf.com` pages over bundled tables inside a skill.
3. `.github/workflows/ci.yml` for what is actually enforced.
4. Root `README.md` for catalog and install instructions.
5. Skill `README.md` for human-facing docs, versioning policy, and changelog.

## Mission and Scope
Mission: give agents accurate, product-specific Jamf knowledge so they stop guessing, packaged so admins can install one skill without the rest.

In scope:
- Skills and plugins covering Jamf products and APIs (Pro, Classic, Protect, Security Cloud, Platform API Gateway, Jamf Account)
- Reference material, worked examples, and output contracts those skills rely on
- Plugin hooks that validate artifacts a skill produces

Out of scope:
- Hosted services or runtime code that calls Jamf APIs on the repo's behalf
- Non-Jamf skills
- Anything requiring credentials to live in the repo

## Implementation Priorities
1. Correctness against published Jamf documentation; flag assumptions instead of guessing.
2. Portability: skill directories run unchanged on every Agent Skills surface.
3. Deterministic output: two runs of one request produce the same files and names.
4. Safety: skills never reproduce secrets, never modify user originals, never run user scripts.
5. Repeated copies of the same version or date value stay synchronized across `SKILL.md`, reference files, and READMEs.

## Key Files
- `README.md`: catalog (Available Skills table), packaging comparison, install, troubleshooting
- `skills/jamf-platform-api-migration/`: only shipped skill (v1.0.0). `SKILL.md` = procedure + output contract; `conversion-rules.md`, `capability-grants.md`, `protect-graphql.md`, `runtime-behavior.md`, `examples.md` = references; `README.md` = humans only
- `.github/workflows/ci.yml`: JSON validation + conditional ruff on PRs to `main`
- `.github/PULL_REQUEST_TEMPLATE.md`: PR checklist (tested, no secrets, docs updated, branch-target reminder)
- `.github/CODEOWNERS`: `@Jamf-Concepts/jamf-concepts-write` owns everything
- `ruff.toml`, `.gitignore`, `SECURITY.md`, `LICENSE.md` (MIT, Jamf Software, LLC)

## Current Hotspots
- `jamf-platform-api-migration` works with and without network: live lookups on `developer.jamf.com` win; bundled tables are fallback. Edits must keep both paths working and keep the report saying which was used.
- The skill checks `main` for a newer published version on every invocation (`SKILL.md` → "Check for a newer version first"). A version bump on `main` is user-visible immediately.
- Root `README.md` references a `connect-action-sets` plugin, `plugins/<plugin-name>/hooks/`, and `xml_validate.py` that do not exist in this repo yet. Treat as documentation debt; do not "fix" by inventing them.
- No `plugins/` directory and no `.claude-plugin/marketplace.json` yet; CI's ruff step is skipped until plugin Python lands.

## Repository Rules
- Branch flow for this repository today: work on `develop` in a fork or local branch, then open a PR to upstream `main`. Upstream `Jamf-Concepts/agent-skills` does not currently have a `develop` branch. Never commit directly to `main`. All changes go through a PR — even small fixes.
- `origin` may be a personal fork; upstream is `Jamf-Concepts/agent-skills`. Know which remote and branch you are pushing to.
- Adding a skill or plugin means updating the Available Skills table in root `README.md` in the same PR.
- Prefer minimal targeted edits over broad rewrites. Avoid hidden behavior changes.
- If a skill's behavior changes, bump its version and add a changelog entry.

## Skill Authoring Style
Match existing `jamf-platform-api-migration` voice unless user explicitly asks otherwise.

1. Plain declarative prose. Rules stated once, as rules, with the reason beside them.
2. **Bold** the load-bearing sentence of a rule; keep emphasis rare so it carries weight.
3. Give defaults instead of questions: the skill settles what it can, states the assumption, and says what to change if wrong.
4. Name concrete examples inline (`pro-delete-computer.sh` gives `platform-delete-computer.sh`) so output is predictable.
5. Relative links between sibling files; reference files stay one level deep.
6. `SKILL.md` is for the harness; `README.md` is for people. Do not duplicate procedure into the README.
7. Examples use placeholders for hosts, IDs, and secrets; secrets are named by variable and line, never quoted.
8. Keep frontmatter portable — no fields that only one surface understands.

## Required Validation
1. All JSON passes `python3 -m json.tool`.
2. Plugin Python passes `ruff check plugins/`.
3. `SKILL.md` frontmatter parses as YAML and `name` matches directory name.
4. Relative links in touched Markdown resolve.
5. Repeated copies of the same version or date string agree across `SKILL.md`, reference files, and README.
6. Root `README.md` Available Skills table matches `skills/` and `plugins/`.
7. For `AGENTS.md`-only changes, review rendered Markdown and cross-file consistency.

## Release Checklist
Apply only for release prep.
1. Version bumped per the skill's semver rules; every hardcoded copy synced.
2. Changelog entry dated and matching shipped behavior.
3. Bundled permissions-map date and any other independently verified data dates refreshed where that data was refreshed.
4. Root `README.md` table current.
5. PR from fork/local `develop` to upstream `main`; CI green.

## Maintenance
This file is versioned with project. When structure, boundaries, or validation requirements change, update `AGENTS.md` in the same PR. Keep file near 200 lines for agent attention.
