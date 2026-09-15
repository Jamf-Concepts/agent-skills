# Capability grants

The grant format, how the grant for a call is resolved, the bundled picker table, and the bridges
from old privilege names and beta grant strings. The grant list in the report is built from this
file against the endpoints the converted script actually emits.

## Format

```text
{capability}:{action}
```

The capability is kebab-case and carries no product name, because one capability is reached by
endpoints across several products. Six actions exist, lowercase and case-sensitive: `create`,
`read`, `update`, `delete`, `deploy`, `execute`. The permissions map abbreviates them `c`, `r`,
`u`, `d`, `dep`, `x` in its capability rows, but a grant string always carries the full word.

Actions do not imply one another. `devices:update` covers writes only, so a script that reads a
record before modifying it needs `devices:read` as well. Every action the script's calls use is
granted.

## Resolving the grant for a call

**Resolve against the endpoints actually emitted, never the ones replaced.** A cross-surface move
can change the grant set, including dropping a grant: the Classic mobile-device update publishes
`devices:update` and `users:update`, while the Pro detail `PATCH` writing the same user-and-location
fields publishes `devices:update` alone. The grant list describes the output script.

**One capability covering calls on two products is one grant.** `devices:read` on a Jamf Pro
inventory read and on a Protect `listComputers` is one row in the report, not two.

### Live lookup: two pages, two questions

Where the network is available, read the grant off the published surface. Pull each page with
`curl -sSL` on its `.md` or `llms.txt` URL, per `conversion-rules.md`, "Pulling a page"; a
summarizing fetch tool is a last resort and nothing it reports is confirmed until the endpoint page
agrees. Two pages per endpoint, because they answer different questions:

1. **The category index** gives the grant a specific endpoint requires and which versions of that
   path exist. `https://developer.jamf.com/platform-api/reference/{category}/llms.txt`, where
   `{category}` is `jamf-pro`, `jamf-pro-classic`, `device-inventory`, `device-groups`,
   `device-management-actions`, `blueprints`, `compliance-benchmarks`, `declaration-reporting`,
   `audit`, `security-cloud-devices`, `security-cloud-categories`, `security-cloud-dns`,
   `security-cloud-enrollment`, `uem-connect`, or `ztna`. Each entry carries
   `**Required Permissions:**` inline. Match the endpoints the script names; one fetch per surface
   the script touches. Titles can wrap across lines, so read the entry, not a line-oriented grep of
   it.
2. **The endpoint's own page** gives which of those versions is current.
   `https://developer.jamf.com/platform-api/reference/{slug}.md`, where the slug comes from the
   index link. The index carries no deprecation flag, so a deprecated version sits in it looking
   identical to its successor. The page's OpenAPI block carries `deprecated` and
   `x-deprecation-date`, plus `x-required-privileges` as an array: the same grant as the prose
   string, machine-readable, and a free corroboration when the prose is ambiguous. More than one
   entry in the array means all are required. It also carries `x-required-privileges-legacy`, the
   old Jamf Pro privilege display name; see the bridges below.

Pace the requests. A burst is answered with a Cloudflare challenge page at HTTP 200, so a fetch can
fail while looking like it succeeded, and a grant read off a challenge page is an invented name an
admin cannot find in the picker. An endpoint page is real when its body opens with `---`
frontmatter. A category index has no frontmatter and is real when it carries
`**Required Permissions:**` entries. A body with neither is discarded and the bundled rules below
apply to that call, with the report saying so.

A missing `x-required-privileges` means unspecified, not "no grant needed." The three
unauthenticated endpoints are listed under **Endpoints with no permission** below.

Conversion never fails on a fetch. Only grant-list precision improves when there is one.

### Offline rules

Cases a reading of the capability row gets wrong:

- **REST device-record deletion is `destructive-device-actions:execute`** on the platform, Pro, and
  Classic surfaces alike. `devices:delete` occurs on no REST endpoint and exists only on Protect's
  `deleteComputer` mutation. A script deleting a computer from both products needs both.
