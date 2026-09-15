# Connect Native Action Cheat Sheet

Fast lookup: task → builtin → verified call. Every entry shows:
- **XML** — for file/disk authoring
- **MCP JSON** — the exact object to pass to `save-connect-action` (or embed in a parent `actions` array)

XML → JSON conversion rules: `&quot;` → `"`, `&amp;` → `&`, `&lt;` → `<`, `&gt;` → `>`. Nesting args (`do`/`then`/`else`) use `{"name":"do","actions":[...]}` with no `value` field. Every action needs a unique UUID `id`; omit `disabled` for enabled actions.

Inline-JS temptations are noted where a native builtin exists. When no native exists, inline JS in `setVariable value=` is fine.

---

## Strings

### `splitString` — split on delimiter

**Inline-JS temptation:** `str.split(',')`

**XML:**
```xml
<action id="UUID" name="splitString" outputVar="parts" disabled="false">
  <arg name="string" value="str"/>
  <arg name="delimiter" value="&quot;,&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"splitString","outputVar":"parts","args":[
  {"name":"string","value":"str"},
  {"name":"delimiter","value":"\",'\""}
]}
```

Returns array. Single-value input with no matching delimiter → one-element array.

---

### `stringContains` — substring or regex match

**Inline-JS temptation:** `str.toLowerCase().includes('x')` or `str.match(/\d/)`

**XML:**
```xml
<action id="UUID" name="stringContains" outputVar="found" disabled="false">
  <arg name="string" value="str"/>
  <arg name="pattern" value="&quot;x&quot;"/>
  <arg name="ignoreCase" value="true"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"stringContains","outputVar":"found","args":[
  {"name":"string","value":"str"},
  {"name":"pattern","value":"\"x\""},
  {"name":"ignoreCase","value":"true"}
]}
```

`pattern` accepts plain string **or regex literal** (`/\d/`). Omit `ignoreCase` when not needed.

---

### `stringEquals` — exact match or regex test

**Inline-JS temptation:** `str === 'x'` or `str.match(/^pattern$/) !== null`

**XML:**
```xml
<action id="UUID" name="stringEquals" outputVar="ok" disabled="false">
  <arg name="string" value="str"/>
  <arg name="pattern" value="/^[\w.]+@[\w.]+$/"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"stringEquals","outputVar":"ok","args":[
  {"name":"string","value":"str"},
  {"name":"pattern","value":"/^[\\w.]+@[\\w.]+$/"}
]}
```

With a regex pattern this is a match test, not literal equality.

---

### `stringStartsWith` / `stringEndsWith`

**XML:**
```xml
<action id="UUID" name="stringStartsWith" outputVar="ok" disabled="false">
  <arg name="string" value="str"/>
  <arg name="pattern" value="&quot;CN=&quot;"/>
  <arg name="ignoreCase" value="true"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"stringStartsWith","outputVar":"ok","args":[
  {"name":"string","value":"str"},
  {"name":"pattern","value":"\"CN=\""},
  {"name":"ignoreCase","value":"true"}
]}
```

---

### `stringToUpper` / `stringToLower`

**XML:**
```xml
<action id="UUID" name="stringToUpper" outputVar="result" disabled="false">
  <arg name="string" value="str"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"stringToUpper","outputVar":"result","args":[
  {"name":"string","value":"str"}
]}
```

---

### `stringLength`

**XML:**
```xml
<action id="UUID" name="stringLength" outputVar="len" disabled="false">
  <arg name="string" value="str"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"stringLength","outputVar":"len","args":[
  {"name":"string","value":"str"}
]}
```

`str.length` inline also works; native preferred for explicitness.

---

### `stringRepeat`

**Inline-JS temptation:** `str.repeat(3)`

**XML:**
```xml
<action id="UUID" name="stringRepeat" outputVar="result" disabled="false">
  <arg name="text" value="str"/>
  <arg name="count" value="3"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"stringRepeat","outputVar":"result","args":[
  {"name":"text","value":"str"},
  {"name":"count","value":"3"}
]}
```

---

### `stringReplaceAll` / `stringReplaceFirst`

**Inline-JS temptation:** `str.split('x').join('y')` or `str.replace('x','y')`

**XML:**
```xml
<action id="UUID" name="stringReplaceAll" outputVar="result" disabled="false">
  <arg name="string" value="str"/>
  <arg name="match" value="&quot;x&quot;"/>
  <arg name="replacement" value="&quot;y&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"stringReplaceAll","outputVar":"result","args":[
  {"name":"string","value":"str"},
  {"name":"match","value":"\"x\""},
  {"name":"replacement","value":"\"y\""}
]}
```

---

### `subString`

**Inline-JS temptation:** `str.substring(0, 5)`

**XML:**
```xml
<action id="UUID" name="subString" outputVar="result" disabled="false">
  <arg name="string" value="str"/>
  <arg name="startIndex" value="0"/>
  <arg name="length" value="5"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"subString","outputVar":"result","args":[
  {"name":"string","value":"str"},
  {"name":"startIndex","value":"0"},
  {"name":"length","value":"5"}
]}
```

---

