# Skyward Qmlativ — API Reference for Connect Action Sets

## Authentication — `defineSkywardQmlativOAuthConnection`

POSTs to `{Global.skywardBaseURL}/oauth/token` with:
- `Authorization: Basic <base64(clientID:clientSecret)>`
- `Content-Type: application/x-www-form-urlencoded`
- `Skyward-Integration-Token: <skywardIssuedSecret>` — **required**; Skyward-issued partner token embedded in the action set, not a customer secret
- Body: `grant_type=client_credentials`

Returns the OAuth response data object (contains `access_token`) on success, `false` on failure.

**Args:**

| Arg | Type | Required | Notes |
|---|---|---|---|
| `clientID` | password | Yes | OAuth2 client ID ("Key" from Qmlativ Integration Access) |
| `clientSecret` | password | Yes | OAuth2 client secret |
| `url` | string | Yes | Skyward base URL (from `Global.skywardBaseURL`) |
| `integrationType` | enum: `default`, `Washington` | No | State-specific token variant |

**⚠️ Known issue in captured version:** An unconditional `setVariable` always overrides to the default integration token (making the Washington variant dead code), and an early `return` fires before the `httpPOST`. Verify the production version in your Connect environment has these removed.

---

## Workers API — `FnRetrieveQmlativEmployeeRecords`

**Returns:** Record map keyed by `NameIDNumber.NameIDNumber`, or `false` on failure.

**Endpoint pattern:**
```
GET {Global.qmlativAPI}/custom/1/{module}/{object}/{pageNumber}/{pageSize}
    ?searchFields=EmployeeDistrict.isActive
    &searchFields=Name.FirstName
    &searchFields=...
Authorization: Bearer {session}
```

**Args:**

| Arg | Type | Required | Notes |
|---|---|---|---|
| `session` | string | No | Bearer token. Opens via `FnOpenConnections("Skyward - Qmlativ")` if not provided. |
| `module` | enum:Employee | No | Qmlativ module name (e.g. `Employee`) |
| `object` | enum:Employee | No | Qmlativ object name (e.g. `Employee`) |

**Pagination:** Uses `Paging.Next` cursor from the response — not offset math. Page size 1000. Loop until `Paging.Next` is null/absent.

**Response shape:**
```json
{
  "statusCode": 200,
  "data": {
    "Objects": [ { "Name": { "FirstName": "Jane", ... }, "NameIDNumber": { "NameIDNumber": "12345" }, ... } ],
    "Paging": { "Next": "/custom/1/Employee/Employee/2/1000?..." }
  }
}
```

**Output record map** keyed by personnel number:
```json
{ "12345": { "EmployeeDistrict": { "isActive": true }, "Name": { "FirstName": "Jane" }, "NameIDNumber": { "NameIDNumber": "12345" } } }
```

Also serialized to `/output/Qmlativ/QmlativEmployees.json`.

---

## Single-Record Lookup — `FnRetrieveQmlativEmployeeRecordsWithID`

Same as above but adds `personnelNumber` arg (required). Iterates all pages until it finds the match, then returns early with a single-entry record map. **Performance note:** Still iterates all pages — no server-side filter. Use `FnRetrieveQmlativEmployeeRecords` once and look up in-memory if multiple lookups are needed.

---

## Required Global Variables

| Global | Purpose |
|---|---|
| `SharedGlobal.skywardBaseURL` | Skyward base URL, e.g. `https://district.skyward.com/api/` |
| `SharedGlobal.qmlativAPI` | Custom API base URL (set by `FnOpenConnections` from `skywardBaseURL`) |
| `SharedGlobal.skywardClientID` | OAuth Client ID ("Key" from Integration Access) |
| `SharedGlobal.skywardClientSecret` | OAuth Client Secret — must be `decrypt(...)` value |

---

## Gotchas

- **`Global.qmlativAPI` must be set** before calling retrieval functions — if null, all API calls fail silently
- **Module and object args must match** Qmlativ's Custom API entity access configuration. Wrong values return empty results, not errors.
- **`NameIDNumber.NameIDNumber` is required** — records missing this field are silently skipped. If employees are disappearing, verify this field is in scope for the integration's Custom API entity access.
- **Pagination uses next-link cursors**, not offset math. Do not assume offset = page × size.
- **Integration token is Skyward-issued** — it is embedded in the action set, not a customer credential. Do not expose it in logs.
