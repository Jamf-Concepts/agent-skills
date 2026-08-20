---
name: connect-action-sets
description: >
  Write, review, edit, validate, or refactor RapidIdentity (idauto) Connect action sets in XML.
  Use this skill whenever the user asks to create a new action set, fix an existing one, add a
  section, refactor logic, apply coding standards, rename action sets or section labels, write
  logging/counting code, build a scheduled job, function, or a CSV export for IDHub, or do anything
  else that involves
  Connect XML. Also trigger when the user asks about naming conventions, section structure,
  suppressTrace, logging, counters, argDefs, parameter descriptions, or any other RapidIdentity
  Connect platform detail. If the user shows XML or references a .dssproject file in any way,
  use this skill.
---

# Connect Action Sets — Authoring Skill

RapidIdentity Connect is an XML-based identity workflow engine by idauto. Action sets are the
core unit of logic. This skill encodes Connect coding standards and XML authoring rules based
on built-in platform actions only.

**Always read `CLAUDE.md` (at the root of the files folder) first if present** — it is the authoritative,
session-specific source of truth and may define project-specific conventions that override or
extend this skill.

---

## Working Mode Detection

Detect which mode to use based on available tools and the user's request:

| Context | Mode |
|---|---|
| RapidID MCP Server tools are available (server `mcp-rapidid`; tools like `get-connect-actions`, `save-connect-action`) and the user is working against a live Connect instance | **API mode** — use MCP tools |
| Working with `.dssproject` files or XML strings on disk / in the conversation | **File mode** — use XML |
| Both available | Follow what the user's request implies |

**In API mode:** Always call `get-connect-projects` and `get-connect-actions` to orient before
doing any design or editing work. The full Connect tool set:

| Tool | Use for |
|---|---|
| `get-connect-projects` | Discover projects |
| `get-connect-actions` | List action sets (`project` filter, empty = all; `metaDataOnly: true` to skip bodies) |
| `get-connect-action` | Fetch one action set (`id` = UUID or `project.name`) |
| `save-connect-action` | Create/update (send the fetched `version` on update) |
| `delete-connect-action` | Delete by id or `project.name` — **always confirm with the user first** |
| `run-connect-action` | Run a **saved** action set; returns the HTML job log |
| `get-connect-files` | List files/dirs in the Connect files module (one level per call) |
| `get-connect-file-content` | Read a file — `Globals.properties`, `SharedGlobals.properties`, scripts, and **job/run logs** (`log/job`, `log/run` paths) |

**The authoring loop in API mode is save → run → read log → fix.** After `save-connect-action`,
verify with `run-connect-action` (or read the latest log via `get-connect-file-content`) instead
of declaring success from a clean save — a green save only proves the body parsed.

**Check Globals against the live tenant.** Before referencing `Global.<key>`, when in API mode,
read the project's `Globals.properties` / `SharedGlobals.properties` with
`get-connect-file-content` rather than guessing from `references/shared-globals.md` alone — the
reference lists conventions; the tenant is the truth.

**In file mode:** All existing XML authoring rules in this skill apply unchanged.

### Reading an existing action set — pretty-print first

Action-set files are stored as **one very long single line** (the format the platform requires). That
is unreadable, and reasoning about nesting from it is where structural mistakes come from. Before
analysing a single-line file, render an indented copy and read that:

```bash
xmllint --format path/to/ActionSet.xml
```

Three rules about the indented form:

1. **It is a read-only view. Never write it back.** The file on disk must stay compact single-line
   (§ XML Format Rules). `xmllint --format` also prepends an `<?xml version="1.0"?>` declaration,
   which this skill forbids — one more reason the pretty output is scratch, never the saved artifact.
2. **`Edit` / `Write` `old_string` must match the real file's bytes, not the indentation you read.**
   In the real file a whole `<action …><arg …/></action>` is contiguous on one line; in the indented
   view it spans many lines, so a multi-element snippet copied from the view **will not match**.
   Anchor edits on a single `<arg …/>` line or a single attribute (those are identical in both
   forms), or re-read the raw file before composing the edit.
3. **A `PostToolUse` hook may already be doing this for you.** If `Read` returns an indented
   action set with a `[hook: connect-xml-pretty]` banner, the pretty-printing has been applied to the
   *display only* — the same two rules above still apply, and the file on disk is untouched.

---

## Quick Reference

| Need | Go to |
|---|---|
| XML format rules, root element, quoting, metacharacter escaping | § XML Format Rules |
| JSON serialise / parse - `toJSON` (out) and `parseJSON`; key ordering, malformed handling | § Serialising structured data / § Parsing JSON |
| String escapes (`\\`, `\"`, `\n`, `\t`, `\uXXXX`) | § setVariable Expression Compiler Rules |
| setVariable vs copyRecord — reference vs deep copy, array mutation rule | § setVariable vs copyRecord |
| Naming (prefixes, camelCase, reserved labels) | § Naming Scheme |
| **`label` quoting — bare on `section`/`forEach`/`while`/`continue`/`break`, quoted only on `caFnCoreLog`** | § Section Labels |
| `about` section content (verbose Purpose + pseudo-code, plain ASCII) | § about Section |
| `defineDefaultVariables` content | § defineDefaultVariables Section |
| Logging — built-in `log` action | § Logging |
| Counting — variable-based counters | § Counting |
| Control flow — forEach, if/while, break, labeled loops/continue | § Control Flow |
| `Can't redefine property 'if.else'` compile error — duplicate then/else, no `else if` in Connect | § if / while / break (callout) |
| JavaScript & engine idioms — arrow fns, named fns, Set, filter, toJSON/parseJSON | § JavaScript & Engine Idioms |
| Try/Catch — error handling via a JS function | § Try/Catch |
| Built-in failure model — `getLastErrorMessage`/`getLastErrorCode`/`clearLastError`, log-ERROR side effect | § Built-in failure model |
| **Seeding an empty object or array — `createRecord` / `createArray`, never `parseJSON('{}')` / `parseJSON('[]')`** | § Records & arrays - construction |
| **Setting a Record field — `setRecordFieldValue`, never a dotted `setVariable`; plus type preservation** | § Records & arrays - construction |
| String & record built-in actions (split, contains, equals, pad, record fields) | § String & Record Built-in Actions |
| Calling other action sets (function mode) | § Function Mode Pattern |
| Community Adapter (ca) authoring — naming, sessions, dependencies, param order | § Community Adapter (ca) Action Set Authoring |
| **Fast task → builtin lookup** (strings, arrays, records, dates, DNs, crypto, connections) | `references/native-action-cheatsheet.md` |
| Connections — FnCoreOpenConnections (canonical), typed built-in actions per system, AES CA | § Connections → `references/connections.md` |
| Global property references | § Global Properties |
| Standard SharedGlobals keys by category (AD, Google, M365, DB, meta, etc.) | `references/shared-globals.md` |
| HTTP actions — REST API patterns | § HTTP Actions |
| `delay` action — timed pauses | § delay Action |
| Change iterators (AD/OpenLDAP) — no `.length`, count in `forEach` | § Change Iterators |
| LDAP polling loop pattern | § LDAP Polling Loop Pattern |
| RI Sponsorship API | `references/ri-sponsorship-api.md` |
| `startPortalWorkflow` — submit a WFM request programmatically from Connect | `references/ri-start-portal-workflow.md` |
| Auditing writes with `logAuditEvent` — eventNames, args, AA perp pattern | § Auditing — logAuditEvent |
| Alternate Actions — input/output contracts per AA type | `references/ri-alternate-actions.md` |
| Workflow variable substitution, valuePairs format, WFM return contract | `references/ri-workflow-variables.md` |
| Connect admin REST API — trigger jobs, processes, files | `references/ri-connect-admin-api.md` |
| Oracle Fusion HCM — auth, Workers endpoint, pagination, gotchas | `references/oracle-fusion-hcm-api.md` |
| Skyward Qmlativ — auth, Custom API endpoint, action set patterns | `references/skyward-qmlativ-api.md` |
| WFM action set pattern | § WFM Action Set Pattern |
| Full skeleton for a new action set | § Skeleton Templates |
| Validation checklist before delivery | § Validation Checklist |
| Common pitfalls (quick fixes) | § Common Pitfalls |
| Working mode detection (MCP vs file) | § Working Mode Detection |
| MCP workflow, JSON object model, XML ↔ JSON conversion | § MCP Workflow → `references/mcp-and-json.md` |

---

## XML Format Rules

- **No `<?xml ...?>` declaration** — omit entirely
- **No indentation or newlines between elements** — compact single-line output only
- **No XML comments** — use Connect `comment` actions instead
- Double-hyphens and arrows are fine in `comment` values — `--`, `-->`, and `<--` are all allowed
- `<arg>` values that are JS string literals must use `&quot;` for embedded double-quotes
  - e.g. `value="&quot;quiet&quot;"` not `value='"quiet"'`
- **Escape XML metacharacters in every `value=` expression** — `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`. This is an XML well-formedness requirement enforced *before* the JS layer: a bare `&` (including the `&&` operator) makes the whole document ill-formed and `xmllint` rejects it. The comparison operators are the usual offenders alongside `&&`:
  - `data && data.jobs ? data.jobs : []` → `value="data &amp;&amp; data.jobs ? data.jobs : []"`
  - `i < len` → `value="i &lt; len"` ; `x >= 0` → `value="x &gt;= 0"`
  - `||` needs no escaping (pipe is not an XML metacharacter); single quotes `'...'` need no escaping inside a double-quoted attribute
  - This is additive to `&quot;` — one expression can need both (e.g. `value="results &amp;&amp; results.name == &quot;ok&quot;"`)
- **Dot notation** for all variable/record field access: `record.fieldName`, `session.session`
- **Bracket notation only** when the key contains `@` or `-`: `record['@dn']`, `record['idauto-pwdPrivate']`
  - Never bracket plain identifiers: ❌ `record['idautoID']` → ✓ `record.idautoID`
- **Every `<action>` element must have `id` and `disabled` attributes:**
  - `id` — an uppercase UUID v4: `id="A1B2C3D4-E5F6-7890-ABCD-EF1234567890"`
  - `disabled="false"` — always present, always `false` unless intentionally disabling an action
  - Without these, the Connect editor renders actions as read-only and non-interactive
  - Example: `<action id="A1B2C3D4-E5F6-7890-ABCD-EF1234567890" name="setVariable" outputVar="" disabled="false">`
- **Use plain ASCII in editor-facing strings** — `comment` values, the `description` attribute, and
  section labels. These display in the Connect editor, which does not render extended punctuation
  reliably. Avoid em/en dashes (`—` `–`), smart/curly quotes, and ellipsis (`…`); use a hyphen-minus
  (`-`), straight quotes, and three periods. (The **log viewer** is the exception — it renders
  Unicode correctly, so this is an editor-display constraint, not a limit on `log` message text.)

### Root Element

**Default for any from-scratch or hand-generated file: the `<actionDefs>` (plural) wrapper.** A
bare-root `<actionDef>` file **will not import through the Connect UI standalone importer**, and
every on-disk manifest action set uses the wrapped form:

```
<actionDefs xmlns="urn:idauto.net:dss:actiondef"><actionDef name="MyActionSet" returnsValue="false" description="...">...</actionDef></actionDefs>
```

The `xmlns` goes on the **outer** element only. (connect-api `build`/`convert`/`write_action_set`/
`json_to_xml` with `wrap=true` emits this correctly.)

A bare `<actionDef>` root appears only *inside* a `.dssproject` archive's `actions/` folder — you
may encounter it when reading, but do not author new standalone files that way.

**Never** include `builtIn`, `community`, or `category` attributes on user-defined action sets, and
never add the `changeCount`/`modifiedMs`/`modifiedBy` reconciliation attributes — all of these are
RI-saved metadata, not authoring inputs.

---

## setVariable Expression Compiler Rules

The Connect expression compiler **parses `setVariable value=` as JavaScript before executing it**.
This is a compile-time check, not a runtime check. Expressions that would be valid JS at runtime
can still fail at compile time if the compiler cannot parse them syntactically.

### Characters that break compilation

The following characters are syntactically significant in JS and will cause a compile error if
they appear bare (unquoted) in a `value=` expression:

- `{` `}` — object literal delimiters
- `[` `]` — array literal delimiters
- `"` — string delimiter (inside a double-quoted XML attribute this also ends the attribute early)

**This means you cannot embed a JSON object or array as a raw literal value.** The compiler sees
`{"id":"foo","label":"bar"}` and tries to parse `{` as a block statement, fails immediately.