### `stringFromTemplate` — `%field%` substitution

**XML:**
```xml
<action id="UUID" name="stringFromTemplate" outputVar="result" disabled="false">
  <arg name="format" value="&quot;Hello %givenName%, your ID is %idautoID%&quot;"/>
  <arg name="args" value="record"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"stringFromTemplate","outputVar":"result","args":[
  {"name":"format","value":"\"Hello %givenName%, your ID is %idautoID%\""},
  {"name":"args","value":"record"}
]}
```

`args` can be a record (uses field names as keys) or an array (uses `%0%`, `%1%`, etc.).

---

### `stringEscape` — 12 escape methods (HTML, URL, LDAP, SQL, CSV, …)

**XML:**
```xml
<action id="UUID" name="stringEscape" outputVar="result" disabled="false">
  <arg name="string" value="str"/>
  <arg name="escapeType" value="&quot;html&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"stringEscape","outputVar":"result","args":[
  {"name":"string","value":"str"},
  {"name":"escapeType","value":"\"html\""}
]}
```

`escapeType` values (12): `ecmascript`, `html`, `java`, `ldap-dn`, `ldap-filter`, `sql`, `mysql`,
`postgresql`, `uri`, `url`, `xml`, `csv`. Input may be a string, array, or Record (values escaped
element-wise). Use `ldap-filter` for values concatenated into LDAP search filters and `ldap-dn` for
DN components — never build filters from raw user data.

---

### `stringRemoveDiacriticals`

**XML:**
```xml
<action id="UUID" name="stringRemoveDiacriticals" outputVar="result" disabled="false">
  <arg name="string" value="str"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"stringRemoveDiacriticals","outputVar":"result","args":[
  {"name":"string","value":"str"}
]}
```

Strips combining diacritics. Precomposed letters (Ø, Å) with no combining-form decomposition pass through unchanged.

---

### `toString` — number/boolean/float to string

**XML:**
```xml
<action id="UUID" name="toString" outputVar="result" disabled="false">
  <arg name="value" value="numVar"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"toString","outputVar":"result","args":[
  {"name":"value","value":"numVar"}
]}
```

---

## Arrays

### `createArray` — empty or pre-sized

**Inline-JS temptation:** `arr = []` — **bare `[]` literal fails the Connect expression compiler**

**Also wrong:** `parseJSON('[]')`. It compiles, so nothing flags it, but `parseJSON` is a
JSON-*string* parser, not a container constructor — seed an empty array with `createArray`.

**XML:**
```xml
<!-- empty -->
<action id="UUID" name="createArray" outputVar="arr" disabled="false"/>
<!-- pre-sized with nulls -->
<action id="UUID" name="createArray" outputVar="arr" disabled="false">
  <arg name="size" value="3"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"createArray","outputVar":"arr","args":[]}
```
```json
{"id":"UUID","name":"createArray","outputVar":"arr","args":[
  {"name":"size","value":"3"}
]}
```

---

### `copyArray` — shallow copy (new array, shared elements)

**Inline-JS temptation:** `setVariable copy = arr` — **alias, not a copy; mutations affect both**

**Shallow:** the copy is a new array object, but nested objects/Records inside it are still shared
references. Fine for the iterate-and-remove mutation guard; NOT a snapshot of an array of Records —
`copyRecord` each element if the Records themselves will mutate. (`sliceArray` is shallow too.)

**XML:**
```xml
<action id="UUID" name="copyArray" outputVar="copy" disabled="false">
  <arg name="array" value="arr"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"copyArray","outputVar":"copy","args":[
  {"name":"array","value":"arr"}
]}
```

---

### `appendArrayItem` / `appendArrayItems`

**Inline-JS temptation:** `arr.push(item)` (returns length, not array)

**XML:**
```xml
<action id="UUID" name="appendArrayItem" disabled="false">
  <arg name="array" value="arr"/>
  <arg name="item" value="item"/>
</action>
<action id="UUID" name="appendArrayItems" disabled="false">
  <arg name="array" value="dest"/>
  <arg name="items" value="src"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"appendArrayItem","args":[
  {"name":"array","value":"arr"},
  {"name":"item","value":"item"}
]}
```
```json
{"id":"UUID","name":"appendArrayItems","args":[
  {"name":"array","value":"dest"},
  {"name":"items","value":"src"}
]}
```

---

### `getArraySize` / `getArrayItem` / `setArrayItem`

**XML:**
```xml
<action id="UUID" name="getArraySize" outputVar="size" disabled="false">
  <arg name="array" value="arr"/>
</action>
<action id="UUID" name="getArrayItem" outputVar="item" disabled="false">
  <arg name="array" value="arr"/>
  <arg name="index" value="2"/>
</action>
<action id="UUID" name="setArrayItem" disabled="false">
  <arg name="array" value="arr"/>
  <arg name="index" value="1"/>
  <arg name="item" value="&quot;x&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"getArraySize","outputVar":"size","args":[
  {"name":"array","value":"arr"}
]}
```
```json
{"id":"UUID","name":"getArrayItem","outputVar":"item","args":[
  {"name":"array","value":"arr"},
  {"name":"index","value":"2"}
]}
```
```json
{"id":"UUID","name":"setArrayItem","args":[
  {"name":"array","value":"arr"},
  {"name":"index","value":"1"},
  {"name":"item","value":"\"x\""}
]}
```

