# Worked conversions

Four before-and-after pairs, each with an abridged report; the shape a real report takes is in the
output contract. Every value is a placeholder: `{region}`, `{tenant}`, `{client-id}`,
`{environment-id}`, `{tenant-id}`, `{username}`, `{serial}`. Replace them; do not run these as they
stand.

## 1. Delete a computer from Jamf Pro and Jamf Protect

Two scripts, two credentials on two hosts, two authentication models. The request was to convert
both to one script over one integration, so merging them is a change made at the admin's request
and is named as such. Environment scope, `bash`, runs from an admin's Mac.

### Before: Jamf Pro

```bash
#!/bin/bash
# Delete computer inventory records from Jamf Pro by serial number.
# Usage: ./pro-delete-computer.sh <serial> [serial...]

JAMF_PRO_URL="https://{tenant}.jamfcloud.com"
JAMF_USER="{username}"
KEYCHAIN_SERVICE="Jamf Pro User Account"

[[ $# -gt 0 ]] || { echo "Usage: $(basename "$0") <serial> [serial...]" >&2; exit 64; }

# Password from the Keychain.
JAMF_PASSWORD=$(security find-generic-password -s "$KEYCHAIN_SERVICE" -w 2>/dev/null) || {
  echo "Could not read the password from Keychain: $KEYCHAIN_SERVICE" >&2
  exit 1
}

# Authenticate.
TOKEN=$(curl -sf -X POST "$JAMF_PRO_URL/api/v1/auth/token" \
  -u "$JAMF_USER:$JAMF_PASSWORD" | jq -r '.token // empty')

if [[ -z "$TOKEN" ]]; then
  echo "POST /api/v1/auth/token did not return a token" >&2
  exit 1
fi

echo "$JAMF_PRO_URL — $# serial(s)"

DELETED=0 MISSING=0 FAILED=0
for serial in "$@"; do
  # Find the record for this serial.
  record=$(curl -sf -H "Authorization: Bearer $TOKEN" \
    --get "$JAMF_PRO_URL/api/v1/computers-inventory" \
    --data-urlencode 'section=GENERAL' \
    --data-urlencode "filter=hardware.serialNumber==\"$serial\"")

  count=$(printf '%s' "$record" | jq -r '.totalCount // empty')
  if [[ -z "$count" ]]; then
    echo "  $serial: inventory lookup failed"; FAILED=$((FAILED + 1)); continue
  elif [[ "$count" == "0" ]]; then
    echo "  $serial: no matching computer record"; MISSING=$((MISSING + 1)); continue
  elif [[ "$count" != "1" ]]; then
    echo "  $serial: $count matching records, skipped — resolve by hand"; FAILED=$((FAILED + 1)); continue
  fi

  id=$(printf '%s' "$record" | jq -r '.results[0].id')
  name=$(printf '%s' "$record" | jq -r '.results[0].general.name')

  # Delete it.
  code=$(curl -sS -o /dev/null -w '%{http_code}' -X DELETE \
    -H "Authorization: Bearer $TOKEN" \
    "$JAMF_PRO_URL/api/v1/computers-inventory/$id")

  if [[ "$code" != "204" ]]; then
    echo "  $serial: DELETE /api/v1/computers-inventory/$id returned $code"; FAILED=$((FAILED + 1)); continue
  fi

  echo "  $serial: deleted \"$name\", Jamf Pro ID $id"
  DELETED=$((DELETED + 1))
done

echo "Deleted $DELETED, not found $MISSING, failed $FAILED"
[[ $FAILED -eq 0 ]]
```

### Before: Jamf Protect

