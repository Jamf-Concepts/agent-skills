# MR Language — Real-World Patterns

## Ingestion Patterns

### OneRoster Ingestion
```
ruleID = ed917774-05d6-440f-b07f-7b7808e7aa24
ruleType = person

// Ingestion: OneRoster → ID Store
// Handles both staff (role=teacher/admin) and students (role=student).

let idautoPersonSystem1ID = sourcedId
let idautoPersonSchoolCodes = orgSourcedIds
let givenName = givenName
let sn = familyName
let idautoPersonMiddleName = middleName
let displayName = givenName + " " + familyName
let mail = email
let idautoPersonSystem2ID = identifier

// employeeType: student | staff
let employeeType = when {
    roles.contains("student")                    -> "student"
    roles.containsAny("teacher", "aide", "proctor") -> "staff"
    else -> ""
}

// Username: teachers keep full username; students capped at 20 chars
let idautoPersonUserNameMV =
    if (roles.contains("teacher"))
        username
    else
        username.substring(0, 20)

// Map org array to a flat list of school codes
let idautoPersonSchoolCodes = orgs.mapWithSelector("sourcedId")
```

### PowerSchool SIS Ingestion
```
ruleID = c0ded644-523e-461b-96ee-c3eac31d633b
ruleType = person

// Ingestion: PowerSchool SIS → ID Store

let givenName = first_name
let sn = last_name
let idautoPersonMiddleName = middle_name
let displayName = first_name + " " + last_name
let mail = email
let employeeType = roles[0]
let idautoPersonGradeLevel = grade_levels
let idautoPersonBirthdate = demographics{"birthday"}
let idautoPersonSchoolCodes = school_ids

// Student ID or HR ID depending on role
let idautoPersonStuID = if (roles.contains("student")) id
let idautoPersonHRID = if (roles.contains("student") == false) id

// Composite ID lookup from array of objects
let idautoPersonSystem1ID = user_ids.find("type", "HR"){"identifier"}

// Grade-based class year
let idautoPersonDeptDescr = if (roles.contains("student")) "Class of " + grade_levels.calcGradYear()

// Derived username from name fields
let idautoPersonUserNameMV = first_name.take(1) + last_name
```

### HR System / Oracle Fusion HCM Ingestion
```
ruleID = a1b2c3d4-0000-0000-0000-000000000001
ruleType = person

// Ingestion: Oracle Fusion Cloud HCM → ID Store

let idautoPersonHRID = PersonNumber
let givenName = FirstName
let sn = LastName.stripQualifiers()
let idautoPersonMiddleName = MiddleName
let displayName = FirstName + " " + LastName
let mail = WorkEmail.lowercase()
let department = DepartmentName
let idautoPersonJobTitle = JobTitle

// Date fields: HCM provides MM/dd/yyyy
let idautoPersonStartDate = HireDate.convertDateFrom("MM/dd/yyyy")
let idautoPersonEndDate = TerminationDate.convertDateFrom("MM/dd/yyyy")

// Staff only — always
let employeeType = "staff"

// Disabled flag: active/inactive from WorkerStatus
let idautoDisabled = if (WorkerStatus != "Active") "TRUE" else "FALSE"
```

---

## Username Policy Patterns

### Student Username (first initial + last name, collision-safe)
```
ruleID = bf696a54-09f7-11ed-bf51-930af7686f25
ruleType = person

// Policy: student username and password generation.

// Strip diacriticals and special chars so accented names work
let idautoPersonUserNameMV = when {
    else -> (givenName.stripDiacriticals().lowercase().take(1) + sn.stripDiacriticals().stripSpecialCharacters().lowercase()).incrementOnCollision(20, 1)
}

// Initial + uppercase last + last 4 of student ID
let userPassword = givenName.lowercase().take(1) + sn.uppercase() + idautoPersonStuID.takeLast(4)
let pwdReset = true

// 4-digit claim code for self-service portal
let idautoPersonClaimCode = randomNumber(4)
```

### Staff Username (first.last, no collision handling)
```
ruleID = ef696a54-09f7-11ed-bf51-930af7686f25
ruleType = person

// Policy: staff username.

let idautoPersonUserNameMV = givenName.stripDiacriticals().stripSpecialCharacters().lowercase() + "." + sn.stripDiacriticals().stripSpecialCharacters().lowercase()
```

### Grade-Based Password Policy
```
ruleID = 524650b4-328d-4e24-937b-6eb513f734c8
ruleType = person

// Policy: password strength by grade level.
// Lower grades (KG-4): use student ID as password (parent-friendly).
// Upper grades (5-12): strong random password.

let userPassword = when {
    idautoPersonGradeLevel.containsAny("KG", "01", "02", "03", "04") -> idautoPersonSystem4ID
    else -> randomString(64)
}
let idautoPersonClaimCode = randomNumber(4)
```