---

### `insertArrayItem` / `insertArrayItems`

**Inline-JS temptation:** `arr.splice(2, 0, 'c')`

**XML:**
```xml
<action id="UUID" name="insertArrayItem" disabled="false">
  <arg name="array" value="arr"/>
  <arg name="index" value="2"/>
  <arg name="item" value="&quot;c&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"insertArrayItem","args":[
  {"name":"array","value":"arr"},
  {"name":"index","value":"2"},
  {"name":"item","value":"\"c\""}
]}
```

`insertArrayItems` replaces `item` with `items` (an array).

---

### `removeArrayItem` / `removeArrayItems` / `removeLastArrayItem`

**XML:**
```xml
<action id="UUID" name="removeArrayItem" outputVar="removed" disabled="false">
  <arg name="array" value="arr"/>
  <arg name="index" value="i"/>
</action>
<action id="UUID" name="removeArrayItems" outputVar="removed" disabled="false">
  <arg name="array" value="arr"/>
  <arg name="index" value="i"/>
  <arg name="count" value="n"/>
</action>
<action id="UUID" name="removeLastArrayItem" outputVar="item" disabled="false">
  <arg name="array" value="arr"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"removeArrayItem","outputVar":"removed","args":[
  {"name":"array","value":"arr"},
  {"name":"index","value":"i"}
]}
```
```json
{"id":"UUID","name":"removeArrayItems","outputVar":"removed","args":[
  {"name":"array","value":"arr"},
  {"name":"index","value":"i"},
  {"name":"count","value":"n"}
]}
```
```json
{"id":"UUID","name":"removeLastArrayItem","outputVar":"item","args":[
  {"name":"array","value":"arr"}
]}
```

**Mutation guard:** always `copyArray` first, iterate the copy, call `removeArrayItem` on the original using `arr.indexOf(item)`. Mutating the array being iterated breaks `forEach`.

---

### `reverseArray`

**XML:**
```xml
<action id="UUID" name="reverseArray" disabled="false">
  <arg name="array" value="arr"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"reverseArray","args":[
  {"name":"array","value":"arr"}
]}
```

Mutates in place.

---

### `sortArray`

**Inline-JS temptation:** `arr.sort()` — case-sensitive, no direction control

**XML:**
```xml
<action id="UUID" name="sortArray" disabled="false">
  <arg name="array" value="arr"/>
  <arg name="ignoreCase" value="true"/>
  <arg name="ascending" value="false"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"sortArray","args":[
  {"name":"array","value":"arr"},
  {"name":"ignoreCase","value":"true"},
  {"name":"ascending","value":"false"}
]}
```

`keyFields` arg (comma-delimited string) for sorting arrays of records by field values.

---

### `joinArray` — array to delimited string

**Inline-JS temptation:** `arr.join(',')`

**XML:**
```xml
<action id="UUID" name="joinArray" outputVar="result" disabled="false">
  <arg name="array" value="arr"/>
  <arg name="delimiter" value="&quot;,&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"joinArray","outputVar":"result","args":[
  {"name":"array","value":"arr"},
  {"name":"delimiter","value":"\",\""}
]}
```

---

### `sliceArray` — subset without modifying original

**Inline-JS temptation:** `arr.slice(1, 3)`

**XML:**
```xml
<action id="UUID" name="sliceArray" outputVar="result" disabled="false">
  <arg name="array" value="arr"/>
  <arg name="startIndex" value="1"/>
  <arg name="endIndex" value="3"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"sliceArray","outputVar":"result","args":[
  {"name":"array","value":"arr"},
  {"name":"startIndex","value":"1"},
  {"name":"endIndex","value":"3"}
]}
```

---

### `arrayContains` — membership test

**Inline-JS temptation:** `arr.indexOf(x) >= 0`

**XML:**
```xml
<action id="UUID" name="arrayContains" outputVar="found" disabled="false">
  <arg name="array" value="arr"/>
  <arg name="value" value="x"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"arrayContains","outputVar":"found","args":[
  {"name":"array","value":"arr"},
  {"name":"value","value":"x"}
]}
```

---

### JS-only array patterns (no native equivalent)

```xml
<!-- Is it an array? -->
<arg name="value" value="Array.isArray(val)"/>

<!-- Normalize single-value-or-array (e.g. LDAP multi-valued attr) -->
<arg name="collection" value="[].concat(record.member)"/>

<!-- Deduplicate -->
<arg name="value" value="arr.filter((v,i) =&gt; arr.indexOf(v) === i)"/>

<!-- Set difference: items in A not in B -->
<!-- Step 1 --> <arg name="value" value="new Set(arrB)"/> <!-- outputVar: setB -->
<!-- Step 2 --> <arg name="value" value="arrA.filter(x =&gt; !setB.has(x))"/>
```

MCP JSON for `[].concat` normalize (inside a `forEach collection` arg):
```json
{"name":"collection","value":"[].concat(record.member)"}
```

