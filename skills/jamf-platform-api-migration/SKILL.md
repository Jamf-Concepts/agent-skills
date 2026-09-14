---
name: jamf-platform-api-migration
description: Converts a script that calls the Jamf Pro API, Jamf Pro Classic API, Jamf Protect API, or Jamf Security Cloud API directly, or a Go program on a pre-GA Jamf Platform Go SDK, into one that reaches the identical outcome over the Jamf Platform API Gateway with a single Jamf Account integration. Use when asked to migrate, convert, or move a Jamf API script, integration, curl command, or workflow to the platform API, the gateway, {region}.api.jamfcloud.com, or capability permissions, or when asked which capability grants a Jamf script needs.
compatibility: Tested with Claude Sonnet and Claude Opus; other models are untested. Reads the script from the conversation or the filesystem, and writes the converted script to a new file wherever a filesystem is reachable. Network access to developer.jamf.com improves grant and version precision; conversion works without it from bundled rules.
metadata:
  version: "1.0.0-rc.1"
  bundled-permissions-map: "2026-09-03"
allowed-tools: Read, Write, Grep, Glob, Bash(curl:*), Bash(dig:*), WebFetch
---

# Jamf Platform API migration

Input: a script in any language that calls the Jamf Pro API, the Classic API, the Jamf Protect API,
or the Jamf Security Cloud API directly against a product host. Output: the same script converted to
call the Platform API Gateway with one integration credential, **written to a new file wherever a
filesystem is reachable and carried in full inside a report** in the format under **Output
contract**. Both artifacts, every time: the file is what the admin runs, the report is what they
read. The contract is an identical outcome with the fewest edits. It is not a refactor, a cleanup, or
a rewrite.

Reference files, all one level from here. Read the ones the script needs before converting:

- [conversion-rules.md](conversion-rules.md): host, service slug, path and version, scope headers,
  the token exchange, the legacy and beta forms to recognize, and the surfaces with no gateway route.
- [capability-grants.md](capability-grants.md): the grant format, the live lookup, the bundled
  picker table, and the offline rules a capability-row reading gets wrong.
- [protect-graphql.md](protect-graphql.md): the single Protect endpoint, the error taxonomy inside
  HTTP 200, the operation-to-capability table, and the coverage gate.
- [runtime-behavior.md](runtime-behavior.md): what the emitted script has to do to work, including
  how it reads its secret.
- [examples.md](examples.md): worked before-and-after conversions.

## Before converting

Four facts decide the output. Take each from the request or the script. For any that neither
settles, do not stop to ask: take the default given below, convert under it, and put the question in
the report's scope section with what to change if the default is wrong. The report is the place to
ask; the reply always carries a converted script or a stop report, never a question on its own.

1. **Scope level of the integration.** Environment or tenant. It decides which one header every
   gateway call carries. Environment scope is the default: an environment-scoped integration reaches
   the platform APIs and every product in the environment with one credential, so where an endpoint
   accepts both scope types the output sends `X-Environment-Id` and the report tells the admin to mint
   the integration at environment scope, with the one-header, one-variable change for tenant scope
   noted. Tenant scope is emitted only where the request says the integration is tenant-scoped, which
   selects specific tenants of one product, or where an emitted endpoint publishes `tenant` alone in
   `x-scope-types` on its page. An endpoint that publishes one scope type only decides the level for
   the whole script, and the report names it and what changed in reach, such as a lookup that now
   spans every tenant in the environment; the platform-native `devices` endpoints and the
   compliance-benchmarks baselines publish `environment` only.
