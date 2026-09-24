# Runtime behavior

What the emitted script must do to work. Each item is a requirement on the output, not a fact to
recite in the report.

## Headers and tokens

- **Exactly one scope header on every gateway call, and none on the token mint.** `X-Environment-Id`
  by default, `X-Tenant-Id` where the integration is tenant-scoped, following `SKILL.md` Before
  converting. Calls left on a product host or a third-party host carry neither.
- **`Authorization: Bearer <token>`.** A bare token is a `401` that reads as a bad credential.
- **Re-mint the token inside any loop that can outlive it.** Tokens last 900 seconds and cannot be
  extended. Track expiry from `expires_in` in the token response and mint when the remaining
  lifetime is short. One check before each call is correct at twenty iterations and at four
  hundred, where minting once per run breaks partway down a long list and minting once per
  iteration wastes a call on every short one. Expiry mid-loop surfaces as a plain-text
  `401 Authentication failed`, which is a different form from the JSON `unauthorized access` that a
  missing credential produces. Where nothing loops, one mint is correct and no re-mint machinery is
  added. Where the script kept its token alive, the re-mint check replaces the keep-alive at the
  same points, since keep-alive has no gateway path. Extending the check to a loop the original
  never kept alive is named in the report as a behavior change, not as parity.
- **On the Jamf Platform Go SDK, none of the token handling above is the script's job.** The SDK
  mints, refreshes, and attaches the token and sends the one scope header. The emitted program
  passes the gateway root as the base URL and exactly one scope option. A Protect call made beside
  the SDK client takes its bearer from `client.AccessToken(ctx)` and sends the same scope header.
- **The scope ID is an identifier, not a secret.** It goes in the script the way the client ID does:
  as a literal, or from the same non-secret configuration source the script already reads its
  identifiers from. It is never read from the secret store.

```bash
TOKEN="" ; TOKEN_EXPIRES_AT=0
ensure_token() {
  [[ $(date +%s) -lt $((TOKEN_EXPIRES_AT - 60)) ]] && return 0
  local response
  response=$(curl -sf -X POST "$GATEWAY/auth/token" \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode 'grant_type=client_credentials' \
    --data-urlencode "client_id=$CLIENT_ID" \
    --data-urlencode "client_secret=$CLIENT_SECRET")
  TOKEN=$(printf '%s' "$response" | jq -r '.access_token // empty')
  [[ -n "$TOKEN" ]] || { echo "POST $GATEWAY/auth/token did not return an access token" >&2; exit 1; }
  TOKEN_EXPIRES_AT=$(( $(date +%s) + $(printf '%s' "$response" | jq -r '.expires_in') ))
}
```

The same check in Python, refreshing a shared headers dict:

```python
import time

TOKEN_EXPIRES_AT = 0

def ensure_token():
    global TOKEN_EXPIRES_AT
    if time.time() < TOKEN_EXPIRES_AT - 60:
        return
    r = requests.post(f"{GATEWAY}/auth/token",
        data={"grant_type": "client_credentials", "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET})
    r.raise_for_status()
    body = r.json()
    headers["Authorization"] = f"Bearer {body['access_token']}"
    TOKEN_EXPIRES_AT = time.time() + body["expires_in"]
```

## Reading a failure

- **Treat `403 BAD_PERMISSIONS` as possibly a wrong route before assuming a missing grant.** An
  unregistered path under a registered slug, an unrecognized version segment, a scope level the
  API is not published at, and a missing capability all return the same 403. Check the route, then
  the version, then the scope level, then the grant. A script that sends an admin to Jamf Account
  on every 403 sends them to re-scope a credential that was never wrong.
- **Classic error bodies are HTML.** Do not pipe a `proclassic` error body to `jq`. A non-JSON 404
  there means the record is gone far more often than it means the route is wrong.
- **Read `expires_in` and `access_token` off the gateway token response.** Not `.token`, not
  `expires`.

## Protect responses

- **Test `.errors` on every Protect response.** Everything returns HTTP 200, so a status check reads
  a failed call as success. `.errors // empty` non-empty is the failure signal.
- **Read `.message` on an `AuthorizationError`.** "Operation not permitted by tenant permissions."
  is a grant gap. "Could not verify tenant permissions." is a platform-side failure that hits every
  operation and clears on its own. Same `errorType`, opposite meanings.
- **Confirm the echoed identifier.** A mutation against a record that does not exist returns 200 with
  a non-nullable-type message and a null result, not a clean error. After `deleteComputer`, the
  script checks `data.deleteComputer.uuid` equals the UUID it sent. Where the script did this against
  the direct API, it keeps doing it.

## Identifiers

- **Resolve by serial.** It is the only identifier every product presents identically and the only
  one that survives re-enrollment. A Jamf Pro record ID and a platform device ID are both re-minted
  when a Mac re-enrolls; a script that caches either between runs targets the wrong record or none.
  The Protect `uuid` is the Mac's hardware UUID and survives, but it is the Jamf Pro `udid`
  lowercased, and the case difference makes it unsafe to hand one product's value to the other.
