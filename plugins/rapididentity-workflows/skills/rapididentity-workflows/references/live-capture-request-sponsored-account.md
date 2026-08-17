# Live capture — "Request Sponsored Account" (sandbox tenant)

Captured 2026-07-28 via `GET /api/rest/admin/workflow/workflowDefinitions/176f6c88-3393-4d89-9540-c95bf922336b`
(riadmin `requests_get_workflow_definition`, sandbox tenant, definition version 4). This is the
ground truth for field names in this skill — when a doc and this capture disagree, this capture
wins. HTML email bodies are elided (`...`) for size; every field name and structure is verbatim.

## Top level

```json
{
  "id": "176f6c88-3393-4d89-9540-c95bf922336b",
  "dn": "CN=176f6c88-3393-4d89-9540-c95bf922336b,OU=workflows",
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
  "id": "96605ef5-7b46-484b-8d5b-821aff00a946",
  "name": "Validate Account",
  "description": "Ensure account is valid to be created",
  "dssUrl": "",
  "username": "",
  "trace": true,
  "actionName": "sandbox.WFMCreateSponsoredAccount",
  "valuePairs": [
    "givenname='%{form.givenname}'",
    "sn='%{form.sn}'",
    "requestcomments='%{request.comments}'",
    "requesteremail='%{requester.mail}'",
    "manager='%{recipient.dn}'",
    "validateOnly='true'",
    "approvercomments='%{approval0.comments}'"
  ],
  "nextActionId": "1b394b7e-e36a-447d-8393-5c8f676d5933"
}
```

## conditionAction (verbatim)

```json
{
  "type": "conditionAction",
  "id": "1b394b7e-e36a-447d-8393-5c8f676d5933",
  "name": "If Valid Account",
  "operand1": "%{dss.success}",
  "operation": "MATCHES_ANY_REGEX",
  "operand2": "true",
  "onTrueActionId": "ef501e2d-e2e3-4255-ad6c-c9be46ba72ba",
  "onFalseActionId": "41510ea2-5660-4502-84ac-f2d989cf18fa"
}
```

## emailAction (body elided — full HTML with inline CSS in the real definition)

`toList` + `message` + `isHtml`/`isCritical` — NOT `to`/`body`:

```json
{
  "type": "emailAction",
  "id": "99eb7874-0dc4-49da-b4e7-104da3e223c7",
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
  "id": "ef501e2d-e2e3-4255-ad6c-c9be46ba72ba",
  "name": "Approval",
  "description": "Creates approval request for department head of the workflow requestor.",
  "approver": {
    "type": "groupApprover",
    "group": {
      "id": "875e4248-0aea-4f09-8197-363f47735837",
      "dn": "idautoID=875e4248-0aea-4f09-8197-363f47735837,ou=Groups,dc=meta",
      "name": "Portal Sponsor"
    }
  },
  "expirationDays": -1,
  "escalationDays": -1,
  "onApproveId": "0821098e-5fed-4b8a-b647-7f04eb8bc266",
  "onDenyId": "c55c6392-1188-4856-93a8-838bd873cd5c"
}
```

## forms (verbatim, two representative items of eight)

Items carry `name` (no separate id field); `requiredActionIds` lists both `start` and the
approval action's id; optional fields use `editableActionIds` instead; `LIST` items have
`listElements` of `{displayValue, value}`; the date field type is `DATE_TIME`:

```json
"forms": [
  {
    "id": "bd3e7470-52c7-4f7e-9bf9-9248098fdeab",
    "displayName": "Request Sponsored Account",
    "workflowFormItems": [
      {
        "name": "givenname",
        "displayName": "First Name",
        "type": "STRING",
        "hideFromRecipient": false,
        "listElements": [],
        "requiredActionIds": ["start", "ef501e2d-e2e3-4255-ad6c-c9be46ba72ba"],
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
        "requiredActionIds": ["start", "ef501e2d-e2e3-4255-ad6c-c9be46ba72ba"],
        "editableActionIds": [],
        "hiddenActionIds": []
      }
    ]
  }
]
```

Other item types seen in this form: `DATE_TIME` (`idautopersonenddate`, "When does access end?").
An `ATTACHMENT` type item was confirmed in a separate live capture (riadmin backlog #31).
