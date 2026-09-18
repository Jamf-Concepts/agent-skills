# Conversion rules

Host, service slug, path and version, scope headers, the token exchange, the legacy and beta forms to
recognize, the surfaces with no gateway route, and how to tell where a script runs. The procedure
these rules serve is in `SKILL.md`.

## The gateway request

```text
https://{region}.api.jamfcloud.com/{slug}/{version}/{resource}
```

- `{region}` is `us`, `eu`, or `apac`. The integration's details in Jamf Account state it. The tenant
  hostname does not, but DNS does: `dig +short <tenant>.jamfcloud.com` answers with a CNAME through an
  ELB name carrying the tenant's AWS region, such as `usw2-...-us-west-2.elb.amazonaws.com`. Map
  `us-west-2` and `us-east-1` to `us`, any `eu-*` to `eu`, any `ap-*` to `apac`. That reads the Jamf
  Pro tenant's region and assumes the gateway matches it, so the report states it as an assumption and
  tells the admin to correct the host if the integration's details disagree.

  **The probe needs a literal, resolvable `.jamfcloud.com` host, and most scripts do not have one.**
  A host left empty for a plist, a prompt, or an argument to fill gives nothing to resolve. A
  self-hosted Jamf Pro on a customer domain, `https://jss.organization.com:8443` and the like, sits
  in no AWS region. A placeholder resolves to nothing. And a Protect host and the gateway host both
  resolve to CloudFront, which carries no region, so a script calling only Protect or Security Cloud
  has nothing to read either. In every one of those the region is assumed `us` and the report says
  so. A lookup that returns nothing means the host was a placeholder; it is not a divergence and not
  worth reporting. Never present an assumed region as a derived one.
- There is no `/api/` prefix. `GET /api/pro/v1/…` is a plain-text 404. The prefix belonged to the
  superseded beta host `us.apigw.jamf.com`, which is why it appears in beta-era examples.
- The slug is the first path segment and is the gateway's routing key. There is no single
  "platform" namespace.

| Slug | Surface |
| --- | --- |
| `pro` | Jamf Pro API |
| `proclassic` | Jamf Pro Classic API |
| `protect` | Jamf Protect, GraphQL, single endpoint |
| `securitycloud` | Jamf Security Cloud: devices, categories, DNS, enrollment, UEM Connect, ZTNA |
| `devices` | Device inventory, platform-native |
| `device-groups` | Device groups, platform-native |
| `device-actions` | Device management actions, platform-native |
| `blueprints` | Blueprints and blueprint components, platform-native |
| `compliance-benchmarks` | Compliance benchmarks and baselines, platform-native |
| `ddm/report` | Declaration reporting, platform-native. The only two-segment slug. |
| `audit` | Audit events, platform-native |
| `licensing`, `partners`, `sso` | Jamf Account, organization-management scope only |

**A wrong path returns `403 BAD_PERMISSIONS`, not 404.** An unregistered route under a registered
slug and a missing capability grant produce the same response, so slugs and resources cannot be
discovered by probing. Take the host and slug from the endpoint page's `servers[0].url` and the
resource from the category index. An unrecognized *first* segment is a plain-text 404 with no JSON
envelope, which is a different failure from the 403.

**A registered slug does not mean an arbitrary resource is published beneath it.** `securitycloud`
serves six reference categories, and an operation outside them, such as a risk query, has no route.
A path invented under a valid slug answers `403 BAD_PERMISSIONS`. Resolve the resource, not just the
slug; a slug that exists is not evidence the operation does.

## Scope headers

Exactly one of `X-Environment-Id` or `X-Tenant-Id` goes on every gateway call, and which one follows
the integration's scope level. Environment scope is the default: it reaches the platform APIs and
every product in the environment with one credential, and it is what the output assumes unless the
request says the integration is tenant-scoped or an endpoint publishes `tenant` alone.

| Integration scope | Header | Reaches |
| --- | --- | --- |
| Platform environment | `X-Environment-Id: <environment UUID>` | Platform APIs, plus the product APIs of every tenant in the environment |
| Tenant | `X-Tenant-Id: <tenant UUID>` | The product APIs of the selected tenants only |

