# Jamf Protect over the gateway

The single endpoint, the error taxonomy, the published operations, and the coverage gate.

## The endpoint

```http
POST https://{region}.api.jamfcloud.com/protect
Content-Type: application/json
Authorization: Bearer <access_token>
X-Environment-Id: <environment UUID>      # or X-Tenant-Id, per the integration's scope
```

Body: `{"query": "<document>", "variables": {…}}`. Exactly that path, and nothing else. There is no
`graphql` segment, no `/api/` prefix, and no other Protect route. Because the operation name in the
body determines what runs, a lookup and a mutation are the same HTTP request shape.

| Request | Response |
| --- | --- |
| `POST /protect` with a valid scope header | `200`, GraphQL data or errors |
| `POST /protect` with no scope header | `400 REQUEST_CONTEXT_NOT_PROVIDED` |
| `POST /protect` with an unknown `X-Environment-Id` | `404 ENVIRONMENT_NOT_FOUND` |
| `POST /protect` with an unknown `X-Tenant-Id` | `403 OWNERSHIP_FORBIDDEN` |
| `POST /protect` with no credential | `401 unauthorized access` |
| `POST /protect/graphql`, `POST /protect/anything`, `GET /protect` | `403 BAD_PERMISSIONS` |
| `POST /api/protect` | plain-text `404` |

An environment-scoped integration reaches Protect for every tenant in the environment. The
published page advises minting a tenant-scoped integration if an operation returns 403 under
environment scope. Treat that as a fallback to try after checking the route and the grant, not as a
requirement: a Protect 403 is a routing or grant problem first.

Only the client-credentials flow authorizes Protect operations.

**The conversion is a transport change.** The schema over the gateway is the same schema. The
document, its variables, and every parse path in the response go across verbatim. Only the host,
the path, the `Authorization` shape, and the scope header move. A field selected in the document but
unused downstream stays selected; removing it changes what is asked for.

## Errors arrive inside HTTP 200

Every executed request returns 200. The distinction lives entirely in `.errors[0]`. A script that
branches on HTTP status reads a failed call as success, so the emitted script tests `.errors` on
every response.

| `errorType` and message | Means | Authorized? |
| --- | --- | --- |
| no `errors` key | The operation ran | yes |
| `AuthorizationError`, "Operation not permitted by tenant permissions." | Context resolved; this operation is not granted | **no** |
| `AuthorizationError`, "Could not verify tenant permissions." | Tenant context failed to resolve; hits every operation at once | inconclusive |
| `Validation error of type FieldUndefined` | The operation is not in the schema | not a permissions problem |
| `Validation error of type MissingFieldArgument` | The request shape is wrong; an argument is required | unknown, fix and retry |
| `NotFound` | The resolver ran and found no record | yes |
| `ArgumentValidationError` | The resolver ran and rejected the argument | yes |
| `Lambda:Unhandled` | The resolver ran and crashed | yes |

- **Only `AuthorizationError` is a denial.** `NotFound`, `ArgumentValidationError`, and
  `Lambda:Unhandled` all mean the resolver executed, which means authorization passed.
- **The two `AuthorizationError` messages mean opposite things.** Same `errorType`, same status.
  One is a per-operation grant gap, the other is a platform-side failure that clears on its own.
  Branching on `errorType` alone cannot tell them apart, so the emitted script reads `.message`.

**A miss is not a clean null.** `getComputer` against a UUID that does not exist returns
`Cannot return null for non-nullable type: 'ID' within parent 'Computer'`, with a `message` and no
`errorType`. `deleteComputer` against an already-deleted UUID does the same, with
`data.deleteComputer: null`. It reads like a schema bug rather than a miss. So the emitted script
tests `.errors` for non-emptiness **and** confirms the echoed identifier matches what was requested,
resolves by serial rather than by UUID, and checks for an empty `items` array.

## Operations and their capabilities

The published operation-to-capability table. Grants map to operation names, not paths, because there
is one path.