```bash
#!/bin/bash
# Delete computer records from Jamf Protect by serial number.
# Usage: ./protect-delete-computer.sh <serial> [serial...]

PROTECT_URL="https://{tenant}.protect.jamfcloud.com"
CLIENT_ID="{client-id}"
KEYCHAIN_SERVICE="Jamf Protect API Client"

[[ $# -gt 0 ]] || { echo "Usage: $(basename "$0") <serial> [serial...]" >&2; exit 64; }

# Client password from the Keychain.
CLIENT_SECRET=$(security find-generic-password -s "$KEYCHAIN_SERVICE" -w 2>/dev/null) || {
  echo "Could not read the client password from Keychain: $KEYCHAIN_SERVICE" >&2
  exit 1
}

# Authenticate.
TOKEN=$(curl -sf -X POST "$PROTECT_URL/token" \
  -H 'Content-Type: application/json' \
  -d "{\"client_id\":\"$CLIENT_ID\",\"password\":\"$CLIENT_SECRET\"}" | jq -r '.access_token // empty')

if [[ -z "$TOKEN" ]]; then
  echo "POST $PROTECT_URL/token did not return an access token" >&2
  exit 1
fi

FIND_QUERY='query FindBySerial($serial: String!) {
  listComputers(input: { filter: { serial: { equals: $serial } }, pageSize: 2 }) {
    items { uuid serial hostName connectionStatus }
  }
}'

DELETE_MUTATION='mutation DeleteComputer($uuid: ID!) {
  deleteComputer(uuid: $uuid) { uuid serial hostName }
}'

# graphql <document> <variables-json> -> response body on stdout
graphql() {
  jq -n --arg q "$1" --argjson v "$2" '{query: $q, variables: $v}' \
    | curl -sf -X POST "$PROTECT_URL/graphql" \
        -H 'Content-Type: application/json' \
        -H "Authorization: $TOKEN" \
        -d @-
}

echo "$PROTECT_URL — $# serial(s)"

DELETED=0 MISSING=0 FAILED=0
for serial in "$@"; do
  # Find the computer for this serial.
  record=$(graphql "$FIND_QUERY" "$(jq -n --arg s "$serial" '{serial: $s}')")

  errors=$(printf '%s' "$record" | jq -c '.errors // empty')
  if [[ -n "$errors" ]]; then
    echo "  $serial: listComputers returned errors: $errors"; FAILED=$((FAILED + 1)); continue
  fi

  count=$(printf '%s' "$record" | jq -r '.data.listComputers.items | length')
  if [[ "$count" == "0" ]]; then
    echo "  $serial: no matching Protect computer"; MISSING=$((MISSING + 1)); continue
  elif [[ "$count" != "1" ]]; then
    echo "  $serial: $count matching records, skipped — resolve by hand"; FAILED=$((FAILED + 1)); continue
  fi

  uuid=$(printf '%s' "$record" | jq -r '.data.listComputers.items[0].uuid')
  host=$(printf '%s' "$record" | jq -r '.data.listComputers.items[0].hostName')

  # Delete it.
  result=$(graphql "$DELETE_MUTATION" "$(jq -n --arg u "$uuid" '{uuid: $u}')")

  errors=$(printf '%s' "$result" | jq -c '.errors // empty')
  if [[ -n "$errors" ]]; then
    echo "  $serial: deleteComputer returned errors: $errors"; FAILED=$((FAILED + 1)); continue
  fi

  # Check the uuid came back.
  if [[ "$(printf '%s' "$result" | jq -r '.data.deleteComputer.uuid // empty')" != "$uuid" ]]; then
    echo "  $serial: deleteComputer did not confirm $uuid"; FAILED=$((FAILED + 1)); continue
  fi

  echo "  $serial: deleted \"$host\", Protect UUID $uuid"
  DELETED=$((DELETED + 1))
done

echo "Deleted $DELETED, not found $MISSING, failed $FAILED"
[[ $FAILED -eq 0 ]]
```

### After