- The header is absent from `POST /auth/token`. The token mint carries neither.
- Only gateway requests carry a scope header. A call left on a product host or a third-party host
  gets no `X-Tenant-Id` and no `X-Environment-Id`.
- An endpoint page lists a scope header parameter as `"required": true` for each scope type it is
  published at; that flag decides nothing. `x-scope-types` at the root of the page's OpenAPI block
  does. Where it lists both `tenant` and `environment`, the integration's scope level decides which
  header is sent. Where it lists one, the integration has to be minted at that level or the call
  returns `403 BAD_PERMISSIONS`; the platform-native `devices` endpoints and the
  `compliance-benchmarks` baselines publish `environment` only. See `SKILL.md`, Before converting.
- Omitting the header returns `400 REQUEST_CONTEXT_NOT_PROVIDED`.
- Under environment scope a tenant ID from the script has no header to go in, and one call then
  covers every tenant in the environment. See the beta section below.

## Authentication

One exchange, for every product:

```http
POST https://{region}.api.jamfcloud.com/auth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id={client-id}&client_secret={client-secret}
```

Response: `access_token`, `expires_in: 900`, `refresh_expires_in: 0`, `token_type: Bearer`. Every
subsequent gateway call sends `Authorization: Bearer <access_token>`.

- **`Bearer` is required.** A bare token returns `401`, which reads as a bad credential rather than
  a malformed header. Protect's direct API accepts a bare token, so a header that looks finished on
  a Protect script still has to change.
- **Tokens last 900 seconds and cannot be extended.** There is no keep-alive. A loop that can outlive
  a token re-mints; the mechanics are in `runtime-behavior.md`. A single mint is correct when nothing
  loops: re-minting is required by unbounded iteration, not by the lifetime on its own, so two
  sequential calls keep their one mint and adding re-mint machinery is unrequested change.
- **Tokens are region-locked.** Mint from the host the calls go to.
- **Tokens carry no scope string.** Capabilities resolve server-side per request, so nothing can
  pre-flight a permission check. The script attempts the call and reads the error.

### Legacy forms this exchange replaces

Every form below becomes the one exchange above. None has a gateway path.

| Form in the script | What it was |
| --- | --- |
| `POST /api/v1/auth/token` with `-u user:password` or `Authorization: Basic` | Jamf Pro bearer token from Basic auth |
| `POST /api/v1/auth/keep-alive`, `/api/auth/keepAlive` | Extend that token |
| `POST /api/v1/auth/invalidate-token`, `/api/auth/invalidateToken` | Revoke it |
| `GET /api/auth/current`, `/api/v1/auth`, `/api/v1/oauth2/session-tokens` | Session introspection |
| `POST /api/v1/oauth/token` with `grant_type=client_credentials` | Jamf Pro API client token |
| `Authorization: Basic` directly on a `/JSSResource/…` call | Classic API Basic auth on a resource endpoint |
| `POST https://{tenant}.protect.jamfcloud.com/token` with JSON `{"client_id": …, "password": …}` | Jamf Protect API client token |

- **A script with no token call gains one.** Basic auth on a resource endpoint is a single item with
  no gateway path, so the conversion adds the exchange and replaces the header. Basic auth against
  a product token endpoint is two items, the exchange and the endpoint, and both go.
- **Read the source surface's response field names before changing them.** A Jamf Pro token
  response carries `.token` and an ISO 8601 `expires`; the gateway returns `.access_token` and an
  integer `expires_in`, so converting a Jamf Pro token call changes the response handling on the
  auth call itself. A Protect token response already carries `access_token` and an integer
  `expires_in`, so applying the rename there breaks a parse that was correct.
- **A token exchange that stays is not converted.** Where a product's calls have no gateway route,
  its login keeps its Basic auth, its path, and its `.token` parse. Applying
  `grant_type=client_credentials` or `.access_token` to it breaks the half of the script that never
  moved.
- **Base64 is an encoding.** A hardcoded `Authorization: Basic` value is a plain-text credential
  and is treated as live: reported, never reproduced. The report says so plainly, because
  the reason the line exists is that its author believed otherwise.

## Route resolution

### Jamf Pro API to `pro`

