# SharedGlobals — Standard Variable Reference

All keys in `SharedGlobals.properties` are accessed via `SharedGlobal.variableName` in action sets.  
Keys in `Globals.properties` (project-level) are accessed via `Global.variableName`.

## Naming Convention

`systemName + userType + variableName` — e.g. `adStaffBaseDN`, `googleStudentDefaultOU`

- Unqualified keys (no system/type prefix) are cluster-wide defaults
- Suffixed keys (`Staff`, `Student`, `Sponsored`, `Parent`) are per-population overrides
- Always use `SharedGlobal.*` when referencing keys from this file

## Value Types

| Syntax in .properties | Type in action set | Notes |
|---|---|---|
| `key=plainValue` | string | Accessed as-is |
| `key=encrypt(value)` | string (auto-decrypted) | Never log or concatenate raw; treat as opaque |
| `key=json([...])` | array | Parse-ready; use directly in `forEach collection` or array ops |
| `key=json({...})` | object | Parse-ready; access fields with dot notation |

---

## Metadirectory

System-controlled. **Do not modify.** Used internally by RapidIdentity.

| Key | Type | Value / Notes |
|---|---|---|
| `metaBaseDN` | string | `dc=meta` — root DN; use only when searching across both people and groups |
| `metaEmployeeBaseDN` | string | `ou=Accounts,dc=meta` — base DN for all person queries |
| `metaGroupBaseDN` | string | `ou=Groups,dc=meta` — base DN for all group queries |
| `metaEmployeeEmailDomain` | string | Default email domain for metadirectory accounts |
| `metaUsernameAttr` | string | `idautoPersonUserNameMV` — attribute name for usernames |
| `metaUserRDNAttr` | string | `idautoID` — RDN attribute |
| `metaUserRDNSrc` | string | `idautoID` — source for RDN value |
| `metaUserClasses` | json array | objectClasses for person entries: `["top","idautoPerson"]` |
| `metaGroupClasses` | json array | objectClasses for group entries: `["top","idautoGroup","groupOfNames"]` |
| `metaChangeLog` | string | `o=changelog` — changelog DN |
| `metaSystemDefaultGroups` | json array | Names of all default system groups (do not delete) |
| `metaDateAttributeFormats` | json object | Map of date attribute name → format string (e.g. `yyyyMMddHHmmss'Z'`) |
| `metaUniqueAttributeNames` | json array | All attributes with unique constraints across person and group entries |
| `metaDefaultSponsorDN` | string | DN of the default sponsor for sponsored accounts |
| `metaDefaultGroupOwnerDN` | string | DN of the default group owner |

---

## Email Domains

| Key | Type | Notes |
|---|---|---|
| `mailDomain` | string | Default outbound email domain |
| `mailStaffDomain` | string | Staff email domain |
| `mailStudentDomain` | string | Student email domain |
| `mailSponsoredDomain` | string | Sponsored account email domain |
| `mailParentDomain` | string | Parent account email domain |

---

## Source Systems

### OneRoster 1.2

| Key | Type | Notes |
|---|---|---|
| `oneRosterClientID` | string | OAuth2 client ID |
| `oneRosterClientSecret` | string | OAuth2 client secret |
| `oneRosterTokenURL` | string | Token endpoint |
| `oneRosterBaseURL` | string | Base API URL |

### File (SMB/SFTP) — pattern: `file{Population}{Field}`

| Key | Type | Notes |
|---|---|---|
| `file{X}User` | string | Service account username |
| `file{X}Pwd` | encrypted | Password |
| `file{X}Bridges` | json array | Bridge agent names (e.g. `["b1sftpstaff","b2sftpstaff"]`) |
| `file{X}Name` | string | Filename (e.g. `staff.csv`) |
| `file{X}Path` | string | Remote path |
| `file{X}Protocol` | string | `sftp` or `smb` |

### API (OAuth2 REST) — pattern: `api{Population}{Field}`

| Key | Type | Notes |
|---|---|---|
| `api{X}SystemName` | string | Human-readable system name (for logging) |
| `api{X}ClientID` | string | OAuth2 client ID |
| `api{X}ClientSecret` | string | OAuth2 client secret |
| `api{X}TokenURL` | string | Token endpoint |
| `api{X}URL` | string | Base API URL |