### Sponsored Account Username
```
ruleID = a3e010ba-2fef-11ef-8bfe-2f6e626b9ac5
ruleType = person

// Policy: sponsored/contractor account username (first initial + last, max 24 chars).

let idautoPersonUserNameMV = when {
    else -> (givenName.take(1).lowercase() + sn.lowercase()).incrementOnCollision(24, 1)
}
```

---

## Activation / Deactivation Offset Patterns

### Delayed Activation by Employee Type
```
// Staff accounts activate 3 days after start date; others immediate.
let @activationOffset = when {
    employeeType.contains("staff") -> 259200    // 72 hours = 3 days
    else -> -1                                   // immediate
}

// Staff accounts deactivate 1 day after end date; others immediate.
let @deactivationOffset = when {
    employeeType.contains("staff") -> 86400     // 24 hours = 1 day
    else -> -1
}
```

### Activation by Grade Level
```
let @activationOffset = when {
    idautoPersonGradeLevel.containsAny("12") -> 86400   // seniors: 1 day
    employeeType.contains("staff")           -> 259200  // staff: 3 days
    else -> -1
}

let @deactivationOffset = when {
    employeeType.contains("staff")           -> 86400   // staff: 1 day
    else -> -1
}
```

### Delayed Activation by ID Prefix (per-tenant override)
```
// Specific tenant (identified by idautoID prefix) gets delayed activation.
let @activationOffset = when {
    idautoID.startsWith("0b9d513d") -> 86400
    else -> -1
}
```

---

## Rename Policy Patterns

### Disable Renames Globally
```
let @renameOffset = when {
    else -> -1
}
```

### Immediate Renames for Staff, Deferred for Seniors
```
let @renameOffset = when {
    idautoPersonGradeLevel.containsAny("12") -> 86400   // seniors: 1 day delay
    else -> -1                                            // all others: no rename
}

// Email notification to end user when rename is queued
let @endUserRenameEmailNotification = when {
    idautoPersonGradeLevel.containsAny("12") -> true
    else -> false
}
```

---

## OU Placement Patterns

### Simple Two-Way Split
```
let @ou = when {
    employeeType.contains("staff") -> "OU=Staff,DC=district,DC=edu"
    else -> "OU=Students,DC=district,DC=edu"
}
```

### Disabled Accounts First (Essential Ordering)
```
// Always check disabled status FIRST before any type/school checks
let @ou = when {
    (idautoDisabled == "TRUE" && employeeType.contains("staff")) -> "OU=DisabledStaff,DC=domain,DC=com"
    idautoDisabled == "TRUE"                                     -> "OU=DisabledStudents,DC=domain,DC=com"
    employeeType.contains("staff")                              -> "OU=Staff,DC=domain,DC=com"
    employeeType.contains("student")                            -> "OU=Students,DC=domain,DC=com"
    else                                                        -> "OU=Default,DC=domain,DC=com"
}
```

### Multi-School District with Grade-Level Sub-OUs
```
let @ou = when {
    // Disabled checks always first
    (idautoDisabled == "TRUE" && employeeType.contains("staff")) -> "OU=StaffDisabledAccounts,DC=meta,DC=local"
    (idautoDisabled == "TRUE")                                   -> "OU=StudentDisabledAccounts,DC=meta,DC=local"
    // Staff by school
    (employeeType.contains("staff") && idautoPersonSchoolNames.contains("Branford High School")) -> "OU=Staff,OU=BHS,DC=meta,DC=local"
    (employeeType.contains("staff") && idautoPersonSchoolNames.contains("Branford Middle School")) -> "OU=Staff,OU=BMS,DC=meta,DC=local"
    // Students by school + graduation year
    ((employeeType.contains("student") && idautoPersonSchoolNames.contains("Branford High School")) && (idautoPersonDeptDescr == "Class of 2026")) -> "OU=Class of 2026,OU=Students,OU=BHS,DC=meta,DC=local"
    (employeeType.contains("student") && idautoPersonSchoolNames.contains("Branford High School")) -> "OU=Students,OU=BHS,DC=meta,DC=local"
    (employeeType.contains("student") && idautoPersonSchoolNames.contains("Branford Middle School")) -> "OU=Students,OU=BMS,DC=meta,DC=local"
    // Fallbacks
    employeeType.contains("student") -> "OU=Outplaced,DC=meta,DC=local"
    else                             -> "OU=RapidIDDefaultUser,DC=meta,DC=local"
}
```

