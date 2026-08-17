# RI OpenLDAP Schema — idautoPerson & idautoGroup Attributes

Source: `RICOpenLDAPSchema.json` (live tenant subschema dump); official docs: https://help.rapididentity.com/docs/rapididentity-cloud-directory-schema (updated Oct 23, 2025)

**Syntax key:**
- `string` — DirectoryString (1.3.6.1.4.1.1466.115.121.1.15)
- `dn` — Distinguished Name (1.3.6.1.4.1.1466.115.121.1.12)
- `boolean` — Boolean (1.3.6.1.4.1.1466.115.121.1.7)
- `datetime` — GeneralizedTime (1.3.6.1.4.1.1466.115.121.1.24)
- `integer` — Integer (1.3.6.1.4.1.1466.115.121.1.27)
- `octet` — OctetString / binary (1.3.6.1.4.1.1466.115.121.1.40)
- `uuid` — UUID (1.3.6.1.1.16.1)

**Cardinality:** `single` = SINGLE-VALUE, `multi` = multi-valued

---

## Shared / Top-level

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `idautoID` | single | uuid | eq | Primary key / RDN for all idauto entries. **Unique.** Must not be changed after creation. |
| `idautoDisabled` | single | boolean | eq | `TRUE` = disabled; absent = enabled |
| `idautoSchemaVersion` | single | string | - |  |
| `idautoChallengeSet` | multi | string | - | Challenge/response sets. **Data MUST NOT be updated by Connect.** |
| `idautoChallengeSetTimestamp` | single | datetime | - | Format: `yyyyMMddHHmmssZ`. |
| `idauto-pwdPrivate` | single | octet | - | RSA-encrypted copy of userPassword |
| `idauto-pwdPrivateTS` | single | datetime | eq | Timestamp when idauto-pwdPrivate was last set. Format: `yyyyMMddHHmmssZ`. |

---

## idautoPerson Attributes

**Required:** `idautoID`, `idautoPersonUserNameMV`

**DN structure:** `idautoID=<value>,ou=Accounts,dc=meta`  
**Required objectClass:** `idautoPerson`

### Standard LDAP Attributes (on idautoPerson)

These standard LDAP attributes are defined on the `idautoPerson` entry and are
commonly read and written by Connect action sets.

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `givenName` | single | string | eq, sub | First name |
| `sn` | single | string | eq, sub | Last name |
| `displayName` | single | string | eq, sub | Display name — usually `"<givenName> <sn>"` |
| `mail` | single | string | eq, sub | Primary email. Must contain `@`. **Unique** constraint. |
| `mobile` | multi | string | - | Mobile phone numbers |
| `userPassword` | single | octet | - | Hashed account password |
| `manager` | multi | dn | eq | DNs of the person's managers |
| `directReports` | multi | dn | eq | DNs of all direct reports. **Automatically managed / NOT writeable.** |
| `memberOf` | multi | dn | - | Groups this person belongs to. **Read-only** (slapo-memberof overlay). |
| `employeeType` | multi | string | eq | Account type. Valid values: `staff`, `student`, `teacher`, `sponsored`, `parent`. **Multi-valued** — always use `employeeType.contains("staff")`, never `==`. IDHub only supports policies on `staff`, `student`, `teacher`. |
| `l` | multi | string | eq, sub | Cities |
| `st` | multi | string | eq, sub | States |
| `postalCode` | multi | string | - | Postal codes |