2. **Region.** `us`, `eu`, or `apac`. The integration's details in Jamf Account state it, and the
   request may not. Resolve it in this order, and say in the report which of the two the host came
   from, so a derived region is distinguishable from an assumed one:

   - **The script carries a literal Jamf Cloud hostname.** All three conditions, or skip to the
     next branch: the host is written in the script rather than left empty for a plist, a prompt,
     or an argument to fill; it ends in `.jamfcloud.com`, since a self-hosted Jamf Pro on a
     customer domain sits in no AWS region; and it resolves. Then read the AWS region out of the
     answer: `dig +short <tenant>.jamfcloud.com` returns a CNAME through an ELB name such as
     `usw2-...-us-west-2.elb.amazonaws.com`. Map `us-west-2` and `us-east-1` to `us`, any `eu-*`
     to `eu`, any `ap-*` to `apac`. State it as an assumption, not as fact: this reads the tenant's
     region, and that the gateway region matches it is the assumption. Tell the admin to correct
     the host if the integration's details disagree.

     Most scripts fail one of those conditions. An empty `jamfpro_url` and a placeholder such as
     `https://jss.organization.com:8443` are both ordinary, and a lookup that returns nothing means
     the host was a placeholder, not that anything is wrong. Fall through to the next branch
     without comment. A failed probe is not a divergence and is not worth a line in the report.
   - **Anything else, or no shell.** Assume `us`, state it, and say the admin corrects the host
     from the integration's details. A Protect or Security Cloud host answers nothing useful, because
     both sit behind CloudFront and CloudFront carries no region, so do not probe one and do not
     report a region as derived when it was not.
3. **Where the script runs.** An automation host, an admin's Mac, a container or function, or an
   endpoint that Jamf Pro deploys it to. This decides step 6 and the secret store in
   `runtime-behavior.md`. Read it from the code when the request does not say; the signals are in
   `conversion-rules.md`.
4. **What the script's purpose is.** The calls that carry the outcome versus the ones that are
   incidental. This shapes what the report says about a partial conversion; it does not decide
   whether to convert, which step 2 settles per call.

## Procedure

One rule, stated once. Steps 1 and 6 run once per script. Steps 2 and 3 run per call.

### 1. Replace authentication once per script

Any product token call, keep-alive, invalidate, session check, or Basic auth becomes one
`POST https://{region}.api.jamfcloud.com/auth/token`, form-encoded,
`grant_type=client_credentials`, with `Authorization: Bearer <token>` on every subsequent gateway
call. There is no per-product variant.

The credential line is inside this edit, so its form is decided here. Every item below is required
output, not background:

- **The client ID stays a literal.** It is an identifier, not a secret.
- **The secret is read at runtime from the host's secret store,** never emitted blank and never as a
  placeholder. `CLIENT_SECRET=""`, or the input's placeholder carried across, hands the admin a
  script whose only instruction is to paste a secret into a file.
- **Match the store to the host.** Keychain where the script is demonstrably on macOS; the
  platform's secrets manager read into an environment variable where it is not, since
  `/usr/bin/security` does not exist there. Where the host is not evident from the code, read from
  an environment variable and name both forms in one line rather than guessing one.
- **Whenever the output names a store, it carries that store's one-time import command,** in the
  report. A read command on its own leaves the admin a script that fails on first run against an
  item that does not exist yet. This applies to every store named, including one offered only as the
  alternative for a host you could not confirm.
- **Where the conversion means minting a new integration, name the `-U` trap** beside the Keychain
  import. `-U` matches on service *and* account, so importing with a new client ID adds a second
  item rather than replacing the first, and `find-generic-password -s` then returns whichever it
  finds first, which may be the stale one. The symptom is `invalid_client` while holding a correct
  credential. Say to delete the old item by service and account first.
- **Where the script already resolves its secret from a non-literal store,** that store carries over
  untouched and the runtime read is a recommendation, not an edit.

The exact commands are in `runtime-behavior.md`.

This is one step rather than a per-surface rule because authentication has no gateway equivalent
at all. The product token endpoints are not relocated; they have no path on the gateway, so a URL
rewrite of a token call produces a script that never obtains a token and fails on every later call,
far from the cause. The session model is replaced, not moved.

- Where a script's authentication is already this form, leave it alone: a gateway token exchange,
  its `.access_token` parse, and its `Bearer` header need no change. Applying "convert the auth"
  reflexively damages working code, and auth is the thing the skill changes most often, which is
  what makes this the easy one to get wrong.
- A token exchange against a host that is *staying*, because its calls have no gateway route, is
  not converted. See step 2 and `conversion-rules.md`.
