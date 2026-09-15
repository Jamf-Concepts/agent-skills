# Jamf Platform Agent Skills

Each skill in this repository is a focused body of knowledge about one Jamf product area — its APIs, its file formats, its conventions, and the mistakes worth avoiding. Install one and Claude stops guessing.

## Available Skills

| Skill | Product Area | Format | Description |
| --- | --- | --- | --- |
| [`jamf-platform-api-migration`](skills/jamf-platform-api-migration/) | Jamf Platform | Skill directory | Convert a script that calls the Jamf Pro, Classic, Protect, or Security Cloud APIs directly into one that reaches the identical outcome over the Jamf Platform API Gateway, with the Jamf Account capability grants it needs. |
| [`connect-action-sets`](plugins/connect-action-sets/) | RapidIdentity | Plugin | Author, review, and refactor RapidIdentity Connect action sets in XML: conventions, coding standards, logging patterns, JavaScript semantics, and platform best practices. |
| [`rapididentity-workflows`](plugins/rapididentity-workflows/) | RapidIdentity | Plugin | Author, configure, and troubleshoot RapidIdentity portal workflows and their JSON definitions: action nodes, `%{}` variables, valuePairs wiring, workflow forms, approver types, and entitlement creation. |
| [`generate-mr`](plugins/generate-mr/) | RapidIdentity / IDHub | Plugin | Generate and edit IDHub MR Language (Mapping Rule DSL) for the IDHub Provisioning Pipeline: ingestion, policy, publication, correlation rules, and PVP log triage. |

## Skills and plugins

Everything here is an agent skill. **Format** is how it is packaged and delivered, and it determines how you install it.

| | Skill directory | Plugin |
| --- | --- | --- |
| **What it is** | `SKILL.md` and the reference files beside it | A container that carries one or more skills |
| **Install with** | `curl`, or upload the folder | `claude plugin install` |
| **Update by** | Running the install again | The marketplace, when its version changes |
| **Invoke as** | `/skill-name` | `/plugin-name:skill-name` |
| **Runs in** | Claude Code, claude.ai, the Claude API, and any tool that reads the [Agent Skills](https://agentskills.io) standard | Claude Code |
| **Can also ship** | Nothing but the skill | Hooks, subagents, MCP servers, LSP servers |

A plugin earns its keep when a skill needs more than instructions. `connect-action-sets` ships hooks that validate XML before Claude writes it, which no skill directory can do. Where a skill is instructions and reference material alone, either format works, and the plugin route trades portability for versioned updates.

## Requirements

[Claude Code](https://claude.ai/code), current release, for anything in this repository. Skill directories additionally work anywhere the Agent Skills standard is supported, including claude.ai and the Claude API.

## Installation

Substitute `<skill-name>` or `<plugin-name>` below with the name from the Available Skills table above. Each entry there links to the directory it lives in.

<details>
<summary><b>Skill directory</b> · drop the folder in and invoke it by name</summary>

<br>

Pull one skill out of this repository into your personal skills directory:

```bash
mkdir -p ~/.claude/skills
curl -sL https://github.com/Jamf-Concepts/agent-skills/archive/refs/heads/main.tar.gz | tar -xz -C ~/.claude/skills --strip-components=2 agent-skills-main/skills/<skill-name>
```

Nothing else from the repository comes with it. Invoke the skill in any session as `/<skill-name>`.

To take a skill with its git history instead:

```bash
git clone --filter=blob:none --sparse https://github.com/Jamf-Concepts/agent-skills.git
cd agent-skills && git sparse-checkout set skills/<skill-name>
```

**On claude.ai**, zip the skill's directory and upload it under Settings → Capabilities → Skills. **On the Claude API**, upload the directory through the Skills API and attach the skill to your request. The same files work unchanged in all three places.

</details>

<details>
<summary><b>Plugin</b> · install from the marketplace and get updates</summary>

<br>

Add this repository as a marketplace once:

```bash
claude plugin marketplace add https://github.com/Jamf-Concepts/agent-skills.git
```

Then install what you want:

```bash
claude plugin install <plugin-name>@jamf-agent-skills
```

A plugin's skills are namespaced by the plugin carrying them, so invoke one as `/<plugin-name>:<skill-name>`.

</details>

## Getting Help

Open an issue at <https://github.com/Jamf-Concepts/agent-skills/issues> or ask in [#team-jamf-concepts-developers](https://jamf.slack.com/archives/team-jamf-concepts-developers) on Slack.

## Troubleshooting

**Skill not invoked:** Confirm the skill directory is in `~/.claude/skills/<skill-name>/` and contains a `SKILL.md`. Restart Claude Code.

**Plugin not found after install:** Run `claude plugin list` to verify the plugin installed correctly. Re-run `claude plugin install <plugin-name>@jamf-agent-skills` if needed.

**Hook not firing:** Check that the hooks in `plugins/<plugin-name>/hooks/` are executable and that `hooks.json` correctly references each hook file. Review Claude Code output for Python errors if a hook exits unexpectedly.

**XML validation errors from `xml_validate.py`:** The hook validates well-formedness after every XML edit. The error message includes the parse error — correct the XML before continuing.

## License

Copyright 2024, Jamf Software, LLC.  
Offered under the terms of the [Jamf Concepts Use Agreement](https://resources.jamf.com/documents/jamf-concept-projects-use-agreement.pdf).

For information on how Jamf handles personal data, see the [Jamf Privacy Policy](https://jamf.com/privacy).