### Identity & Names

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `idautoPersonUserNameMV` | multi | string | eq, sub | All usernames (primary + alternates). Used for authentication. **Unique.** |
| `idautoPersonSAMAccountName` | single | string | eq | Current AD sAMAccountName. **Unique.** Max length: 20. |
| `idautoPersonPrevSAMAccountNames` | multi | string | eq | Username history — prevents reuse. **Unique.** Max length: 20 (constraint dropped in `amazon-ricloud-2025-01-23-001`). |
| `idautoPersonRenameUsername` | multi | string | - | Staged new username pending rename |
| `idautoPersonRenameFlagDate` | single | string | eq | Date rename was triggered. Format: `yyyy-MM-dd`. |
| `idautoPersonRenameOverride` | single | boolean | eq | `TRUE` = block automated renames |
| `idautoPersonMiddleName` | single | string | - |  |
| `idautoPersonPreferredName` | single | string | - | Preferred first name |
| `idautoPersonPreferredLastName` | single | string | - | Preferred last name |
| `idautoPersonPronouns` | multi | string | - |  |
| `idautoPersonGender` | single | string | - |  |
| `idautoPersonBirthdate` | single | string | - | Format: `yyyy-MM-dd`. |
| `idautoPersonPhotoURL` | single | string | - |  |
| `idautoPersonProfileUrl` | single | string | - |  |

### IDs & External Keys

All attributes in this section have a **unique** constraint.

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `idautoPersonDistrictID` | single | string | eq | District-assigned identifier |
| `idautoPersonStuID` | single | string | eq, sub | Student ID |
| `idautoPersonHRID` | single | string | eq, sub | HR system ID |
| `idautoPersonPayrollID` | single | string | eq | Payroll ID |
| `idautoPersonNationalID` | single | string | eq | National/government ID |
| `idautoPersonStateID` | single | string | eq | State-assigned ID |
| `idautoPersonSchoolID` | single | string | eq | Primary school ID |
| `idautoPersonManagerID` | single | string | eq | Manager's idautoPersonDistrictID |
| `idautoPersonSystem1ID` | single | string | eq | External system 1 ID |
| `idautoPersonSystem2ID` | single | string | eq | External system 2 ID |
| `idautoPersonSystem3ID` | single | string | eq | External system 3 ID |
| `idautoPersonSystem4ID` | single | string | eq | External system 4 ID |
| `idautoPersonSystem5ID` | single | string | eq | External system 5 ID |

### Dates & Lifecycle

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `idautoPersonStartDate` | single | datetime | eq | Student activation date. Format: `yyyyMMddHHmmssZ`. |
| `idautoPersonEndDate` | single | datetime | eq | Student deactivation date. Format: `yyyyMMddHHmmssZ`. |
| `idautoPersonEnrollDate` | single | datetime | eq | Enrollment date. Format: `yyyyMMddHHmmssZ`. |
| `idautoPersonActivationDate` | single | string | - | Format: `yyyy-MM-dd`. |
| `idautoPersonTermDate` | single | string | - | Termination date. Format: `yyyy-MM-dd`. |
| `idautoPersonGraduationDate` | single | string | - | Format: `yyyy-MM-dd`. |
| `idautoPersonStaffStartDate` | single | datetime | eq | Staff activation date. Format: `yyyyMMddHHmmssZ`. |
| `idautoPersonStaffEndDate` | single | datetime | eq | Staff deactivation date. Format: `yyyyMMddHHmmssZ`. |
| `idautoPersonStaffLastDateWorked` | single | datetime | eq | Format: `yyyyMMddHHmmssZ`. |
| `idautoPersonStaffAccessTermDate` | single | datetime | eq | Format: `yyyyMMddHHmmssZ`. |
| `idautoPersonContractStartDate` | single | datetime | eq | Sponsored/contractor activation. Format: `yyyyMMddHHmmssZ`. |
| `idautoPersonContractEndDate` | single | datetime | eq | Sponsored/contractor deactivation. Format: `yyyyMMddHHmmssZ`. |
| `idautoPersonContractLastDateWorked` | single | datetime | eq | Format: `yyyyMMddHHmmssZ`. |
| `idautoPersonContractAccessTermDate` | single | datetime | eq | Format: `yyyyMMddHHmmssZ`. |
| `idautoPersonAllAccessTermDate` | single | datetime | - | Format: `yyyyMMddHHmmssZ`. |
| `idautoPersonSafeIdCompromisedDate` | single | datetime | pres | Format: `yyyyMMddHHmmssZ`. |