- Token mint request and response shapes, and which product token responses change field names,
  are in `conversion-rules.md`.
- A Go program on the Jamf Platform Go SDK has no token call to replace. The SDK performs the
  exchange from the base URL and credentials it is constructed with, so this step is the base URL,
  the scope option, and the credential values. See `conversion-rules.md`, "Scripts built on the
  Jamf Platform Go SDK."

### 2. Resolve each call's route

Per call, first match wins:

1. A platform-native endpoint that reaches the same outcome.
2. The same product operation over the gateway, at its current published version.
3. The same outcome on a different product surface.
4. Stop: the surface has no gateway equivalent. Say so rather than emitting a broken call.

"Reaches the same outcome" includes "with an identifier the rest of the script can still use" and
"with the same semantics." A platform-native read that returns a platform device ID does not serve a
Classic write keyed on a Jamf Pro record ID, so the same-surface route wins there even though a
platform endpoint exists. Two candidates can require the identical grant, so the grant list gives no
signal about which is right. Decide on semantics and identifiers: an endpoint whose body is
`{added, removed}` is a delta and does not substitute for a `PUT` that replaces a whole collection,
and a path taking a UUID does not serve a script holding an integer ID.

Resolution runs per call, not per script. One script's calls can land on different branches, such as
a Classic read with no gateway route moving to the Pro surface while its Classic write stays on
`proclassic`. Deciding "this is a Classic script" once and applying it file-wide gets calls wrong.

Resolve against the operation list, never against documentation prose. A keyword match in an
endpoint's description is not an endpoint; a description can name a term only to exclude it.

Beta-era paths were not uniformly shaped. One call in a script can carry a `/tenant/{id}/` segment
while another does not, so a single substitution pass reaches the right answer for the wrong reason
and misses a segment sitting where the pattern did not expect it. Resolve each call.

**SDK-built programs.** A Go program that imports `github.com/Jamf-Concepts/jamfplatform-go-sdk`
makes no HTTP calls of its own, so there are no URLs to resolve. Its routes are the SDK's method
names and its version segments are their suffixes. The conversion is a library version, a base URL,
a scope option, and the credential values, per the section in `conversion-rules.md`. It is not
rewritten into raw HTTP, and a raw-HTTP program is not rewritten onto the SDK.

**Version resolution is part of routing.** The version the script carries is a candidate, not the
answer. Resolve to the highest published non-deprecated version of that path. A deprecated version
still answers today and stops without notice, so preserving it ships a script with a silent expiry
date, and a source version may have no gateway route at all. Two calls in one script can resolve to
different versions. The procedure is in `conversion-rules.md`.

**Script-level decline, and its boundary.** Decline the whole script only when **every** non-auth
call lacks a gateway route. Then a conversion would mint a token, make no working call, and still
look migrated, which is worse than an untouched script; auth being convertible is never itself a
reason to convert.

If even one non-auth call has a route, convert what converts. Do not decline a script because the
calls you judge central have no route while others do: convert the ones with routes, leave the
others on their product host exactly as written, and say in the report which calls moved, which
stayed, and that the script's purpose still depends on the ones that stayed. A caller reading that
can act on it. Weighing which calls matter more is not part of route resolution, which runs per
call.

### 3. Adjust response handling only where step 2 changed the response shape

Name every such change. Check the target version's schema before rewriting a parse; a version bump
is not a licence to re-derive it. Where a successor keeps the same envelope, the existing parsing
stays exactly as written.

Steps 2 and 4 pull against each other and the tie-break is fixed. Where a resolved route or version
changes the response shape, step 2 wins and step 3 names the edit. Everywhere else step 4 wins.

### 4. Change nothing else

Structure, names, control flow, logging, comments, formatting, and the script's existing defects all
stay as written. The working test is that an admin can diff the output against the original and see
only the calls change.

- **Defects are preserved, not repaired.** A status check testing the wrong exit code, an unchecked
  failure, a dead error branch, a hardcoded ID contradicting the variable meant to supply it: fixing
  any of them makes the converted script behave differently from the original on exactly the
  records an admin would be checking. Name the defect in the report, give the fix as a
  recommendation, and leave it in the code.
