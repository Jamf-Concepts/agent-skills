# Security Policy

This repository packages Jamf-specific knowledge — API conventions, file formats, and platform patterns — into Claude agent skills that developers install to guide AI-assisted work with Jamf products. Vulnerabilities here could cause Claude to produce incorrect or harmful API calls, misrepresent security-sensitive data structures, or give misleading guidance about credential handling in automation scripts.

For Jamf Concepts' broader security posture, see **[concepts.jamf.com/en/security](https://concepts.jamf.com/en/security/)**.

## Supported versions

Security fixes are applied to the latest released version. Please make sure you can reproduce an issue on the most recent release before reporting it.

## Reporting a vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Instead, report privately using one of:

- Jamf's [Vulnerability Disclosure Program](https://www.jamf.com/trust-center/vulnerability-disclosure/), or
- The **Report a vulnerability** button under this repository's **Security** tab.

Please include:

- A description of the issue and its potential impact.
- Steps to reproduce, or a proof of concept.
- The skill or plugin version and the SHA or release you observed it on.

You can expect an initial acknowledgement within a few business days. Once a fix is available, the report will be disclosed publicly with credit to the reporter, unless you ask to remain anonymous.

## Scope

In-scope examples: incorrect or misleading guidance embedded in skill content that could lead to insecure coding patterns (e.g., advice to store credentials insecurely, skip permission scoping, or use unencrypted transport); flaws in plugin hook scripts that execute code on the developer's machine; issues in the plugin packaging or install mechanism that could allow untrusted skill content injection.

Out of scope: vulnerabilities in Claude Code itself, the Jamf Platform API, Jamf Pro, or any external service referenced by a skill. Please report those to the relevant vendor.