### Status & Overrides

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `idautoPersonSourceStatus` | single | string | - | Status value from source system |
| `idautoPersonSponsoredAccountStatus` | single | string | - | Sponsorship status |
| `idautoPersonStatusOverride` | single | boolean | eq | `TRUE` = block all automated status changes |
| `idautoPersonStatusOverrideExpiration` | single | datetime | - | When override expires. Format: `yyyyMMddHHmmssZ`. |
| `idautoPersonStatusOverrideReason` | single | string | - |  |
| `idautoPersonPasswordSet` | single | boolean | - |  |
| `idautoPersonClaimFlag` | single | boolean | - | Cleared (not set to `FALSE`) when resetting |
| `idautoPersonClaimCode` | single | string | eq | Minimum 8 characters (schema version `2025-02-19-000`+) |
| `idautoRequestAssociations` | multi | string | eq | IDs of granted workflow entitlements. **Data MUST NOT be updated by Connect.** Read to check entitlement status. |

### Role & Employment

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `idautoPersonAffiliation` | single | string | eq, sub | Primary affiliation |
| `idautoPersonAffiliations` | multi | string | eq, sub | All affiliations |
| `idautoPersonEmployeeTypes` | multi | string | eq | All employee types (use `[].concat()` when iterating) |
| `idautoPersonJobCode` | single | string | eq, sub | Primary job code |
| `idautoPersonJobCodes` | multi | string | eq, sub |  |
| `idautoPersonJobTitle` | multi | string | eq, sub |  |
| `idautoPersonJobTitles` | multi | string | eq, sub |  |
| `idautoPersonDeptCode` | single | string | eq, sub | Primary department code |
| `idautoPersonDeptCodes` | multi | string | eq, sub |  |
| `idautoPersonDeptDescr` | single | string | eq, sub | Primary department description |
| `idautoPersonDeptDescrs` | multi | string | eq, sub |  |
| `idautoPersonActivityCodes` | multi | string | - |  |
| `idautoPersonManagedOrgs` | multi | string | - | Orgs this person manages |

### Location & School

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `idautoPersonLocCode` | single | string | eq, sub | Primary location code |
| `idautoPersonLocCodes` | multi | string | eq, sub |  |
| `idautoPersonLocName` | single | string | eq, sub | Primary location name |
| `idautoPersonLocNames` | multi | string | eq, sub |  |
| `idautoPersonSchoolCodes` | multi | string | eq | All school codes |
| `idautoPersonSchoolNames` | multi | string | eq, sub |  |
| `idautoPersonGradeLevel` | multi | string | eq |  |
| `idautoPersonCourseCodes` | multi | string | eq, sub |  |
| `idautoPersonCourseIDs` | multi | string | eq, sub |  |
| `idautoPersonBadgeIDs` | multi | string | - | Proximity badge IDs |

### Contact

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `idautoPersonEmailAddresses` | multi | string | eq, sub | Additional email addresses |
| `idautoPersonHomeEmail` | single | string | eq, sub |  |
| `idautoPersonHomePhone` | single | string | - |  |
| `idautoPersonOfficePhone` | single | string | - |  |
| `idautoPersonPhoneExtension` | single | string | - |  |
| `idautoPersonStreetAddress` | multi | string | - |  |
| `idautoPersonWorkStreetAddress` | multi | string | - |  |
| `idautoPersonWorkCity` | single | string | - |  |
| `idautoPersonWorkState` | single | string | - |  |
| `idautoPersonWorkPostalCode` | single | string | - |  |
| `idautoPersonWorkCountry` | single | string | - |  |
| `idautoPersonCountry` | multi | string | - |  |
| `idautoPersonADProfilePath` | single | string | - |  |
| `idautoPersonPreferredLanguage` | single | string | - |  |

### Relationships

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `idautoPersonStudents` | multi | dn | eq | DNs of students associated with this teacher person. **Automatically managed / NOT writeable.** |
| `idautoPersonTeachers` | multi | dn | eq | DNs of teachers associated with this person |