```bash
#!/bin/bash
# Delete computer records from Jamf Pro and Jamf Protect by serial number, over
# the Jamf Platform API Gateway.
# Usage: ./platform-delete-computer.sh <serial> [serial...]

GATEWAY="https://{region}.api.jamfcloud.com"
CLIENT_ID="{client-id}"
ENVIRONMENT_ID="{environment-id}"
KEYCHAIN_SERVICE="Jamf Platform API Integration"

[[ $# -gt 0 ]] || { echo "Usage: $(basename "$0") <serial> [serial...]" >&2; exit 64; }

# Client secret from the Keychain.
CLIENT_SECRET=$(security find-generic-password -s "$KEYCHAIN_SERVICE" -w 2>/dev/null) || {
  echo "Could not read the client secret from Keychain: $KEYCHAIN_SERVICE" >&2
  exit 1
}

TOKEN=""
TOKEN_EXPIRES_AT=0

# Authenticate. Tokens expire in 15 minutes and cannot be extended, so re-mint
# when one is close.
ensure_token() {
  [[ $(date +%s) -lt $((TOKEN_EXPIRES_AT - 60)) ]] && return 0

  local response
  response=$(curl -sf -X POST "$GATEWAY/auth/token" \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode 'grant_type=client_credentials' \
    --data-urlencode "client_id=$CLIENT_ID" \
    --data-urlencode "client_secret=$CLIENT_SECRET")

  TOKEN=$(printf '%s' "$response" | jq -r '.access_token // empty')
  if [[ -z "$TOKEN" ]]; then
    echo "POST $GATEWAY/auth/token did not return an access token" >&2
    exit 1
  fi
  TOKEN_EXPIRES_AT=$(( $(date +%s) + $(printf '%s' "$response" | jq -r '.expires_in') ))
}

FIND_QUERY='query FindBySerial($serial: String!) {
  listComputers(input: { filter: { serial: { equals: $serial } }, pageSize: 2 }) {
    items { uuid serial hostName connectionStatus }
  }
}'

DELETE_MUTATION='mutation DeleteComputer($uuid: ID!) {
  deleteComputer(uuid: $uuid) { uuid serial hostName }
}'

# graphql <document> <variables-json> -> response body on stdout
graphql() {
  jq -n --arg q "$1" --argjson v "$2" '{query: $q, variables: $v}' \
    | curl -sf -X POST "$GATEWAY/protect" \
        -H 'Content-Type: application/json' \
        -H "Authorization: Bearer $TOKEN" \
        -H "X-Environment-Id: $ENVIRONMENT_ID" \
        -d @-
}

echo "$GATEWAY — environment $ENVIRONMENT_ID — $# serial(s)"

DELETED=0 MISSING=0 FAILED=0
for serial in "$@"; do
  echo "  $serial"

  # Per-product result: 0 deleted, 1 failed, 2 not found. A Mac in Jamf Pro but
  # not in Protect is normal, so a miss on one side is not a failure of the other.
  pro=0 protect=0

  # --- Jamf Pro --------------------------------------------------------------

  # Find the record for this serial.
  ensure_token
  record=$(curl -sf -H "Authorization: Bearer $TOKEN" \
    -H "X-Environment-Id: $ENVIRONMENT_ID" \
    --get "$GATEWAY/devices/v1/devices" \
    --data-urlencode "filter=serialNumber==\"$serial\"")

  count=$(printf '%s' "$record" | jq -r '.totalCount // empty')
  if [[ -z "$count" ]]; then
    echo "    Jamf Pro: device lookup failed"; pro=1
  elif [[ "$count" == "0" ]]; then
    echo "    Jamf Pro: no matching device record"; pro=2
  elif [[ "$count" != "1" ]]; then
    echo "    Jamf Pro: $count matching records, skipped — resolve by hand"; pro=1
  else
    id=$(printf '%s' "$record" | jq -r '.results[0].id')
    name=$(printf '%s' "$record" | jq -r '.results[0].name')

    # Delete it.
    ensure_token
    code=$(curl -sS -o /dev/null -w '%{http_code}' -X DELETE \
      -H "Authorization: Bearer $TOKEN" \
      -H "X-Environment-Id: $ENVIRONMENT_ID" \
      "$GATEWAY/devices/v1/devices/$id")

    if [[ "$code" != "204" ]]; then
      echo "    Jamf Pro: DELETE /devices/v1/devices/$id returned $code"; pro=1
    else
      echo "    Jamf Pro: deleted \"$name\", platform device ID $id"
    fi
  fi

  # --- Jamf Protect ----------------------------------------------------------

  # Find the computer for this serial.
  ensure_token
  record=$(graphql "$FIND_QUERY" "$(jq -n --arg s "$serial" '{serial: $s}')")

  errors=$(printf '%s' "$record" | jq -c '.errors // empty')
  count=$(printf '%s' "$record" | jq -r '.data.listComputers.items | length')

  if [[ -n "$errors" ]]; then
    echo "    Jamf Protect: listComputers returned errors: $errors"; protect=1
  elif [[ "$count" == "0" ]]; then
    echo "    Jamf Protect: no matching computer"; protect=2
  elif [[ "$count" != "1" ]]; then
    echo "    Jamf Protect: $count matching records, skipped — resolve by hand"; protect=1
  else
    uuid=$(printf '%s' "$record" | jq -r '.data.listComputers.items[0].uuid')
    host=$(printf '%s' "$record" | jq -r '.data.listComputers.items[0].hostName')

    # Delete it.
    ensure_token
    result=$(graphql "$DELETE_MUTATION" "$(jq -n --arg u "$uuid" '{uuid: $u}')")

    errors=$(printf '%s' "$result" | jq -c '.errors // empty')
    echoed=$(printf '%s' "$result" | jq -r '.data.deleteComputer.uuid // empty')

    if [[ -n "$errors" ]]; then
      echo "    Jamf Protect: deleteComputer returned errors: $errors"; protect=1
    elif [[ "$echoed" != "$uuid" ]]; then
      # Check the uuid came back.
      echo "    Jamf Protect: deleteComputer did not confirm $uuid"; protect=1
    else
      echo "    Jamf Protect: deleted \"$host\", Protect UUID $uuid"
    fi
  fi

  # --- Roll up --------------------------------------------------------------

  if [[ $pro -eq 1 || $protect -eq 1 ]]; then
    FAILED=$((FAILED + 1))
  elif [[ $pro -eq 2 && $protect -eq 2 ]]; then
    MISSING=$((MISSING + 1))
  else
    DELETED=$((DELETED + 1))
  fi
done

echo "Deleted $DELETED, not found $MISSING, failed $FAILED"
[[ $FAILED -eq 0 ]]
```