**Note — two different failure layers.** The characters above break the **JS compile** step. A
separate concern is **XML well-formedness**: `&`, `<`, and `>` must be escaped as `&amp;`, `&lt;`,
`&gt;` or the document fails to parse *before* the compiler ever runs. The `&&` operator and the
comparison operators (`<`, `>`, `<=`, `>=`) are the usual offenders. See § XML Format Rules.

### String delimiter choice — prefer single quotes

Inside an XML `value="..."` attribute, single quotes are literal characters requiring no escaping.
Use single-quoted JS strings whenever a string constant contains double quotes:

```xml
<!-- WORKS but noisy: backslash-escaped quotes; prefer single-quote delimiters -->
<arg name="value" value="&quot;\&quot;groups\&quot;:&quot; + someVar"/>

<!-- RIGHT: single-quote outer delimiter, &quot; for embedded double quotes -->
<arg name="value" value="'&quot;groups&quot;:' + someVar"/>
<!-- Runtime result: "groups":value  ← correct JSON key -->
```

### String escapes (confirmed Connect behavior)

Values are XML-decoded, then processed as JavaScript string literals. Standard JS escapes work:

| Write in source | Produces | Use for |
|---|---|---|
| `\\` | `\` | literal backslash (UNC paths, Windows paths, regex, LDAP DN escapes) |
| `\&quot;` (i.e. `\"`) | `"` | a literal double-quote inside a double-quoted string |
| `\'` | `'` | a literal apostrophe inside a single-quoted string |
| `\n` | newline | multi-line strings / log entries |
| `\t` | tab | tab separation |
| `\uXXXX` | Unicode char | e.g. `\u00e9` → é |

The backslash is the escape character, so a **literal** backslash must be doubled. A single `\`
escapes the next character — `&quot;\&quot;` escapes the closing quote and breaks the string.

```xml
<!-- WRONG: single backslash escapes the closing quote -->
<arg name="value" value="testVar + &quot;\&quot; + text"/>

<!-- RIGHT: doubled backslash yields one literal backslash -->
<arg name="value" value="testVar + &quot;\\&quot; + text"/>
```

Backslash is not an XML metacharacter, so `\\` sits literally in the attribute. Every literal
backslash in the final string is one `\\` in the source, so a UNC path doubles each one:

```xml
<!-- Produces:  \\server\share -->
<arg name="value" value="&quot;\\\\server\\share&quot;"/>
```

Delimiter choice is therefore a **readability** preference, not a correctness one: `\"` works, but
single-quote delimiters avoid the `\&quot;` noise for strings containing double quotes (e.g. JSON
keys: prefer `'&quot;groups&quot;:'` over `&quot;\&quot;groups\&quot;:&quot;`).

### Serialising structured data - use the `toJSON` action

To turn an object, array, or Record into a JSON string, use the built-in **`toJSON`** action -
not `JSON.stringify`. `toJSON(item)` produces compact JSON; `toJSON(item, true)` produces 4-space
indented output (the replacement for `JSON.stringify(obj, null, 4)`). `toJSON` is the
type-agnostic serializer: it handles plain objects, `createRecord` Records, and objects built up
across multiple `setVariable` / `setRecordFieldValue` calls - no concatenation gymnastics required.

`toJSON` is available **both** as an action (with `outputVar`, shown below) and inline as an
expression function (e.g. `toJSON({...})`, as used in the httpPOST body in § HTTP Actions). The
action form is the general-purpose pattern; use whichever reads cleanly.

```xml
<!-- compact -->
<action name="toJSON" outputVar="result"><arg name="item" value="obj"/></action>
<!-- 4-space indented -->
<action name="toJSON" outputVar="resultPretty"><arg name="item" value="obj"/><arg name="indent" value="true"/></action>
```

Key ordering: a `createRecord` Record serialises with its keys **alphabetically sorted**; a plain
object or a `parseJSON`-seeded object keeps **insertion order**. Numbers normalise (`1234`, not
`1234.0`).

Do **not** build JSON by concatenating a Record into text - `&quot;&quot; + record` yields a Java map
`toString` (`{employeeNumber=1234.0, givenName=Jesse}`: `=`, no quotes, Java double), which is not
valid JSON. Use `toJSON(record)`.

> **StackOverflow caveat (corrected).** Earlier guidance said accumulating properties and then
> calling `JSON.stringify(obj)` always throws `java.lang.StackOverflowError` (Rhino `NativeJSON.str`
> recursion). In practice this is **type-specific**: it can occur with live Java-wrapped objects
> (directory / LDAP result objects), but plain Records and `parseJSON`-seeded objects serialise
> cleanly. The durable rule is simply **use `toJSON`** - it is safe regardless of object type.

### Parsing JSON - use the `parseJSON` action

To turn a JSON **string** into a value, use the built-in **`parseJSON`** action (not `JSON.parse`).
It returns fully native JS values:

- objects (dot / bracket / nested access all work)
- real arrays (`Array.isArray` is true; `.length`, indexing, `.map`, `.filter`, arithmetic work)
- top-level scalars (`parseJSON('42')` -> number, `parseJSON('&quot;x&quot;')` -> string, `parseJSON('true')` -> boolean)
- `null`, with unicode preserved

```xml
<action name="parseJSON" outputVar="parsed"><arg name="json" value="payload"/></action>
```

**Never seed an empty container with `parseJSON`.** `parseJSON('{}')` does sidestep the bare-`{}`
compile error, but it is the wrong tool: use the **`createRecord`** action for an empty object and
**`createArray`** for an empty array. `parseJSON` is for parsing an actual JSON *string* and nothing
else. See § Records & arrays - construction.

**Malformed input does not abort the set.** `parseJSON` on invalid JSON auto-logs its own ERROR
line (from the platform `json-actions.js`) and returns `undefined` - it does not throw. To branch
cleanly without that noisy auto-error, pre-gate with the `isValidJSON` guard (see § Try/Catch).

**Do not parse what is already parsed.** `json()`-wrapped SharedGlobals and action-set args typed
as `object` arrive as native values; `parseJSON` / `JSON.parse` is only for raw JSON *strings*
(HTTP response bodies, file reads, string-typed args). See § Global Properties.

### Building large JSON strings (legacy fallback)

Prefer building a Record/object and calling `toJSON`. The string-concatenation pattern below is a
**fallback** for assembling already-serialised fragments or when you must control exact byte output.

```xml
<!-- Step 1: init accumulator -->
<action name="setVariable"><arg name="name" value="sectionsStr"/><arg name="value" value="&quot;&quot;"/></action>

<!-- Step 2: first entry (no leading comma) -->
<action name="setVariable">
  <arg name="name" value="sectionsStr"/>
  <arg name="value" value="'&quot;sectionKey&quot;:' + toJSON({label: &quot;My Label&quot;, rowCount: counts.myKey})"/>
</action>

<!-- Step 3: subsequent entries (prepend comma) -->
<action name="setVariable">
  <arg name="name" value="sectionsStr"/>
  <arg name="value" value="sectionsStr + ',' + '&quot;nextKey&quot;:' + toJSON({label: &quot;Next Label&quot;, rowCount: counts.nextKey})"/>
</action>

<!-- Step 4: wrap in outer structure via array join -->
<action name="setVariable">
  <arg name="name" value="finalJSON"/>
  <arg name="value" value="'{' + [fieldA, fieldB, '&quot;sections&quot;:{' + sectionsStr + '}'].join(',') + '}'"/>
</action>
```

### Summary table

| Situation | Correct approach |
|---|---|
| Serialise any object / array / Record | `toJSON(obj)` (action with `outputVar`, or inline) |
| Pretty / indented output | `toJSON(obj, true)` - 4-space indent |
| Parse a JSON string | `parseJSON(str)` (action) - returns a native value |
| Seed an empty object | **`createRecord`** action - never `parseJSON('{}')` |
| Seed an empty array | **`createArray`** action - never `parseJSON('[]')` or bare `[]` |
| Set a field on a Record | **`setRecordFieldValue`** action - never `setVariable name="rec.field"` |
| Reference a `json()` Global | `Global.X` directly - already native, never parse |
| Accumulated object -> serialise | `toJSON(obj)` (overflow risk is specific to Java-wrapped objects, not plain Records) |
| Assemble pre-serialised fragments | String-concatenation fallback (above) |
| String constant containing `"` | Single-quote outer delimiter: `'&quot;key&quot;:value'` |

---

## Records & arrays — construction

Two hard rules, both about using the native container actions instead of treating a Record or an
array like a plain JS value.

### 1. Build the container with `createRecord` / `createArray`, never `parseJSON`

Applies equally to **objects and arrays** — `parseJSON('[]')` is exactly as wrong as
`parseJSON('{}')`.

```xml
<!-- WRONG: parseJSON is a JSON-string parser, not a container constructor -->
<action name="parseJSON" outputVar="rec"><arg name="json" value="'{}'"/></action>
<action name="parseJSON" outputVar="list"><arg name="json" value="'[]'"/></action>

<!-- RIGHT -->
<action name="createRecord" outputVar="rec"/>
<action name="createArray" outputVar="list"/>
```

`parseJSON('{}')` "works" — which is exactly why it spreads — but it misuses a parser to dodge the
bare-`{}` compile error, and it yields a plain JS object rather than a Record, so the Record actions
(`setRecordFieldValue`, `hasRecordField`, `copyRecord`, `recordEquals`) are no longer the natural way
to work with it. Reach for the constructor that matches the type you want. Bare `{}` / `[]` literals
remain a compile error (§ setVariable Expression Compiler Rules); `createRecord` / `createArray` are
the answer to that, not `parseJSON`.

### 2. Set fields with `setRecordFieldValue`, never a dotted `setVariable`

```xml
<!-- WRONG: pokes a field by dotted variable name, bypassing the Record API -->
<action name="setVariable"><arg name="name" value="row.seq"/><arg name="value" value="rowSeq"/></action>
<action name="setVariable"><arg name="name" value="row.jobCode"/><arg name="value" value="fieldJobCode"/></action>

<!-- RIGHT -->
<action name="setRecordFieldValue"><arg name="record" value="row"/><arg name="field" value="&quot;seq&quot;"/><arg name="value" value="rowSeq"/></action>
<action name="setRecordFieldValue"><arg name="record" value="row"/><arg name="field" value="&quot;jobCode&quot;"/><arg name="value" value="fieldJobCode"/></action>
```

Dot notation *reads* fine on a Record (`row.seq` returns the value, per § String & Record Built-in
Actions), and the dotted-`setVariable` form usually assigns without complaint. Use the action anyway:
it is the documented setter, it keeps the field name a real quoted string (so a name with a `-` or `@`
needs no special handling), and it reads as a Record operation in the editor and in a trace instead of
as a variable assignment that happens to contain a dot. For a multi-valued field use
`setRecordFieldValues` with `values`.

### Type preservation — why this matters beyond style

`createRecord` + `setRecordFieldValue` **preserves the native JS type** of each value: assign a number
and it stays a number, assign `true` and `typeof` reports `boolean`.

**`createRecordFromObject` does not** — it coerces every value to a string, so `true` becomes `"true"`
and `50` becomes `"50"`. It is a convenience for seeding from an existing object, not the safe default.

This is a correctness issue wherever a caller compares strictly or does arithmetic. A `percentTotal`
built through a string-coercing path fails `percentTotal !== 100` even when the value is right, and an
`ok` flag becomes the string `"false"`, which is **truthy**. If a Record's values are consumed by
anything other than string concatenation, build it with `createRecord` + `setRecordFieldValue` and
keep `createRecordFromObject` for the string-map case. (Verified 2026-06-28; see the knowledge-base
article `rapididentity/connect/connect-library/records-json.md`.)

---

## setVariable vs copyRecord — Reference vs Deep Copy

`setVariable` does **not** copy an object or array. It creates a second variable name that
points to the **same object in memory**. Both names are aliases for the same data structure.

```xml
<!-- WRONG: this does NOT make a copy -->
<action name="copyRecord" outputVar="oldRecord"><arg name="record" value="connectOperator[0]"/></action>
<action name="setVariable"><arg name="name" value="newRecord"/><arg name="value" value="oldRecord"/></action>

<!-- oldRecord and newRecord are now the same object -->
<!-- Modifying newRecord also modifies oldRecord -->
<action name="setRecordFieldValue"><arg name="record" value="newRecord"/><arg name="field" value="&quot;someAttr&quot;"/><arg name="value" value="&quot;test&quot;"/></action>
<!-- FnHasRecordChanged will return false — they're the same object, nothing "changed" -->
```

