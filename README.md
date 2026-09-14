# Jamf Platform Agent Skills

## About

A collection of Claude Code plugins — packaged agent skills for working with the Jamf Platform.

## Available Skills

| Plugin | Product Area | Description |
|--------|-------------|-------------|
| [`connect-action-sets`](plugins/connect-action-sets/) | RapidIdentity | Author, review, and refactor RapidIdentity Connect action sets in XML — conventions, logging patterns, JavaScript semantics, and platform best practices. |
| [`rapididentity-workflows`](plugins/rapididentity-workflows/) | RapidIdentity | Author, configure, and troubleshoot RapidIdentity portal workflows and their JSON definitions: action nodes, `%{}` variables, valuePairs wiring, workflow forms, approver types, and entitlement creation. |
| [`generate-mr`](plugins/generate-mr/) | RapidIdentity / IDHub | Generate and edit IDHub MR Language (Mapping Rule DSL) code for the IDHub Provisioning Pipeline: ingestion, policy, publication, correlation rules, and PVP log triage. |

## Requirements

- [Claude Code](https://claude.ai/code) (latest)

## Installation

**Step 1 — Add this repository as a marketplace:**

```bash
claude plugin marketplace add https://github.com/Jamf-Concepts/agent-skills.git
```

**Step 2 — Install the skill(s) you want:**

```bash
claude plugin install connect-action-sets@jamf-agent-skills
claude plugin install rapididentity-workflows@jamf-agent-skills
claude plugin install generate-mr@jamf-agent-skills
```

Once installed, invoke a skill from within Claude Code using its slash-command name (e.g. `/rapididentity-workflows`). See each plugin's directory for full usage details.

## Contributing

Have skills for a Jamf Platform product? Contributions are welcome.

Each plugin lives in `plugins/<plugin-name>/` and follows the `.claude-plugin` structure. Use the existing plugins as reference implementations, then open a PR against the `develop` branch — and update the Available Skills table above as part of that PR. See [CLAUDE.md](CLAUDE.md) for branch conventions.

## License

Copyright 2024, Jamf Software, LLC.  
Offered under the terms of the [Jamf Concepts Use Agreement](https://resources.jamf.com/documents/jamf-concept-projects-use-agreement.pdf).
