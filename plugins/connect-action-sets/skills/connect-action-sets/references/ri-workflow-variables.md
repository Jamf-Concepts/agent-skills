# RapidIdentity — Workflow Variable Substitution Reference

`%{...}` tokens resolve at workflow execution time. Used in `valuePairs`, email body/subject, and `conditionAction` operands. For use when authoring WFM action sets and workflow definitions.

## Variable Substitution Table

| Token | Resolves to |
|---|---|
| `%{form.<fieldname>}` | Form field value submitted by the requester |
| `%{requester.dn}` | LDAP DN of the user who submitted the request |
| `%{requester.mail}` | Email address of the requester |
| `%{requester.givenname}` | Requester first name |
| `%{requester.sn}` | Requester last name |
| `%{recipient.dn}` | LDAP DN of the target identity |
| `%{recipient.mail}` | Email address of the target identity |
| `%{approval0.approver.dn}` | DN of the user who acted on the first approval step |
| `%{dss.success}` | `true` / `false` — whether the last DSS action set call succeeded |
| `%{dss.result}` | Return value string from the last DSS action set call |
| `%{request.id}` | UUID of the current workflow request |
| `%{requestor.comments}` | Comments entered by the requester at submission |

> **Note:** `%{requester.*}` and `%{requestor.*}` are both in production — both spellings work. Prefer `%{requester.*}` for new work.

---

## DSS valuePairs Format

`valuePairs` entries are `key='value'` strings, one per array element. The value is single-quoted and supports `%{...}` tokens:

```json
"valuePairs": [
  "givenname='%{form.givenname}'",
  "sn='%{form.sn}'",
  "validateOnly='true'",
  "sponsorDN='%{requester.dn}'"
]
```

- `dssUrl: ""` — Empty string means the local Connect instance.
- `actionName` — Format is `projectName.ActionSetName` (e.g. `"WFMCreateSponsoredAccount"` for `<Main>` project).
- `trace: true` — Enable Connect trace logging for this action call.

---

## WFM Action Set Return Contract

WFM action sets called by `dssAction` or `advancedDssAction` must return a JSON string. The workflow reads fields via `%{dss.<fieldname>}`.

Standard required fields:

```xml
<action name="createRecord" outputVar="results"/>
<action name="setRecordFieldValue"><arg name="record" value="results"/><arg name="field" value="&quot;success&quot;"/><arg name="value" value="false"/></action>
<action name="setRecordFieldValue"><arg name="record" value="results"/><arg name="field" value="&quot;message&quot;"/><arg name="value" value="&quot;&quot;"/></action>
```

Return via: `<action name="return"><arg name="value" value="toJSON(results)"/></action>`

After a `dssAction` with `resultValidationRegex: "true"`, the workflow succeeds only if the return value matches the regex. Use `advancedDssAction` + a `conditionAction` on `%{dss.success}` when you need to branch on success/failure explicitly.

---

## WFM Action Set argDefs

Standard argDefs for every WFM action set:

```xml
<argDefs>
  <argDef name="logOnly"      type="boolean" optional="true" description="Suppress writes when true."/>
  <argDef name="logLevel"     type="enum:quiet,normal,debug" optional="true" description="Logging verbosity."/>
  <argDef name="validateOnly" type="boolean" optional="true" description="Validate all inputs and return without writing when true."/>
</argDefs>
```

Every WFM action set **must return from every exit path** — there must be no code path that exits without calling `return toJSON(results)`.

---

## Form Field Types

| Type | Notes |
|---|---|
| `STRING` | Plain text |
| `INTEGER` | Whole number |
| `BOOLEAN` | `true` / `false` |
| `DATE` | ISO 8601 date. Workflow emits as full timestamp (`2026-05-01T01:24:14.000Z`) — use `.substring(0,10)` to get `YYYY-MM-DD` |
| `DATE_TIME` | ISO 8601 datetime |
| `LIST` | Dropdown — values from `listElements` array |
| `USER` | User picker — value is the selected user's DN |
| `GROUP` | Group picker — value is the selected group's DN |
| `FILE_ATTACHMENT` | File upload |

`DATE_TIME` form fields: always trim to `YYYY-MM-DD` when passing to APIs that expect a plain date:
```xml
<arg name="value" value="toJSON({expirationDate: (dateField ? dateField.substring(0,10) : null)})"/>
```