Use `copyRecord` (for records) or `copyArray` (for arrays) to get a true independent copy:

```xml
<!-- RIGHT: copyRecord allocates a new object in memory -->
<action name="copyRecord" outputVar="oldRecord"><arg name="record" value="connectOperator[0]"/></action>
<action name="copyRecord" outputVar="newRecord"><arg name="record" value="oldRecord"/></action>

<!-- Now modifying newRecord does NOT affect oldRecord -->
<action name="setRecordFieldValue"><arg name="record" value="newRecord"/><arg name="field" value="&quot;someAttr&quot;"/><arg name="value" value="&quot;test&quot;"/></action>
<!-- FnHasRecordChanged will correctly detect the difference -->
```

### When each applies

| Situation | Use |
|---|---|
| Extract a single record from a results array | `copyRecord outputVar="record"` with `record="results[0]"` — never `setVariable` |
| Snapshot a record before processing to compare later | `copyRecord` |
| Snapshot an array before processing to compare later | `copyArray` — but note it is **shallow**: for an array of Records whose *contents* will mutate, `copyRecord` each element into the snapshot |
| Iterate an array and remove items inside the loop | `copyArray` — iterate the copy, remove from original |
| Normalize a multi-valued LDAP attribute inline (e.g. in `forEach collection`) | `[].concat(record.member)` — use directly in the expression; no intermediate variable needed |
| Pass a record into logic you own and will not mutate | `setVariable` is fine |
| Any path where `setRecordFieldValue` / `setRecordFieldValues` will run on the copy | `copyRecord` |

### Checking getLDAPRecords results

`getLDAPRecords` returns `null` when there are no matches, or an **array** when matches are found
(including exactly one match). Use a null/length guard directly — no `copyArray` step needed:

```xml
<action name="getLDAPRecords" outputVar="results">...</action>
<action name="if">
  <arg name="condition" value="!results || results.length == 0"/>
  <arg name="then">
    <!-- no results -->
  </arg>
  <arg name="else">
    <!-- results found -->
  </arg>
</action>
```

Extract a specific record with `copyRecord`, not `setVariable`:
```xml
<action name="copyRecord" outputVar="groupRecord"><arg name="record" value="results[0]"/></action>
```

### Normalizing multi-valued LDAP attributes inline

A multi-valued attribute (e.g. `member`, `objectClass`) comes back as a string when only one
value is present. Use `[].concat(attr)` inline — directly in the `forEach collection` arg or
in an expression. No intermediate variable needed:

```xml
<!-- Count: -->
<arg name="value" value="([].concat(groupRecord.member)).length"/>

<!-- Iterate: -->
<action name="forEach">
  <arg name="variable" value="memberDn"/>
  <arg name="collection" value="[].concat(groupRecord.member)"/>
  ...
</action>

<!-- Check existence before concat: -->
<action name="if">
  <arg name="condition" value="groupRecord.member"/>
  <arg name="then">
    <action name="forEach">
      <arg name="variable" value="memberDn"/>
      <arg name="collection" value="[].concat(groupRecord.member)"/>
      ...
    </action>
  </arg>
</action>
```

### Array mutation rule

When removing items from an array inside a `forEach`, always `copyArray` first, iterate the
copy, and call `removeArrayItem` with `indexOf` on the **original**. Mutating the array being
iterated breaks the loop.

```xml
<action name="copyArray" outputVar="array1Copy"><arg name="array" value="array1"/></action>
<action name="forEach">
  <arg name="collection" value="array1Copy"/>
  <arg name="variable" value="item"/>
  <arg name="do">
    <action name="if">
      <arg name="condition" value="/* condition to remove */"/>
      <arg name="then">
        <action name="removeArrayItem">
          <arg name="array" value="array1"/>
          <arg name="index" value="array1.indexOf(item)"/>
        </action>
      </arg>
    </action>
  </arg>
</action>
```

---

## Naming Scheme

### Action Set Prefixes

| Type | Prefix |
|---|---|
| Scheduled Job — sync/import/export | `Sync` |
| Scheduled Job — maintenance/events | `Manage` |
| Function — reusable library | `Fn` |
| REST Endpoint | `REST` |
| Report | `Report` |
| CSV builder — sole output is a CSV file for downstream ingestion (e.g. IDHub) | `Build` |
| Utility | `Util` |
| Alternate Action (portal post-action hooks) | `AA` — do not rename |
| Dynamic List (portal dropdown population) | `DL` — do not rename |
| Project meta | `_` |

Rules:
- No underscores except `_*` names (the `DL` prefix uses no underscore)
- CamelCase throughout: `SyncADSToRI`, `ManageGroupMemberships`, `FnGetUser`, `BuildStaffCSVForIDHub`

**`Build` vs. `Sync` vs. `Report`:** Use `Build` when the action set's *only* output is a CSV file
that another system ingests, and it is not a human-facing report. IDHub import files are always
`Build` (e.g. `BuildStaffCSVForIDHub`), but the prefix applies to any CSV-only producer. If the
action set also performs the downstream import/sync itself, it's a `Sync`; if it produces a
human-facing report, it's a `Report`.

### Section Labels

- All section labels: `camelCase`
- **Never** name a section label the same as a Connect built-in action or reserved variable
  - `return` is forbidden → use `returnSuccess`, `returnRecord`, `returnResult`, etc.
  - `log`, `section`, `if`, `forEach` are also forbidden as section labels
- **Never quote a `label` value — write the bare identifier, no `&quot;...&quot;`.** `label` is
  `type="name"` on `section`, `forEach`, `while`, `continue`, and `break` — a bare token, not a JS
  expression:
  ```xml
  <!-- RIGHT -->
  <arg name="label" value="checkExcludedDomain"/>
  <!-- WRONG: the label becomes the literal text "checkExcludedDomain", quote characters included -->
  <arg name="label" value="&quot;checkExcludedDomain&quot;"/>
  ```
  **Do not generalize this to every `label` arg by name** — `caFnCoreLog`'s `label` parameter is
  `type="string"` (an expression), so it *is* quoted like any other string literal:
  `<arg name="label" value="&quot;fetchAllUsers&quot;"/>`. Same argument name, different `type`,
  opposite quoting rule. Before quoting or not quoting a `label`, check the owning action:
  `section`/`forEach`/`while`/`continue`/`break` → bare; `caFnCoreLog` → quoted. When unsure of a
  new or unfamiliar action's `label` type, `lookup_action` it rather than guessing from a nearby
  example. The validator does not catch a wrongly-quoted `name`-type `label` — it exempts `label`
  from expression checking entirely, so this passes `build`/`validate` clean while still being wrong.
  This is the same `type="name"` rule that governs `setVariable`'s `name` arg and `forEach`'s
  `variable` arg — none of those are ever quoted either.

### Description Template

```
[Type] - [Source] to [Target]: One-sentence description.
```

Examples:
- `Scheduled Job - ADS to RI: Imports user accounts from Active Directory into RapidIdentity.`
- `Function - RI: Looks up a user record by idautoID and returns it.`
- `Utility: Monitors connection errors and sends an alert when a downstream system is unreachable.`
- `Build - DB to IDHub: Builds the staff import CSV consumed by IDHub.`

---

## Action Set Structure

Every action set must follow this top-level section order — no bare top-level actions:

```
about                   (suppressTrace="true")
defineDefaultVariables  (suppressTrace="true")
[functional sections]   (suppressTrace="true" — all of them, no exceptions)
```

**All sections must have `suppressTrace="true"` — including inner/nested sections.**

---

## about Section

Required first section. Contains `comment` actions only. The goal is that a reader who has never
seen the action set can understand what it does and how to call it without reading the logic.

Order:

1. `Last Modified By:` / `Last Modified Date:`
2. `Purpose:` — **a high-level logical overview**, not a single sentence. State what the action set
   does, its inputs and outputs, and the key branches/decisions. Indent continuation lines two
   spaces.
3. `Overview (pseudo-code):` — *optional but encouraged.* A short, plain-language sketch of the flow
   so a caller can see the shape of the logic. Use indentation for nesting; describe loops and
   conditions in words (e.g. `for each row:` / `if terminated: skip and continue`).
4. `Parameters:` — one line per parameter, mark optionals `[optional]`.
5. `Change Log` separator + dated entries.

**Keep comment text plain ASCII.** Comments display in the Connect editor, which does not render
extended punctuation reliably. Avoid em/en dashes (`—` `–`), smart/curly quotes, and ellipsis (`…`);
use a hyphen-minus (`-`), straight quotes, and three periods. Regular dashes and arrows (`-->`,
`<--`) are fine.

```xml
<action name="section">
  <arg name="label" value="about"/>
  <arg name="suppressTrace" value="true"/>
  <arg name="do">
    <action name="comment"><arg name="comment" value="Last Modified By: Name"/></action>
    <action name="comment"><arg name="comment" value="Last Modified Date: YYYY-MM-DD HH:mm"/></action>
    <action name="comment"><arg name="comment" value="Purpose:"/></action>
    <action name="comment"><arg name="comment" value="  Builds the staff import CSV consumed by IDHub from the staff database."/></action>
    <action name="comment"><arg name="comment" value="  Reads staff rows, maps each to the IDHub field layout, writes one row per"/></action>
    <action name="comment"><arg name="comment" value="  active employee, skips terminated records, and logs counts at the end."/></action>
    <action name="comment"><arg name="comment" value="Overview (pseudo-code):"/></action>
    <action name="comment"><arg name="comment" value="  open DB session"/></action>
    <action name="comment"><arg name="comment" value="  rows = query staff table"/></action>
    <action name="comment"><arg name="comment" value="  for each row:"/></action>
    <action name="comment"><arg name="comment" value="    if row is terminated: skip++ and continue"/></action>
    <action name="comment"><arg name="comment" value="    map row to IDHub layout, append CSV row, add++"/></action>
    <action name="comment"><arg name="comment" value="  write CSV to output path"/></action>
    <action name="comment"><arg name="comment" value="  log counts"/></action>
    <action name="comment"><arg name="comment" value="Parameters:"/></action>
    <action name="comment"><arg name="comment" value="  logOnly [optional]: Suppress writes when true."/></action>
    <action name="comment"><arg name="comment" value="  logLevel [optional]: quiet | normal | debug."/></action>
    <action name="comment"><arg name="comment" value="================== Change Log =================="/></action>
    <action name="comment"><arg name="comment" value="YYYY-MM-DD (Name): Initial version."/></action>
  </arg>
</action>
```

---

## defineDefaultVariables Section

Required second section. Must always contain at minimum the `process` metadata object and
the `logLevel` default:

```xml
<action name="section">
  <arg name="label" value="defineDefaultVariables"/>
  <arg name="suppressTrace" value="true"/>
  <arg name="do">
    <action name="setVariable">
      <arg name="name" value="process"/>
      <arg name="value" value="{actionSetName:getCurrentActionSetName(),processID:getProcessID(),processJobName:getProcessJobName()||getProcessTopLevelActionSetName(),processLogFile:getProcessLogFile(),processProject:getProcessProject() == &quot;&quot; ? &quot;Main&quot; : getProcessProject(),processStartTime:formatDate(getProcessStartTime(),&quot;yyyy-MM-dd HH:mm:ss&quot;,Global.localTimeZone),runningIDHub:runningIDHub()}"/>
    </action>
    <action name="setVariable">
      <arg name="name" value="logLevel"/>
      <arg name="value" value="logLevel || &quot;quiet&quot;"/>
    </action>
  </arg>
</action>
```

The single `process` object replaces the old standalone `actionSetName` variable and captures the
full runtime context in one place. Reference its fields with dot notation everywhere `actionSetName`
used to appear — e.g. log prefixes become `process.actionSetName + ": ..."`.

| Field | Source | Notes |
|---|---|---|
| `actionSetName` | `getCurrentActionSetName()` | Name of this action set |
| `processID` | `getProcessID()` | Current process id |
| `processJobName` | `getProcessJobName() \|\| getProcessTopLevelActionSetName()` | Scheduled-job name, or the top-level action set name when run ad hoc (no job) |
| `processLogFile` | `getProcessLogFile()` | Active log file for the process |
| `processProject` | `getProcessProject() == "" ? "Main" : getProcessProject()` | Project name; the default/unnamed project reports `""`, normalized to `Main` |
| `processStartTime` | `formatDate(getProcessStartTime(), "yyyy-MM-dd HH:mm:ss", Global.localTimeZone)` | Process start, formatted in the configured local timezone (`Global.localTimeZone`) |
| `runningIDHub` | `runningIDHub()` | `true` when the environment is running ID Hub |