MCP JSON for deduplicate:
```json
{"name":"value","value":"arr.filter((v,i) => arr.indexOf(v) === i)"}
```

Note: `&&`, `<`, `>` are written as-is in JSON values (`filter(x => !setB.has(x))`). Only XML needs the entity escapes.

---

## Records

### `createRecord` / `createRecordFromObject`

**Inline-JS temptation:** `obj = {}` — **bare `{}` literal fails the Connect expression compiler**

**Also wrong:** `parseJSON('{}')`. It compiles, but `parseJSON` is a JSON-*string* parser, not a
container constructor — use `createRecord` for an empty object and `createArray` for an empty array.

**XML:**
```xml
<action id="UUID" name="createRecord" outputVar="rec" disabled="false"/>
<action id="UUID" name="createRecordFromObject" outputVar="rec" disabled="false">
  <arg name="object" value="parsedObj"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"createRecord","outputVar":"rec","args":[]}
```
```json
{"id":"UUID","name":"createRecordFromObject","outputVar":"rec","args":[
  {"name":"object","value":"parsedObj"}
]}
```

`createRecordFromObject` coerces all values to strings — boolean `true` becomes `"true"`, number `50`
becomes `"50"`. `createRecord` + `setRecordFieldValue` preserves native types. Prefer the latter for any
Record whose values are compared strictly (`"false"` is truthy; `"50" !== 50`) or used in arithmetic.

---

### `copyRecord` — deep copy

**Inline-JS temptation:** `setVariable copy = rec` — **alias, not a copy**

**XML:**
```xml
<action id="UUID" name="copyRecord" outputVar="copy" disabled="false">
  <arg name="record" value="rec"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"copyRecord","outputVar":"copy","args":[
  {"name":"record","value":"rec"}
]}
```

Always `copyRecord` before mutating. Required for `FnHasRecordChanged` snapshots.

---

### `setRecordFieldValue` / `getRecordFieldValue` / `getRecordFieldNames`

**XML:**
```xml
<action id="UUID" name="setRecordFieldValue" disabled="false">
  <arg name="record" value="rec"/>
  <arg name="field" value="&quot;givenName&quot;"/>
  <arg name="value" value="&quot;Alice&quot;"/>
</action>
<action id="UUID" name="getRecordFieldValue" outputVar="val" disabled="false">
  <arg name="record" value="rec"/>
  <arg name="field" value="&quot;givenName&quot;"/>
</action>
<action id="UUID" name="getRecordFieldNames" outputVar="names" disabled="false">
  <arg name="record" value="rec"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"setRecordFieldValue","args":[
  {"name":"record","value":"rec"},
  {"name":"field","value":"\"givenName\""},
  {"name":"value","value":"\"Alice\""}
]}
```
```json
{"id":"UUID","name":"getRecordFieldValue","outputVar":"val","args":[
  {"name":"record","value":"rec"},
  {"name":"field","value":"\"givenName\""}
]}
```
```json
{"id":"UUID","name":"getRecordFieldNames","outputVar":"names","args":[
  {"name":"record","value":"rec"}
]}
```

---

### `setRecordFieldValues` / `getRecordFieldValues` / `addRecordFieldValue` / `clearRecordFieldValues`

**XML:**
```xml
<action id="UUID" name="setRecordFieldValues" disabled="false">
  <arg name="record" value="rec"/>
  <arg name="field" value="&quot;roles&quot;"/>
  <arg name="values" value="rolesArr"/>
</action>
<action id="UUID" name="addRecordFieldValue" disabled="false">
  <arg name="record" value="rec"/>
  <arg name="field" value="&quot;roles&quot;"/>
  <arg name="value" value="&quot;writer&quot;"/>
</action>
<action id="UUID" name="clearRecordFieldValues" disabled="false">
  <arg name="record" value="rec"/>
  <arg name="field" value="&quot;roles&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"setRecordFieldValues","args":[
  {"name":"record","value":"rec"},
  {"name":"field","value":"\"roles\""},
  {"name":"values","value":"rolesArr"}
]}
```
```json
{"id":"UUID","name":"addRecordFieldValue","args":[
  {"name":"record","value":"rec"},
  {"name":"field","value":"\"roles\""},
  {"name":"value","value":"\"writer\""}
]}
```
```json
{"id":"UUID","name":"clearRecordFieldValues","args":[
  {"name":"record","value":"rec"},
  {"name":"field","value":"\"roles\""}
]}
```

`clearRecordFieldValues` sets the field to null (not empty array). `addRecordFieldValues` takes a `values` array arg.

---

### `hasRecordField` / `hasRecordFieldValue`

**XML:**
```xml
<action id="UUID" name="hasRecordField" outputVar="has" disabled="false">
  <arg name="record" value="rec"/>
  <arg name="field" value="&quot;email&quot;"/>
</action>
<action id="UUID" name="hasRecordFieldValue" outputVar="has" disabled="false">
  <arg name="record" value="rec"/>
  <arg name="field" value="&quot;roles&quot;"/>
  <arg name="value" value="&quot;admin&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"hasRecordField","outputVar":"has","args":[
  {"name":"record","value":"rec"},
  {"name":"field","value":"\"email\""}
]}
```
```json
{"id":"UUID","name":"hasRecordFieldValue","outputVar":"has","args":[
  {"name":"record","value":"rec"},
  {"name":"field","value":"\"roles\""},
  {"name":"value","value":"\"admin\""}
]}
```