- **A capability that reads a stored secret is separate from the capability that reads the record
  holding it.** `recovery-lock:read`, `disk-encryption-recovery-key:read`, and
  `computer-device-lock-pin:read` do not follow from `devices:read`, and the picker puts them in a
  different section. Where a Jamf Pro privilege was a server *action* rather than an object
  privilege, expect a distinct capability rather than an action on the object.
- **Protect capabilities map to operation names, not paths,** and the published tables cover
  operations only. A nested field's grant, such as `computer { hostName }` inside `listAlerts`, is
  not answerable from the docs. Grant the operation's capability, name the uncertainty, and do not
  drop the field. The operation table is in `protect-graphql.md`.
- **Two capabilities where two old privileges applied.** See the table below.

## Picker path

A slug on its own is not actionable. Jamf Account's permission picker is searched by name and
shows the slug nowhere, so every emitted grant carries the section and permission name the picker
displays. The table below is bundled from the published permissions map dated 2026-09-03, which
spans Jamf Pro, Classic, Protect, and Security Cloud despite its name. Capability names and picker
sections are a short vocabulary that changes slowly, which is what makes bundling them different
from bundling an endpoint catalog: the endpoint-to-grant lookup stays live, because the script names
its own endpoints and the skill resolves a handful of calls, not a catalog.

The **Actions published** column is the action set the capability exposes. It is not the grant for
a specific method; read that off the endpoint. The two differ in places, and device-record deletion
is the standing example.