All seven are built-in value-returning functions, so the object literal is built inline in one
`setVariable` — same construction style as the `counts` initializer below. (As with any leading-`{`
value expression, verify it compiles in your instance.)

If counters are used, initialize them here:
```xml
<action name="setVariable"><arg name="name" value="counts"/><arg name="value" value="{processed:0,add:0,update:0,skip:0,error:0}"/></action>
```

---

## Logging — built-in `log` action

Use the native `log` action for all logging.

### Basic log call

```xml
<action name="log">
  <arg name="message" value="&quot;Processing: &quot; + record.cn"/>
  <arg name="level" value="&quot;INFO&quot;"/>
</action>
```

### log level values

`TRACE` | `DEBUG` | `INFO` | `WARN` | `ERROR` — always uppercase on the `log` action's `level` arg.

**Two distinct vocabularies — do not conflate them.** The `log` action's `level` arg uses the
uppercase severities above (`INFO`, `ERROR`, …). The `logLevel` *parameter* an action set accepts
to gate its own verbosity uses the lowercase words `quiet | normal | debug` (see below). They are
unrelated: `level` is the severity stamped on one log line; `logLevel` is the caller-controlled
threshold that decides whether a given line runs at all.

### Log viewer formatting — plain text, with `\n` and `\t`

The log viewer renders **plain text**. It does not interpret HTML or markdown — `<b>`, `&nbsp;`,
`*bold*` appear literally. It **does** honor standard whitespace escapes, so format with those:

- `\n` produces a real line break — use it for multi-line log entries.
- `\t` produces a real tab — use it for simple column alignment.
- Unicode/extended punctuation renders correctly, so no ASCII-only restriction applies here.

```xml
<!-- Multi-line, tab-aligned summary in one log call -->
<action name="log">
  <arg name="message" value="&quot;Run summary:\n  processed\t&quot; + counts.processed + &quot;\n  added\t&quot; + counts.add + &quot;\n  errors\t&quot; + counts.error"/>
  <arg name="level" value="&quot;INFO&quot;"/>
</action>
```

This concerns `log` actions only — it is not a constraint on data written to target systems
(CSV, LDAP, REST bodies), which may legitimately contain markup.

### logLevel gate pattern

When action sets accept a `logLevel` parameter, gate verbose log calls with an `if`:

```xml
<action name="if">
  <arg name="condition" value="logLevel === &quot;debug&quot;"/>
  <arg name="then">
    <action name="log">
      <arg name="message" value="&quot;Record dump: &quot; + toJSON(record)"/>
      <arg name="level" value="&quot;DEBUG&quot;"/>
    </action>
  </arg>
</action>
```

Recommended `logLevel` convention:

| logLevel | What to log |
|---|---|
| `quiet` (default) | Errors and failures only |
| `normal` | Progress, counts, key state changes |
| `debug` | Everything including record dumps |

### Log color schema — `Global.connectLogColorSchema`

Always initialize `logColors` in `defineDefaultVariables` using `Object.assign` with defaults first, then `Global.connectLogColorSchema` layered on top. This ensures all keys are always present even if the Global is missing or only partially defined:

```xml
<action name="setVariable">
  <arg name="name" value="logColors"/>
  <arg name="value" value="Object.assign({changedData:&quot;chocolate&quot;,complete:&quot;teal&quot;,counts:&quot;black&quot;,data:&quot;blue&quot;,debug:&quot;purple&quot;,error:&quot;red&quot;,fail:&quot;darkred&quot;,info:&quot;royalBlue&quot;,logOnly:&quot;slateGray&quot;,processing:&quot;steelBlue&quot;,query:&quot;darkcyan&quot;,skipped:&quot;mediumpurple&quot;,sourceData:&quot;dimGray&quot;,success:&quot;green&quot;,targetData:&quot;darkslategray&quot;,test:&quot;darkorange&quot;,warn:&quot;goldenrod&quot;,whitespace:&quot;white&quot;},Global.connectLogColorSchema||{})"/>
</action>
```

Then reference colors as `logColors.keyName` on every `log` action's `color` arg:

| Key | Color | Use for |
|---|---|---|
| `changedData` | chocolate | Values that were changed |
| `complete` | teal | Final success / job complete |
| `counts` | black | Count summaries |
| `data` | blue | General data values |
| `debug` | purple | Debug dumps |
| `error` | red | Errors |
| `fail` | darkred | Fatal failures / abort |
| `info` | royalBlue | General informational progress |
| `logOnly` | slateGray | Suppressed writes (logOnly mode) |
| `processing` | steelBlue | In-progress work |
| `query` | darkcyan | LDAP/DB filter strings |
| `skipped` | mediumpurple | Skipped records |
| `sourceData` | dimGray | Raw source/input data |
| `success` | green | Successful operations |
| `targetData` | darkslategray | Target system data |
| `test` | darkorange | Test/dry-run output |
| `warn` | goldenrod | Warnings |
| `whitespace` | white | Visual spacers |

---

## Counting — variable-based counters

Use a plain object variable for counts. Never create individual top-level counter variables.

Initialize in `defineDefaultVariables`:
```xml
<action name="setVariable">
  <arg name="name" value="counts"/>
  <arg name="value" value="{processed:0,add:0,update:0,skip:0,error:0}"/>
</action>
```

Increment during processing:
```xml
<action name="setVariable">
  <arg name="name" value="counts.processed"/>
  <arg name="value" value="counts.processed + 1"/>
</action>
```

Log summary at the end:
```xml
<action name="log">
  <arg name="message" value="&quot;Counts -- processed: &quot; + counts.processed + &quot; | add: &quot; + counts.add + &quot; | update: &quot; + counts.update + &quot; | skip: &quot; + counts.skip + &quot; | error: &quot; + counts.error"/>
  <arg name="level" value="&quot;INFO&quot;"/>
</action>
```

---

## Control Flow

Connect provides built-in control-flow actions. None of them are JavaScript statements — they are
actions with nesting args, so the same `do`/`then`/`else` rules from § XML Format Rules apply.

### forEach

Loop arg names are **`variable`** (the loop-variable name) and **`collection`** (the array). Never
`item`/`items`. Normalize a possibly-single value with `[].concat(...)` directly in `collection`.

```xml
<action name="forEach">
  <arg name="variable" value="member"/>
  <arg name="collection" value="[].concat(groupRecord.member)"/>
  <arg name="do">
    <action name="log"><arg name="message" value="member"/></action>
  </arg>
</action>
```

### if / while / break / return

- `if` takes `condition` + `then` (+ optional `else`).
- `while` takes only `condition` + `do` — no `else`.
- `break` exits the nearest loop.
- **`return` exits the entire action set**, not the current section or loop — it is a function-style
  return, never a section escape. With no `value` arg it returns `undefined` (not `null`); the value
  reaches the caller only if the calling action specified an `outputVar`. To skip the rest of a loop
  iteration use `continue`; to leave a loop use `break`; to break out of a labeled section use
  `break` with the section's `label`.

> **Common compile error: `Can't redefine property 'if.else'`.** This means an `if` action has
> **two** `else` args (or two `then` args) as direct children — almost always because a block meant
> for a *nested* `if`'s `else` branch was mistakenly attached as a second `else` on the **outer**
> `if` instead. This happens easily when hand-editing a three-way branch (`if A ... else if B ...
> else ...`), since Connect has no native `else if` — a three-way branch is always an `if` nested
> inside the outer `else`, and the innermost default block belongs to the *inner* `if`'s `else`,
> not the outer one's.
>
> ```xml
> <!-- WRONG: two <arg name="else"> children on the same outer if -->
> <action name="if"><arg name="condition" value="a"/>
>   <arg name="then">...</arg>
>   <arg name="else"><action name="if"><arg name="condition" value="b"/>
>     <arg name="then">...</arg>
>     <!-- inner if has no else here -->
>   </action></arg>
>   <arg name="else">...default block...</arg>  <!-- ORPHANED second else -->
> </action>
>
> <!-- RIGHT: default block is the INNER if's else -->
> <action name="if"><arg name="condition" value="a"/>
>   <arg name="then">...</arg>
>   <arg name="else"><action name="if"><arg name="condition" value="b"/>
>     <arg name="then">...</arg>
>     <arg name="else">...default block...</arg>  <!-- belongs here -->
>   </action></arg>
> </action>
> ```
>
> To diagnose: for every `if` action, count its direct `<arg name="then">` and `<arg name="else">`
> children — each must appear at most once. A quick check (Python/`xml.etree.ElementTree` or
> equivalent) that walks every `action` element and flags duplicate direct `arg name=` children
> finds this instantly, faster than eyeballing deeply nested single-line XML. See also item 18 in
> § Validation Checklist and the matching row in § Common Pitfalls.

### Labeled loops and continue

A `forEach` (or `while`) may carry a `label`; `continue` and `break` can then target that label by
name. Use this when an inner condition should skip to the next iteration of a specific outer loop.

```xml
<action name="forEach">
  <arg name="label" value="FieldIterator"/>
  <arg name="variable" value="field"/>
  <arg name="collection" value="fields"/>
  <arg name="do">
    <action name="if">
      <arg name="condition" value="field == &quot;IGNORE&quot;"/>
      <arg name="then">
        <action name="continue"><arg name="label" value="FieldIterator"/></action>
      </arg>
      <arg name="else"/>
    </action>
    <!-- process field -->
  </arg>
</action>
```

---

## JavaScript & Engine Idioms

The Connect expression engine is at least partially ES6-capable. The following are confirmed working
and are the established idioms used in the ConnectLibrary examples — arrow functions and `new Set()`
are live-verified in deployed production action sets (`FnSyncGroupToGoogle`, `SyncGroupsFull`,
`FnRISaveRecord`, `BuildAllUsersCSVForIDHub`).

> **Unverified ES6+ — do not use without a live test:** template literals (backticks), `const`/`let`,
> destructuring, optional chaining (`?.`), nullish coalescing (`??`), spread/rest (`...`),
> async/await, `class`, `Promise`. Stick to `var`, `function`, and string concatenation for these
> cases. (Note: some external lint tooling — connect-api `expr.py`, riadmin `connect_check_expression` —
> flags even arrow functions as errors; that specific rule is a confirmed false positive. Arrows work.)

### Arrow functions

Arrow functions evaluate inside expressions, including as callbacks to `filter`, `map`, etc.:

```xml
<arg name="value" value="arrayA.filter(x =&gt; !setB.has(x))"/>
<arg name="value" value="exArray.filter((value, index) =&gt; exArray.indexOf(value) === index)"/>
```

### Named functions via setVariable

Define a reusable function by assigning a **named function** to a variable with `setVariable`. The
function binds to that variable name and may recurse. This is the house idiom (e.g. `arrayDeepCopy`,
`recursiveArraySort` in `FnHasRecordChanged`). Multi-line bodies are allowed inside the `value`
attribute — the editor stores the newlines; the "single-line compact" XML rule governs element
structure, not attribute contents.

```xml
<action name="setVariable">
  <arg name="name" value="arrayDeepCopy"/>
  <arg name="value" value="function arrayDeepCopy(arr){ if(Array.isArray(arr)){ var c = arr.slice(0); for(var i=0;i&lt;c.length;i++){ c[i]=arrayDeepCopy(c[i]); } return c; } else { return arr; } }"/>
</action>
<action name="setVariable">
  <arg name="name" value="deep"/>
  <arg name="value" value="arrayDeepCopy(original)"/>
</action>
```

### Set — unique values and array differencing

`new Set(arr)` plus `.has()` is the clean way to compute membership differences — exactly what group
add/remove reconciliation needs:

```xml
<action name="setVariable"><arg name="name" value="setB"/><arg name="value" value="new Set(arrayB)"/></action>
<!-- items only in A (to add) -->
<action name="setVariable"><arg name="name" value="onlyInA"/><arg name="value" value="arrayA.filter(x =&gt; !setB.has(x))"/></action>
```

### Array idioms

| Need | Expression |
|---|---|
| Unique values | `arr.filter((v,i) =&gt; arr.indexOf(v) === i)` |
| Duplicate values | `arr.filter((v,i) =&gt; arr.indexOf(v) !== i)` |
| Unique as CSV string | `arr.filter((v,i) =&gt; arr.indexOf(v) === i).join(',')` |
| Merge two arrays | `arrayA.concat(arrayB)` |
| Normalize single value/record → array | `[].concat(value)` |
| Set difference (A not in B) | `new Set(b)` then `a.filter(x =&gt; !setB.has(x))` |

