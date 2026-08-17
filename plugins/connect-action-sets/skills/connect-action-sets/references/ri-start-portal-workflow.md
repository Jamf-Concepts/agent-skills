# RapidIdentity Connect — `startPortalWorkflow` Built-in Action

`startPortalWorkflow` programmatically submits a WFM workflow request from within a Connect
action set. It is the Connect equivalent of a user clicking "Request" in the portal.

---

## Signature

```xml
<action name="startPortalWorkflow" outputVar="result">
  <arg name="connection"   value="sessionPortal"/>
  <arg name="type"         value="&quot;GRANT&quot;"/>
  <arg name="recipientId"  value="someUser.idautoID"/>
  <arg name="entitlementId" value="&quot;424c2500-c58e-4d2e-be0f-15c5ed3e1b7b&quot;"/>
  <arg name="formData"     value="formRecord"/>
</action>
```

### Parameters

| Arg | Type | Required | Notes |
|---|---|---|---|
| `connection` | portal session | Yes | Session from `defineCloudPortalConnection` or `FnOpenConnections` with `target="Portal"` |
| `type` | string | Yes | Request type — `"GRANT"` is the standard value for entitlement/access requests |
| `recipientId` | string | Yes | The `idautoID` of the person who will receive the entitlement (the subject) |
| `entitlementId` | string | Yes | UUID of the WFM resource/entitlement to request — **hardcoded per workflow** (see note below) |
| `formData` | Record | No | A Connect `Record` whose fields map to the workflow form fields. Key names must match the form field names as defined in the workflow definition |

### Return value

`result` is truthy on success (a request ID or similar response object), falsy on failure. Branch on `result` directly:

```xml
<action name="if">
  <arg name="condition" value="result"/>
  <arg name="then"><!-- success --></arg>
  <arg name="else"><!-- failure --></arg>
</action>
```

---

## Required session

`startPortalWorkflow` requires a **portal session** (not an LDAP session). Obtain via
`defineCloudPortalConnection` (manifest pattern) or via a project-local `FnOpenConnections`
with `target="Portal"`.

The LDAP metadirectory session (`sessionRI`) is used only to resolve LDAP attributes needed
to build `recipientId` and `formData` — it is not passed to `startPortalWorkflow` itself.

---

## `entitlementId` — how to find it

The `entitlementId` is the UUID of a WFM resource record, visible in the RI admin portal under
Workflow Manager > Resources. It is stable per tenant but **not portable across tenants** —
always parameterize it via a Global variable rather than hardcoding in the action set body:

```xml
<arg name="entitlementId" value="Global.wfmCertifySponsoredEntitlementId"/>
```

---

## `formData` — preparing the Record

`formData` is a Connect `Record` (from `createRecord` / `copyRecord`). Field names must exactly
match the workflow form field names. Use `filterRecordFields` to strip fields the form does not
expect, and `renameRecordFields` if the LDAP attribute name differs from the form field name.

Pattern from `AltAction_CertifySponsored`:

```xml
<!-- 1. Build the record (copy from an existing record or create fresh) -->
<action name="copyRecord" outputVar="formRecord">
  <arg name="record" value="record"/>
</action>

<!-- 2. Strip to only the fields the form expects -->
<action name="filterRecordFields">
  <arg name="record" value="formRecord"/>
  <arg name="fields" value="&quot;sponsored_dn,displayname,idautoid,idautopersonenddate&quot;"/>
</action>

<!-- 3. Rename any field whose LDAP name differs from the form field name -->
<action name="renameRecordFields">
  <arg name="record" value="formRecord"/>
  <arg name="oldFields" value="&quot;idautoPersonEndDate&quot;"/>
  <arg name="newFields" value="&quot;idautopersonenddate&quot;"/>
</action>

<!-- 4. Submit -->
<action name="startPortalWorkflow" outputVar="result">
  <arg name="connection"    value="sessionPortal"/>
  <arg name="type"          value="&quot;GRANT&quot;"/>
  <arg name="recipientId"   value="perpRecord.idautoID"/>
  <arg name="entitlementId" value="Global.wfmCertifySponsoredEntitlementId"/>
  <arg name="formData"      value="formRecord"/>
</action>
```

---

## Relationship to `startTask` (WFMPortal API)

`startPortalWorkflow` is the **Connect built-in action** for server-side workflow submission.
The WFMPortal REST API's `POST /api/rest/workflow/startTask` is the equivalent call made from
browser JavaScript (via `httpPOST` in a Connect gateway action set). Both submit a GRANT
request to the same WFM engine. Use `startPortalWorkflow` in background/scheduled action sets;
use `startTask` when proxying a browser-initiated request through the RESTPoint gateway.

---

## Common use cases

- **Alternate Actions (AA):** Trigger a workflow automatically when a portal event fires
  (e.g. certify a sponsored account as part of an AA hook on the sponsored account detail page)
- **Scheduled/batch jobs:** Programmatically submit requests for a set of users (e.g. bulk
  re-certification, auto-enrollment)
- **Connect-driven onboarding:** Submit an access request for a new hire immediately after
  their LDAP account is created, before they log in for the first time

---

## Full skeleton

```xml
<!-- Prereq: sessionPortal from defineCloudPortalConnection -->
<!-- Prereq: sessionRI from openMetadirLDAPConnection, for LDAP lookups -->

<!-- 1. Resolve the recipient and any needed LDAP attributes -->
<action name="getLDAPRecord" outputVar="targetRecord">
  <arg name="ldapConnection" value="sessionRI"/>
  <arg name="dn" value="targetDN"/>
  <arg name="attributes" value="&quot;idautoID,displayName&quot;"/>
</action>

<!-- 2. Build formData Record -->
<action name="createRecord" outputVar="formRecord"/>
<action name="setRecordFieldValue">
  <arg name="record" value="formRecord"/>
  <arg name="field" value="&quot;displayname&quot;"/>
  <arg name="value" value="targetRecord.displayName"/>
</action>
<!-- ... add other form fields ... -->

<!-- 3. Submit workflow -->
<action name="if">
  <arg name="condition" value="!logOnly"/>
  <arg name="then">
    <action name="startPortalWorkflow" outputVar="wfResult">
      <arg name="connection"    value="sessionPortal"/>
      <arg name="type"         value="&quot;GRANT&quot;"/>
      <arg name="recipientId"  value="targetRecord.idautoID"/>
      <arg name="entitlementId" value="Global.wfmTargetEntitlementId"/>
      <arg name="formData"     value="formRecord"/>
    </action>
    <action name="if">
      <arg name="condition" value="wfResult"/>
      <arg name="then">
        <action name="log"><arg name="message" value="&quot;Workflow started for &quot; + targetRecord.displayName"/><arg name="color" value="&quot;green&quot;"/></action>
      </arg>
      <arg name="else">
        <action name="log"><arg name="message" value="&quot;Workflow FAILED for &quot; + targetRecord.displayName"/><arg name="color" value="&quot;red&quot;"/></action>
      </arg>
    </action>
  </arg>
</action>
```

---

## Source

Confirmed from `AltAction_CertifySponsored.xml` (Alternate Action — certifies a sponsored
account by submitting a GRANT request to a specific WFM entitlement). The `entitlementId`
`424c2500-c58e-4d2e-be0f-15c5ed3e1b7b` in that file is tenant-specific and should not be
reused; always resolve via a Global variable.