- **Do not reduce the number of calls.** A filter plus a section parameter can often return in one
  call what the script fetched in two. Reaching the same output that way is a rewrite. The call
  count, the failure modes, and the second call's dependency on the first belong to the script.
- **Check remaining call sites before removing anything.** An import or helper left looking dead
  by a converted call may still serve a call that did not move.
- **Leave payloads that are not API responses alone.** A webhook body, a script parameter, a report
  file: none has a route to resolve or a shape change.
- **A field selected in a GraphQL query but unused downstream is still part of the request.**
  Removing it to avoid a grant question, or as a tidy-up, changes what is asked for.
- **A variable the conversion adds takes the script's own naming style.** Beside `jssAPIUsername`
  and `jssAddress`, a new variable is `jss`-prefixed; beside `jamfpro_url`, it is `jamfpro_region`,
  not `jamf_region`. A variable whose every use is an API call is repointed in place under its own
  name, never replaced by a new one.
- **Commented-out code is code and stays.** The output contract's rule about correcting a comment
  block the conversion made wrong covers prose describing setup, privileges, or URLs. A commented-out
  line of code is left where it is.
- **Trailing whitespace may not survive the editing tools.** Where it does not, say so in the report
  rather than claiming the diff is confined to the calls.
- **A user-facing string the conversion made wrong or incomplete is corrected and named.** A
  beta-era token-failure message that says "check the client ID and secret" is no longer the first
  thing to check once GA has deleted every beta client: the first cause of `invalid_client` is now a
  client that does not exist, and the message sends the admin to re-check a secret that is fine.
  Add the deleted-client cause to the message, or say in the report why the string was left as it is.
- **When asked to combine scripts, merge without restructuring.** Keep the shared scaffolding once, put
  each script's calls inline as branches of the one loop, keep one counter set with a per-item roll-up,
  and introduce no function the originals lacked. A merge that turns each script into a function has
  refactored both.

### 5. Name every change

Every edit goes in the report, including anything declined and anything decided on the skill's own
judgment. Silent edits to a customer's script are not acceptable output. The report format is the
**Output contract** below.

### 6. Stop on execution context, never on the credential itself

A script that Jamf Pro deploys to endpoints *and* that holds credential variables does not convert.
Both halves are required: a policy script making no API calls is not caught, and an automation-host
script with an embedded credential converts normally. The output is the rule, the reason, and named
alternatives, never a converted script, not hedged, not partial, and not marked "for reference if
you move it."

The reason, which is what makes every workaround visibly a workaround: there is no device-side
platform API authentication. A Mac cannot authenticate to the platform API as itself at this time.
Until it exists, a credential
in an on-device script is therefore shared across every Mac in scope, and the platform secret that
would replace it reaches every tenant at the integration's scope level, in a payload readable in the
Jamf Pro admin console and written to disk fleet-wide. The blast radius goes up. The detection
signals, why every on-endpoint credential store is a relocation rather than a fix, and the
alternatives are in `conversion-rules.md`.

An embedded credential on its own never stops anything. A username and password are replaced by a
client ID and secret in the course of any conversion, so an empty, unfilled, or obviously fake
value raises nothing at all. A value that would still authenticate is reported and rotated, never
refused, and never reproduced in the output. The same script with an empty credential still does
not convert when Jamf Pro deploys it; a stop that rests on the secret being populated will convert
the next policy script whose variable is blank.

The deployment signals in `conversion-rules.md` come in two strengths. A conclusive set stops the
conversion. A single suggestive signal, with nothing in the request saying where the script runs,
does not: convert under the stated assumption that the script runs from an admin's Mac or an
automation host, name the assumption, and say that the stop applies if Jamf Pro in fact deploys it.
A refusal on a guess leaves the admin with nothing; a conversion with a named assumption leaves them
a script and the fact they need to decide.

## Cases the rules do not cover

