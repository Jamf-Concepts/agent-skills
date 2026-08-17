# TODO — Skill Update Queue

Queue of proposed updates to the `connect-action-sets` skill. Add an entry whenever a new
pattern, pitfall, or correction is discovered during real Connect work but not worth stopping
to fix immediately. Process the backlog periodically: fold entries into `connect-action-sets/SKILL.md`
or the relevant `references/*.md` file, re-zip to `connect-action-sets.skill`, move the archived
copy into `archive/`, and check off or remove the entry here.

## How to add an entry

```
- [ ] Short description of the change. Context: where/why this came up. (YYYY-MM-DD)
```

## Queue

- [ ] Correct the `stringReplaceAll` / `stringReplaceFirst` arg name in SKILL.md § String actions:
  the table lists `match`, but the platform requires **`pattern`** (and `pattern` is a *regex*, not a
  literal). `references/connect-builtin-actions.json` has it right — `[('string', False),
  ('pattern', False), ('replacement', True), ('ignoreCase', True)]` — so only the SKILL.md prose table
  is wrong. Also check `references/native-action-cheatsheet.md` for the same error. Worth adding a
  general note that the SKILL.md summary tables are hand-written and the JSON catalog is the
  authoritative source for arg names, so verify against it before using a builtin's args.
  Context: authoring the header-recovery fallback in `BuildLogReviewGoogleSheet` (LogReview server).
  Both xmllint and `_scripts/validate_xml.py` passed and `connect_fmt_validate` reported no error —
  nothing catches a wrong builtin arg name locally. It only failed at *runtime*, as
  `java.lang.IllegalArgumentException: Error compiling action set 'BuildLogReviewGoogleSheet':
  Missing required property 'stringReplaceAll.pattern'`, costing a deploy + job-run cycle.
  Consider also whether riadmin's `connect_validate` should gain a builtin-arg-name check, since it
  already resolves the builtin registry for its `unknown_action` rule. (2026-08-13)

- [ ] Add a § on Java-String vs JS-String coercion. Several file/IO builtins return a **Java String**
  (`typeof` is `"object"`, not `"string"`), where `.length` resolves to the Java `length()` *method
  object* rather than a number — so `name.length > 4` is silently `false` and any guard built on it
  fails with no error. Confirmed for `getFileName`; `listFiles` by contrast returns a genuine JS array
  of JS strings, and `lastIndexOf`/`toLowerCase`/`substring` all behave normally on the Java String —
  it is specifically `.length` that breaks. The fix is to coerce once at the boundary:
  `("" + getFileName(...))`. Worth auditing which other builtins return Java Strings
  (`loadFileAsString` is another suspect) and stating the rule that any string crossing out of a
  builtin should be coerced before arithmetic or `.length` use. Context: this silently disabled the
  entire `pushCategoryTabs` CSV filter in `BuildLogReviewGoogleSheet` — 10 tabs, 0 created, 0 errors
  logged, sub-second runtime, no clue in the log. It is the second time this class of bug has hit this
  same action set. (2026-08-13)

## Processed

- [x] 2026-07-28 mcp-rapidid alignment pass (v1.3.0): scanned the mcp-rapidid Go codebase +
  ri-sdk-go v1.7.0 and updated the skill to cover the full tool surface — added
  run-connect-action (returns the HTML job log; save → run → read log → fix loop),
  get-connect-files / get-connect-file-content (verify Global.* keys against live
  Globals/SharedGlobals.properties; read job/run logs via log/job & log/run paths; compressed
  files buggy server-side), delete by project.name, `<Main>` project naming, companion identity
  tools table (search-users, get-user-activity-from-audit-log for logAuditEvent verification,
  etc.), and server env/auth troubleshooting (RI_HOST, RI_SERVICE_IDENTITY_SECRET_KEY,
  RI_LOG_LEVEL). Note: mcp-rapidid bundles its own stale copy of this skill under skills/ —
  consider syncing it or pointing that repo at this marketplace. (2026-07-28)

## Processed

- [x] 2026-07-28 knowledge-base reconciliation pass: corrected `copyArray` from "deep copy" to
  **shallow copy** (SKILL.md tables + cheatsheet § copyArray; nested Records still shared);
  expanded `stringEscape` from 3 to the full **12 escape types** incl. `ldap-filter`/`ldap-dn`/`csv`
  (SKILL.md + cheatsheet); added § Built-in failure model (built-ins never throw — return
  undefined/false + set lastErrorMessage/lastErrorCode; `log level="ERROR"` clears-then-overwrites
  lastErrorMessage; getLastError* not cleared on read); added `return`-exits-entire-action-set to
  § Control Flow; strengthened § JavaScript & Engine Idioms with live-verified evidence (arrows +
  `new Set` in deployed `FnSyncGroupToGoogle`/`SyncGroupsFull`) and an explicit unverified-ES6+
  list; added 7 Common Pitfalls rows (failure model ×2, LATIN1 file encoding, getIdautoIDForUser
  not read-only, shallow copyArray, LDAP filter escaping). Source: Y:\ knowledge-base
  builtin-actions references (codebase-sourced, 2026-07-28) cross-checked against live tenant
  export evidence. (2026-07-28)

- [x] Correct the § Root Element guidance: a from-scratch action set must use the `<actionDefs>`
  (plural) wrapper root, not a bare `<actionDef>`. The skill currently says "Inside a `.dssproject`
  archive (actions/ folder) — bare `<actionDef>`," but a bare-root file **will not import through
  the Connect UI standalone importer**, and every on-disk manifest action set actually uses the
  wrapped form. Make `<actionDefs xmlns="urn:idauto.net:dss:actiondef"><actionDef name=… returnsValue=…
  description=…>…</actionDef></actionDefs>` the default for hand/generated XML (xmlns on the outer
  element only); note connect-api `build`/`convert`/`write_action_set`/`json_to_xml` with `wrap=true`
  emits it correctly; and state that `builtIn`/`community`/`category` and the `changeCount`/`modifiedMs`/
  `modifiedBy` reconciliation attributes are RI-saved metadata — do NOT add them to a from-scratch
  file. Context: authored FnRIPortalSession/FnRIWorkflowDefinition/FnRIEntitlement for the
  rapididentity-connect Utilities project from scratch; all passed xmllint + validate_xml.py +
  connect-api build, but the Connect UI rejected the import until wrapped in `<actionDefs>`.
  (queued 2026-07-20, processed 2026-07-28 — § Root Element rewritten: wrapped form is the default
  for all from-scratch/hand-generated XML, bare root only encountered inside .dssproject archives,
  RI-saved metadata attributes called out as non-authoring inputs)

- [x] Document the `Can't redefine property 'if.else'` failure mode more prominently — added a
  callout under § if / while / break covering the specific cause (hand-authored `if/else if/else`
  attaches the default block to the outer `if` instead of the inner nested `if`, since Connect has
  no native `else if`), plus a wrong/right XML example, a Quick Reference row, an updated checklist
  item 18, and a new Common Pitfalls row. Context: hit this in DeKalb's FnLoadTargetRecords.xml.
  (queued 2026-07-06, processed 2026-07-06)