```text
https://{tenant}.jamfcloud.com/api/{version}/{resource}
→  https://{region}.api.jamfcloud.com/pro/{version}/{resource}
```

The resource path, query syntax, request bodies, and response schemas carry over. RSQL filters
carry over unchanged. The version segment is resolved, not preserved.

**Pulling a page.** developer.jamf.com serves every page as raw markdown: append `.md` to a page
URL, and `llms.txt` is the index for a section or a category. Pull with `curl -sSL` on that URL.
The file arrives unchanged, which is the point: a fetch tool that summarizes a page before the
model sees it invents paths and operations that are not in the file. Drop any version segment from
a page URL; a versioned URL returns the rendered HTML shell. Where no shell is available and a
summarizing fetch tool is the only option, ask it for the page text unchanged, and treat any path,
version, or operation it reports as unconfirmed until the endpoint page's OpenAPI block, pulled the
same way, agrees. Never emit a route the index alone suggested.

An endpoint page carries a `# OpenAPI definition` heading followed by a fenced JSON block for that
one operation. This reads the fields that matter off it:

```bash
# usage: jamf-doc.sh delete_v4-computers-inventory-id-1
curl -sSL "https://developer.jamf.com/platform-api/reference/${1}.md" \
| awk '/^```json$/{f=1;next} /^```$/{if(f)exit} f' \
| jq -r '
    (.paths | to_entries[0])   as $p
  | ($p.value | to_entries[0]) as $op
  | [ ($op.key | ascii_upcase),
      (.servers[0].url + $p.key),
      "scope: \(.["x-scope-types"] | join("|"))",
      "grants: \($op.value["x-required-privileges"] // ["none"] | join(", "))",
      "legacy: \($op.value["x-required-privileges-legacy"] // ["n/a"] | join(", "))",
      "deprecated: \($op.value.deprecated // false) \($op.value["x-deprecation-date"] // "")"
    ] | join("\n")'
```

`servers[0].url` is the host template plus slug, `paths` has exactly one key, the exact versioned
path, `x-scope-types` is which scope levels the operation is published at, and more than one entry
in `x-required-privileges` means all are required. Every page opens with `---` frontmatter and one
line of crawler boilerplate before the H1.

**Version resolution.** The gateway routes whatever version it is given, and superseded versions
still answer transitionally, then stop without notice with a bare `403 BAD_PERMISSIONS` that names
nothing. A 200 today is not evidence a version is current. So:

1. Pull the category index,
   `https://developer.jamf.com/platform-api/reference/jamf-pro/llms.txt`. Each entry's slug carries
   the method, version, and path, so the entries for a resource give every version of that path the
   surface publishes. Take the slug from the index link; do not construct it. Numeric suffixes such
   as `-1` are collision artifacts with no meaning, and the same endpoint can appear with and
   without one. Absence from the index means withdrawn. Presence means nothing more than
   published, because the index carries no deprecation flag: a deprecated version sits beside its
   successor with an identical permission string.
2. Pull each candidate's own page, `https://developer.jamf.com/platform-api/reference/{slug}.md`,
   and read `deprecated` and `x-deprecation-date` off the OpenAPI block under
   `# OpenAPI definition`. The same block carries `servers[0].url`, the exact path,
   `x-required-privileges`, `x-required-privileges-legacy`, and `x-scope-types`.
3. Emit the highest published version that is not deprecated. Two calls in one script can resolve
   to different answers, and the source version may publish no gateway route at all, so "keep the
   version the script is on" is not the rule.
4. Before rewriting any parse, read the target version's response schema. A version bump that keeps
   the envelope changes nothing downstream. Read the success status and response body off the
   schema too, not off the summary line; the prose can describe a body the operation does not
   return.

Pace the fetches. A burst is answered with a Cloudflare challenge page at HTTP 200. An endpoint
page is real when its body opens with `---` frontmatter; a category index has no frontmatter and is
real when it carries `**Required Permissions:**` entries. A body with neither is the challenge page,
not the document.

**A version can be wrong because it has no route, not because it is deprecated.** Where the same
version exists for a neighboring object type, the near-miss is the other object type rather than the
other version. Resolve the exact path.