### Logging objects - use `toJSON`

Logging an object as the **sole** `message` arg renders it readably, but concatenating an object
into a string (`&quot;x: &quot; + obj`) yields `[object Object]` (and a Record yields a Java map string).
Serialise with `toJSON(obj)`, or `toJSON(obj, true)` for indented multi-line output:

```xml
<arg name="message" value="&quot;Record: &quot; + toJSON(record, true)"/>
```

---

## Try/Catch

Connect has **no native try/catch action**. To trap a JavaScript error (e.g. a null-pointer or a
`JSON.parse` failure) instead of letting it abort the whole action set, define a JS function via
`setVariable` that wraps the risky operation in a real `try/catch`, then call it. This follows the
named-function idiom above. Use `catch(e)` (with the binding) for engine compatibility — prefer it
over the bare ES2019 `catch {}` form.

```xml
<!-- define once, e.g. in defineDefaultVariables -->
<action name="setVariable">
  <arg name="name" value="isValidJSON"/>
  <arg name="value" value="function isValidJSON(text){ try { JSON.parse(text); return true; } catch(e) { return false; } }"/>
</action>

<!-- call it; the failure path returns cleanly instead of crashing the action set -->
<action name="setVariable"><arg name="name" value="ok"/><arg name="value" value="isValidJSON(payload)"/></action>
<action name="if">
  <arg name="condition" value="!ok"/>
  <arg name="then">
    <action name="log">
      <arg name="message" value="&quot;Invalid JSON, handled without crashing: &quot; + payload"/>
      <arg name="level" value="&quot;ERROR&quot;"/>
      <arg name="color" value="logColors.error"/>
    </action>
  </arg>
  <arg name="else"/>
</action>
```

The `catch` block is also where you enhance diagnostics — log the offending input, or return a
sentinel like `"ERROR"` so the caller can branch on it (halt, send mail, etc.). Reference: the PSO
"Try Catch" page,
`https://idauto.atlassian.net/wiki/spaces/PSO/pages/3145465977/Try+Catch`.

Note: the built-in `parseJSON` action does **not** throw on malformed input - it auto-logs an ERROR
and returns `undefined`. The `isValidJSON` guard above (which calls native `JSON.parse` inside the
try/catch) is for **suppressing that auto-error and branching cleanly**, not for preventing a crash.

### Built-in failure model — check returns, not exceptions

Try/catch is only for **JavaScript-level** errors in your own expressions. Connect **built-in
actions never throw**: on failure they log via the platform error channel, return `undefined` or
`false`, and set the process error state. The durable pattern is therefore *check the return value
of every built-in that matters*, then read the error state for diagnostics:

| Action | Behavior |
|---|---|
| `getLastErrorMessage` | Returns the last error message set by a failed built-in. **Not cleared by reading it.** |
| `getLastErrorCode` | Returns the last error code — often an LDAP result code (`NO_SUCH_OBJECT`, `INVALID_DN_SYNTAX`, `ALREADY_EXISTS`). Not every failure sets a code; many set only the message. |
| `clearLastError` | Clears both. Call explicitly after handling an error, or stale state leaks into later checks. |

**`log` at `level="ERROR"` has a side effect:** it calls `clearLastError()` and then sets
`lastErrorMessage` to *your logged message*. After an error-level log, `getLastErrorMessage()`
returns what you just logged, not the original platform error — capture the platform message
*first* if you need it:

```xml
<action name="setVariable"><arg name="name" value="ldapError"/><arg name="value" value="getLastErrorMessage()"/></action>
<action name="log">
  <arg name="message" value="process.actionSetName + &quot;: save failed -- &quot; + ldapError"/>
  <arg name="level" value="&quot;ERROR&quot;"/>
  <arg name="color" value="logColors.error"/>
</action>
```

---

## String & Record Built-in Actions

Connect ships built-in actions for common string, array, record, and JSON operations. **Prefer these over inline JS.** Full call syntax for every builtin is in `references/native-action-cheatsheet.md`.

### String actions

| Action | Key args | Notes |
|---|---|---|
| `splitString` | `string`, `delimiter` | Returns an array. Single-value input yields a one-element array. |
| `stringContains` | `string`, `pattern`, `ignoreCase` | `pattern` accepts plain string **or regex literal** (`/\d/`). |
| `stringEquals` | `string`, `pattern`, `ignoreCase` | With regex pattern, acts as a match test, not literal equality. |
| `stringStartsWith` / `stringEndsWith` | `string`, `pattern`, `ignoreCase` | Boundary checks. |
| `stringToUpper` / `stringToLower` | `string` | Case conversion. |
| `stringLength` | `string` | Returns integer length. |
| `stringRepeat` | `text`, `count` | Returns `text` repeated `count` times. |
| `stringReplaceAll` | `string`, `match`, `replacement`, `ignoreCase` | Replace all occurrences. |
| `stringReplaceFirst` | same | Replace first occurrence only. |
| `subString` | `string`, `startIndex`, `length` | Extract substring. |
| `stringFromTemplate` | `format`, `args` | `%field%` or `%index%` substitution from a record or array. |
| `stringEscape` | `string`, `escapeType` | 12 types: `ecmascript`, `html`, `java`, `ldap-dn`, `ldap-filter`, `sql`, `mysql`, `postgresql`, `uri`, `url`, `xml`, `csv`. Use `ldap-filter` when concatenating user data into LDAP filters, `ldap-dn` for DN components, `csv` for CSV cell values. Accepts string/array/Record input. |
| `stringRemoveDiacriticals` | `string` | Strips combining diacritics; precomposed letters (Ø, Å) pass through. |

JS string methods (`.padStart()`, `.padEnd()`, `.trim()`, etc.) also work inline when no native equivalent exists.

### Array actions

| Action | Key args | Notes |
|---|---|---|
| `createArray` | `size?` | Empty array or pre-sized with nulls. **Never** use a bare `[]` literal, and **never** `parseJSON('[]')` — see § Records & arrays - construction. |
| `copyArray` | `array` | **Shallow** copy — a new array, but nested objects/Records are still shared references. Sufficient for the mutation guard (removing items while iterating); NOT sufficient to snapshot an array of Records for later comparison — `copyRecord` each element for that. `setVariable` is an alias, not a copy. |
| `appendArrayItem` / `appendArrayItems` | `array`, `item` / `array`, `items` | Append one item or all items from src. |
| `getArraySize` | `array` | Integer size. |
| `getArrayItem` / `setArrayItem` | `array`, `index` | Read or write by index. |
| `insertArrayItem` / `insertArrayItems` | `array`, `index`, `item`/`items` | Insert at index. |
| `removeArrayItem` | `array`, `index` | Remove one item, returns it. |
| `removeArrayItems` | `array`, `index`, `count` | Remove N items, returns removed array. |
| `removeLastArrayItem` | `array` | Pop last item, returns it. |
| `reverseArray` | `array` | Mutates in place. |
| `sortArray` | `array`, `ascending?`, `ignoreCase?`, `keyFields?` | Full-featured sort. Prefer over JS `.sort()`. |
| `joinArray` | `array`, `delimiter?` | Concatenate to string. Prefer over `arr.join()`. |
| `sliceArray` | `array`, `startIndex`, `endIndex?` | Returns new subarray; original unchanged. Shallow — nested objects still shared. |
| `arrayContains` | `array`, `value` | Boolean membership test. |

### Record actions

| Action | Key args | Notes |
|---|---|---|
| `createRecord` | — | Empty Record — **never** `parseJSON('{}')`. `createRecordFromObject(obj)` builds from a JS object but **coerces every value to a string**; prefer `createRecord` + `setRecordFieldValue` to keep native types. See § Records & arrays - construction. |
| `copyRecord` | `record` | Deep copy — always use before mutating. `setVariable` is an alias. |
| `setRecordFieldValue` / `getRecordFieldValue` | `record`, `field`, `value?` | Single-field set/get. |
| `setRecordFieldValues` / `getRecordFieldValues` | `record`, `field`, `values?` | Multi-valued field set/get. |
| `addRecordFieldValue` / `addRecordFieldValues` | `record`, `field`, `value`/`values` | Append to multi-valued field. |
| `clearRecordFieldValues` | `record`, `field` | Clears to null (not empty array). |
| `getRecordFieldNames` | `record` | Array of field names. |
| `hasRecordField` / `hasRecordFieldValue` | `record`, `field`, `value?` | Existence / value membership checks. |
| `removeRecordField` / `removeRecordFields` | `record`, `field`/`fields` | Remove fields. `delete rec.field` does not work on Records. |
| `removeRecordFieldValue` / `removeRecordFieldValues` | `record`, `field`, `value`/`values` | Remove specific values from multi-valued field. |
| `renameRecordField` / `renameRecordFields` | `record`, `oldName`, `newName` / comma-delimited pairs | Rename field keys. |
| `copyRecordField` / `copyRecordFields` | `source`, `field`/`fields`, `destination` | Copy fields across records. |
| `filterRecordFields` | `record`, `fields` | Keep only named fields; remove all others. |
| `recordEquals` | `record1`, `record2` | Field-by-field equality check. |
| `createRecordFromXML` | `xmlObject`, `excludeAttrs?` | Build Record from parsed XML; child elements become fields. |

### JSON actions

| Action | Args | Returns |
|---|---|---|
| `parseJSON` | `json` | Native JS value (object / array / scalar / null). Malformed input auto-logs an ERROR and returns `undefined` (no abort). |
| `toJSON` | `item`, `indent?` (boolean) | JSON string; `indent=true` gives 4-space pretty output. Also callable inline. |

Prefer these over `JSON.parse` / `JSON.stringify`. Record keys serialise alphabetically; plain and `parseJSON`-seeded objects keep insertion order. `"" + record` yields a Java map string — always use `toJSON(record)`.


## Function Mode Pattern

If an optional `session` parameter is provided, use it directly — never open/close connections.
Only open/close when no session is provided. Use the correct typed connection action for the
target system (see § Connections).

```xml
<action name="if">
  <arg name="condition" value="!session"/>
  <arg name="then">
    <!-- e.g. for RapidIdentity: -->
    <action name="openMetadirLDAPConnection" outputVar="session"/>
    <!-- e.g. for Active Directory: openADConnection (with bridgeInfo args) -->
    <!-- e.g. for Google: defineGoogleExtendedOAuthConnection (with Global args) -->
    <!-- e.g. for Portal: defineCloudPortalConnection -->
    <action name="setVariable">
      <arg name="name" value="closeSession"/>
      <arg name="value" value="true"/>
    </action>
  </arg>
</action>
```

Close at the end only when `closeSession` is true (and only for closeable connection types — OAuth2 /
HTTP Basic connections like Microsoft Graph and Google OAuth are never closed; see
`references/connections.md`):
```xml
<action name="if">
  <arg name="condition" value="closeSession"/>
  <arg name="then">
    <action name="close">
      <arg name="closeable" value="session"/>
    </action>
  </arg>
</action>
```

---

## Community Adapter (ca) Action Set Authoring

These rules apply specifically when authoring **Community Adapter** action sets. Where they
differ from the rules elsewhere in this skill (notably the `defineDefaultVariables`
always-include rule), the rules in this section override them for Community Adapter work.

### What Community Adapters are

A Community Adapter is a portable, self-contained Connect project that wraps an external
system's API — or a set of core utilities — in typed action sets (e.g. `caEntra` for Microsoft
Entra/Graph, `caIDHub` for the IDHub External REST API, `caCoreFunctions` for the core `Fn*`
utility library). They are designed to be imported and called by any project without depending
on another project's internals.

### Naming convention

`ca{adapter}{category}{function}`

| Token | Meaning | Examples |
|---|---|---|
| `ca` | Community Adapter (literal prefix) | — |
| `{adapter}` | abbreviation / short name | `Entra`, `Fn`, `IDHub` |
| `{category}` | functional or system category of the action set | `AD`, `Group`, `User` |
| `{function}` | the function the action set serves | `IsAccountDisabled` |

No underscores. Example: `caFnADIsAccountDisabled`

### defineDefaultVariables (CA override)

Include the `process` (or `processVariables`) object **only if the user explicitly asks for
it** — do not add it by default. This overrides the always-include rule in § defineDefaultVariables
Section, for Community Adapter action sets only.

### Logging with FnCoreLog / caFnCoreLog

