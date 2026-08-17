![GitHub release (latest by date)](https://img.shields.io/github/v/release/Jamf-Concepts/agent-skills?display_name=tag)
![GitHub all releases](https://img.shields.io/github/downloads/Jamf-Concepts/agent-skills/total)
![GitHub issues](https://img.shields.io/github/issues-raw/Jamf-Concepts/agent-skills)
![GitHub closed issues](https://img.shields.io/github/issues-closed-raw/Jamf-Concepts/agent-skills)
![GitHub pull requests](https://img.shields.io/github/issues-pr-raw/Jamf-Concepts/agent-skills)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed-raw/Jamf-Concepts/agent-skills)

# agent-skills

> A Claude plugin marketplace of packaged skills that give AI agents working knowledge of the Jamf platform.

## About

Each plugin covers a single task or product area, so agents operate with real Jamf/RapidIdentity
context instead of generic knowledge. Currently ships three plugins (one skill each), all in the
RapidIdentity domain:

| Plugin | Domain | Triggers on |
|---|---|---|
| `connect-action-sets` | Connect action set XML | Connect XML, `.dssproject`, action sets, suppressTrace, argDefs, scheduled jobs, CSV builds |
| `rapididentity-workflows` | Portal workflows, entitlements, Requests module | workflow JSON, `%{}` variables, advancedDssAction, valuePairs, approvals, entitlement creation |
| `generate-mr` | IDHub MR Language (Mapping Rule DSL) | `.mr` files, mapping/ingestion/policy/publication rules, PVP log triage |

The skills are kept as separate plugins deliberately: each has its own trigger vocabulary and
loads only when relevant; cross-domain tasks trigger multiple skills together, and they
cross-reference each other. (This marketplace was migrated from the standalone
`jessehalljamf/rapididentity-skills` repo, which itself began as the `connect-action-sets` skill
only — the workflows and MR skills were consolidated in from their original standalone repos on
2026-07-28.)

## Requirements

- [Claude Code](https://claude.com/claude-code), Claude Desktop, Claude Cowork, or claude.ai chat
- For live-tenant RapidIdentity operations (user search, entitlements, groups, audit logs), pair
  with [`mcp-rapidid`](https://github.com/Jamf-Concepts/mcp-rapidid) — a standalone MCP server,
  not a plugin in this marketplace. Install it per its own README.

## Installation

### Claude Code (recommended)

```bash
claude plugin marketplace add Jamf-Concepts/agent-skills
```

Then install any or all of: `connect-action-sets`, `rapididentity-workflows`, `generate-mr`
(via `/plugin` or `claude plugin install <name>@jamf-identity-plugins`).

For local testing: `claude --plugin-dir ./plugins/<plugin-name>`.

### Claude Desktop / Cowork

Upload the per-plugin bundles: [`connect-action-sets.plugin`](./connect-action-sets.plugin),
[`rapididentity-workflows.plugin`](./rapididentity-workflows.plugin),
[`generate-mr.plugin`](./generate-mr.plugin).

### Claude.ai chat (per-skill upload)

Chat installs skills individually: [`connect-action-sets.skill`](./connect-action-sets.skill),
[`rapididentity-workflows.skill`](./rapididentity-workflows.skill),
[`generate-mr.skill`](./generate-mr.skill).

## Usage

Skills are namespaced by plugin: `/connect-action-sets:connect-action-sets`,
`/rapididentity-workflows:rapididentity-workflows`, `/generate-mr:generate-mr`. Model
auto-triggering from skill descriptions is unaffected by namespacing.

In Desktop, Cowork, and claude.ai chat there is no slash-command invocation — that syntax is
Claude Code-only. Skills there auto-trigger purely from matching the skill's description against
your request; just describe the task naturally (e.g. mention Connect XML or a `.dssproject` file)
and Claude loads the relevant skill on its own.

`connect-action-sets` also bundles Claude Code hooks for navigating minified Connect XML
(pretty-printed sidecar on `Read`, well-formedness check after `Edit`/`Write`, a `Grep` guard
against single-line context bombs) — these auto-install with the plugin, no manual setup. If your
project runs JUnit/Gradle tests, set `CONNECT_HOOKS_PROJECT_PACKAGE` (e.g. `net.idauto`) so
test-failure summaries filter stack frames to your package.

## Repo layout

```
.claude-plugin/marketplace.json        # the marketplace manifest
plugins/
├── connect-action-sets/
│   ├── .claude-plugin/plugin.json
│   ├── hooks/                         # hooks.json + minified-XML read/grep guards, edit validator
│   └── skills/connect-action-sets/    # SKILL.md + 13 references
├── rapididentity-workflows/
│   ├── .claude-plugin/plugin.json
│   └── skills/rapididentity-workflows/  # SKILL.md + live-capture reference
└── generate-mr/
    ├── .claude-plugin/plugin.json
    └── skills/generate-mr/            # SKILL.md + 3 references
TODO.md                                # skill-correction queue (see header for workflow)
```

## Notable references inside the skills

| Need | Location |
|------|----------|
| XML format rules, escaping, root element | `connect-action-sets` SKILL.md § XML Format Rules |
| Full builtin-action catalogue (grep it, never load whole) | `connect-action-sets` `references/connect-builtin-actions.json` |
| Task → builtin → verified call lookup | `connect-action-sets` `references/native-action-cheatsheet.md` |
| Connection patterns by target system | `connect-action-sets` `references/connections.md` |
| Workflow JSON ground truth (live tenant capture) | `rapididentity-workflows` `references/live-capture-request-sponsored-account.md` |
| MR Language patterns and builtins | `generate-mr` `references/patterns.md`, `references/builtins.md` |
| PVP log triage (logs can exceed 1GB — never read whole) | `generate-mr` `references/debugging-pvp-logs.md` |

## Contributing

Open a PR against the `develop` branch. See [CLAUDE.md](CLAUDE.md) for branch and org conventions.

## License

Copyright 2024, Jamf Software, LLC.
Offered under the terms of the [Jamf Concepts Use Agreement](https://resources.jamf.com/documents/jamf-concept-projects-use-agreement.pdf).
