```text
     ██  █████  ███    ███ ███████
     ██ ██   ██ ████  ████ ██
     ██ ███████ ██ ████ ██ █████
██   ██ ██   ██ ██  ██  ██ ██
 █████  ██   ██ ██      ██ ██

P L A T F O R M   A P I   M I G R A T I O N

four APIs     ──┐
four tokens   ──┼──▶  one platform gateway
four hosts    ──┘
```

![version](https://img.shields.io/badge/version-1.0.0--rc.1-1E88E5)
![models](https://img.shields.io/badge/tested%20on-Claude%20Opus%20%7C%20Sonnet-8A2BE2)
![permissions map](https://img.shields.io/badge/mappings%20updated-2026--09--03-00897B)
![runs nothing](https://img.shields.io/badge/runs%20your%20script-never-C62828)

An Agent Skill that converts any script calling the Jamf Pro API, the Jamf Pro Classic API, the
Jamf Protect API, or the Jamf Security Cloud API directly, or a Go program on a pre-GA release of
the Jamf Platform Go SDK, into one that reaches the identical outcome over the Jamf Platform API
Gateway, with Jamf Account integration capability guidance in place of per-product credentials.

It reports every change it made, the capability grants the integration needs and where each sits in
Jamf Account's permission picker, anything it declined to convert, and anything it had to decide
without a documented rule.

> This file is for people. `SKILL.md` and the files beside it are what an AI harness reads.

## Install

**Claude Code.** Drop the directory into your skills directory:

```bash
mkdir -p ~/.claude/skills
curl -sL https://github.com/Jamf-Concepts/agent-skills/archive/refs/heads/main.tar.gz \
  | tar -xz -C ~/.claude/skills --strip-components=2 \
      agent-skills-main/skills/jamf-platform-api-migration
```

That pulls this one directory out of the repository and leaves everything else behind. To take it with
its git history instead:

```bash
git clone --filter=blob:none --sparse https://github.com/Jamf-Concepts/agent-skills.git
cd agent-skills && git sparse-checkout set skills/jamf-platform-api-migration
```

Then, in any session:

```text
/jamf-platform-api-migration
```

Paste the script or point at its path. That is the whole ask.

Two things come back: the converted script **written to a new file beside your original**, named for
it with `-platform` added — `assign-user.sh` gives `assign-user-platform.sh`, `report.py` gives
`report-platform.py` — and a report carrying that same script in full along with every change it
made. Your original is read and left alone. On a surface with no filesystem, claude.ai among them,
the report is the whole answer and its first line says so.

The skill does not interview you before it works. Four things decide the output, and it settles each
one itself and tells you what it assumed:

| What | How it decides |
| --- | --- |
| **Scope level** | Environment by default, because one environment-scoped integration reaches every product in the environment. Tenant scope if you say so, or if an endpoint publishes tenant alone. |
| **Region** | Derived by resolving your Jamf Pro or Classic hostname when the script carries one. Otherwise assumed `us`. The report always says which. |
| **Where it runs** | Read from the code: an automation host, your Mac, a container or function, or an endpoint Jamf Pro deploys to. |
| **What it is for** | Which calls carry the outcome and which are incidental. |

Every one of those lands in the report with what to change if the assumption is wrong. You get a
converted script or a clear stop, never a question in place of an answer.

**claude.ai.** Zip this directory and upload it under Settings, Capabilities, Skills. The same files
work unchanged.

**Claude Developer Platform.** Upload the directory through the Skills API and attach the skill to
your request. `SKILL.md` carries only the portable frontmatter fields, so nothing here is specific
to one surface.

## What it needs

- **A model it was tested on.** Claude Sonnet or Claude Opus. Other frontier or local models may
  produce successful conversions, but the outcome is untested.
- **The script.** Any language. It reads shell, Python, and anything else that makes HTTP calls.
- **Permission to write one file.** The skill writes the converted script beside your original, and
  asks first the way any file write in Claude Code does. Decline it and the report still carries the
  script in full.
- **Network access to `developer.jamf.com`,** recommended but not required. With it, the skill pulls
  each endpoint's published page and reads the permission string, the scope types, and the current
  version off it. Without it, the conversion still completes from the bundled rules and the report
  says which conclusions were not verified live.

It does not need, and never asks for, a client secret. It does not run the input script or the
output script, and it makes no calls to the gateway.

## What it never does

- **Reproduce a secret.** A credential found in the input is identified by variable name and line,
  never quoted, never decoded.
- **Touch your original.** The conversion goes in a new file. The input is read and never edited,
  renamed, or written over, and neither is anything else already on disk: where the name it wants is
  taken, it adds a suffix and tells you which one it used.
- **Convert a script that Jamf Pro deploys to endpoints and that holds credential variables.** There
  is no device-side platform API authentication, so a platform secret on an endpoint is shared
  fleet-wide. The output for that case is the rule, the reason, and the alternatives.
- **Refactor.** The converted script differs from the original only in the calls that had to change:
  authentication, host, service slug, path and version, scope headers, and response handling where a
  resolved version changed the response shape. Defects in the original stay in the output and are
  reported with a recommended fix.

## Layout

| File | What Claude reads it for |
| --- | --- |
| `SKILL.md` | The procedure and the output contract |
| `conversion-rules.md` | Host, slug, path, headers, auth, legacy forms, no-route surfaces |
| `capability-grants.md` | Grant format, live lookup, bundled picker table, name bridges |
| `protect-graphql.md` | The single Protect endpoint, error taxonomy, operations, coverage gate |
| `runtime-behavior.md` | What the emitted script must do to work, including the secret read |
| `examples.md` | Worked before-and-after conversions |
| `README.md` | This file. Claude does not need it. |

<details>
<summary><b>Versioning</b>: what the number means and what moves it</summary>

<br>

Current version: **1.0.0-rc.1**, bundled permissions map dated **2026-09-03**. Both live in the
frontmatter of `SKILL.md`, and every report the skill writes opens with them.

To see what you have, read `metadata.version` in the frontmatter of `SKILL.md`. That answer is the same
however you got the directory — pulled from the repository, cloned, or uploaded as a zip to claude.ai or
the Skills API. Releases are tagged `jamf-platform-api-migration-v<version>`; the skill name is in the
tag because the repository holds more than this one skill.

What moves the number:

- **Patch** (1.0.x): the bundled permissions map refreshed, wording fixed, no conversion rule changed.
- **Minor** (1.x.0): a conversion rule added or changed, so a script converted under the previous
  version can come out differently.
- **Major** (x.0.0): the report's structure changed, so anything reading the output has to change too.

The permissions-map date is separate from the version because it goes stale on Jamf's schedule, not
this repository's. When the two disagree with developer.jamf.com, the live page wins and the report
says which conclusions came from the bundled copy.

</details>

<details>
<summary><b>Changelog</b></summary>

<br>

- **1.0.0-rc.1**, unreleased. Release candidate for the first public version.

</details>

<details>
<summary><b>Audit notes</b>: what is bundled, what is fetched, and how to check it</summary>

<br>

**Bundled data.** `capability-grants.md` carries a copy of the capability list, picker sections, and
old-to-new name bridges from
`https://developer.jamf.com/platform-api/reference/jamf-pro-permissions-map`, taken from the version
dated 2026-09-03. It is bundled rather than fetched because a burst of requests to the documentation
site is answered with a challenge page at HTTP 200, so a live read can fail while looking like it
succeeded. To check the bundled copy against the current page:

```bash
curl -sSL https://developer.jamf.com/platform-api/reference/jamf-pro-permissions-map.md | head -3
```

The first line is `---` and the second is `updatedAt:`. A later date than the one in
`capability-grants.md` means the bundled tables may be behind; the per-endpoint grant lookup is live
regardless, so a stale bundle affects picker wording and name bridges, not the grant strings
themselves.

**Known-version table.** `conversion-rules.md` carries a short table of endpoint versions for use
without a network, verified 2026-09-09. With a network the skill resolves versions live and the
table is not consulted.

**Region resolution.** Where the script carries a Jamf Pro or Classic hostname, the skill resolves
it with `dig` and reads the AWS region out of the ELB name behind it. That gives the tenant's
region; that the gateway region matches it is an assumption, and the report says so. A Protect or
Security Cloud host answers nothing useful, because both sit behind CloudFront, which carries no
region, so those scripts get `us` as a stated assumption instead.

**What the skill fetches.** Only `developer.jamf.com` pages: a category index and individual
endpoint pages, paced. Plus the DNS lookup above. Nothing is sent anywhere.

**Divergences.** Every report ends with the points where the script presented something no rule
covers and what the skill concluded from the published surface. A divergence that recurs across
scripts is a rule this skill is missing.
[Open an issue](https://github.com/Jamf-Concepts/agent-skills/issues) with the divergence text; do not
include the script if it holds a credential.

</details>