If the user has instructed you to use `FnCoreLog` or `caFnCoreLog`, define a variable
`actionSetName = getCurrentActionSetName()` and pass that variable to the `actionSetName`
parameter of the `FnCoreLog` / `caFnCoreLog` call.

### Parameter (argDef) order

Order parameters as follows, including **only** those that are actually present:

1. `logOnly`
2. `logLevel`
3. session(s) — if multiple session objects are required, they all go here
4. parameters required by the action set
5. `about` — always the final parameter

The `about` parameter exists to surface documentation in the Connect UI. Populate its `description`
with the same verbose Purpose + high-level overview described in § about Section — plain ASCII, no
HTML. Keep it as a single attribute string (use ` | ` or `;` as separators).

### Sessions

- **Do not open connections with action sets that live outside the adapter's own project
  folder.** This specifically rules out shared helpers like `FnCoreOpenConnections` and
  `FnOpenConnections`. Use a Connect **built-in** connection action
  (`defineCloudPortalConnection()`, `openMetadirLDAPConnection()`, `openADConnection`), or a
  connection action set that lives **within the same project folder**.
- If only one session is required, name the parameter `session`.
- If more than one session is required, label each by system, e.g. `sessionGoogle`, `sessionAD`.
- For **RapidIdentity MetaDirectory** and **RapidIdentity Portal**, the session parameter may be
  **optional**. When the session is not supplied via the parameter, establish a new connection
  and close it on `!session`:
  - RapidIdentity Portal → `defineCloudPortalConnection()`
  - RapidIdentity MetaDirectory → `openMetadirLDAPConnection()`

```xml
<action name="if">
  <arg name="condition" value="!session"/>
  <arg name="then"><action name="defineCloudPortalConnection" outputVar="sessionPortal"/></arg>
  <arg name="else"><action name="setVariable"><arg name="name" value="sessionPortal"/><arg name="value" value="session"/></action></arg>
</action>
<!-- ... work ... -->
<action name="section">
  <arg name="label" value="closeConnections"/>
  <arg name="suppressTrace" value="true"/>
  <arg name="do">
    <action name="if">
      <arg name="condition" value="!session"/>
      <arg name="then"><action name="close"><arg name="closeable" value="sessionPortal"/></action></arg>
      <arg name="else"/>
    </action>
  </arg>
</action>
```

### Dependencies — standalone only

A CA action set may call only Connect built-in actions or action sets **within its own project
folder**. Never call action sets that live outside its project folder — including another
Community Adapter's action sets. The "within its own folder" test is what matters; an action set
being user-defined is fine, since CA action sets are themselves user-defined before conversion.

### Action-selection priority

When deciding which Connect action to use, follow this order:

1. Always prefer a Connect **built-in** action.
2. Otherwise, use an action set in the **same project or project folder**.
3. Custom JavaScript via `setVariable` — last resort only.

---

## Connections

For non-Community-Adapter action sets, use `FnCoreOpenConnections` (`ref_ConnectLibrary`) as the single entry point. It opens one or more connections per call and returns a `conns` record keyed by prefix (`conns.ad.session`, `conns.google.session`, etc.). For CA sets, use the built-in typed actions directly (CA sets cannot call outside their project folder).

| Target system | Non-CA approach | CA approach |
|---|---|---|
| Active Directory | `FnCoreOpenConnections(targetSystem="ad")` | `openADConnection` + `getIdBridgeConnectInfo` |
| Google | `FnCoreOpenConnections(targetSystem="google")` | `defineGoogleExtendedOAuthConnection` |
| Microsoft 365 | `FnCoreOpenConnections(targetSystem="microsoft")` | OAuth2 `httpPOST` for bearer token |
| RapidIdentity Metadirectory | `FnCoreOpenConnections(targetSystem="RapidIdentity")` | `openMetadirLDAPConnection` (no args) |
| RapidIdentity Portal | `FnCoreOpenConnections(targetSystem="Portal")` | `defineCloudPortalConnection` (no args) |
| Database | `FnCoreOpenConnections(targetSystem="db")` | `openDatabaseConnection` + bridge |
| AES encrypt/decrypt | AES CA actions directly (`GenerateAESKey`, `AESEncrypt`, `AESDecrypt`) | same |

Only **closeable** connection/IO actions are closed with `<action name="close"><arg name="closeable" value="session"/></action>`. OAuth2 / HTTP Basic connections (Microsoft Graph, Google OAuth) hold a token, not a handle, and are **not** closed.

**Full per-system details — `FnCoreOpenConnections` Global key requirements, built-in connection args, `getLDAPRecords` `baseDn`/`attributes` selection, the AES sequence, failure handling, and closing — are in `references/connections.md`. Read it before authoring any connection logic. Fast calling-pattern lookup: `references/native-action-cheatsheet.md` § Connections.**

---
## Auditing — logAuditEvent

Call `logAuditEvent` **after** every successful write to an external system — Active Directory, Google, Microsoft 365, RapidIdentity/OpenLDAP, or any other target. Never call it before the write or on a failure path; use `successful: false` if you need to record a failed attempt.

**Triggers:** saving/updating/creating/deleting an account or group, adding or removing a group member, changing a password, moving or renaming an account.

### Arguments

| Arg | Required | Notes |
|---|---|---|
| `eventName` | Yes | See event name list below |
| `targetSystem` | No | Use the audit name Global: `Global.adAuditName`, `Global.googleAuditName`, `Global.microsoftAuditName`, `Global.rapidIdentityAuditName` |
| `targetID` | No | The `idautoID` of the record being acted on |
| `target` | No | Display identifier: `record.displayName \|\| record.idautoPersonSAMAccountName \|\| record.mail \|\| record['@dn']` |
| `successful` | Yes | `true` after a confirmed write; `false` on failure |
| `extendedProperties` | No | **Always pass the record being changed.** |
| `perpetratorID` | No | Only in Alternate Actions or user-driven flows — use the `perp_dn` input property (see `references/ri-alternate-actions.md`) |
| `perpetratorDN` | No | Same as above |
| `groupID` | No | Pass a shared ID to group multiple related events into one logical operation |

### Standard Pattern

```xml
<action name="logAuditEvent">
  <arg name="eventName" value="&quot;updateAccount&quot;"/>
  <arg name="targetSystem" value="Global.adAuditName"/>
  <arg name="targetID" value="record.idautoID"/>
  <arg name="target" value="record.displayName || record.idautoPersonSAMAccountName || record.mail || record['@dn']"/>
  <arg name="successful" value="true"/>
  <arg name="extendedProperties" value="record"/>
</action>
```

### eventName Values

**Account:**
`createAccount` · `updateAccount` · `deleteAccount` · `disableAccount` · `enableAccount` · `moveAccount` · `renameAccount` · `changePassword`

**Group:**
`createGroup` · `updateGroup` · `deleteGroup` · `moveGroup` · `renameGroup` · `addGroupMember` · `removeGroupMember`

**Mailbox:**
`createMailbox` · `updateMailbox` · `deleteMailbox` · `disableMailbox` · `enableMailbox`

**Distribution List:**
`createDistributionList` · `updateDistributionList` · `deleteDistributionList` · `moveDistributionList` · `renameDistributionList` · `addDistributionListMember` · `removeDistributionListMember`

---

## Global Properties

**Never hardcode** DNs, hostnames, paths, filenames, or credentials. Reference them via a Global.

**In an action set, a global is always referenced as `Global.variableName`** — regardless of where
the value is defined. This holds even for values defined in `SharedGlobals.properties`: they are
still referenced as `Global.variableName`, **never** `SharedGlobal.variableName`. The
`SharedGlobal.` prefix is never used in action set expressions.

- `Global.propertyKey` — the only form used to reference a global in an action set

The canonical set of standard shared global keys — organized by system (AD, Google, M365, Database,
OneRoster, File/SFTP, Metadirectory, RI defaults) with type annotations (string, encrypted, json
array, json object) — is in **`references/shared-globals.md`**. Check there first before inventing a
key name. (Those keys are defined in `SharedGlobals.properties`, but you still reference them as
`Global.<key>` in the action set.)

**`json()`-wrapped globals are pre-parsed natives.** A value defined as `json([...])` or
`json({...})` in `SharedGlobals.properties` is parsed by Connect at load time, so `Global.<key>` is
already a native array/object - index it, read `.length`, access properties, and call array methods
directly. **Never** wrap it in `parseJSON` / `JSON.parse`: that coerces the native value to a string
first and throws `SyntaxError` at runtime. (This mirrors `encrypt()` values, which are
auto-decrypted on access.) Parsing is only ever for raw JSON *strings*.

---

## argDef Rules

Every parameter must have a `description` attribute. Types:
`string` | `boolean` | `number` | `object` | `array` | `enum:val1,val2,...`

```xml
<argDefs>
  <argDef name="logOnly"   type="boolean" optional="true"  description="Suppress all write operations when true."/>
  <argDef name="logLevel"  type="enum:quiet,normal,debug" optional="true" description="Controls logging verbosity."/>
  <argDef name="session"   type="object" optional="true" description="Existing directory session. Opens one if not provided."/>
</argDefs>
```

---

## Skeleton Templates

### Function action set

```xml
<actionDef xmlns="urn:idauto.net:dss:actiondef" name="FnMyFunction" returnsValue="true" description="Function - RI: One-sentence description."><argDefs><argDef name="session" type="object" optional="true" description="Existing directory session; opens one if omitted."/><argDef name="logOnly" type="boolean" optional="true" description="Suppress writes when true."/><argDef name="logLevel" type="enum:quiet,normal,debug" optional="true" description="Logging verbosity."/></argDefs><actions><action id="00000001-0000-0000-0000-000000000001" name="section" outputVar="" disabled="false"><arg name="label" value="about"/><arg name="suppressTrace" value="true"/><arg name="do"><action id="00000001-0000-0000-0000-000000000002" name="comment" outputVar="" disabled="false"><arg name="comment" value="Last Modified By: "/></action><action id="00000001-0000-0000-0000-000000000003" name="comment" outputVar="" disabled="false"><arg name="comment" value="Last Modified Date: YYYY-MM-DD"/></action><action id="00000001-0000-0000-0000-000000000004" name="comment" outputVar="" disabled="false"><arg name="comment" value="Purpose:"/></action><action id="00000001-0000-0000-0000-00000000000A" name="comment" outputVar="" disabled="false"><arg name="comment" value="  One-paragraph logical overview: what it does, inputs, outputs, key branches."/></action><action id="00000001-0000-0000-0000-00000000000B" name="comment" outputVar="" disabled="false"><arg name="comment" value="Overview (pseudo-code):"/></action><action id="00000001-0000-0000-0000-00000000000C" name="comment" outputVar="" disabled="false"><arg name="comment" value="  describe the flow in plain words, indented for nesting"/></action><action id="00000001-0000-0000-0000-000000000005" name="comment" outputVar="" disabled="false"><arg name="comment" value="Parameters:"/></action><action id="00000001-0000-0000-0000-000000000006" name="comment" outputVar="" disabled="false"><arg name="comment" value="  session [optional]: Existing directory session."/></action><action id="00000001-0000-0000-0000-000000000007" name="comment" outputVar="" disabled="false"><arg name="comment" value="  logOnly [optional]: Suppress writes when true."/></action><action id="00000001-0000-0000-0000-000000000008" name="comment" outputVar="" disabled="false"><arg name="comment" value="  logLevel [optional]: quiet | normal | debug."/></action><action id="00000001-0000-0000-0000-000000000009" name="comment" outputVar="" disabled="false"><arg name="comment" value="================== Change Log =================="/></action><action id="00000001-0000-0000-0000-000000000010" name="comment" outputVar="" disabled="false"><arg name="comment" value="YYYY-MM-DD (Name): Initial version."/></action></arg></action><action id="00000002-0000-0000-0000-000000000001" name="section" outputVar="" disabled="false"><arg name="label" value="defineDefaultVariables"/><arg name="suppressTrace" value="true"/><arg name="do"><action id="00000002-0000-0000-0000-000000000002" name="setVariable" outputVar="" disabled="false"><arg name="name" value="process"/><arg name="value" value="{actionSetName:getCurrentActionSetName(),processID:getProcessID(),processJobName:getProcessJobName()||getProcessTopLevelActionSetName(),processLogFile:getProcessLogFile(),processProject:getProcessProject() == &quot;&quot; ? &quot;Main&quot; : getProcessProject(),processStartTime:formatDate(getProcessStartTime(),&quot;yyyy-MM-dd HH:mm:ss&quot;,Global.localTimeZone),runningIDHub:runningIDHub()}"/></action><action id="00000002-0000-0000-0000-000000000003" name="setVariable" outputVar="" disabled="false"><arg name="name" value="logLevel"/><arg name="value" value="logLevel || &quot;quiet&quot;"/></action><action id="00000002-0000-0000-0000-000000000004" name="setVariable" outputVar="" disabled="false"><arg name="name" value="logColors"/><arg name="value" value="Object.assign({changedData:&quot;chocolate&quot;,complete:&quot;teal&quot;,counts:&quot;black&quot;,data:&quot;blue&quot;,debug:&quot;purple&quot;,error:&quot;red&quot;,fail:&quot;darkred&quot;,info:&quot;royalBlue&quot;,logOnly:&quot;slateGray&quot;,processing:&quot;steelBlue&quot;,query:&quot;darkcyan&quot;,skipped:&quot;mediumpurple&quot;,sourceData:&quot;dimGray&quot;,success:&quot;green&quot;,targetData:&quot;darkslategray&quot;,test:&quot;darkorange&quot;,warn:&quot;goldenrod&quot;,whitespace:&quot;white&quot;},Global.connectLogColorSchema||{})"/></action><action id="00000002-0000-0000-0000-000000000005" name="setVariable" outputVar="" disabled="false"><arg name="name" value="counts"/><arg name="value" value="{processed:0,add:0,update:0,skip:0,error:0}"/></action></arg></action><action id="00000003-0000-0000-0000-000000000001" name="section" outputVar="" disabled="false"><arg name="label" value="establishConnections"/><arg name="suppressTrace" value="true"/><arg name="do"><action id="00000003-0000-0000-0000-000000000002" name="comment" outputVar="" disabled="false"><arg name="comment" value="Function mode: use provided session or open one."/></action></arg></action><action id="00000004-0000-0000-0000-000000000001" name="section" outputVar="" disabled="false"><arg name="label" value="mainLogic"/><arg name="suppressTrace" value="true"/><arg name="do"><action id="00000004-0000-0000-0000-000000000002" name="comment" outputVar="" disabled="false"><arg name="comment" value="Core logic here."/></action></arg></action><action id="00000005-0000-0000-0000-000000000001" name="section" outputVar="" disabled="false"><arg name="label" value="closeConnections"/><arg name="suppressTrace" value="true"/><arg name="do"><action id="00000005-0000-0000-0000-000000000002" name="comment" outputVar="" disabled="false"><arg name="comment" value="Close only if we opened (check closeSession flag)."/></action></arg></action><action id="00000006-0000-0000-0000-000000000001" name="section" outputVar="" disabled="false"><arg name="label" value="outputCounts"/><arg name="suppressTrace" value="true"/><arg name="do"><action id="00000006-0000-0000-0000-000000000002" name="log" outputVar="" disabled="false"><arg name="message" value="&quot;Counts -- processed: &quot; + counts.processed + &quot; | add: &quot; + counts.add + &quot; | update: &quot; + counts.update + &quot; | skip: &quot; + counts.skip + &quot; | error: &quot; + counts.error"/><arg name="level" value="&quot;INFO&quot;"/></action></arg></action></actions></actionDef>
```