### Report

**Set up the integration.** Platform environment scope. Every gateway call carries
`X-Environment-Id`; the token mint carries no scope header.

The grants:

| Grant | Picker | Needed by |
| --- | --- | --- |
| `devices:read` | Inventory › Devices | `GET /devices/v1/devices`, Protect `listComputers` |
| `destructive-device-actions:execute` | Device actions › Destructive device actions | `DELETE /devices/v1/devices/{id}` |
| `devices:delete` | Inventory › Devices | Protect `deleteComputer` |

`devices:read` covers the read on both products and is one grant. The two deletes take two
different grants: no REST device-record deletion uses `devices:delete`, and `devices:delete` exists
only on the Protect mutation.

- Mint an environment-scoped integration in Jamf Account with the three grants above. Note the
  environment ID from its details panel.
- Import the secret once:
  `security add-generic-password -U -s "Jamf Platform API Integration" -a "{client-id}" -w '{client-secret}' -T /usr/bin/security ~/Library/Keychains/login.keychain-db`.
  If this integration ever gets re-minted with a new client ID, delete the old item by service and
  account first; `-U` does not replace an item whose account differs, and the lookup then returns
  whichever it finds first.

**Changes.**

- Authentication. Two exchanges became one `POST /auth/token`, form-encoded, client credentials.
  The Jamf Pro exchange was a username and password against `/api/v1/auth/token`, which has no
  gateway path; its `.token` parse became `.access_token`, and `expires_in` is now read to track
  expiry. The Protect exchange against `/token` had the same response field names and its parse
  is unchanged. `Authorization` on the Protect calls gained the `Bearer` prefix, which the gateway
  requires and the direct Protect API did not.
- Authentication. A re-mint check was added before each call, because the loop over serials is
  unbounded and a 900-second token cannot be extended. The original Jamf Pro script minted once.
- Credentials. `CLIENT_ID` keeps its name and holds a different value: a Jamf Account integration's
  client ID, not the Protect API client's. `KEYCHAIN_SERVICE` names a new item. The Jamf Pro
  username and its Keychain item are gone. The secret is still read from the Keychain at runtime,
  which is the store both originals already used.