---

### `removeRecordField` / `removeRecordFields`

**Inline-JS temptation:** `delete rec.field` — **does not work on Connect Records**

**XML:**
```xml
<action id="UUID" name="removeRecordField" disabled="false">
  <arg name="record" value="rec"/>
  <arg name="field" value="&quot;tempField&quot;"/>
</action>
<action id="UUID" name="removeRecordFields" disabled="false">
  <arg name="record" value="rec"/>
  <arg name="fields" value="&quot;a,b,c&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"removeRecordField","args":[
  {"name":"record","value":"rec"},
  {"name":"field","value":"\"tempField\""}
]}
```
```json
{"id":"UUID","name":"removeRecordFields","args":[
  {"name":"record","value":"rec"},
  {"name":"fields","value":"\"a,b,c\""}
]}
```

---

### `renameRecordField` / `renameRecordFields`

**XML:**
```xml
<action id="UUID" name="renameRecordField" disabled="false">
  <arg name="record" value="rec"/>
  <arg name="oldName" value="&quot;first&quot;"/>
  <arg name="newName" value="&quot;givenName&quot;"/>
</action>
<action id="UUID" name="renameRecordFields" disabled="false">
  <arg name="record" value="rec"/>
  <arg name="fields" value="&quot;first:givenName,last:sn&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"renameRecordField","args":[
  {"name":"record","value":"rec"},
  {"name":"oldName","value":"\"first\""},
  {"name":"newName","value":"\"givenName\""}
]}
```
```json
{"id":"UUID","name":"renameRecordFields","args":[
  {"name":"record","value":"rec"},
  {"name":"fields","value":"\"first:givenName,last:sn\""}
]}
```

---

### `copyRecordField` / `copyRecordFields` / `filterRecordFields`

**XML:**
```xml
<action id="UUID" name="copyRecordFields" disabled="false">
  <arg name="source" value="src"/>
  <arg name="fields" value="&quot;sn,dept&quot;"/>
  <arg name="destination" value="dest"/>
</action>
<action id="UUID" name="filterRecordFields" disabled="false">
  <arg name="record" value="rec"/>
  <arg name="fields" value="&quot;givenName,sn,mail&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"copyRecordFields","args":[
  {"name":"source","value":"src"},
  {"name":"fields","value":"\"sn,dept\""},
  {"name":"destination","value":"dest"}
]}
```
```json
{"id":"UUID","name":"filterRecordFields","args":[
  {"name":"record","value":"rec"},
  {"name":"fields","value":"\"givenName,sn,mail\""}
]}
```

`filterRecordFields` removes all fields NOT in the keep list (mutates in place).

---

### `recordEquals`

**XML:**
```xml
<action id="UUID" name="recordEquals" outputVar="equal" disabled="false">
  <arg name="record1" value="rec1"/>
  <arg name="record2" value="rec2"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"recordEquals","outputVar":"equal","args":[
  {"name":"record1","value":"rec1"},
  {"name":"record2","value":"rec2"}
]}
```

---

### `createRecordFromXML`

**XML:**
```xml
<action id="UUID" name="parseXML" outputVar="xmlObj" disabled="false">
  <arg name="xml" value="xmlStr"/>
</action>
<action id="UUID" name="createRecordFromXML" outputVar="rec" disabled="false">
  <arg name="xmlObject" value="xmlObj"/>
  <arg name="excludeAttrs" value="true"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"parseXML","outputVar":"xmlObj","args":[
  {"name":"xml","value":"xmlStr"}
]}
```
```json
{"id":"UUID","name":"createRecordFromXML","outputVar":"rec","args":[
  {"name":"xmlObject","value":"xmlObj"},
  {"name":"excludeAttrs","value":"true"}
]}
```

Child elements of the root node become Record fields. `excludeAttrs=true` omits XML attributes.

---

## JSON

### `parseJSON` — string to native value

**Inline-JS temptation:** `JSON.parse(str)` — skip for Records (can StackOverflow on Java-wrapped objects)

**XML:**
```xml
<action id="UUID" name="parseJSON" outputVar="obj" disabled="false">
  <arg name="json" value="str"/>
</action>
<!-- Seed empty object: -->
<action id="UUID" name="parseJSON" outputVar="obj" disabled="false">
  <arg name="json" value="&quot;{}&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"parseJSON","outputVar":"obj","args":[
  {"name":"json","value":"str"}
]}
```
```json
{"id":"UUID","name":"parseJSON","outputVar":"obj","args":[
  {"name":"json","value":"\"{}\""}
]}
```

Malformed input auto-logs an ERROR and returns `undefined` — does not abort. Pre-gate with `isValidJSON` JS function for clean branching.

---

### `toJSON` — native value to JSON string