### Scheduled Job (Manage/Sync)

Same skeleton but `returnsValue="false"` and `description` uses the `Scheduled Job -` prefix.
Common additional parameters: `logOnly`, `logLevel`, `resetCookie`, `fullSync`.

---

## Validation Checklist

Before delivering any XML:

1. **`xmllint --noout file.xml`** — must pass with zero errors
2. **No `<?xml` declaration** at the top
3. **All sections** have `suppressTrace="true"`
4. **No bare top-level actions** — all actions inside a section
5. **No hardcoded DNs, hostnames, or credentials** — reference via `Global.*`
6. **No `builtIn` or `community` attributes** on user-defined action sets
7. **Bracket notation only** for keys with `@` or `-`; plain identifiers use dot notation
8. **`&quot;` used** for embedded double-quotes in `<arg value="...">` attributes
9. **XML metacharacters escaped in `value=`** — `&&`→`&amp;&amp;`, `<`→`&lt;`, `>`→`&gt;`. Item 1
    (`xmllint`) catches this, but check explicitly — bare `&&` is the most common ill-formedness bug
10. **Tag balance** — count `<arg name="do">`, `<arg name="then">`, `<arg name="else">` opens
    vs `</arg>` closes; they must match
11. **All `argDef` elements** have a `description` attribute
12. **`logAuditEvent` called** after every write to an external system (`targetID` = idautoID, `extendedProperties` = the record)
13. **Structured data is serialised with `toJSON(obj)`** (not `JSON.stringify`); bare `{...}` /
    `[...]` literals still fail the compiler in a `setVariable value=` - seed with the
    **`createRecord`** / **`createArray`** actions, never `parseJSON('{}')` / `parseJSON('[]')`
14. **String constants containing `"` use single-quote delimiters** — `'&quot;key&quot;:value'`
    not `&quot;\\&quot;key\\&quot;:&quot;value&quot;` (prefer single-quote delimiters; a literal backslash must be doubled — see § String escapes)
15. **Every `<action>` has `id` (uppercase UUID) and `disabled="false"`** — missing these makes
    actions read-only and non-interactive in the Connect editor
16. **Editor-facing text is plain ASCII** — no em/en dashes, smart quotes, ellipsis, or HTML/markdown
    in `comment` values, the `description` attribute, or section labels (log messages are exempt)
17. **Literal backslashes are doubled** — a literal `\` in any string value is written `\\`
18. **No `if` action has duplicate direct `then`/`else` args.** Two common causes, same symptom
    (`Can't redefine property 'if.else'` or `'if.<action>'`): (a) hand-authoring a three-way
    `if/else if/else` branch and attaching the default block to the outer `if` instead of the
    inner nested `if` — see the callout under § if / while / break; (b) via the MCP JSON, sibling
    actions placed after a mid-block nested `if`/`while` in the same `then`/`else`/`do` get hoisted
    onto the parent `if`. Fix: make the nested block the last element of its container, or flatten
    to ternary `setVariable`s. After any MCP save, re-fetch and confirm the `version` incremented
    (a client timeout does not mean the save failed)
19. **No `parseJSON` used as a container constructor, and no dotted `setVariable` writing a Record
    field.** Grep for `parseJSON` with a `'{}'` / `'[]'` argument, and for `setVariable` whose
    `name` is `<var>.<field>` on a Record — these should be `createRecord`, `createArray`, and
    `setRecordFieldValue`. Check too that any Record whose values are compared strictly or used in
    arithmetic was **not** built with `createRecordFromObject`, which stringifies every value.
    See § Records & arrays - construction

---

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Section label `return` | Rename to `returnSuccess`, `returnRecord`, etc. |
| `&quot;quoted&quot;` value on `section`/`forEach`/`while`/`continue`/`break`'s `label` arg | Write the bare identifier — `label` is `type="name"` on these, not an expression. The validator does not catch this (it exempts `label` from expression checking), so it passes clean while the label literally contains quote characters. `caFnCoreLog`'s `label` is the one exception — that one IS `type="string"` and does get quoted. See § Section Labels |
| Hardcoded base DNs or hostnames | Use `Global.*` references |
| `SharedGlobal.` prefix in an action set | Reference every global as `Global.variableName` — `SharedGlobal.` is never used in action set expressions |
| `builtIn="false"` on user action set | Remove the attribute entirely |
| `record['idautoID']` bracket notation | Change to `record.idautoID` — brackets only for `@` or `-` keys |
| Individual counter variables (`addCount`, `updateCount`) | Use a single `counts` object |
| Opening a connection inside a function when a session was passed | Check `!session` first |
| Using generic `openConnection` for AD, RI, Google, Portal | Non-CA: use `FnCoreOpenConnections`; CA: use the typed built-in — see `references/connections.md` |
| XML written with pretty-print indentation | Flatten to single-line compact output |
| Bare `{...}` or `[...]` literal in `setVariable value=` | Fails the JS compiler — seed with the `createRecord` / `createArray` actions; see § Records & arrays - construction and `references/native-action-cheatsheet.md` |
| `parseJSON('{}')` / `parseJSON('[]')` to seed an empty container | Never do this — `parseJSON` parses JSON *strings*. Use `createRecord` (object) / `createArray` (array). See § Records & arrays - construction |
| `setVariable name="rec.field"` to set a Record field | Use `setRecordFieldValue` (`record`/`field`/`value`); `setRecordFieldValues` for multi-valued. Dot notation is for *reading* |
| `createRecordFromObject` for a Record whose values get compared or added | It stringifies every value — `true` → `"true"` (truthy!), `50` → `"50"` (fails `!== 100`). Build with `createRecord` + `setRecordFieldValue` to keep native types |
| Bare `&&`, `<`, or `>` in a `value=` expression | Escape as `&amp;&amp;`, `&lt;`, `&gt;` — bare metacharacters make the XML ill-formed before the JS compiler runs |
| `setVariable` to copy a Record or extract from results array | Use `copyRecord` — `setVariable` aliases, not copies; mutation on one affects both. Applies to snapshots, `results[0]` extraction, and loop guards |
| `setVariable` to copy an array before removing items in a loop | Use `copyArray` — same alias problem; mutating the array being iterated breaks `forEach` |
| `FnHasRecordChanged` returns false when changes were made | Both args point to the same object due to `setVariable` aliasing — `copyRecord` for the snapshot before mutation |
| `<action>` missing `id` or `disabled` | Actions render read-only in Connect editor — every action needs `id="UPPERCASE-UUID"` and `disabled="false"` |
| `forEach` with `item` / `items` args | Wrong arg names — use `variable` (loop var name) and `collection` (the array) |
| `getLDAPRecords` with `attributes` value `[]` | Bare array literal fails the expression compiler — use `"*,+"`, `"*"`, or `"attr1,attr2"` |
| Nesting arg (`do`/`then`/`else`) has a `"value"` field | Remove `value` from nesting args — its presence causes `Property must be a list of actions`; correct form: `{"name":"do","actions":[...]}` |
| HTML or markdown in a `log` message | The log viewer is plain text — tags appear literally; use `\n`, `\t`, and the `color` arg for layout |
| Em dash / smart quotes in a comment, description, or section label | Use plain ASCII — the Connect editor does not render extended punctuation (log messages are fine) |
| Single backslash for a literal `\` | Double it — a literal backslash is `\\`; a single `\` escapes the next character |
| `recordChanges.length` on a change iterator result | Always `undefined` — the result is a Connect iterator, not an array; count by incrementing a variable inside `forEach` — see § Change Iterators |
| Sibling actions after a mid-block nested `if` (MCP save) | They get hoisted onto the parent `if` and break compile (`Can't redefine property 'if.<action>'`) — make the nested `if` the last element, or flatten to ternary `setVariable`s |
| Hand-authored `if/else if/else` puts the default block on the outer `if` | Connect has no `else if` — a three-way branch nests an `if` inside the outer `else`; the default block belongs to the *inner* `if`'s `else`, not a second `else` on the outer `if`. Same `Can't redefine property 'if.else'` error — see callout under § if / while / break |
| `"" + record` or `JSON.stringify(obj)` to build JSON | Yields a Java map `toString`; `JSON.stringify` also misses Records — always use `toJSON(record)` |
| `parseJSON` on malformed input | Auto-logs its own ERROR, returns `undefined`, does not abort — pre-gate with `isValidJSON` JS function for clean branching |
| `JSON.parse(Global.jsonWrappedVar)` | Throws `SyntaxError` — a `json()` global is already a native value; reference it directly without parsing |
| Running a bare, unsaved action via the MCP | `NullPointerException` in `compileActionDef` — save the action set first, then run by name; see `references/mcp-and-json.md` |
| Expecting a failed built-in to throw | Built-ins never throw — they return `undefined`/`false` and set `lastErrorMessage`/`lastErrorCode`. Check return values; see § Built-in failure model |
| Reading `getLastErrorMessage()` after an ERROR-level `log` | `log level="ERROR"` clears and **overwrites** `lastErrorMessage` with your own message — capture the platform error into a variable *before* logging it |
| `loadFileAsString` producing mangled accented characters | Its default encoding is **LATIN1 (ISO-8859-1), not UTF-8** — pass the encoding arg explicitly for UTF-8 files; `saveToFile` defaults also differ by type (UTF-8 for XML, ISO-8859-1 for strings) |
| Treating `getIdautoIDForUser`/`getIdautoIDForGroup` as read-only lookups | They **create the idautoID if missing** — calling one on the wrong DN mints a new immutable ID; not safe as an existence probe |
| `copyArray` as a snapshot of an array of Records | `copyArray` is **shallow** — the Records inside are still shared; mutating them mutates the "snapshot". `copyRecord` each element |
| Concatenating raw values into an LDAP filter | Use `stringEscape` with `escapeType="ldap-filter"` (or `ldap-dn` for DN parts) — unescaped `( ) * \` in user data breaks or injects into the filter |

---

## HTTP Actions — REST API Patterns

### `httpPOST` — JSON body requirement

The `data` argument of `httpPOST` is sent as-is as the request body. A raw JS object will
serialize as `[object Object]`, causing a 400 parse error. **Always wrap the body in `toJSON()`**
when the endpoint expects JSON (`toJSON` is the standard JSON serializer throughout - see § Serialising structured data - not an HTTP-only idiom):

```xml
<action name="setVariable">
  <arg name="name" value="body"/>
  <arg name="value" value="toJSON({field1: value1, field2: value2})"/>