---

## Databases — pattern: `db{Population}{Field}`

| Key | Type | Notes |
|---|---|---|
| `db{X}User` | string | Database service account username |
| `db{X}Pwd` | encrypted | Password |
| `db{X}Name` | string | Database name |
| `db{X}Bridges` | json array | Bridge agent names |
| `db{X}DriverClass` | string | JDBC driver class |
| `db{X}SelectQueryFileName` | string | SQL query filename (under `Global.queriesPath`) |
| `db{X}ConnStringTemplate` | string | JDBC connection string template with `%bridgeHostName%` and `%bridgePort%` placeholders |

### JDBC driver classes

| Database | Driver class |
|---|---|
| MSSQL (jTDS) | `net.sourceforge.jtds.jdbc.Driver` |
| MySQL / MariaDB | `org.mariadb.jdbc.Driver` |
| PostgreSQL | `org.postgresql.Driver` |
| Oracle | `oracle.jdbc.OracleDriver` |
| AS400 | `com.ibm.as400.access.AS400JDBCDriver` |
| SQLite | `org.sqlite.JDBC` |
| FileMaker | `com.filemaker.jdbc.Driver` |

### MSSQL connection string template

```
jdbc:jtds:sqlserver://%bridgeHostName%:%bridgePort%;databaseName=%databaseName%;useLOBs=false;ssl=request;loginTimeout=30
```

---

## Target Systems

### Active Directory — pattern: `ad{Domain}{Field}`

| Key | Type | Notes |
|---|---|---|
| `ad{X}UserUPN` | string | Service account UPN (e.g. `service@example.com`) |
| `ad{X}Pwd` | encrypted | Password |
| `ad{X}Bridges` | json array | Bridge agent names (e.g. `["b1addc","b2addc"]`) |
| `ad{X}FQDN` | string | Fully qualified domain name |
| `ad{X}NetBIOS` | string | NetBIOS domain name |
| `ad{X}UPNDomain` | string | UPN suffix domain |
| `ad{X}BaseDN` | string | Root DN for the domain (e.g. `DC=example,DC=net`) |
| `ad{X}GroupsBaseDN` | string | OU for groups |
| `ad{X}UserDefaultDN` | string | OU for active accounts |
| `ad{X}UserDisabledDN` | string | OU for disabled accounts |
| `ad{X}UniqueAttributeName` | string | AD attribute used as the correlation key (e.g. `employeeID`) |

Unqualified (`adUserUPN`, `adPwd`, `adBaseDN`, etc.) = default/single-domain config.  
`adStaff*` / `adStudent*` = per-population multi-domain configs.

### Google Workspace — pattern: `google{Population}{Field}`

| Key | Type | Notes |
|---|---|---|
| `google{X}Domain` | string | Google domain (e.g. `example.com`) |
| `google{X}OAuthCredentialName` | string | Name of the OAuth2 credential stored in Connect |
| `google{X}ImpersonateUserId` | string | Service account email for domain-wide delegation |
| `google{X}OAuthScopes` | json array | OAuth scopes (Admin SDK user, group, orgunit) |
| `google{X}UserDefaultOU` | string | Default Google OU path for active accounts |
| `google{X}UserDisabledOU` | string | Google OU path for disabled accounts |

### Microsoft 365 — pattern: `microsoft{Field}`

| Key | Type | Notes |
|---|---|---|
| `microsoftDomain` | string | Primary onmicrosoft.com domain |
| `microsoftMailDomain` | string | Mail routing domain |
| `microsoftDirectoryTenantID` | string | Azure AD tenant GUID |
| `microsoftApplicationClientID` | string | App registration client ID |
| `microsoftClientSecretValue` | string | App registration client secret (store as encrypted in production) |
| `microsoftGraphAPIURL` | string | `https://graph.microsoft.com/v1.0/` |
| `microsoftIDBridge` | json array | Bridge agent names for Exchange agent |
| `microsoftUser` | string | Exchange agent service account |
| `microsoftPwd` | encrypted | Exchange agent password |
| `microsoftOrg` | string | Organization domain |
| `microsoftCertThumbprint` | string | Certificate thumbprint for cert-based auth |
| `microsoftAppID` | string | Application ID for cert-based auth |