| Capability | Operations |
| --- | --- |
| `devices:read` | `getComputer`, `listComputers`, `requestComputerTimeline` |
| `devices:update` | `updateComputer`, `setComputerPlan` |
| `devices:delete` | `deleteComputer` |
| `users:read` | `listUsers` |
| `users:delete` | `deleteUser` |
| `protection-plans:read` | `getPlan`, `listPlans` |
| `detection-analytics:read` | `getAnalytic`, `listAnalytics` |
| `detection-analytics:update` | `updateAnalyticSet` |
| `threat-alerts:read` | `getAlert`, `listAlerts` |
| `threat-alerts:update` | `updateAlerts` |
| `prevent-lists:read` | `getPreventList`, `listPreventLists` |
| `prevent-lists:create` | `createPreventList` |
| `prevent-lists:update` | `updatePreventList` |
| `prevent-lists:delete` | `deletePreventList` |
| `threat-definition-versions:read` | `listThreatPreventionVersions` |
| `unified-logging-filters:read` | `getUnifiedLoggingFilter`, `listUnifiedLoggingFilters` |
| `unified-logging-filters:create` | `createUnifiedLoggingFilter` |
| `unified-logging-filters:update` | `updateUnifiedLoggingFilter` |
| `unified-logging-filters:delete` | `deleteUnifiedLoggingFilter` |
| `security-audit-log:read` | `listAuditLogsByDate`, `listAuditLogsByOp`, `listAuditLogsByUser` |

`devices:delete` exists only here. Every REST device-record deletion, on the platform, Pro, and
Classic surfaces alike, is `destructive-device-actions:execute`. A script that deletes a computer
from both Jamf Pro and Jamf Protect therefore needs both grants on the one integration, and the
read that resolves each identifier needs `devices:read` on top.

**A nested field's grant is not answerable from the published tables.** The tables cover operations
only. `computer { hostName }` selected inside `listAlerts` has no published grant of its own. Grant
the operation's capability, name the uncertainty in the report, and do not drop the field to make
the question go away.

Four operations exist in the schema with no published capability: `listBaselineRules`, which is
deprecated, has no capability, and is refused with `AuthorizationError`; and
`listUnifiedLoggingFilterSets`, `createUnifiedLoggingFilterSet`, and
`updateUnifiedLoggingFilterSet`, whose grant is not published. A script calling one of the filter-set
operations gets `unified-logging-filters` as the nearest capability and a named divergence.

## What exists over the gateway

The gateway schema publishes 34 operations: 20 queries, 14 mutations, no subscriptions. They are the
operations in the table above plus `listBaselineRules` and the three filter-set operations. That is
the whole of Protect's public API surface carried over, plus a slice of the console's: computers,
alerts, plans read-only, users read and delete, audit logs.

**Console operations have no gateway route.** Roles and API clients, analytics authoring, console
and dashboard queries, organization settings, groups, exception sets, USB control sets, telemetry,
action configs, insights and fleet compliance, plans authoring, and users authoring are absent from
the gateway schema. Sent to `POST /protect` they return `FieldUndefined`, meaning absent from the
schema rather than merely unauthorized. `/protect/app`, `/protect/v1/app`, and `/protect/console`
return the generic 403. This is the capability model: the missing areas have no capability slug
anywhere, so no grant could reach them. Roles and API clients move to Jamf Account.

**This is the conversion gate for a Protect script.** A script calling a console operation has
nothing to convert that call to. Where that call carries the script's purpose, decline the script;
where it is incidental, convert the rest and name what stayed and why. In both cases the direct
Protect API still answers, so the script has not stopped working.

To confirm an operation against the live schema when the tables above are in doubt, introspection
answers without any capability grant:

```bash
curl -sS -X POST "https://{region}.api.jamfcloud.com/protect" \
  -H "Authorization: Bearer $TOKEN" -H "X-Environment-Id: {environment-id}" \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ __schema { queryType { fields { name } } mutationType { fields { name } } } }"}'
```

Introspection is not filtered by permissions, so it says what the gateway *could* serve, not what
the integration may call. To test authorization for a query, select only `__typename` and read
`.errors[0]` against the table above. Never probe a mutation; every one changes or deletes data.

## Operation-name traps

- **Capability slugs do not predict operation names.** `protection-plans` guards `listPlans`, not
  `listProtectionPlans`; `threat-definition-versions` guards `listThreatPreventionVersions`. A
  guess produces `FieldUndefined`, a schema error that looks nothing like a permissions error.
- **`listAlerts` requires its `input` argument** even though every field inside `AlertQueryInput` is
  optional. `{ listAlerts { … } }` is `MissingFieldArgument`; `listAlerts(input: { pageSize: 1 })`
  runs. The other `list*` operations take `input` optionally.
- **Unified logging filters and filter sets are two object types with near-identical names,** and
  the schema is asymmetric. Filters have get, list, create, update, and delete. Filter sets have
  only list, create, and update: there is no `deleteUnifiedLoggingFilterSet` and no
  `getUnifiedLoggingFilterSet`. Dropping or adding `Set` silently targets the other type where both
  exist and produces `FieldUndefined` where only one does.
- **Two trace IDs.** `x-tyk-trace-id` is the gateway hop; `x-amzn-requestid` is the Protect
  backend. Quote both when reporting a Protect issue.