**Inline-JS temptation:** `JSON.stringify(obj)` — fails for Records (`{key=val}` Java map string)

**XML:**
```xml
<!-- compact -->
<action id="UUID" name="toJSON" outputVar="str" disabled="false">
  <arg name="item" value="obj"/>
</action>
<!-- 4-space indented -->
<action id="UUID" name="toJSON" outputVar="str" disabled="false">
  <arg name="item" value="obj"/>
  <arg name="indent" value="true"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"toJSON","outputVar":"str","args":[
  {"name":"item","value":"obj"}
]}
```
```json
{"id":"UUID","name":"toJSON","outputVar":"str","args":[
  {"name":"item","value":"obj"},
  {"name":"indent","value":"true"}
]}
```

Also callable inline: `toJSON(obj)` or `toJSON(obj, true)` in any `value=` expression. Record keys serialize alphabetically; plain and `parseJSON`-seeded objects keep insertion order.

---

## Dates

### `now` / `today` / `parseDate` / `formatDate`

**XML:**
```xml
<!-- current epoch ms — use inline -->
<arg name="value" value="now()"/>

<action id="UUID" name="today" outputVar="d" disabled="false">
  <arg name="timezone" value="Global.localTimeZone"/>
</action>
<action id="UUID" name="parseDate" outputVar="d" disabled="false">
  <arg name="date" value="str"/>
  <arg name="pattern" value="&quot;yyyy-MM-dd&quot;"/>
</action>
<action id="UUID" name="formatDate" outputVar="str" disabled="false">
  <arg name="date" value="d"/>
  <arg name="pattern" value="&quot;yyyy-MM-dd&quot;"/>
  <arg name="timezone" value="Global.localTimeZone"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"today","outputVar":"d","args":[
  {"name":"timezone","value":"Global.localTimeZone"}
]}
```
```json
{"id":"UUID","name":"parseDate","outputVar":"d","args":[
  {"name":"date","value":"str"},
  {"name":"pattern","value":"\"yyyy-MM-dd\""}
]}
```
```json
{"id":"UUID","name":"formatDate","outputVar":"str","args":[
  {"name":"date","value":"d"},
  {"name":"pattern","value":"\"yyyy-MM-dd\""},
  {"name":"timezone","value":"Global.localTimeZone"}
]}
```

`today(tz)` returns a UTC Date whose instant corresponds to local midnight in that zone.

---

### `adjustDate` / `truncateDate`

**XML:**
```xml
<action id="UUID" name="adjustDate" outputVar="d" disabled="false">
  <arg name="date" value="d"/>
  <arg name="amount" value="-1"/>
  <arg name="unit" value="&quot;day&quot;"/>
</action>
<action id="UUID" name="truncateDate" outputVar="d" disabled="false">
  <arg name="date" value="d"/>
  <arg name="unit" value="&quot;day&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"adjustDate","outputVar":"d","args":[
  {"name":"date","value":"d"},
  {"name":"amount","value":"-1"},
  {"name":"unit","value":"\"day\""}
]}
```
```json
{"id":"UUID","name":"truncateDate","outputVar":"d","args":[
  {"name":"date","value":"d"},
  {"name":"unit","value":"\"day\""}
]}
```

`unit` values: `day`, `month`, `year`.

---

### `dateFromFILETIME` / `dateToFILETIME`

**XML:**
```xml
<action id="UUID" name="dateFromFILETIME" outputVar="d" disabled="false">
  <arg name="filetime" value="filetimeVal"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"dateFromFILETIME","outputVar":"d","args":[
  {"name":"filetime","value":"filetimeVal"}
]}
```

---

## DNs

### `equalsDN` / `isChildOfDN` / `isDescendantOfDN`

**XML:**
```xml
<action id="UUID" name="equalsDN" outputVar="eq" disabled="false">
  <arg name="dn1" value="dn1"/>
  <arg name="dn2" value="dn2"/>
</action>
<action id="UUID" name="isChildOfDN" outputVar="is" disabled="false">
  <arg name="dn" value="dn"/>
  <arg name="parent" value="parentDn"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"equalsDN","outputVar":"eq","args":[
  {"name":"dn1","value":"dn1"},
  {"name":"dn2","value":"dn2"}
]}
```
```json
{"id":"UUID","name":"isChildOfDN","outputVar":"is","args":[
  {"name":"dn","value":"dn"},
  {"name":"parent","value":"parentDn"}
]}
```

`equalsDN` is case-insensitive. `isChildOfDN` checks direct parent; `isDescendantOfDN` checks any ancestor.

---

### `getRDN` / `getParentDN` / `splitDN`

**XML:**
```xml
<action id="UUID" name="getRDN" outputVar="rdn" disabled="false">
  <arg name="dn" value="dn"/>
</action>
<action id="UUID" name="getParentDN" outputVar="parent" disabled="false">
  <arg name="dn" value="dn"/>
  <arg name="levels" value="1"/>
</action>
<action id="UUID" name="splitDN" outputVar="parts" disabled="false">
  <arg name="dn" value="dn"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"getRDN","outputVar":"rdn","args":[
  {"name":"dn","value":"dn"}
]}
```
```json
{"id":"UUID","name":"getParentDN","outputVar":"parent","args":[
  {"name":"dn","value":"dn"},
  {"name":"levels","value":"1"}
]}
```
```json
{"id":"UUID","name":"splitDN","outputVar":"parts","args":[
  {"name":"dn","value":"dn"}
]}
```

