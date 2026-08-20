# MR Language Built-in Function Reference

## Single-Valued (String) Built-ins

### Case and Formatting
```
givenName.lowercase()              // "Alex" → "alex"
givenName.uppercase()              // "Alex" → "ALEX"
givenName.titleCase()              // "alex johnson" → "Alex Johnson"
```

### Extraction
```
givenName.take(1)                  // "Alex" → "A" (safe: never throws)
sn.takeLast(4)                     // "Smith" → "mith"
field.substring(start)             // ⚠ throws if out of bounds
field.substring(start, end)        // ⚠ throws if field shorter than end
field.getWord(0)                   // split on whitespace, take index 0
field.getWord(0, "@")              // split on "@", take index 0
```

### String Manipulation
```
field.replace("old", "new")        // replace first occurrence
field.replace("old", "new", true)  // case-insensitive replace
field.stripDiacriticals()          // é→e, ñ→n, ü→u
field.stripSpaces()                // remove all whitespace
field.stripSpecialCharacters()     // remove non-alphanumeric
field.stripQualifiers()            // remove Jr., Sr., Ph.D., etc.
```

### Predicates (return boolean)
```
field.startsWith("prefix")
field.endsWith("suffix")
field.containsText("substring")    // case-sensitive, for STRING fields
field.isEmpty()                    // true if ""
field.isNotEmpty()                 // true if not ""
```

### Length
```
field.length                       // property, no parentheses
```

### Date Conversion
All patterns use Java DateTimeFormatter tokens:
- `yyyy` = 4-digit year, `yy` = 2-digit year
- `MM` = 2-digit month, `M` = 1 or 2 digit month
- `dd` = 2-digit day, `d` = 1 or 2 digit day
- `HH` = 24-hour hour, `mm` = minutes, `ss` = seconds
- `MMM` = abbreviated month name (Jan, Feb...)

```
// To/from RI standard (yyyy-MM-dd)
dob.convertDateFrom("MM/dd/yyyy")           // "10/31/2002" → "2002-10-31"
dob.convertDateFrom("dd-MMM-yyyy")          // "31-Oct-2002" → "2002-10-31"
dob.convertDateFrom("yyyyMMdd")             // "20021031" → "2002-10-31"
field.convertDateTo("M/d/yyyy")             // "2002-10-31" → "10/31/2002"
field.convertDateTo("MMddyyyy")             // "2002-10-31" → "10312002"

// One-step format conversion
dob.convertDate("M/d/yyyy", "MMddyyyy")

// Datetime
field.convertDateTimeFrom("MM/dd/yyyy HH:mm:ss")
field.convertDateTimeTo("MM/dd/yyyy HH:mm")
field.convertDateTime("MM/dd/yyyy HH:mm:ss", "MMddyyyy HH:mm")
```

### Grad Year (single-valued grade level)
```
grade.calculateGradYear()          // "09" (CEDS) → e.g., "2028"
grade.calculateGradYear(8)         // school year rolls over in August
```

### Collision-Safe Username (policy rules only)
```
(givenName.take(1).lowercase() + sn.lowercase()).incrementOnCollision(20, 1)
// maxBaseLength=20, start collision suffix at 1 (produces jsmith, jsmith1, jsmith2...)
```

---

## Multi-Valued (List) Built-ins

### Indexed Access
```
roles[0]           // first element
roles[1]           // second element (empty string if list too short)
```

### Membership Tests (return boolean)
```
roles.contains("student")                          // exact, case-sensitive
roles.containsAny("student", "pupil")              // any exact match
roles.containsExactly("student")                   // list has ONLY these values
```

### Empty Checks (null-safe — use these instead of if(field) for lists)
```
field.isListEmpty()       // true if null OR empty list
field.isListNotEmpty()    // true if has at least one element
field.listCount           // property, no parentheses
```

### Grad Year (multi-valued grade level list)
```
grade_levels.calcGradYear()        // first element used; e.g., ["09"] → "2028"
grade_levels.calcGradYear(8)       // custom cutoff month
```

### Array-of-Object Access
```
// mapWithSelector: extract a sub-field from every object in the array
// orgs = [{"sourcedId":"111","type":"school"},{"sourcedId":"000","type":"district"}]
orgs.mapWithSelector("sourcedId")   // → ["111", "000"]

// anyChildContains: does any object have subField == value?
orgs.anyChildContains("type", "district")     // exact match
orgs.anyChildContainsText("type", "district") // substring match

// find + {}: find first matching object, then extract a key from it
// user_ids = [{"type":"HR","identifier":"HR-123"},{"type":"SIS","identifier":"STU-456"}]
user_ids.find("type", "HR"){"identifier"}     // → "HR-123"
```

---

## Standalone Functions (no source field)

```
randomNumber(4)      // → "8423" — N-digit random numeric string
randomString(32)     // → "Kj3mNP..." — N-char secure alphanumeric
now()                // → "20240207142900Z" (LDAP Generalized Time)
today()              // → "2024-02-07" (ISO-8601 date)
```

---

## Object/Array Literal Syntax (for structured sink output)

```
// Single object
{"key": value, "key2": value2}

// Array of values
[value1, value2, value3]

// Array of objects
[{"key": val}, {"key": val2}]

// Nested
{"outer": {"inner": field}, "flag": true}
```