- **Read `hardware.serialNumber` on a platform device detail record.** `GET /devices/v1/devices`
  returns a top-level `serialNumber` on each list item. `GET /devices/v1/devices/{id}` returns
  top-level `serialNumber: null` and carries the value at `hardware.serialNumber`. A conversion that
  reads `.serialNumber` off a detail record silently gets null.
- **Filter server-side.** `filter=serialNumber=="{serial}"` on the platform device list and
  `filter=hardware.serialNumber=="{serial}"` on the Pro computer inventory both return
  `totalCount: 1` for one match, so the script does not page the fleet and match client-side.

## Cross-product deletes

A delete that removes a computer from both Jamf Pro and Jamf Protect is two calls needing a
different grant each, on top of whatever the resolving reads require, since a read action is granted
separately:

| Call | Grant |
| --- | --- |
| `GET /devices/v1/devices?filter=serialNumber=="{serial}"` | `devices:read` |
| `DELETE /devices/v1/devices/{device-id}` | `destructive-device-actions:execute` |
| `POST /protect`, `listComputers` filtered on serial | `devices:read` |
| `POST /protect`, `deleteComputer(uuid: "{protect-uuid}")` | `devices:delete` |

The platform delete does not cascade. `DELETE /devices/v1/devices/{id}` removes the Jamf Pro record
and the platform view of it; the Protect record survives untouched. Not-found differs by route: the
REST delete returns a JSON `404` with `code: NOT_FOUND`; the mutation returns 200 with a message and
no `errorType`.

## The secret

**The output never ships a bare empty secret.** The credential variables stay, with the client ID
as a literal because it is an identifier and not a secret, and the secret is read at runtime from
the host's secret store, with a worked example in the output. A `CLIENT_SECRET=""` with no guidance
anywhere hands the admin a script whose only implied instruction is to paste a secret into a file,
which is the habit the conversion exists to break.

This does not conflict with the fewest-edits rule, and the reason matters or it reads as licence to
refactor. The credential line is already inside the region being converted: a Basic auth user and
password become a client ID and secret, and a beta client ID and secret name an integration GA
deleted. Either way the line's value has to change, so the runtime read is the form a required edit
takes rather than an extra one. Where the script **already** resolves the secret from a non-literal
store, such as a plist, an environment variable, a Keychain item, or a prompt ladder, that store
carries over untouched and the read below goes in the report as a recommendation. Converting a
working resolution ladder to Keychain is the refactor the rule does not permit.

### macOS: Keychain, two commands

In the script:

```bash
CLIENT_ID="{client-id}"
KEYCHAIN_SERVICE="Jamf Platform API Integration"
CLIENT_SECRET=$(security find-generic-password -s "$KEYCHAIN_SERVICE" -w)
```

`-w` prints only the password. macOS prompts once per calling application unless the item's access
list already allows it.

In the report, the one-time import the admin runs with the secret in their clipboard:

```bash
security add-generic-password -U -s "Jamf Platform API Integration" -a "{client-id}" \
  -w '{client-secret}' -T /usr/bin/security ~/Library/Keychains/login.keychain-db
```

Give both. The read on its own does not tell an admin who has just minted an integration what to do
with the secret.

**The `-U` trap goes in the output wherever a new integration gets minted.** `-U` matches on service
*and* account, so re-running the import with a new client ID adds a second item rather than replacing
the first, and `find-generic-password -s` then returns whichever it finds first, which may be the
stale one. The symptom is `invalid_client` against a live client, indistinguishable from a wrong
secret, so an admin re-minting after GA walks into it holding a correct credential. Delete the old
item by service *and* account, then confirm which account the lookup resolves to:

```bash
security delete-generic-password -s "Jamf Platform API Integration" -a "{old-client-id}" \
  ~/Library/Keychains/login.keychain-db
security find-generic-password -s "Jamf Platform API Integration" | grep '"acct"'
```

A rotated secret on the same client ID replaces in place; a new client ID does not.

### Anywhere else: the platform's secret store

Match the secret store to where the script runs. Keychain is macOS-only, so a Lambda, a container,
or a Linux automation host gets that platform's secrets manager read into an environment variable,
and never `security`, which is not present there:

```python
CLIENT_SECRET = os.environ["JAMF_CLIENT_SECRET"]   # populated from the platform's secrets manager
```

**Where the host is not evident, condition the recommendation instead of guessing.** A `zsh` or
`bash` script calling `osascript`, `ioreg`, `defaults`, or `/usr/local/bin/jamf` is on macOS and
Keychain is unconditional. A Python or Go script with no macOS-only call could be running anywhere,
so the output names Keychain as the macOS form and the platform's secret store otherwise, in one
line rather than a survey. Emitting a bare `security` call into a script that may run on Linux
produces a script that fails on first run.

**On a script Jamf Pro deploys, none of this applies.** A Keychain item on an endpoint is a
relocation, not a fix, which is why the conversion stops there rather than recommending one. See
`conversion-rules.md`, "Where the script runs."