### Provisioning Targets

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `idautoPersonToSystem1` | single | boolean | - | Provisioned to system 1 |
| `idautoPersonToSystem2` | single | boolean | - |  |
| `idautoPersonToSystem3` | single | boolean | - |  |
| `idautoPersonToSystem4` | single | boolean | - |  |
| `idautoPersonToSystem5` | single | boolean | - |  |

### App Roles

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `idautoPersonAppRoleFriendlyNames` | multi | string | - | Human-readable role names |
| `idautoPersonAppRoles1` through `idautoPersonAppRoles10` | multi | string | eq | App role values per system slot |

### Extension Attributes

| Attribute | Cardinality | Type | Index |
|---|---|---|---|
| `idautoPersonExt1` through `idautoPersonExt25` | multi | string | eq, sub |
| `idautoPersonExtBool1` through `idautoPersonExtBool5` | single | string | eq |

---

## idautoGroup Attributes

**DN structure:** `idautoID=<value>,ou=Groups,dc=meta`  
**Required objectClasses:** `groupOfNames`, `idautoGroup`  
**Required:** `idautoID`, unique `cn` (plus `member` from parent `groupOfNames` — may be empty DN `""`)

### Core Attributes

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `idautoID` | single | uuid | eq | Required unique GUID of the group. **Unique.** Must not be changed after creation. |
| `cn` | single | string | eq, sub | Required group name. **Unique.** |
| `description` | single | string | eq, sub | Optional group description |

### Membership

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `member` | multi | dn | eq | Static member DNs (inherited from groupOfNames). Use `[].concat(record.member)` when iterating — may be string when single value. |
| `idautoGroupStaticIncludes` | multi | dn | eq | Additional static include DNs |
| `idautoGroupStaticExcludes` | multi | dn | eq | Static exclude DNs |

### Dynamic Filters

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `idautoGroupIncludeFilter` | single | string | - | LDAP filter for dynamic include |
| `idautoGroupIncludeBaseDN` | single | dn | - | Base DN for include filter search |
| `idautoGroupExcludeFilter` | single | string | - | LDAP filter for dynamic exclude |
| `idautoGroupExcludeBaseDN` | single | dn | - | Base DN for exclude filter search |

### Ownership & Contact

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `idautoGroupOwners` | multi | dn | eq | Owner DNs |
| `idautoGroupCoOwners` | multi | dn | eq | Co-owner DNs |
| `idautoGroupCoOwnerEditable` | single | boolean | - | Whether co-owners can edit membership |
| `idautoGroupEmailAddress` | single | string | eq, sub | Group email address. **Unique.** |
| `idautoGroupEmailAliases` | multi | string | eq, sub | Additional email aliases. **Unique.** |

### Sync & Provisioning

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `idautoGroupLastSynced` | single | datetime | eq | Last sync timestamp. Format: `yyyyMMddHHmmssZ`. |
| `idautoGroupSyncInterval` | single | integer | - | Sync interval in **hours** (not minutes). **Obsolete** as of 2023.05.0 — replaced by cron-expression-based sync. |
| `idautoGroupToSystem1` through `idautoGroupToSystem10` | single | boolean | - | Provisioned to system slot |

### Extension Attributes

| Attribute | Cardinality | Type | Index |
|---|---|---|---|
| `idautoGroupExt1` through `idautoGroupExt5` | multi | string | eq, sub |

---

## Operational Attributes

Read-only attributes available on all entries (person and group). Not associated with any object class.

| Attribute | Cardinality | Type | Index | Notes |
|---|---|---|---|---|
| `memberOf` | multi | dn | - | Groups the entry belongs to. Managed by slapo-memberof overlay. Read-only. |
| `entryDN` | single | dn | - | The DN of the object itself. Read-only. |
| `createTimestamp` | single | datetime | - | When the entry was created. Read-only. Format: `yyyyMMddHHmmssZ`. |
| `modifyTimestamp` | single | datetime | - | When the entry was last modified. Read-only. Format: `yyyyMMddHHmmssZ`. |
| `creatorsName` | single | dn | - | DN of the creator. Read-only. |
| `modifiersName` | single | dn | - | DN of the most recent modifier. Read-only. |