Known resolutions, for use when the network is unavailable. Verified against the published surface
2026-09-09; re-verify when there is a network.

| Resource | Published | Current | Note |
| --- | --- | --- | --- |
| `/computers-inventory` | `v3`, `v4` | `v4` | `v3` deprecated 2026-07-14. No `v1` or `v2` route. `section=` and `filter=` carry over. |
| `/computers-inventory-detail/{id}` | `v3`, `v4` | `v4` | Hyphenated throughout; there is no `/computers-inventory/detail/` path. No `v1`. |
| `/computer-groups/smart-groups`, `/computer-groups/static-groups` | `v3` | `v3` | No `v2` route for computer groups. |
| `/mobile-device-groups/smart-groups` | `v2` | `v2` | The `v2` that computer groups lack. |
| `/mobile-devices/{id}`, `/mobile-devices/{id}/detail` | `v2` | `v2` | |

Without a network, state in the report that version currency was not verified and which calls rest
on this table versus on the script's own version.

**A script's server URL variable can feed uses that are not API calls.** Console links, report
columns, log lines, output messages. Repointing the variable wholesale at the gateway breaks every
one of them silently, because the gateway does not serve the console. Where such uses exist, resolve
the gateway host into its own variable and leave the non-API uses on the product URL. Where every
use of the variable is an API call, repoint it in place under its own name; a new variable there is
a rename the fewest-edits rule does not permit.

### Classic API to `proclassic`

```text
https://{tenant}.jamfcloud.com/JSSResource/{resource}
→  https://{region}.api.jamfcloud.com/proclassic/{resource}
```

`JSSResource` is stripped and **no version segment is added**. The resource path carries over as
written, including `serialnumber/{serial}`, `id/{id}`, and `subset/{subset}`.

- **Reads negotiate on `Accept`.** Both `application/json` and `application/xml` answer 200. Leave
  the script's `Accept` header alone when it parses XML; switching it breaks the parsing without
  failing the call. With no `Accept` header at all, or `Accept: */*`, the gateway returns XML with
  `Content-Type: text/xml`, the same as Jamf Pro's own default, so a script that sends no `Accept`
  and parses XML needs no header added. `Accept: application/json` answers JSON with
  `Content-Type: text/plain`, and the JSON form of a Classic list carries no `size` element.
- **Writes are XML only.** A JSON body with `Content-Type: application/json` is a `415`. An XML body
  with `application/xml`, `text/xml`, or no `Content-Type` at all succeeds. The write operations
  declare no request body in their published specs, so the page cannot say this, and a converted
  Classic write that switched to JSON fails on first run. Keep the XML body.
- **Error bodies are Jamf Pro HTML, not the gateway's JSON envelope.** A `415` and a 404 for a
  deleted record alike return a Tomcat status page. A converted Classic script that pipes an error
  body to `jq` gets a parse failure instead of a message, and a non-JSON 404 there means the record
  is gone far more often than it means the route is wrong. This is the one surface where a failure
  looks nothing like a platform call's failure, so error-shape reasoning that holds everywhere else
  is suspended for it.
- **Classic's JSON wraps the record in its resource name and nests fields under the subset.** The
  Jamf Pro object does not. `['computer']['general']['udid']` on the Classic surface is `['udid']`
  on the Pro surface. A cross-surface move changes the depth of the parse path, not just the field
  names.

**The Classic computer record has no gateway route.** `findcomputers`, the `findcomputersby*` record
lookups including their `subset` forms, and every `updatecomputerby*` form are absent from the
published surface.
`createcomputerbyid` and its `macaddress`, `name`, `serialnumber`, and `udid` forms,
`deletecomputerbyid`, `matchcomputers`, and the history, management, and hardware-software report
reads are present. Mobile devices and computer groups publish their full find, create, update, and
delete sets including `subset`.

A Classic computer read or write therefore moves cross-surface to the Pro API, which is a
product-surface change rather than a path rewrite and changes the request and response from XML to
JSON:

| Classic operation | Route | Grant |
| --- | --- | --- |
| Read a subset | `GET /pro/v4/computers-inventory?section={SECTION}&filter=…` | `devices:read` |
| Read the whole record | `GET /pro/v4/computers-inventory-detail/{id}` | `devices:read` |
| Write | `PATCH /pro/v4/computers-inventory-detail/{id}` | `devices:update` |