| Capability | Actions published | Picker section | Picker name |
|---|---|---|---|
| `access-management` | r,u | Admin identity and access | Access management |
| `account-groups` | r | Admin identity and access | Admin account groups |
| `accounts` | c,r,u,d | Admin identity and access | Admin account |
| `activation-code` | r,u | Infrastructure | Activation code |
| `activation-profiles` | c,r,u,d | Enrollment | Activation profiles |
| `ad-cs-settings` | c,r,u,d | Infrastructure | AD Certificate Services connector |
| `advanced-device-searches` | c,r,u,d | Inventory | Advanced device searches |
| `advanced-user-searches` | c,r,u,d | Inventory | Advanced user searches |
| `ai-policies` | c,r,u,d | Compliance | AI policies |
| `allowed-file-extension` | c,r,d | Global settings | Allowed file upload extensions |
| `apache-tomcat-settings` | u | Infrastructure | Tomcat server |
| `app-request` | r,u | Global settings | App request settings |
| `apple-configurator-enrollment` | r,u | Global settings | Apple Configurator enrollment settings |
| `applications` | c,r,u,d | App lifecycle management | Apps |
| `audit` | r | Admin identity and access | Audit events |
| `blueprints` | c,r,u,d,dep | Deployment | Blueprints |
| `buildings` | c,r,u,d | Organizational context | Buildings |
| `cache` | r,u | Infrastructure | Cache |
| `categories` | c,r,u,d | Organizational context | Categories |
| `change-password` | x | Admin identity and access | Change admin password |
| `classes` | c,r,u,d | Organizational context | Classes |
| `cloud-distribution-point` | r,u | Infrastructure | Cloud Distribution Point |
| `cloud-services-settings` | r,u | Infrastructure | Jamf Cloud Services connection |
| `compliance-benchmarks` | c,r,d | Compliance | Compliance Benchmarks |
| `compliance-benchmarks` | r | Compliance | Compliance Benchmarks baseline rules |
| `computer-check-in` | r,u | Global settings | Device check-in configuration |
| `computer-device-lock-pin` | r | Device secrets | Device lock PIN |
| `computer-inventory-collection-settings` | r,u | Global settings | Device inventory collection settings |
| `conditional-access` | r | Global settings | Intune conditional access configuration |
| `configuration-profiles` | c,r,u,d | Deployment | Configuration profiles |
| `content-categories` | r | Secure enterprise access | Content categories |
| `custom-hostname-mappings` | r,u,d | Secure enterprise access | Custom hostname mappings |
| `custom-paths` | c,d | Global settings | Inventory collection custom file paths |
| `deal-registration` | c,r | Organization management scope | Partner deal registration |
| `declarations` | r | Deployment | Declarations reporting |
| `departments` | c,r,u,d | Organizational context | Departments |
| `destructive-device-actions` | x | Device actions | Destructive device actions |
| `detection-analytics` | r,u | Endpoint security | Detection analytics |
| `device-actions` | r,d,x | Device actions | Device actions |
| `device-compliance-information` | r | Compliance | Conditional access device compliance |
| `device-enrollment-program-instances` | c,r,u,d | Infrastructure | Automated Device Enrollment connection |
| `device-groups` | c,r,u,d | Inventory | Device groups |
| `device-history` | r | Inventory | Device history |
| `devices` | c,r,u,d | Inventory | Devices |
| `digicert-settings` | c,r,u,d | Infrastructure | DigiCert Trust Lifecycle Manager |
| `directory-bindings` | c,r,u,d | Deployment | Directory bindings |
| `disk-encryption-configurations` | c,r,u,d | Deployment | Disk encryption |
| `disk-encryption-recovery-key` | r | Device secrets | FileVault recovery key |
| `dismiss-notifications` | x | Global settings | Dismiss notifications |
| `distribution-points` | c,r,u,d | Infrastructure | Distribution points |
| `distributor-actions` | c,r,u | Organization management scope | Distributor actions |
| `dock-items` | c,r,u,d | Deployment | Dock items |
| `ebooks` | c,r,u,d | App lifecycle management | eBooks |
| `enrollment-customization` | c,r,u,d | Global settings | Enrollment customization |
| `enrollment-invitations` | c,r,u,d | Enrollment | Enrollment invitations |
| `enrollment-profiles` | c,r,u,d | Enrollment | Enrollment profiles |
| `extension-attributes` | c,r,u,d | Inventory | Device extension attributes |
| `file-uploads` | c | Admin file uploads | Admin file uploads |
| `flush-policy-logs` | x | Infrastructure | Log flushing |
| `gsx-connection` | r,u | Infrastructure | Apple GSX connection |
| `ibeacon` | c,r,u,d | Organizational context | iBeacon regions |
| `impact-alert-notification-settings` | r,u | Global settings | Notification settings |
| `infrastructure-managers` | c,r,u,d | Infrastructure | Infrastructure Manager instances |
| `inventory-preload-records` | c,r,u,d | Global settings | Inventory preload |
| `jamf-cloud-distribution-service-files` | c,r,d | Infrastructure | Jamf Cloud Distribution Service files |
| `jamf-connect-deployments` | r,u,dep | Deployment | Jamf Connect deployment |
| `jamf-packages-action` | r | App lifecycle management | App package information |
| `jamf-protect-deployments` | r,u,dep | Deployment | Jamf Protect deployment |
| `json-web-token-configuration` | c,r,u,d | Infrastructure | JSON web token configuration |
| `jss-information` | r | Infrastructure | Jamf Pro SLASA |
| `jss-url` | r,u | Infrastructure | Jamf Pro server URL |
| `ldap-servers` | c,r,u,d | Admin identity and access | LDAP / cloud IdP |
| `licensed-software` | c,r,u,d | App lifecycle management | Licensed software |
| `licensing` | r | Organization management scope | Licensing |
| `local-admin-passwords` | r,u,x | Device secrets | Local Admin Passwords (LAPS) |
| `login-disclaimer` | u | Global settings | Login disclaimer |
| `m2m` | r | Infrastructure | M2M tenant ID |
| `managed-software-updates` | c,r,u | Deployment | Software updates |
| `mdm-profile-renewal-settings` | r,u | Global settings | MDM profile renewal settings |
| `network-segments` | c,r,u,d | Organizational context | Network segments |
| `onboarding` | r,u | Global settings | Onboarding configuration |
| `packages` | c,r,u,d | Deployment | Packages |
| `parent-app` | r,u | Global settings | Parent app settings |
| `patch-external-source` | c,r,u,d | App lifecycle management | External patch sources |
| `patch-internal-source` | r | App lifecycle management | Internal patch sources |
| `patch-management-software-titles` | c,r,u,d | App lifecycle management | Patch titles |
| `patch-policies` | c,r,u,d | App lifecycle management | Patch policies |
| `pki` | r,u | Infrastructure | PKI certificates |
| `policies` | c,r,u,d | Deployment | Policies |
| `prestage-enrollments` | c,r,u,d | Enrollment | PreStage enrollments |
| `prevent-lists` | c,r,u,d | Endpoint security | Prevent lists |
| `printers` | c,r,u,d | Deployment | Printers |
| `protection-plans` | r,u | Endpoint security | Protection plans |
| `provisioning-profiles` | c,r,u,d | App lifecycle management | Provisioning profiles |
| `push-certificates` | r,u | Infrastructure | APNS certificate |
| `re-enrollment` | r,u | Global settings | Re-enrollment settings |
| `recovery-lock` | r | Device secrets | Recovery lock password |
| `remote-administration` | c,r,u,d | Global settings | TeamViewer configuration |
| `remote-assist` | r | Global settings | Remote Assist |
| `removable-mac-address` | c,r,u,d | Global settings | Removable MAC addresses |
| `restricted-software` | c,r,u,d | App lifecycle management | Restricted software |
| `retention-policy` | r,u | Infrastructure | Retention policy |
| `return-to-service` | r,u,d | Global settings | Return to service configuration |
| `scripts` | c,r,u,d | Deployment | Scripts |
| `search-domains` | r,u,d | Secure enterprise access | Search domains |
| `security-audit-log` | r | Endpoint security | Security audit log |
| `self-service` | c,r,u,d | Global settings | Self Service configuration |
| `sites` | c,r,u,d | Organizational context | Sites |
| `smtp-server` | r,u | Infrastructure | SMTP |
| `software-update-servers` | c,r,u,d | Infrastructure | Software update servers |
| `sso-connections` | c,r,u,d | Organization management scope | SSO connections |
| `sso-domains` | c,r,u,d | Organization management scope | SSO domains |
| `sso-settings` | r,u | Admin identity and access | Single Sign-On |
| `teacher-app` | r,u | Global settings | Teacher app settings |
| `threat-alerts` | r,u | Endpoint security | Threat alerts |
| `threat-definition-versions` | r | Endpoint security | Threat definition versions |
| `uem-connect` | c,r,u,d | Global settings | UEM Connect configuration |
| `unified-logging-filters` | c,r,u,d | Endpoint security | Unified logging filters |
| `user-extension-attributes` | c,r,u,d | Inventory | User extension attributes |
| `user-groups` | c,r,u,d | Inventory | User groups |
| `user-initiated-enrollment` | r,u | Global settings | User-initiated enrollment settings |
| `user-sessions` | r | Admin identity and access | Admin user sessions |
| `users` | c,r,u,d | Inventory | Users |
| `volume-purchasing-locations` | c,r,u,d | App lifecycle management | Volume purchasing |
| `webhooks` | c,r,u,d | Global settings | Webhooks |
| `ztna` | c,r,u,d | Secure enterprise access | Zero-Trust Network Access (ZTNA) |

