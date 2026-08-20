# Oracle Fusion Cloud HCM — API Reference for Connect Action Sets

## Authentication

### Basic Auth

```xml
<action name="setVariable">
  <arg name="name" value="oracleAuthHeader"/>
  <arg name="value" value="&quot;Basic &quot; + btoa(Global.oracleUser + &quot;:&quot; + Global.oraclePwd)"/>
</action>
```

Passed as `Authorization` header on every request. All credentials from `Global.*` — never hardcode.

### OAuth 2.0 Client Credentials

Token endpoint: `POST https://<hostname>/oauth2/v1/token`

```xml
<action name="httpPOST" outputVar="tokenResponse">
  <arg name="url" value="Global.oracleHost + &quot;/oauth2/v1/token&quot;"/>
  <arg name="headers" value="{&quot;Content-Type&quot;:&quot;application/x-www-form-urlencoded&quot;}"/>
  <arg name="data" value="&quot;grant_type=client_credentials&amp;client_id=&quot; + Global.oracleClientId + &quot;&amp;client_secret=&quot; + Global.oracleClientSecret + &quot;&amp;scope=&quot; + Global.oracleScope"/>
</action>
<action name="setVariable">
  <arg name="name" value="oracleBearerToken"/>
  <arg name="value" value="tokenResponse.data.access_token"/>
</action>
```

Token expires in `expires_in` seconds (typically 3600). Refresh before expiry.

**Auth failures:**
| Symptom | Cause |
|---|---|
| 401 | Wrong credentials, locked account, or MFA blocking Basic Auth |
| 200 with empty `items` | Auth succeeded but data security profile excludes target workers |
| 403 | Account lacks required function security role |
| Token endpoint 400 | Wrong `grant_type` or `scope` |

---

## Workers API

```
GET https://<hostname>/hcmRestApi/resources/11.13.18.05/workers
```

### Key Query Parameters

| Parameter | Notes |
|---|---|
| `limit` | Records per page. Max 500. Default 25. Always use 500. |
| `offset` | 0-based pagination offset |
| `expand` | Comma-separated child resources: `assignments`, `communications`, `addresses`, `phones` |
| `fields` | Projection — comma-separated fields to return. Reduces payload. |
| `q` | SCIM-style filter (e.g. `assignments.AssignmentStatusType=ACTIVE_ASSIGN`) |
| `onlyData` | `true` strips HATEOAS links — reduces payload ~20–40%. Always use. |
| `effectiveDate` | `YYYY-MM-DD`. Defaults to today. |

**Minimal active-workers request:**
```
GET /hcmRestApi/resources/11.13.18.05/workers?limit=500&expand=assignments&onlyData=true
```

### Key Response Fields

| Field | Notes |
|---|---|
| `PersonId` | Oracle internal integer ID — stable. Use as correlation key. |
| `PersonNumber` | Human-readable employee number — may also be stable |
| `FirstName`, `LastName`, `MiddleName` | Name fields |
| `assignments[].PrimaryFlag` | **Filter to `true`** — persons can have multiple assignments |
| `assignments[].AssignmentStatusType` | `ACTIVE_ASSIGN` = active; `INACTIVE_ASSIGN`, `ACTIVE_NO_WORK`, `SUSPENDED` = disabled |
| `assignments[].WorkerType` | `E` = employee, `C` = contingent worker |
| `assignments[].JobCode`, `JobName` | Position/role |
| `assignments[].DepartmentName` | Department |
| `assignments[].EffectiveEndDate` | `4712-12-31` = no end date (still active) |
| `assignments[].ManagerId` | Manager's `PersonId` — requires second lookup for name/email |
| `communications[].EmailAddress` | Email address |
| `communications[].PrimaryFlag` | Filter to `true` for primary email |

### Pagination Loop

```xml
<action name="setVariable"><arg name="name" value="oracleOffset"/><arg name="value" value="0"/></action>
<action name="setVariable"><arg name="name" value="oraclePageSize"/><arg name="value" value="500"/></action>
<action name="setVariable"><arg name="name" value="oracleHasMore"/><arg name="value" value="true"/></action>

<action name="while">
  <arg name="condition" value="oracleHasMore"/>
  <arg name="do">
    <action name="httpGET" outputVar="apiResponse">
      <arg name="url" value="Global.oracleHost + &quot;/hcmRestApi/resources/11.13.18.05/workers?limit=&quot; + oraclePageSize + &quot;&amp;offset=&quot; + oracleOffset + &quot;&amp;expand=assignments&amp;onlyData=true&quot;"/>
      <arg name="headers" value="{&quot;Authorization&quot;:&quot;Basic &quot; + oracleAuthHeader, &quot;Accept&quot;:&quot;application/json&quot;}"/>
    </action>
    <!-- process apiResponse.data.items -->
    <action name="setVariable"><arg name="name" value="oracleHasMore"/><arg name="value" value="apiResponse.data.hasMore"/></action>
    <action name="setVariable"><arg name="name" value="oracleOffset"/><arg name="value" value="oracleOffset + oraclePageSize"/></action>
  </arg>
</action>
```

---

## Key Gotchas

- **Always filter to `PrimaryFlag: true`** on assignments and communications — multiple records per person otherwise
- **`4712-12-31` is the active-sentinel** for `EffectiveEndDate`. Don't compare to today without handling this explicitly.
- **`ACTIVE_NO_WORK`** is ambiguous — confirm with customer whether these should be provisioned or disabled
- **Empty `items` with 200** = data security configuration issue, not an API error
- **Assignments on the response require `expand=assignments`** — not included by default
- **Manager resolution requires a second lookup** — `ManagerId` is a `PersonId`, not a username or DN
- **Rate limits:** No published limits, but Oracle throttles at tenant level. Use `limit=500`. Add short delays between pages for large datasets. Retry on 429/503.

---

## Relevant Global Variables

Store all of these in `SharedGlobals.properties` (or `Globals.properties` for per-project overrides):

| Global Key | Purpose |
|---|---|
| `Global.oracleHost` | Base URL, e.g. `https://tenant.fa.oraclecloud.com` |
| `Global.oracleUser` | Basic Auth username (service account) |
| `Global.oraclePwd` | Basic Auth password — must be `decrypt(...)` value |
| `Global.oracleClientId` | OAuth2 client ID |
| `Global.oracleClientSecret` | OAuth2 client secret — must be `decrypt(...)` value |
| `Global.oracleScope` | OAuth2 scope |