---

## Publication Patterns

### Active Directory Publication
```
ruleID = <ad-adapter-guid>
ruleType = person

// Publication: ID Store → Active Directory

let sAMAccountName = idautoPersonUserNameMV
let userPrincipalName = idautoPersonUserNameMV + "@district.edu"
let givenName = givenName
let sn = sn
let displayName = displayName
let cn = displayName
let mail = idautoPersonUserNameMV + "@district.edu"
let description = if (employeeType.contains("student"))
    "Student - " + idautoPersonDeptDescr
    else "Staff - " + department

let @ou = when {
    idautoDisabled == "TRUE"       -> "OU=Disabled,DC=district,DC=edu"
    employeeType.contains("staff") -> "OU=Staff,OU=Employees,DC=district,DC=edu"
    else                           -> "OU=Students,DC=district,DC=edu"
}
```

### Google Workspace Publication
```
ruleID = <google-adapter-guid>
ruleType = person

// Publication: ID Store → Google Workspace

let primaryEmail = idautoPersonUserNameMV + "@school.org"
let givenName = givenName
let familyName = sn
let orgName = idautoPersonSchoolName

// Build structured email object
let emails = [{"address": idautoPersonUserNameMV + "@school.org", "primary": true, "type": "work"}]

// External IDs list
let externalIds = [{"type": "organization", "value": idautoPersonStuID}]

// Org unit path (not OU=... syntax — Google uses path notation)
let orgUnitPath = when {
    employeeType.contains("staff") -> "/Staff"
    else -> "/Students"
}
```

### Microsoft 365 Publication
```
ruleID = <m365-adapter-guid>
ruleType = person

// Publication: ID Store → Microsoft 365

let displayName = displayName
let givenName = givenName
let surname = sn
let userPrincipalName = idautoPersonUserNameMV + "@district.onmicrosoft.com"
let mailNickname = idautoPersonUserNameMV
let mail = idautoPersonUserNameMV + "@district.edu"
let department = department
let jobTitle = idautoPersonJobTitle

// Account enabled flag (M365 uses boolean)
let accountEnabled = if (idautoDisabled == "TRUE") false else true
```

---

## Correlation / Consolidation Patterns

### Simple Student+Staff Correlation
```
ruleID = a1b2c3d4-0000-0000-0000-000000000010
ruleType = person

// Correlation: match incoming records to existing ID Store identities.
// Students match by student ID; staff match by HR ID.

let key exact a idautoPersonStuID = if (roles.contains("student")) id
let key exact b idautoPersonHRID = if (roles.contains("student") == false) id
```

### Multi-System Consolidation (merging duplicates)
```
ruleID = a1b2c3d4-0000-0000-0000-000000000020
ruleType = person

// Consolidation: merge records from SIS and HR feeds.
// SIS record wins for name; HR record wins for department.

let givenName = givenName
let sn = sn
let mail = mail
let employeeType = employeeType
let idautoPersonStuID = idautoPersonStuID
let idautoPersonHRID = idautoPersonHRID
```

### AD Sink-Side Correlation
```
// Match existing AD accounts to IDHub persons.
// objectGUID is the primary key; sAMAccountName is the fallback.

let key exact k_primary objectGUID = idautoPersonSystem1ID
let key exact k_fallback sAMAccountName = idautoPersonUserNameMV
```

---

## Advanced Patterns

### Packed Password Policy
```
// Specify password, pwdReset, and sync policy in one pseudo-attribute.
// The @passwordSyncPolicy controls when IDHub writes passwords:
//   ALWAYS | CHANGES_ONLY | NEVER
let @passwordPolicy = {
    "userPassword": givenName.lowercase().take(1) + sn.uppercase() + "1",
    "pwdReset": false,
    "@passwordSyncPolicy": "CHANGES_ONLY"
}
```

### Composite Date Workaround (Date-only field → Datetime field)
```
// Some systems provide only a date but the sink requires a datetime.
// Append a literal time string, then parse as datetime.
let idautoPersonStaffStartDate = (HireDate + "@00:00:00").convertDateTimeFrom("MM/dd/yyyy'@'HH:mm:ss")
```

### Extracting a Username from Email
```
// "alex.johnson@school.edu" → "alex.johnson"
let idautoPersonUserNameMV = mail.getWord(0, "@")
```

### Conditional Multi-Valued Attribute
```
// Only populate the school code list if the person is a student.
let idautoPersonSchoolCodes = if (roles.contains("student")) school_ids
```

### Null Suppression
```
// Explicitly suppress a field so it is not written to the ID Store.
let idautoPersonProfileUrl = null
```