- Routes. `GET /api/v1/computers-inventory` became the platform-native
  `GET /devices/v1/devices` with `filter=serialNumber=="…"`. The same-surface route would have been
  `/pro/v4/computers-inventory`: `v1` publishes no gateway route and `v3` is deprecated as of
  2026-07-14, so the version would have moved either way. The platform route returns a platform
  device ID that the delete on the same surface accepts.
- Routes. `DELETE /api/v1/computers-inventory/{id}` became `DELETE /devices/v1/devices/{id}`.
- Routes. `POST /graphql` on the Protect host became `POST /protect` on the gateway. The two
  GraphQL documents and their variables are unchanged.
- Response handling. On the device list the name is `.results[0].name`, not
  `.results[0].general.name`, and the `section=GENERAL` parameter has no equivalent and was
  dropped. `totalCount` and `results[]` are unchanged.
- Output. The success line says "platform device ID" rather than "Jamf Pro ID", because the value
  printed is now the platform identifier.
- Structure, at the admin's request. The two scripts were merged into one, with a per-product
  result and a roll-up so that a Mac present in Jamf Pro but not in Protect is a partial success
  rather than a failure, which neither original could express.

**Declined.** Nothing.

**Divergences.** None.

**Recommendations.** `curl -sf` on the lookups discards the error body, so a `403` from a wrong
route or a missing grant prints only "lookup failed". Both originals had this and it was left. To
see the body: replace `-sf` with `-sS` and test `.totalCount` before `.errors`.

## 2. Classic API: update a mobile device's user by serial

A `zsh` script an admin runs from their Mac. Basic auth directly on Classic resource endpoints, XML
in and out. Tenant scope.

### Before

```bash
#!/bin/zsh
# Assign a user to a mobile device. Usage: assign-user.sh <serial> <username> <email>
JSS="https://{tenant}.jamfcloud.com"
API_USER="{username}"
API_PASS="$(security find-generic-password -s "Jamf Pro API Account" -w)"

serial="$1"; user="$2"; email="$3"

xml=$(curl -s -u "$API_USER:$API_PASS" -H 'Accept: application/xml' \
  "$JSS/JSSResource/mobiledevices/serialnumber/$serial")
id=$(echo "$xml" | xmllint --xpath 'string(/mobile_device/general/id)' -)
[[ -n "$id" ]] || { echo "No device for $serial" >&2; exit 1; }

curl -s -u "$API_USER:$API_PASS" -H 'Content-Type: application/xml' -X PUT \
  -d "<mobile_device><location><username>$user</username><email_address>$email</email_address></location></mobile_device>" \
  "$JSS/JSSResource/mobiledevices/id/$id" > /dev/null

echo "Assigned $user to device $id ($JSS/mobileDevices.html?id=$id)"
```

### After

```bash
#!/bin/zsh
# Assign a user to a mobile device. Usage: assign-user.sh <serial> <username> <email>
JSS="https://{tenant}.jamfcloud.com"
GATEWAY="https://{region}.api.jamfcloud.com"
TENANT_ID="{tenant-id}"
CLIENT_ID="{client-id}"
CLIENT_SECRET="$(security find-generic-password -s "Jamf Platform API Integration" -w)"

TOKEN=$(curl -s -X POST "$GATEWAY/auth/token" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'grant_type=client_credentials' \
  --data-urlencode "client_id=$CLIENT_ID" \
  --data-urlencode "client_secret=$CLIENT_SECRET" | jq -r '.access_token')

serial="$1"; user="$2"; email="$3"

xml=$(curl -s -H "Authorization: Bearer $TOKEN" -H "X-Tenant-Id: $TENANT_ID" -H 'Accept: application/xml' \
  "$GATEWAY/proclassic/mobiledevices/serialnumber/$serial")
id=$(echo "$xml" | xmllint --xpath 'string(/mobile_device/general/id)' -)
[[ -n "$id" ]] || { echo "No device for $serial" >&2; exit 1; }

curl -s -H "Authorization: Bearer $TOKEN" -H "X-Tenant-Id: $TENANT_ID" -H 'Content-Type: application/xml' -X PUT \
  -d "<mobile_device><location><username>$user</username><email_address>$email</email_address></location></mobile_device>" \
  "$GATEWAY/proclassic/mobiledevices/id/$id" > /dev/null

echo "Assigned $user to device $id ($JSS/mobileDevices.html?id=$id)"
```