The rules in these files are a sample of what scripts contain, not a census. A real script will
present a surface, an auth shape, a parsing chain, or a response format no rule names, and that is
the normal case. Resolve it from the published surface on developer.jamf.com, using the lookup in
`capability-grants.md` and `conversion-rules.md`, rather than pattern-matching the nearest
plausible rule. Then report the divergence: what the script presented, what the conversion
concluded, and what it concluded it from. A confident guess in the same voice as a documented rule
is the failure this exists to prevent, because an admin cannot tell the two apart in the output.

Where the network is unavailable, say which conclusions rest on bundled rules alone and which
would have been verified live.

## Output contract

The report opens with one line naming the skill version and the bundled permissions-map date from
this file's frontmatter, and whether developer.jamf.com was reached, in the form
`jamf-platform-api-migration 1.0.0-rc.1 · permissions map 2026-09-03 · live lookups: yes`. An admin who
posts the output somewhere can then be told which rules produced it.

**The version line is required and is never omitted.** Exactly one short sentence precedes it and
nothing else does: the first line of the reply, naming the file the converted script was written to,
in the form `Written to assign-user-platform.sh.` Where no file could be written it says that
instead. Where the output is a stop report, which writes no file, it says in one sentence that the
script does not convert, or that two inputs produced two stop reports. That sentence is the whole of
the reply's introduction — no heading above it, no summary under it, nothing announcing what is
coming — and every numbered section comes after the version line, so a reply whose first content is a
heading or the converted script has skipped it and is wrong.

**The converted script is written to a file, and the same script is in the report.** Both, every
time, wherever a filesystem is reachable. A code block with no file leaves an admin who pointed the
skill at a script on their disk to copy the answer back out of a transcript by hand. A file with a
pointer to it in place of section 1 loses the script the moment the report is pasted into a ticket,
and section 1 forbids it. Neither one on its own is the deliverable.

- **The converted script is the only file the skill ever writes.** Not the report, not notes, not a
  summary, not a copy of the input. The report is the reply itself: writing it to a file hands the
  admin a document where they asked for an answer, and on a stop it manufactures the very file the
  stop rule says not to write. One file, and it is a runnable script.
- **Where.** The directory the input was read from. A script that arrived as text in the
  conversation, with no path, goes in the working directory.
- **Name.** The input's name with `-platform` before the extension: `assign-user.sh` gives
  `assign-user-platform.sh`, `report.py` gives `report-platform.py`, an input with no extension
  gives `name-platform`. Text with no filename at all gives `jamf-platform-migration` and the
  language's extension. The name is not a judgment call — a second run, or a diff against the first,
  has to be able to predict it from the request alone.
- **Where several inputs merge into one script, the name comes from the first input the request
  listed,** whole and unaltered: `pro-delete.sh` and `protect-delete.sh` merged give
  `pro-delete-platform.sh`. Do not trim them down to a prefix they share, blend their names, or
  invent a descriptive one; section 4 is where the merge gets explained, not the filename.
- **Never over the input, never over anything else.** The input is read and left as it is, in place:
  no edit, no rename, no backup copy, no writing the conversion back over it. If the target name is
  already taken, add `-2`, `-3` and let the lead-in name what was used. The original is the only
  thing the admin has to check the conversion against.
- **The same text in both, and the file is written first.** Write the file, then produce section 1 by
  reading back what was written rather than rendering the script a second time: two renderings of one
  conversion drift, silently, and the drift lands in the copy the admin reads. The two are
  byte-identical. Where the writing tool changes something on the way out, trailing whitespace being
  the known case, the report says so, as it already has to.
- **A stop report writes no file at all.** Nothing converted, so there is nothing to write, and a
  file on disk contradicts a report that declined to produce one. Writing the stop report itself to a
  file is not a substitute for the script that was never emitted; the reply carries the report and
  the directory stays as it was found.
- **Where no file can be written** — a surface with no filesystem, or a write that is refused — the
  lead-in says so plainly and section 1 is the only copy the admin gets. Do not leave them to work
  out that nothing reached disk.

The report follows the version line, in this order. Omit a section only when it is empty, and say so
in one line rather than dropping it.

