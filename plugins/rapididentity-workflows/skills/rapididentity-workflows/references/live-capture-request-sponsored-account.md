# Live capture — "Request Sponsored Account" (sandbox tenant)

Captured 2026-07-28 via `GET /api/rest/admin/workflow/workflowDefinitions/00000000-0000-4000-a000-000000000001`
(sandbox tenant, definition version 4). This is the
ground truth for field names in this skill — when a doc and this capture disagree, this capture
wins. HTML email bodies are elided (`...`) for size; every field name and structure is verbatim.

## Top level

```json
{
  "id": "00000000-0000-4000-a000-000000000001",
  "dn": "CN=00000000-0000-4000-a000-000000000001,OU=workflows",
  "version": 4,
  "name": "Request Sponsored Account",
  "description": "Request a Sponsored account with approval from Portal Sponsor users.",
  "status": "ACTIVE",
  "actions": [ ... 13 actions ... ],
  "forms": [ ... 1 form ... ]
}
```

## advancedDssAction (verbatim except valuePairs elided mid-list)

Note the project-qualified `actionName` and the `dssUrl`/`username`/`trace` fields:

```json
{
  "type": "advancedDssAction",
  "id": "00000000-0000-4000-a000-000000000002",
  "name": "Validate Account",
  "description": "Ensure account is valid to be created",
  "dssUrl": "",
  "username": "",
  "trace": true,
  "actionName": "sandbox.WFMValidateAccount",
  "valuePairs": [
    "givenname='%{form.givenname}'",
    "sn='%{form.sn}'",
    "requestcomments='%{request.comments}'",
    "requesteremail='%{requester.mail}'",
    "manager='%{recipient.dn}'",
    "validateOnly='true'",
    "approvercomments='%{approval0.comments}'"
  ],
  "nextActionId": "00000000-0000-4000-a000-000000000003"
}
```

## conditionAction (verbatim)

```json
{
  "type": "conditionAction",
  "id": "00000000-0000-4000-a000-000000000003",
  "name": "If Valid Account",
  "operand1": "%{dss.success}",
  "operation": "MATCHES_ANY_REGEX",
  "operand2": "true",
  "onTrueActionId": "00000000-0000-4000-a000-000000000004",
  "onFalseActionId": "00000000-0000-4000-a000-000000000005"
}
```

## emailAction (body elided — full HTML with inline CSS in the real definition)

`toList` + `message` + `isHtml`/`isCritical` — NOT `to`/`body`:

```json
{
  "type": "emailAction",
  "id": "00000000-0000-4000-a000-000000000006",
  "name": "Send Welcome Email",
  "description": "Send a welcome email to the new user using the idautopersonhomeemail value",
  "from": "noreply@rapididentity.com",
  "toList": ["%{form.idautopersonhomeemail}"],
  "subject": "Welcome to RapidIdentity",
  "message": "<!DOCTYPE html><html lang=\"en\">...</html>",
  "isHtml": true,
  "isCritical": false,
  "nextActionId": "end"
}
```

## approvalAction (verbatim)

```json
{
  "type": "approvalAction",
  "id": "00000000-0000-4000-a000-000000000004",
  "name": "Approval",
  "description": "Creates approval request for department head of the workflow requestor.",
  "approver": {
    "type": "groupApprover",
    "group": {
      "id": "00000000-0000-4000-a000-000000000007",
      "dn": "idautoID=00000000-0000-4000-a000-000000000007,ou=Groups,dc=meta",
      "name": "Portal Sponsor"
    }
  },
  "expirationDays": -1,
  "escalationDays": -1,
  "onApproveId": "00000000-0000-4000-a000-000000000008",
  "onDenyId": "00000000-0000-4000-a000-000000000009"
}
```

## forms (verbatim, two representative items of eight)

Items carry `name` (no separate id field); `requiredActionIds` lists both `start` and the
approval action's id; optional fields use `editableActionIds` instead; `LIST` items have
`listElements` of `{displayValue, value}`; the date field type is `DATE_TIME`:

```json
"forms": [
  {
    "id": "00000000-0000-4000-a000-00000000000a",
    "displayName": "Request Sponsored Account",
    "workflowFormItems": [
      {
        "name": "givenname",
        "displayName": "First Name",
        "type": "STRING",
        "hideFromRecipient": false,
        "listElements": [],
        "requiredActionIds": ["start", "00000000-0000-4000-a000-000000000004"],
        "editableActionIds": [],
        "hiddenActionIds": []
      },
      {
        "name": "idautopersonemployeetypes",
        "displayName": "Account Type",
        "type": "LIST",
        "hideFromRecipient": false,
        "listElements": [
          { "displayValue": "Charter", "value": "Charter" },
          { "displayValue": "Contractor", "value": "Contractor" },
          { "displayValue": "Service", "value": "Service" },
          { "displayValue": "Shared", "value": "Shared" },
          { "displayValue": "Vendor", "value": "Vendor" },
          { "displayValue": "Other", "value": "Other" }
        ],
        "requiredActionIds": ["start", "00000000-0000-4000-a000-000000000004"],
        "editableActionIds": [],
        "hiddenActionIds": []
      }
    ]
  }
]
```

Other item types seen in this form: `DATE_TIME` (`idautopersonenddate`, "When does access end?").
An `ATTACHMENT` type item was confirmed in a separate live capture.