`splitDN` returns an array of RDN strings. Optional `limit` arg caps how many levels are split.

---

## Crypto

### `encodeStringToBase64` / `decodeBase64ToString`

**XML:**
```xml
<action id="UUID" name="encodeStringToBase64" outputVar="b64" disabled="false">
  <arg name="string" value="str"/>
</action>
<action id="UUID" name="decodeBase64ToString" outputVar="str" disabled="false">
  <arg name="base64" value="b64"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"encodeStringToBase64","outputVar":"b64","args":[
  {"name":"string","value":"str"}
]}
```
```json
{"id":"UUID","name":"decodeBase64ToString","outputVar":"str","args":[
  {"name":"base64","value":"b64"}
]}
```

---

### `hashString` — MD5 / SHA-256

**XML:**
```xml
<action id="UUID" name="hashString" outputVar="hash" disabled="false">
  <arg name="string" value="str"/>
  <arg name="algorithm" value="&quot;SHA-256&quot;"/>
  <arg name="returnType" value="&quot;HEX&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"hashString","outputVar":"hash","args":[
  {"name":"string","value":"str"},
  {"name":"algorithm","value":"\"SHA-256\""},
  {"name":"returnType","value":"\"HEX\""}
]}
```

`algorithm`: `MD5`, `SHA-256`. `returnType`: `HEX`, `BASE64`.

---

### `macString` — HMAC-SHA256

**XML:**
```xml
<action id="UUID" name="macString" outputVar="mac" disabled="false">
  <arg name="string" value="str"/>
  <arg name="key" value="secret"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"macString","outputVar":"mac","args":[
  {"name":"string","value":"str"},
  {"name":"key","value":"secret"}
]}
```

---

## Connections — FnCoreOpenConnections

### Single system

**XML:**
```xml
<action id="UUID" name="FnCoreOpenConnections" outputVar="conns" disabled="false">
  <arg name="targetSystem" value="&quot;ad&quot;"/>
</action>
<action id="UUID" name="if" disabled="false">
  <arg name="condition" value="!conns || !conns.ad || !conns.ad.session"/>
  <arg name="then">
    <action id="UUID" name="log" disabled="false">
      <arg name="message" value="&quot;AD connection failed&quot;"/>
      <arg name="level" value="&quot;ERROR&quot;"/>
    </action>
    <action id="UUID" name="return" disabled="false">
      <arg name="value" value="false"/>
    </action>
  </arg>
  <arg name="else"/>
</action>
<action id="UUID" name="setVariable" disabled="false">
  <arg name="name" value="sessionAD"/>
  <arg name="value" value="conns.ad.session"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"FnCoreOpenConnections","outputVar":"conns","project":"ref_ConnectLibrary","args":[
  {"name":"targetSystem","value":"\"ad\""}
]},
{"id":"UUID","name":"if","args":[
  {"name":"condition","value":"!conns || !conns.ad || !conns.ad.session"},
  {"name":"then","actions":[
    {"id":"UUID","name":"log","args":[
      {"name":"message","value":"\"AD connection failed\""},
      {"name":"level","value":"\"ERROR\""}
    ]},
    {"id":"UUID","name":"return","args":[
      {"name":"value","value":"false"}
    ]}
  ]},
  {"name":"else"}
]},
{"id":"UUID","name":"setVariable","args":[
  {"name":"name","value":"sessionAD"},
  {"name":"value","value":"conns.ad.session"}
]}
```

### Multiple systems at once

**XML:**
```xml
<action id="UUID" name="FnCoreOpenConnections" outputVar="conns" disabled="false">
  <arg name="targetSystem" value="&quot;ad,google,microsoft&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"FnCoreOpenConnections","outputVar":"conns","project":"ref_ConnectLibrary","args":[
  {"name":"targetSystem","value":"\"ad,google,microsoft\""}
]}
```

`conns.ad.session`, `conns.google.session`, `conns.microsoft.session` all available after one call. Add failure guards per prefix as needed.

**CA constraint:** Community Adapter sets must NOT call `FnCoreOpenConnections` — use typed built-in actions (`openADConnection`, `defineGoogleExtendedOAuthConnection`, etc.) directly.

---

## XML

### `parseXML` / `toXML` / `xpath`

**XML:**
```xml
<action id="UUID" name="parseXML" outputVar="xmlObj" disabled="false">
  <arg name="xml" value="xmlStr"/>
</action>
<action id="UUID" name="xpath" outputVar="result" disabled="false">
  <arg name="xml" value="xmlObj"/>
  <arg name="xpath" value="&quot;//user/givenName&quot;"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"parseXML","outputVar":"xmlObj","args":[
  {"name":"xml","value":"xmlStr"}
]}
```
```json
{"id":"UUID","name":"xpath","outputVar":"result","args":[
  {"name":"xml","value":"xmlObj"},
  {"name":"xpath","value":"\"//user/givenName\""}
]}
```