1. **Converted script.** Complete, in one code block, ready to run once the out-of-script steps in
   section 8 are done. Never a fragment, never a diff, and never replaced by a pointer to the file
   that was written: the report has to carry the script on a surface that has no filesystem, and the
   block is what survives being pasted somewhere else. Present whether or not a file was written,
   and where one was, a copy of it rather than a second rendering of the same conversion.
2. **Scope level, region, and headers.** Which scope level the output assumes, and the one header
   every gateway call carries. Then one line on the region in the host, saying which way it was
   settled: derived by resolving the script's Jamf Pro or Classic hostname, naming the AWS region
   the lookup returned and that the gateway is assumed to match it, or assumed `us` because the
   script carried no host that answers. Either way the admin is told to correct the host if the
   integration's details in Jamf Account disagree. An assumed region is never reported as a derived
   one.
3. **Capability grants.** One row per grant, resolved against the endpoints the output actually
   emits, never the ones it replaced. Each row carries the grant string, the section and permission
   name Jamf Account's picker shows for it, and the calls that need it. One capability covering
   calls on two products is one row. Nothing here is emitted as comments in the script.
4. **Changes.** Every edit, grouped as authentication, routes and versions, response handling,
   removals, and other. Each with its reason. Specifically:
   - A change the script's behavior did not force needs its reason, or the admin reverts it. Moving
     off a deprecated version is the case in point: the script works today, so "moved to the current
     version" is not enough. Give the deprecation flag and its date.
   - A variable whose name survives but whose value is now a different credential. Both a Protect
     API client and a platform integration call their identifier a client ID, so the rename that
     would have documented the change never happens and the diff reads as though the value carried
     over. Say the value is replaced.
   - Parsing machinery the conversion made dead. An XML tidy-and-sed chain has no equivalent once
     the body is JSON; its removal is a named change.
   - A removed call whose endpoint has no route, together with what fed it and what called it. A
     function reduced to a dead probe goes, and its call sites go with it. A silently deleted
     teardown step reads as an oversight.
   - A privileges or setup comment block the author wrote that the conversion made wrong.
     Correct or remove it. The rule against volunteering grant strings as comments stops the skill
     adding them; it says nothing about leaving a now-false block in the file an admin reads first.
     The same applies to a user-facing string the script prints that the conversion made wrong, such
     as a token-failure message telling the admin to check a credential the script no longer uses.
     Commented-out code is not a comment block and stays as written.
   - Where a required change unavoidably removes a defect, name it as a behavior change, never as
     parity. Moving a read cross-surface makes the response JSON, which retires an XML helper that
     was broken, so the converted script populates fields the original never did. That is the
     honest report. Repairing a defect the conversion did not have to touch is not.
   - An error check that gained coverage without changing a line. A check that was blind to
     Protect's errors inside HTTP 200 still is, but over the gateway it now catches
     `403 BAD_PERMISSIONS`, `404 ENVIRONMENT_NOT_FOUND`, `400 REQUEST_CONTEXT_NOT_PROVIDED`, and
     `401`, which are real failures the product call never produced. Report both halves.
   - Credential exposure the conversion introduces or worsens. A `bash -x` that echoed a Basic
     auth pair now echoes a client secret and a bearer token.
   - The credential count as it actually ends up. Where one product's calls have no gateway route
     they stay on that product's host, a gateway bearer token does not authenticate them, and the
     converted script still holds two credential sets and mints two tokens. "Two tokens became one"
     is the expected story and is wrong there.
5. **Declined.** Every call left unconverted and why, distinguishing the calls that *could* have
   moved from the ones that could not. A refusal that does not make that distinction is
   indistinguishable from having failed to look, and an admin cannot act on it. "No gateway
   equivalent" does not mean broken: the product APIs still answer, so a script that cannot move has
   not stopped working. Say both, or a routing fact reads as an outage. The reason a call or a
   script cannot convert is the missing route, never the script's unrelated defects; a refusal
   resting on typos and race conditions reached the right answer for the wrong reason.
