# Jamf Platform Agent Skills

## About

This repository is a growing library of [Claude Code](https://claude.ai/code) plugins — packaged agent skills that extend Claude's capabilities for working with Jamf platform products and partner integrations.

Today it ships with a set of skills for RapidIdentity, authored by the Jamf CE team. The vision is broader: as the Jamf platform expands and the CE and engineering communities build out skills for Jamf Pro, Jamf Connect, Jamf Protect, Jamf School, and ecosystem integrations, this is where they live and are shared publicly with the community.

If your team works with a Jamf platform product and has built skills worth sharing, contributions are welcome.

## Available Skills

| Plugin | Product Area | Description |
|--------|-------------|-------------|
| [`connect-action-sets`](plugins/connect-action-sets/) | RapidIdentity | Author, review, and refactor RapidIdentity Connect action sets in XML — conventions, logging patterns, JavaScript semantics, and platform best practices. |
| [`rapididentity-workflows`](plugins/rapididentity-workflows/) | RapidIdentity | Author, configure, and troubleshoot RapidIdentity portal workflows and their JSON definitions: action nodes, `%{}` variables, valuePairs wiring, workflow forms, approver types, and entitlement creation. |
| [`generate-mr`](plugins/generate-mr/) | RapidIdentity / IDHub | Generate and edit IDHub MR Language (Mapping Rule DSL) code for the IDHub Provisioning Pipeline: ingestion, policy, publication, correlation rules, and PVP log triage. |

## Requirements

- [Claude Code](https://claude.ai/code) (latest)

## Installation

Install the full skill collection as a Claude Code plugin:

```bash
claude plugin install Jamf-Concepts/agent-skills
```

Or reference a specific plugin directory when installing individually.

Once installed, invoke skills from within Claude Code using their slash-command names (e.g. `/rapididentity-workflows`, `/connect-action-sets`, `/generate-mr`). See each plugin's directory for full usage details.

## Contributing

Have skills for another Jamf platform product? Contributions are welcome.

Each plugin lives in `plugins/<plugin-name>/` and follows the `.claude-plugin` structure. Use the existing plugins as reference implementations, then open a PR against the `develop` branch. See [CLAUDE.md](CLAUDE.md) for branch conventions.

Planned areas for future skills include Jamf Pro API workflows, Jamf Connect configuration, Jamf Protect policy authoring, and Jamf School automation — but any Jamf platform product is fair game.

## License

Copyright 2024, Jamf Software, LLC.  
Offered under the terms of the [Jamf Concepts Use Agreement](https://resources.jamf.com/documents/jamf-concept-projects-use-agreement.pdf).