Rules that bite on that move:

- **Classic field names do not carry across.** `<real_name>` is `realname`, `<email_address>` is
  `email`, and `<department>` and `<building>` become `departmentId` and `buildingId`, which take
  IDs rather than names. A name the script holds has to be resolved to an ID first, which is a
  named change.
- **Subset names and section names are false friends.** Classic's `subset/General` carries
  `mac_address`; the Pro API's `GENERAL` section does not, because it lives in `HARDWARE`. Resolve
  each field's location on the target surface rather than matching the container's name.
- **A parsing helper's output format is part of the contract around it.** `xpath` emits matching
  nodes with their tags, so code that builds a payload from its output may supply no element names
  of its own. A JSON extraction returns bare values, and that code now has to supply them. Check
  what the replaced extraction was handing downstream before declaring the parse converted.
- The cross-surface write is a `PATCH` of a JSON object, not a `PUT` of an XML document. The grant
  set can change with the surface; see `capability-grants.md`.

### Jamf Protect to `protect`

```text
POST https://{tenant}.protect.jamfcloud.com/graphql
→  POST https://{region}.api.jamfcloud.com/protect
```

- **The path carries no operation.** The `graphql` segment is dropped, not prefixed with the slug,
  because one endpoint serves every operation and the body decides what runs. `/protect/graphql`
  is `403 BAD_PERMISSIONS`. Slug-plus-path is the wrong transform for a single-endpoint API.
- **A Protect conversion is a transport change, not a surface change.** The GraphQL schema over the
  gateway is the same schema, so the document, its variables, and every parse path in the response
  go across verbatim. Only the host, the path, the `Authorization` shape, and the scope header move.
- The token exchange changes form: the JSON `{"client_id", "password"}` body against `/token`
  becomes the form-encoded gateway exchange. The response field names do not change.
- Which operations exist over the gateway, the error taxonomy, and the coverage gate are in
  `protect-graphql.md`.

### Jamf Security Cloud to `securitycloud`

One slug serves six published categories: devices, categories, DNS, enrollment, UEM Connect, and
ZTNA. Resolve each call against the matching category index,
`https://developer.jamf.com/platform-api/reference/security-cloud-{category}/llms.txt` and
`.../uem-connect/llms.txt`, `.../ztna/llms.txt`. An operation that none of them publishes, such as
a device risk query, has no gateway route and stays on its product host with its own credential.

### Already on the gateway: beta to GA

A script written against the public beta needs converting even though it makes no product API
calls. Between beta and GA the host, the prefix, the scoping mechanism, some slugs, and some
versions changed, so "already platform" is not "already current."

| Beta form | GA form |
| --- | --- |
| `https://us.apigw.jamf.com/api/…` | `https://{region}.api.jamfcloud.com/…`, no `/api/` |
| `/tenant/{tenantId}/…` or `/environment/{id}/…` in the path | The scope header, following the *new* integration's scope level |
| `cb/engine` slug | `compliance-benchmarks` |
| `{action}:{product}:{capability}` grant strings | `{capability}:{action}`, converted per `capability-grants.md` |
| Beta integration client ID and secret | A new integration, valid for six months. GA deleted every beta client. |

- **A tenant ID in a beta path does not automatically become `X-Tenant-Id`.** The header follows
  the new integration's scope level, and the beta client's scope did not survive it. Under
  environment scope the tenant ID has no header to go in and one call covers every tenant in the
  environment. The output assumes environment scope, states it, and gives the tenant alternative in
  one line.
- **Every beta-era slug is re-verified individually.** `pro` survived unchanged. `cb/engine` did
  not, and the beta form under the GA host is a plain-text 404 rather than the usual
  `403 BAD_PERMISSIONS`, so there is no JSON envelope and nothing for a `jq` parse to report.
  Fixing only the host produces exactly that.
- **Beta paths were not uniformly shaped.** One call can carry `/tenant/{id}/` while the next does
  not. Resolve each call rather than running one substitution over the file.