</action>
<action name="httpPOST" outputVar="apiResponse">
  <arg name="url" value="sessionPortal.url + &quot;api/rest/v2/someEndpoint&quot;"/>
  <arg name="headers" value="{&quot;Accept&quot;: &quot;application/json&quot;, &quot;Content-Type&quot;: &quot;application/json&quot;, &quot;Authorization&quot;: &quot;Bearer &quot; + sessionPortal.token}"/>
  <arg name="data" value="body"/>
</action>
```

### Date formatting for REST APIs

Workflow `DATE_TIME` form fields emit a full ISO 8601 timestamp (e.g. `2026-05-01T01:24:14.000Z`).
Most RI REST APIs expect plain `YYYY-MM-DD`. Use `.substring(0,10)` to trim:

```xml
<arg name="value" value="toJSON({expirationDate: (dateField ? dateField.substring(0,10) : null)})"/>
```

### HTTP status code handling

Always check `statusCode` explicitly. Key RI Sponsorship API codes:

| Code | Meaning |
|---|---|
| `200` | Success |
| `400` | Bad request — malformed body or invalid field value |
| `409` | Conflict — duplicate detected (when `checkForDuplicates: true`) |

---

## `delay` Action — Timed Pauses

Use the built-in `delay` action to pause execution. Required in polling loops where a downstream
system may not have committed a record yet.

```xml
<action name="delay">
  <arg name="seconds" value="1"/>
</action>
```

---

## LDAP Polling Loop Pattern

Use this pattern when an LDAP record may not yet exist after an upstream write (e.g. after a
REST API creates a sponsored account, the metadirectory sync has not completed yet).

```xml
<!-- Init loop state in defineDefaultVariables or before the loop -->
<action name="setVariable"><arg name="name" value="lookupAttempt"/><arg name="value" value="0"/></action>
<action name="setVariable"><arg name="name" value="lookupMaxAttempts"/><arg name="value" value="15"/></action>
<action name="setVariable"><arg name="name" value="foundRecord"/><arg name="value" value="null"/></action>

<action name="while">
  <arg name="condition" value="!foundRecord &amp;&amp; lookupAttempt &lt; lookupMaxAttempts"/>
  <arg name="do">
    <action name="setVariable"><arg name="name" value="lookupAttempt"/><arg name="value" value="lookupAttempt + 1"/></action>
    <action name="getLDAPRecords" outputVar="ldapResults">
      <arg name="ldapConnection" value="sessionRI"/>
      <arg name="baseDn" value="Global.metaEmployeeBaseDN"/>
      <arg name="scope" value="&quot;sub&quot;"/>
      <arg name="filter" value="&quot;(idautoPersonUserNameMV=&quot; + username + &quot;)&quot;"/>
      <arg name="attributes" value="&quot;idautoPersonClaimCode,mail,idautoPersonUserNameMV&quot;"/>
      <arg name="maxResults" value="1"/>
    </action>
    <action name="if">
      <arg name="condition" value="ldapResults &amp;&amp; ldapResults.length &gt; 0"/>
      <arg name="then">
        <action name="copyRecord" outputVar="foundRecord"><arg name="record" value="ldapResults[0]"/></action>
        <action name="break"/>
      </arg>
      <arg name="else">
        <action name="delay"><arg name="seconds" value="1"/></action>
      </arg>
    </action>
  </arg>
</action>

<!-- Warn if record never found after all attempts -->
<action name="if">
  <arg name="condition" value="!foundRecord"/>
  <arg name="then">
    <action name="log">
      <arg name="message" value="process.actionSetName + &quot;: lookupRecord -- record not found after &quot; + lookupMaxAttempts + &quot; attempts.&quot;"/>
      <arg name="level" value="&quot;WARN&quot;"/>
      <arg name="color" value="logColors.warn"/>
    </action>
  </arg>
</action>
```

**Rules:**
- Always initialize `foundRecord = null` before the loop
- Test `ldapResults && ldapResults.length > 0` directly — `getLDAPRecords` returns `null` (no match) or an array
- Extract the record with `copyRecord`, never `setVariable` (which would alias, not copy)
- Use `break` inside the `then` branch once the record is found — do not continue polling
- Put `delay(1)` in the `else` branch only, so there is no delay on the successful attempt
- Log a `WARN` (not `ERROR`) if the loop exhausts — the caller decides how to handle a null result
- Cap at 15 attempts for a 1-second delay (15 seconds max wait); adjust for longer sync windows

---

## Change Iterators — no `.length`, count inside `forEach`

`openADChangeIterator` and `openOpenLDAPChangeIterator` return a **Connect iterator object**, not an
array. You **cannot** get the number of records from the changelog via `recordChanges.length` — it
returns `undefined`, and the records are not visible or enumerable until a `forEach` iterates the
iterator. Logging the object directly shows something like
`[ADChangeIterator DC=services,DC=local:sub:(&(objectClass=user)(!(objectClass=computer)))]`.

This applies to **both** the Active Directory and OpenLDAP change iterators.

The only way to count the records returned is to initialize a counter before the loop and increment
it inside the `forEach`:

```xml
<action name="setVariable"><arg name="name" value="total"/><arg name="value" value="0"/></action>
<action name="forEach">
  <arg name="variable" value="recordChange"/>
  <arg name="collection" value="recordChanges"/>
  <arg name="do">
    <action name="setVariable"><arg name="name" value="total"/><arg name="value" value="total + 1"/></action>
    <!-- process recordChange -->
  </arg>
</action>
<action name="log"><arg name="message" value="&quot;Total: &quot; + total"/></action>
```

**Rules:**
- Never test or branch on `recordChanges.length` — it is always `undefined` for a change iterator
- Initialize the counter (e.g. `total = 0`) before the loop; increment inside the `forEach do`
- The records only become accessible one at a time inside the loop body via the loop `variable`

---

## RI Sponsorship API

The RI Sponsorship API creates and manages sponsored accounts. It has several use-case-specific
details: the create-account request body shape, resolving custom attribute UUIDs from
`bootstrapInfo`, `409` duplicate handling, and the relevant endpoints.

**See `references/ri-sponsorship-api.md` for endpoints, the request body, and the custom-attribute
UUID resolution pattern.**

> For Alternate Actions that wrap sponsored-account operations, also see `references/ri-alternate-actions.md` — the Sponsorship AA input/output contracts differ from the direct Sponsorship API.

---
## WFM Action Set Pattern

Action sets that back portal workflows use the `WFM` prefix and follow a specific pattern:

- **Always return** `JSON.stringify(results)` from every exit path — the workflow reads `%{dss.fieldName}`
- **Accept `validateOnly`** — when true, validate all inputs and return without writing
- **Accept `logOnly`** — when true, skip all writes and return a logOnly message
- **Initialize a `results` record** in `defineDefaultVariables` with `success=false` and all output fields as empty strings
- **Every return path** must set `results.message` before returning

Standard results fields for a WFM action set:

```xml
<action name="createRecord" outputVar="results"/>
<action name="setRecordFieldValue"><arg name="record" value="results"/><arg name="field" value="&quot;success&quot;"/><arg name="value" value="false"/></action>
<action name="setRecordFieldValue"><arg name="record" value="results"/><arg name="field" value="&quot;message&quot;"/><arg name="value" value="&quot;&quot;"/></action>
```

Workflow variable substitution reference (full table including `%{form.*}`, `%{requester.*}`, `%{approval0.*}`, etc.) and form field type encoding: **`references/ri-workflow-variables.md`**.

---

## Reference Files

Always-on lookups:
- `references/connect-builtin-actions.json` — Full catalog of all built-in Connect action definitions (name, argDefs, description, returnsValue). **Consult this when you need to verify an action's exact parameter names, types, or whether it returns a value.** Use targeted reads or grep — do not load the entire file into context at once. (The count grows as the platform adds actions, so don't rely on a fixed number.)
- `references/openldap-schema.md` — Full RI OpenLDAP schema: all `idautoPerson` and `idautoGroup` attributes with cardinality (single/multi) and type. **Always consult this before referencing any LDAP attribute** — it determines whether `[].concat()` is needed and which `baseDn` Global to use.

Load-when-relevant (these were split out of SKILL.md to keep it lean):
- `references/connections.md` — Per-system connection details: AD, RI Metadirectory (incl. `getLDAPRecords` `baseDn`/`attributes` selection), Portal, Google + `callGoogleAPI`, Microsoft 365, Database, the AES Community Adapter encrypt/decrypt sequence, failure handling, and closing. **Read before authoring any connection logic.**
- `references/mcp-and-json.md` — MCP workflow (read/explore, design, push, delete), the JSON object model (file JSON vs API JSON, argDef/action/arg shapes), and field-by-field XML ↔ JSON conversion. **Read when working against a live instance via the MCP or converting formats.**
- `references/ri-sponsorship-api.md` — RI Sponsorship API endpoints, create-account request body, and custom-attribute UUID resolution. **Read only for sponsored-account work.**
- `references/ri-start-portal-workflow.md` — `startPortalWorkflow` built-in action: signature, required portal session, `entitlementId` lookup, `formData` Record prep, and a full skeleton. **Read when submitting a WFM request programmatically from Connect (e.g. an Alternate Action or scheduled job).**
- `references/ri-alternate-actions.md` — Input properties and return contracts for all 10 Alternate Action types (Profiles, Groups, Sponsorship). **Read when writing an AA action set.**
- `references/ri-workflow-variables.md` — `%{...}` variable substitution table, `valuePairs` format, WFM return contract, form field types. **Read when writing WFM action sets or workflow definitions.**
- `references/ri-connect-admin-api.md` — Connect admin REST endpoints for triggering jobs, listing/killing processes, reading/writing files, listing action sets. **Read when writing action sets that manage Connect itself.**
- `references/oracle-fusion-hcm-api.md` — Oracle Fusion HCM Workers API: auth patterns (Basic + OAuth2), endpoint, pagination, key fields, gotchas. **Read when writing action sets that call Oracle HCM.**
- `references/skyward-qmlativ-api.md` — Skyward Qmlativ Custom API: auth action set, retrieval functions, pagination, global variables. **Read when writing action sets that call Skyward Qmlativ.**
- `references/shared-globals.md` — Standard SharedGlobals variable names by category with type annotations (encrypted, json array, json object, string). **Read when looking up the canonical key name for any system credential, base DN, path, or configuration value.**

Load the always-on files when you need a specific action's parameters or an LDAP attribute; load the
others only for the matching task. The SKILL.md body covers everything needed for day-to-day authoring.

---

## MCP Workflow

The RapidID MCP Server (`mcp-rapidid`) covers the full authoring loop: discovery
(`get-connect-projects`, `get-connect-actions`, `get-connect-action`), write
(`save-connect-action`, `delete-connect-action` — always confirm before deleting), execution
(`run-connect-action` — returns the HTML job log), and project files
(`get-connect-files`, `get-connect-file-content` — Globals/SharedGlobals, scripts, job/run logs).
It also exposes identity tools (`search-users`, `search-groups`, `get-group-members`,
`get-user-activity-from-audit-log`, …) useful for test data and post-run verification.

`mcp-rapidid` supports opt-in usage telemetry (`MCP_RAPIDID_TELEMETRY=true` in its MCP server
config) — anonymous tool name/duration/error data sent to TelemetryDeck, off by default, no
credentials/args/PII collected. See the server's README § Telemetry for the full data list.

**Full MCP workflow (read/explore, run-and-verify, file access, the JSON object model, and
field-by-field XML ↔ JSON conversion rules) is in `references/mcp-and-json.md`.**

---