## Endpoints that need two capabilities

Where two old privileges map to two different capabilities, both are still required.

| Endpoint | Requires |
| --- | --- |
| `POST /computers`, `POST /mobile-devices` and their update analogues | `devices` + `users` |
| `/patchpolicies` read | `patch-policies:read` + `patch-management-software-titles:read` |
| `/categories` list | `categories:read` + `self-service:read` |
| `/slasa` accept | `jss-information` + `activation-code:update` |
| `POST /mobiledevicecommands/command` | `destructive-device-actions:execute` + `devices:create` |
| `/gsx-connection` | `push-certificates:read` + `gsx-connection:read` |
| `/mobile-device-groups/static-group-membership/{id}/assignments` | `device-groups:read` + `devices:read` |

One endpoint accepts either of two capabilities rather than requiring both: `/logflush` takes
`flush-policy-logs:execute` **or** `policies:delete`.

## Endpoints with no permission

`/jamf-pro-information` and `/jamf-pro-version` are unauthenticated and need no capability. The
`/notifications` list is unauthenticated, although dismissing a notification needs
`dismiss-notifications:execute`.

## Resources with no capability

| Resource | Reason |
| --- | --- |
| Personal device profiles (BYOD) | Deprecated |
| Managed preference profiles (legacy MCX) | Deprecated |
| Peripherals and peripheral types | Deprecated |
| macOS compliance baselines (Protect `listBaselineRules`) | Deprecated |
| Jamf Pro API roles, API privileges, API integrations | Managed in Jamf Account |