### Report

**Set up the integration.** Tenant scope, as requested. Every gateway call carries `X-Tenant-Id`.

The grants:

| Grant | Picker | Needed by |
| --- | --- | --- |
| `devices:read` | Inventory › Devices | `GET /proclassic/mobiledevices/serialnumber/{serial}` |
| `devices:update` | Inventory › Devices | `PUT /proclassic/mobiledevices/id/{id}` |
| `users:update` | Inventory › Users | `PUT /proclassic/mobiledevices/id/{id}` |

The Classic mobile-device update publishes two capabilities. Both are required.

- Mint a tenant-scoped integration with the three grants and note the
  tenant ID. Import the secret with `security add-generic-password -U -s "Jamf Platform API Integration" -a "{client-id}" -w '{client-secret}' -T /usr/bin/security ~/Library/Keychains/login.keychain-db`.

**Changes.**

- Authentication. The script had no token call; Basic auth on each resource call was the whole of
  it, and Basic auth has no gateway path. One `POST /auth/token` exchange was added and both
  `-u` arguments became `Authorization: Bearer`. One mint is enough: nothing loops.
- Credentials. `API_USER` and `API_PASS` are gone. `CLIENT_ID` is a literal and `CLIENT_SECRET` is
  read from the Keychain at runtime, which is where the password already came from; the item name
  changed because the credential did.
- Routes. Both `/JSSResource/…` paths became `/proclassic/…` on the gateway with no version segment
  added. The resource paths are unchanged.
- Headers. `Accept: application/xml` on the read is unchanged, because the script parses XML and the
  Classic read answers 200 in either type. The XML body and `Content-Type: application/xml` on the
  write are unchanged, because Classic writes over the gateway accept XML only; a JSON body returns
  `415`.
- Host. `JSS` stays, because the final line builds a console link from it and the gateway does not
  serve the console. The gateway host is a separate variable.

**Declined.** Nothing.

**Divergences.** None.

**Recommendations.** Neither `curl` checks its status, so a `415`, a 404 for a device deleted
between the two calls, or a `403` from a missing grant prints "Assigned". Unchanged from the
original. Classic error bodies are HTML, so if a check is added, test `%{http_code}` rather than
parsing the body as JSON.

## 3. Jamf Protect: list open alerts

A Python script with no macOS-only call, so it may run anywhere. Environment scope.

### Before

```python
import os
import requests

TENANT = "https://{tenant}.protect.jamfcloud.com"
CLIENT_ID = "{client-id}"
PASSWORD = os.environ["PROTECT_API_PASSWORD"]

tok = requests.post(f"{TENANT}/token", json={"client_id": CLIENT_ID, "password": PASSWORD})
tok.raise_for_status()
token = tok.json()["access_token"]

QUERY = """
query OpenAlerts($input: AlertQueryInput!) {
  listAlerts(input: $input) {
    items { uuid severity created status computer { hostName } }
    pageInfo { next }
  }
}
"""
r = requests.post(
    f"{TENANT}/graphql",
    json={"query": QUERY, "variables": {"input": {"pageSize": 100, "filter": {"status": {"equals": "Open"}}}}},
    headers={"Authorization": token},
)
r.raise_for_status()
for a in r.json()["data"]["listAlerts"]["items"]:
    print(a["created"], a["severity"], a["computer"]["hostName"], a["uuid"])
```

### After