6. **Divergences.** Every point where the conversion went outside what the rules describe, with
   what it hit, what it concluded, and the evidence. Empty is a valid answer and is stated.
7. **Recommendations.** Repairs the conversion did not force, each with the code to apply it, none
   applied. Defects named in section 4 land here with their fix. A secret-resolution ladder the
   script already has stays as written, with the runtime read given here as a recommendation. A
   recommended Protect `.errors` check carries the reading rules from `protect-graphql.md`: only
   `AuthorizationError` is a denial, its two messages mean opposite things, and `NotFound`,
   `ArgumentValidationError`, and `Lambda:Unhandled` mean the resolver ran.
8. **Out-of-script changes.** What has to happen outside the file before the script runs:
   - Mint the integration in Jamf Account with the grants in section 3. Where the script was
     written against the public beta, say plainly that GA deleted every beta integration client, so
     a fully correct conversion still returns `401 {"error":"invalid_client"}` on its first call
     until a new integration exists. `invalid_client` is also what a wrong secret returns, so the
     response cannot distinguish a deleted client from a mistyped one; the Jamf Account
     integrations list is what settles it, and an admin who assumes a typo re-checks the secret
     instead of minting a client.
   - The one-time secret import, in the form `runtime-behavior.md` gives for the host the script
     runs on.
   - A credential the script reads from its caller, such as webhook headers, an event payload, or
     the environment, changes name when it changes type, and the caller has to be reconfigured to
     match. Name that change. A script correct in isolation that depends on an unmade change
     elsewhere fails on the first real event.
   - The execute bit on the file that was written, where the original carried one. It is created
     without it, so `chmod +x` is the difference between a runnable script and a permission error on
     the first attempt. Nothing to say where no file was written or the original was not executable.
   - Rotation of any live credential the input contained.

**Secrets in the report.** Never reproduce a secret in order to report it. The variable name and
line identify it completely for anyone holding the script, while echoing the value copies it into a
transcript. No quoted value, no quoted line of input containing it, and no decoding an encoded one
for reference. A hardcoded `Authorization: Basic` value is a plain-text credential and is reported
as one, plainly, because the reason the line exists is that its author believed otherwise.

### Stop report

When step 6 or a script-level decline in step 2 stops the conversion, the output is a report with no
converted script and no file written. It opens with the same version line and carries:

1. The rule that stopped it and the reason behind the rule.
2. What the conclusion rests on: the signals in the code, each named.
3. What would have converted, in prose: each call's route and the capability its operation needs,
   and that the skill will convert it once the script runs somewhere else. Naming a capability an
   operation needs is a different statement from a grant list for an emitted script, and only the
   second is wrong when nothing is emitted. Without this, a stop is indistinguishable from a
   failure to look and reads as "unsupported."
4. Which calls could have moved and were declined on purpose, as distinct from the calls that have
   no route. A refusal that does not draw that line reads as a failure to look.
5. What does not survive the move: an on-device self-lookup, such as `ioreg` for the Mac's own
   serial, has no equivalent on an automation host, so the operation becomes an iteration over
   devices, which is a rewrite rather than a conversion. And what a retained product path does over
   the gateway: `403 BAD_PERMISSIONS`, not 404, which reads as a permissions problem. That is why,
   where no non-auth call has a route, converting the auth alone is worse than leaving the script
   untouched. It says nothing about a script that does have a convertible call: step 2 governs that
   one, and there a partial conversion is the required answer.
6. The alternatives, named specifically. A stop with no alternative is a wall. For a Jamf
   Pro-deployed script: an automation host that Jamf Pro fires a webhook at, holding the script and
   one credential under one owner and running the operation server-side; Jamf Routines, which does
   this without standing up a server; JAWA, at `github.com/jamf/JAWA`. Where the values wanted are
   Jamf Pro's own, a configuration profile or an extension attribute reaches the same outcome with
   no API call and no credential at all.
7. Everything else observed, and that none of it is the reason: a live credential, a token echoed
   to a world-readable log, the script's ordinary bugs. A stop has to rest on the right reason or it
   generalizes wrongly.