---

## RapidIdentity Defaults

### General

| Key | Type | Notes |
|---|---|---|
| `companyName` | string | Customer display name (used in emails, logs) |
| `renameStaffOffsetDays` | string | Days to defer staff username renames |
| `renameStudentOffsetDays` | string | Days to defer student username renames |
| `localTimeZone` | string | IANA timezone (e.g. `America/Chicago`) |
| `helpdeskURL` | string | Helpdesk URL for user-facing emails |
| `notifyEmail` | string | Admin notification email address |

### File Paths (Connect file system)

| Key | Type | Notes |
|---|---|---|
| `importsPath` | string | `/imports/` |
| `exportsPath` | string | `/exports/` |
| `reportsPath` | string | `/reports/` |
| `mappingsPath` | string | `/mappings/` |
| `queriesPath` | string | `/queries/` — SQL files for DB action sets |
| `emailTemplatesPath` | string | `/emailTemplates/` — HTML email templates |

### File Names

| Key | Type | Notes |
|---|---|---|
| `emailSubjectLines` | string | JSON file name for email subject lines |
| `orgMappings` | string | JSON file for org/school code mappings |
| `connectionErrorTemplate` | string | HTML template filename |
| `welcomeEmailTemplate` | string | HTML template for new user welcome email |
| `thresholdTemplate` | string | HTML template for provisioning threshold alerts |
| `renameSuccessNotificationTemplate` | string | HTML template for rename notifications |

### URLs & Branding

| Key | Type | Notes |
|---|---|---|
| `portalURL` | string | Canonical portal URL (e.g. `https://customer.us001-rapididentity.com`) |
| `portalVanityURL` | string | Customer vanity URL |
| `idautoLogo` | string | Logo URL for email templates |

### Attribute Mapping

| Key | Type | Notes |
|---|---|---|
| `riADUserUniqueIDAttribute` | string | ID Store attribute that holds the AD correlation key |
| `riGoogleUserUniqueIDAttribute` | string | ID Store attribute that holds the Google correlation key |
| `riMicrosoftUserUniqueIDAttribute` | string | ID Store attribute that holds the M365 correlation key |
| `riWelcomeEmailFlagAttribute` | string | Boolean attribute used to track welcome email sent (e.g. `idautoPersonExtBool1`) |
| `riClaimCodeExpirationDateAttribute` | string | Attribute used to store claim code expiration date |
| `riClaimCodeExpirationDays` | string | Number of days before a claim code expires |

### Thresholds

| Key | Type | Notes |
|---|---|---|
| `createPercentCheck` | string | Max % of accounts that can be created in one run before aborting |
| `disablePercentCheck` | string | Max % that can be disabled |
| `enablePercentCheck` | string | Max % that can be enabled |
| `renamePercentCheck` | string | Max % that can be renamed |
| `updatePercentCheck` | string | Max % that can be updated |

### Multi-Purpose

| Key | Type | Notes |
|---|---|---|
| `connectLogColorSchema` | json object | Color map for log output — merged into `logColors` in `defineDefaultVariables` |
| `letters` | json array | `["A","B",..."Z"]` — alphabet array for username generation |
| `microsoftGroupSyncAttributeGraphValues` | json array | Valid values for group type sync to M365 |
| `pwdExpNotifyDays` | json object | Day-count map for password expiry notifications |

### IDHub

| Key | Type | Notes |
|---|---|---|
| `idHubStagingPath` | string | Connect file path for IDHub staging files |
| `idHubArchivePath` | string | Connect file path for IDHub archive |
| `idHubProcessPath` | string | Connect file path for IDHub processing |

### Audit System Names

| Key | Type | Notes |
|---|---|---|
| `adAuditName` | string | Display name for AD in audit logs (e.g. `Active Directory`) |
| `googleAuditName` | string | Display name for Google in audit logs |
| `microsoftAuditName` | string | Display name for M365 in audit logs |
| `rapidIdentityAuditName` | string | Display name for RI in audit logs |