```python
import os
import requests

GATEWAY = "https://{region}.api.jamfcloud.com"
ENVIRONMENT_ID = "{environment-id}"
CLIENT_ID = "{client-id}"
CLIENT_SECRET = os.environ["JAMF_CLIENT_SECRET"]

tok = requests.post(
    f"{GATEWAY}/auth/token",
    data={"grant_type": "client_credentials", "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET},
)
tok.raise_for_status()
token = tok.json()["access_token"]

QUERY = """
query OpenAlerts($input: AlertQueryInput!) {
  listAlerts(input: $input) {
    items { uuid severity created status computer { hostName } }
    pageInfo { next }
  }
}
"""
r = requests.post(
    f"{GATEWAY}/protect",
    json={"query": QUERY, "variables": {"input": {"pageSize": 100, "filter": {"status": {"equals": "Open"}}}}},
    headers={"Authorization": f"Bearer {token}", "X-Environment-Id": ENVIRONMENT_ID},
)
r.raise_for_status()
for a in r.json()["data"]["listAlerts"]["items"]:
    print(a["created"], a["severity"], a["computer"]["hostName"], a["uuid"])
```

### Report

**Set up the integration.** Platform environment scope. The one gateway call carries
`X-Environment-Id`; the token mint carries no scope header.

The grants:

| Grant | Picker | Needed by |
| --- | --- | --- |
| `threat-alerts:read` | Endpoint security › Threat alerts | `listAlerts` |

The nested `computer { hostName }` selection has no published grant of its own; the published tables
cover operations only. The field was left in the document. If the call returns
`AuthorizationError` with "Operation not permitted by tenant permissions." after `threat-alerts:read`
is granted, add `devices:read` and retest.

- Mint an environment-scoped integration with `threat-alerts:read`. Note the environment ID.
- The environment variable the caller sets is now `JAMF_CLIENT_SECRET`, holding the integration's
  secret. Where the script runs on macOS, `security find-generic-password -s "Jamf Platform API Integration" -w`
  populates it; anywhere else, the platform's secrets manager does. A script correct in isolation
  that depends on the old variable name fails on the first run.

**Changes.**

- Authentication. The JSON `{"client_id", "password"}` body against `/token` became the
  form-encoded client-credentials exchange against `/auth/token`. The response fields
  `access_token` and `expires_in` are the same on both, so the parse is unchanged. The
  `Authorization` header gained the `Bearer` prefix, which the gateway requires and the direct
  Protect API did not. One mint: the script makes two sequential calls and nothing loops.
- Credentials. `CLIENT_ID` keeps its name and holds a Jamf Account integration's client ID, not
  the Protect API client's. The secret is read from the environment as before; the variable is
  `JAMF_CLIENT_SECRET` because the value is now an integration secret rather than a Protect
  password.
- Routes. `/graphql` on the Protect host became `/protect` on the gateway. The document, its
  variables, and the parse path are unchanged.
- Error handling. `raise_for_status()` is unchanged. It was blind to Protect's errors inside
  HTTP 200 and still is. Over the gateway it now catches `403 BAD_PERMISSIONS`,
  `404 ENVIRONMENT_NOT_FOUND`, `400 REQUEST_CONTEXT_NOT_PROVIDED`, and `401`, which are real HTTP
  failures the product call never produced.

**Declined.** Nothing.

**Divergences.** The grant for the nested `computer` field, as noted above.

**Recommendations.** The script never tests `.errors`, so a grant gap or a schema error prints a
`KeyError` on `["data"]` rather than the message. Unchanged from the original. To surface it:

```python
body = r.json()
if body.get("errors"):
    raise SystemExit(body["errors"][0].get("message"))
```

## 4. A Go program on a beta-era Jamf Platform Go SDK

A nightly inventory export written against the SDK before GA. Tenant-scoped then; the admin is
minting the new integration at environment scope. Runs on a Linux automation host.

### Before

`go.mod`:

```text
require github.com/Jamf-Concepts/jamfplatform-go-sdk v0.16.1
```

`main.go`:

```go
package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/Jamf-Concepts/jamfplatform-go-sdk/jamfplatform"
	"github.com/Jamf-Concepts/jamfplatform-go-sdk/jamfplatform/devices"
)

func main() {
	client := jamfplatform.NewClient(
		"https://us.apigw.jamf.com/api",
		os.Getenv("JAMFPLATFORM_CLIENT_ID"),
		os.Getenv("JAMFPLATFORM_CLIENT_SECRET"),
		jamfplatform.WithTenantID(os.Getenv("JAMFPLATFORM_TENANT_ID")),
	)

	ctx := context.Background()
	ds, err := devices.New(client).ListDevices(ctx, nil, "")
	if err != nil {
		log.Fatal(err)
	}
	for _, d := range ds {
		fmt.Printf("%s,%s,%s\n", d.ID, d.Name, d.SerialNumber)
	}
}
```

### After

`go.mod`:

```text
require github.com/Jamf-Concepts/jamfplatform-go-sdk v0.23.0
```

`main.go`:

```go
package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/Jamf-Concepts/jamfplatform-go-sdk/jamfplatform"
	"github.com/Jamf-Concepts/jamfplatform-go-sdk/jamfplatform/devices"
)

func main() {
	client := jamfplatform.NewClient(
		"https://us.api.jamfcloud.com",
		os.Getenv("JAMFPLATFORM_CLIENT_ID"),
		os.Getenv("JAMFPLATFORM_CLIENT_SECRET"),
		jamfplatform.WithEnvironmentID(os.Getenv("JAMFPLATFORM_ENVIRONMENT_ID")),
	)

	ctx := context.Background()
	ds, err := devices.New(client).ListDevices(ctx, nil, "")
	if err != nil {
		log.Fatal(err)
	}
	for _, d := range ds {
		fmt.Printf("%s,%s,%s\n", d.ID, d.Name, d.SerialNumber)
	}
}
```

### Report

**Set up the integration.** Platform environment scope, as requested. The SDK sends
`X-Environment-Id` on every call and nothing on the token exchange.

The grants:

| Grant | Picker | Needed by |
| --- | --- | --- |
| `devices:read` | Inventory › Devices | `ListDevices`, which calls `GET /devices/v1/devices` |

- Mint an environment-scoped integration in Jamf Account with `devices:read`. Note the environment
  ID. The old tenant-scoped beta integration no longer exists; a program still carrying its values
  returns `401 {"error":"invalid_client"}` on the first call, which is also what a wrong secret
  returns. The Jamf Account integrations list settles which.
- In the nightly job's environment: replace the values of `JAMFPLATFORM_CLIENT_ID` and
  `JAMFPLATFORM_CLIENT_SECRET`, remove `JAMFPLATFORM_TENANT_ID`, and add
  `JAMFPLATFORM_ENVIRONMENT_ID`. A job that still sets the tenant variable and not the environment
  one starts the program with an empty scope and the gateway returns
  `400 REQUEST_CONTEXT_NOT_PROVIDED`.

**Changes.**

- Library. The SDK requirement moved from v0.16.1 to v0.23.0. Below v0.17.0 the SDK scoped requests
  by URL path and had no `WithEnvironmentID`; below v0.20.0 it targeted the retired gateway host.
  Run `go get github.com/Jamf-Concepts/jamfplatform-go-sdk@v0.23.0 && go mod tidy`.
- Base URL. `https://us.apigw.jamf.com/api` became `https://us.api.jamfcloud.com`, the gateway root
  with no path. The SDK appends the service slug and `/auth/token` itself; a base URL with a path
  sends the token exchange to a path the gateway does not serve.
- Scope. `WithTenantID` became `WithEnvironmentID`, because the new integration is minted at
  environment scope and the option has to match the credential. The environment variable it reads
  is `JAMFPLATFORM_ENVIRONMENT_ID`. Had the new integration been tenant-scoped, `WithTenantID` would
  have stayed with a replaced value.
- Credentials. `JAMFPLATFORM_CLIENT_ID` and `JAMFPLATFORM_CLIENT_SECRET` keep their names and hold
  a new integration's values. GA deleted the beta integration this program was built against.
- Routes, versions, response handling. None. `ListDevices` is the platform-native device list at
  `v1`, current, and the SDK pages it. The loop body is unchanged.

**Declined.** Nothing.

**Divergences.** None.

**Recommendations.** None. Token refresh and paging are the SDK's; the secret is already read from
the environment, which is the runtime form for a Linux host.