`xpath` returns a newline-delimited string for multi-match results — split with `splitString(result, "\n")`. Attribute dot-notation access on parsed XML objects is broken; use child element text instead.

---

## Control Flow

### `forEach`

**XML:**
```xml
<action id="UUID" name="forEach" disabled="false">
  <arg name="variable" value="item"/>
  <arg name="collection" value="arr"/>
  <arg name="do">
    <!-- child actions -->
  </arg>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"forEach","args":[
  {"name":"variable","value":"item"},
  {"name":"collection","value":"arr"},
  {"name":"do","actions":[
    /* child action objects */
  ]}
]}
```

Arg names are `variable` and `collection` — never `item`/`items`. Add `{"name":"label","value":"LoopName"}` for labeled loops — `label` is `type="name"`, so in XML it's `<arg name="label" value="LoopName"/>`, never `value="&quot;LoopName&quot;"`. Same for `while`/`continue`/`break`'s `label`. See § Section Labels in SKILL.md.

---

### `if`

**XML:**
```xml
<action id="UUID" name="if" disabled="false">
  <arg name="condition" value="x &gt; 0"/>
  <arg name="then">
    <!-- child actions -->
  </arg>
  <arg name="else"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"if","args":[
  {"name":"condition","value":"x > 0"},
  {"name":"then","actions":[
    /* child action objects */
  ]},
  {"name":"else"}
]}
```

Always include both `then` and `else`. Empty `else` is `{"name":"else"}` — no `value`, no `actions`. In JSON, `>` and `<` are literal (no entity escaping needed).

---

### `while`

**XML:**
```xml
<action id="UUID" name="while" disabled="false">
  <arg name="condition" value="count &lt; 5"/>
  <arg name="do">
    <!-- child actions -->
  </arg>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"while","args":[
  {"name":"condition","value":"count < 5"},
  {"name":"do","actions":[
    /* child action objects */
  ]}
]}
```

`while` has no `else`.

---

### `break` / `continue` / `return` / `delay`

**XML:**
```xml
<action id="UUID" name="break" disabled="false"/>
<action id="UUID" name="continue" disabled="false">
  <arg name="label" value="OuterLoop"/>
</action>
<action id="UUID" name="return" disabled="false">
  <arg name="value" value="result"/>
</action>
<action id="UUID" name="delay" disabled="false">
  <arg name="seconds" value="1"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"break","args":[]}
```
```json
{"id":"UUID","name":"continue","args":[
  {"name":"label","value":"OuterLoop"}
]}
```
```json
{"id":"UUID","name":"return","args":[
  {"name":"value","value":"result"}
]}
```
```json
{"id":"UUID","name":"delay","args":[
  {"name":"seconds","value":"1"}
]}
```

---

## section

**XML:**
```xml
<action id="UUID" name="section" disabled="false">
  <arg name="label" value="mySection"/>
  <arg name="suppressTrace" value="true"/>
  <arg name="do">
    <!-- child actions -->
  </arg>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"section","args":[
  {"name":"label","value":"mySection"},
  {"name":"suppressTrace","value":"true"},
  {"name":"do","actions":[
    /* child action objects */
  ]}
]}
```

All sections must have `suppressTrace: "true"`. Never use a Connect reserved word as a section label (`return`, `log`, `if`, `forEach`, `section`).

---

## log

**XML:**
```xml
<action id="UUID" name="log" disabled="false">
  <arg name="message" value="&quot;Processing: &quot; + record.cn"/>
  <arg name="level" value="&quot;INFO&quot;"/>
  <arg name="color" value="logColors.info"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"log","args":[
  {"name":"message","value":"\"Processing: \" + record.cn"},
  {"name":"level","value":"\"INFO\""},
  {"name":"color","value":"logColors.info"}
]}
```

`level` values: `TRACE`, `DEBUG`, `INFO`, `WARN`, `ERROR` (always uppercase). The log viewer is plain text — `\n` and `\t` produce real whitespace; HTML tags appear literally.

---

## setVariable / copyRecord / copyArray

**XML:**
```xml
<action id="UUID" name="setVariable" disabled="false">
  <arg name="name" value="myVar"/>
  <arg name="value" value="someExpression"/>
</action>
<action id="UUID" name="copyRecord" outputVar="copy" disabled="false">
  <arg name="record" value="original"/>
</action>
<action id="UUID" name="copyArray" outputVar="copy" disabled="false">
  <arg name="array" value="original"/>
</action>
```

**MCP JSON:**
```json
{"id":"UUID","name":"setVariable","args":[
  {"name":"name","value":"myVar"},
  {"name":"value","value":"someExpression"}
]}
```
```json
{"id":"UUID","name":"copyRecord","outputVar":"copy","args":[
  {"name":"record","value":"original"}
]}
```
```json
{"id":"UUID","name":"copyArray","outputVar":"copy","args":[
  {"name":"array","value":"original"}
]}
```

`setVariable` creates an alias for objects/arrays/records — use `copyRecord` or `copyArray` when you need an independent copy before mutating.