- **Versions are re-verified**, per the procedure above. GA left existing versions in place, and a
  version the beta script used may since have been deprecated or may never have had a route for
  that object type.
- **Auth that is already correct is left alone.** A beta script's `POST /auth/token` exchange,
  `.access_token` parse, and `Bearer` header need no change. Only the client ID and secret values
  change, because they name an integration that no longer exists.

### Scripts built on the Jamf Platform Go SDK

A Go program that imports `github.com/Jamf-Concepts/jamfplatform-go-sdk/...` makes no HTTP calls of
its own. The SDK builds the URL, performs the token exchange, sends the scope header, refreshes the
token, and pages list results. Its conversion is a library-version and configuration change, not a
call-by-call rewrite, and the rules above apply to it through the SDK's own surface:

1. **Pin a GA release.** Header scoping and `WithEnvironmentID` arrived in v0.17.0; the GA host and
   credential model arrived in v0.20.0 (2026-09-03). A script pinned below v0.17.0 in `go.mod` still
   scopes by URL path, and one below v0.20.0 still targets the retired host. Move the requirement to
   the current release: `go get github.com/Jamf-Concepts/jamfplatform-go-sdk@latest`, then
   `go mod tidy`. Name the version the script was on and the one it moves to.
2. **The base URL is the gateway root, with no path.** `https://{region}.api.jamfcloud.com`. The
   SDK appends `/{slug}/{version}/…` and `/auth/token` itself, so a base URL carrying `/api`, the
   retired `{region}.apigw.jamf.com` host, or a `/tenant/{id}` segment sends the token exchange to a
   path the gateway does not serve and fails during authentication rather than on the call.
3. **The scope option matches the new integration, and exactly one is set.** `WithTenantID` sends
   `X-Tenant-Id`; `WithEnvironmentID` sends `X-Environment-Id`; neither sends nothing, which is the
   organization-scope form the `account` package uses. Crossing a tenant ID with an
   environment-scoped credential is refused with `403 OWNERSHIP_FORBIDDEN`. Setting both is a
   mistake, not a combination. A tenant ID the script carried does not automatically stay a tenant
   ID; the option follows the scope the new integration is minted at, and the output states which.
4. **The credential values are replaced.** GA deleted every beta integration. The environment
   variable names the script reads can stay; the values are a new integration's client ID and
   secret. Say so, because nothing in the diff shows it.
5. **Version resolution applies to method names.** Pro methods carry a version suffix,
   `ListBuildingsV1`, `GetComputerInventoryV4`. A suffix is a version segment and resolves the same
   way: against the published surface, to the highest non-deprecated version. The SDK can still
   expose a method for a deprecated version, so a method that compiles is not evidence the version
   is current. Where the resolved method returns a different struct, step 3 of the procedure names
   the change.
6. **No re-mint machinery and no pagination loop is added.** The SDK refreshes the token and pages
   every list call. A script that wrapped an SDK call in its own paging or token handling keeps it;
   that is the script's structure and is left alone.

What the SDK does not wrap, and what the conversion does there:

| Surface | In the SDK | What the script does |
| --- | --- | --- |
| Jamf Protect | No package | The GraphQL call is a hand-built `POST {base}/protect` beside the SDK client, using `client.AccessToken(ctx)` for the bearer and the same scope header the client sends. Every rule in `protect-graphql.md` applies to it. |
| Classic computer record read and update | Absent, as on the gateway | The `pro` package's computer-inventory methods, per the cross-surface rule above |
| Audit | Package present, every call refused at GA | Declined, with the reason: the grant is not issued to external integrations |
| Jamf Account | `account` package, organization scope, US gateway only | Left as the SDK documents it |

**Three inputs that look alike and are not.** A raw-HTTP Go program converts call by call like any
other language; it is not rewritten onto the SDK, because that is a refactor. A program already on
this SDK converts as above; it is not rewritten into raw HTTP. A program on a *different* Go client
library for the product APIs has a library to replace, not calls to route, and replacing a library
is a rewrite: the report names this SDK as the target and what its equivalents are for the calls
the script makes, and declines the code change.

## Constructs replaced by a different system

Some things are replaced by a different system rather than a different endpoint. The answer is that
the workflow leaves scripting, not that a path is missing.