A script calling one of these has no grant to request and no route to move to. See
`conversion-rules.md`, "Surfaces with no gateway equivalent."

## Bridges from old names

### From a Jamf Pro privilege name

A script's author-written privileges comment, or a Jamf Pro API role definition, names privileges
by display name: "Read Computers", "Update Mobile Devices". The published bridge is
`x-required-privileges-legacy` on the endpoint page, which carries the old display name beside the
GA capability, so no guessing is required where the network is available. Classic operations carry
no legacy name.

Offline, most names convert mechanically: the capability is the resource portion of the old
privilege in kebab-case and the action moves to the end. `Read Buildings` is `buildings:read`. The
exceptions are where the mapping is not one to one:

| Old privilege pair or set | GA capability |
| --- | --- |
| Computers + Mobile Devices | `devices` |
| Computer Groups + Mobile Device Groups, smart and static alike | `device-groups` |
| Smart User Groups + Static User Groups | `user-groups` |
| Computer Extension Attributes + Mobile Device Extension Attributes | `extension-attributes` |
| macOS Configuration Profiles + Mobile Device Configuration Profiles | `configuration-profiles` |
| Computer Invitations + Mobile Device Invitations | `enrollment-invitations` |
| Advanced Computer Searches + Advanced Mobile Device Searches | `advanced-device-searches` |
| Computer PreStage Enrollments + Mobile Device PreStage Enrollments | `prestage-enrollments` |
| Mac Applications + Mobile Device Applications | `applications` |
| Jamf Connect Settings + Deployments + Deployment Retry | `jamf-connect-deployments` |
| Jamf Protect Settings + Deployments + Deployment Retry | `jamf-protect-deployments` |
| Self Service Branding Configuration + Self Service | `self-service` |

One old privilege splits into two. Computer Commands and Mobile Device Commands become
`device-actions:{r,d,x}` for routine commands and command status, and
`destructive-device-actions:{x}` for erase, unmanage, and remove MDM profile. And one endpoint is
reassigned: `PUT /local-admin-password/{clientManagementId}/set-password` sits under
`local-admin-passwords`, chosen by subject rather than mechanism.

### From a beta grant string

The public beta named grants `{action}:{product}:{capability}`. The published guidance says most old
names convert mechanically, and the mechanical part is two of three steps: drop the product token
and move the action to the end. The third step is re-checking the capability token itself, because
tokens collapsed between beta and GA: smart and static groups collapsed into one capability and
computer and mobile device groups collapsed into another, so `read:pro:smart-computer-groups` is
`device-groups:read`, and `smart-computer-groups:read` does not exist. Resolve the capability
against the picker table above, or live against the endpoint the script calls, before emitting it.

| Beta form | GA form |
| --- | --- |
| `read:pro:buildings` | `buildings:read` |
| `create:pro:departments` | `departments:create` |
| `update:pro:scripts` | `scripts:update` |
| `execute:pro:change-password` | `change-password:execute` |
| `read:pro:smart-computer-groups` | `device-groups:read` |
| `read:pro:computers` | `devices:read` |
