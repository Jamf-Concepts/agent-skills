# Jamf Platform Agent Skills

## About

A collection of agent skills for working with the Jamf Platform — some packaged as Claude Code plugins, some as plain skill directories you drop in.

## Available Skills

| Skill | Product Area | Install | Description |
|--------|-------------|---------|-------------|
| [`jamf-platform-api-migration`](skills/jamf-platform-api-migration/) | Jamf Platform | Skill directory | Convert a script that calls the Jamf Pro, Classic, Protect, or Security Cloud APIs directly into one that reaches the identical outcome over the Jamf Platform API Gateway, with the Jamf Account capability grants it needs. |
| [`connect-action-sets`](plugins/connect-action-sets/) | RapidIdentity | Plugin | Author, review, and refactor RapidIdentity Connect action sets in XML — conventions, logging patterns, JavaScript semantics, and platform best practices. |
| [`rapididentity-workflows`](plugins/rapididentity-workflows/) | RapidIdentity | Plugin | Author, configure, and troubleshoot RapidIdentity portal workflows and their JSON definitions: action nodes, `%{}` variables, valuePairs wiring, workflow forms, approver types, and entitlement creation. |
| [`generate-mr`](plugins/generate-mr/) | RapidIdentity / IDHub | Plugin | Generate and edit IDHub MR Language (Mapping Rule DSL) code for the IDHub Provisioning Pipeline: ingestion, policy, publication, correlation rules, and PVP log triage. |

The **Install** column says which of the two paths below to follow.

## Requirements

- [Claude Code](https://claude.ai/code) (latest)
- A skill directory is the open Agent Skill format — `SKILL.md` plus the files beside it — so those also work on claude.ai and anywhere else that reads the format. Plugins are Claude Code only.

## Installation

### A skill directory

Pull the one directory you want out of this repository and into your skills directory:

```bash
mkdir -p ~/.claude/skills
curl -sL https://github.com/Jamf-Concepts/agent-skills/archive/refs/heads/main.tar.gz \
  | tar -xz -C ~/.claude/skills --strip-components=2 \
      agent-skills-main/skills/jamf-platform-api-migration
```

Everything else in the repository is left behind. Invoke it in any session with its name, `/jamf-platform-api-migration`.

To take it with its git history instead:

```bash
git clone --filter=blob:none --sparse https://github.com/Jamf-Concepts/agent-skills.git
cd agent-skills && git sparse-checkout set skills/jamf-platform-api-migration
```

On claude.ai, zip the skill's directory and upload it under Settings, Capabilities, Skills. The same files work unchanged.

### A plugin

**Step 1 — Add this repository as a marketplace:**

```bash
claude plugin marketplace add https://github.com/Jamf-Concepts/agent-skills.git
```

**Step 2 — Install the plugin(s) you want:**

```bash
claude plugin install connect-action-sets@jamf-agent-skills
claude plugin install rapididentity-workflows@jamf-agent-skills
claude plugin install generate-mr@jamf-agent-skills
```

A plugin's skills are namespaced by the plugin that carries them, so invoke one as `/plugin-name:skill-name` — `/rapididentity-workflows:rapididentity-workflows`. See each plugin's directory for full usage details.

## Contributing

Have skills for a Jamf Platform product? Contributions are welcome.

A skill that ships as a plugin lives in `plugins/<plugin-name>/`, follows the `.claude-plugin` structure, and is registered in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json). A skill that ships as a directory lives in `skills/<skill-name>/` and needs no registration — its `SKILL.md` is the whole contract. Give it a `README.md` too, so the directory explains itself to anyone who clicks into it.

Use the existing entries as reference implementations, then open a PR against the `develop` branch — and update the Available Skills table above as part of that PR. See [CLAUDE.md](CLAUDE.md) for branch conventions.

## License

Copyright 2024, Jamf Software, LLC.  
Offered under the terms of the [Jamf Concepts Use Agreement](https://resources.jamf.com/documents/jamf-concept-projects-use-agreement.pdf).