- **Jamf Pro API roles, API privileges, and API integrations** publish nothing over the gateway.
  Platform credentials are integrations granted capabilities in Jamf Account. The near-miss to
  avoid is `accounts` and `account-groups`, which are published and are a different construct:
  Jamf Pro admin accounts, not API credentials.
- **A local binary invocation is not an API call.** `/usr/local/bin/jamf recon` takes no grant and
  has no route to move to. Converting it into a `device-actions` request turns a local inventory
  submission into a remote MDM command, which is a different operation reaching a different result.

## Surfaces with no gateway equivalent

Two different stops. Step 2 stops because a route is missing. Step 6 stops because of where the
script runs, even though every route resolves. Both are reported in the stop format in `SKILL.md`,
and neither means the script has stopped working: the product APIs still answer. Every row below
describes the gateway, never the product: a resource with no route here is one Jamf Pro still serves
unless the row says otherwise.

No route, by design or not yet:

| Surface | Status | What the report says |
| --- | --- | --- |
| The nine authentication paths and Basic auth | Removed by design | Replaced by the one exchange; not a stop |
| API clients, API roles, API privileges | Removed by design | Managed in Jamf Account; the workflow leaves scripting |
| Peripherals and peripheral types | Deprecated in Jamf Pro | No capability exists; no gateway route. The product endpoint still answers. |
| `/v2/local-admin-password/*` | Unavailable through the gateway | Stays on the Jamf Pro API with its own credential |
| `/preview/remote-administration-configurations` | Unavailable through the gateway | Stays on the Jamf Pro API, even though the index still lists it |
| Classic computer record read and update | Absent | Cross-surface to the Pro API; see above |
| Protect console operations | Absent from the gateway schema | No route; see `protect-graphql.md` |
| Security Cloud operations outside the six categories | Unpublished | No route |

Where **every** non-auth call in a script sits in this table, the script is declined at the script
level. Where only some do, the rest converts and the report names what stayed, why, and that the
script's purpose may still depend on what stayed. How central a call is does not decide this; having
a route does.

## Where the script runs

Step 6 in `SKILL.md` stops a script that Jamf Pro deploys to endpoints and that holds credential
variables. Detect the deployment from the code, and say what the conclusion rests on:

- `$4` or a later positional parameter read as configuration while `$1`, `$2`, and `$3` go unread.
  Jamf Pro passes the mount point, the computer name, and the username in the first three, so a
  script that starts its own parameters at `$4` was written for a policy. The offsets are also
  mandatory: renumbering `$4` to `$1` to close an apparent gap breaks the policy silently, and the
  script then reads a mount point as configuration.
- A local `ioreg` or `system_profiler` self-lookup feeding an API lookup of that same machine.
- A `/usr/local/bin/jamf` call by absolute path.
- An interactive prompt to the logged-in user: an `osascript` `display dialog`, a `read` at the
  console, a notification. A script that asks the person in front of the Mac for input runs on
  that Mac. A script that prompts for its own serial's email address is a Self Service script.
- `$3` used as the current username.

Any one alone is suggestive. Two together, or a self-lookup with a prompt to the logged-in user, is
conclusive. On a suggestive signal alone with nothing in the request saying where the script runs,
the conversion proceeds under a stated assumption, per `SKILL.md` step 6; on a conclusive set it
stops.

**Why the stop exists.** There is no device-side platform API authentication. A Mac cannot
authenticate to the platform API as itself at this time. Until it exists, a
credential in an on-device script is shared
across every Mac in scope, and the platform secret that would replace it reaches the tenant through
the gateway at the integration's scope level, in a payload readable in the Jamf Pro admin console
and written to disk fleet-wide. The blast radius goes up, not down.

**Every on-endpoint credential store is a relocation, not a fix, and none of them is offered.** A
Keychain item moves the secret out of the script payload and leaves it on every Mac. A
configuration profile and an encrypted string in the script take longer routes to the same place. A
Jamf Pro script parameter is the worst of them because it lands in the policy log. Narrowing the
integration's capabilities is better and is also not the fix. The alternatives the report names are
in the stop format in `SKILL.md`.
