# Diagnosing PVP Failures from `pvp.log`

`pvp.log` (the IDHub Provisioning Pipeline job log) can be **hundreds of MB to >1GB** — a
full `students_pvp.log` has been seen at over 1GB with 20k+ lines, many of them multi-KB
JSON diff dumps. Never `cat`/`Read` the whole file. Use the recipe below to go from "why
did this run have failures" to a root cause in a few targeted commands.

## Step 1 — Read the aggregate stats block first, not individual lines

Every run ends with a `net.idauto.BatchOrchestrator` / `net.idauto.LCSJobStatusPublisher`
INFO block (duplicated) containing the run's full stats as JSON. Grab it with `tail` — it's
always near the end of the file:

```bash
tail -c 5000 pvp.log
```

Key fields:
- `sourceStats.ingested` / `.consolidated` / `.filterStats.removed` — source-side funnel
- `idStoreStats.synchronizationStats.personStats.updateStats.total/succeeded/failed`
- `.successDetails` — breakdown of what succeeded (e.g. `{"disabled": 696, "roleStats": {"staff": 696}}`)
- `.failureDetails` — breakdown of what failed (e.g. `{"uncategorizedError": 13785, "roleStats": {"staff": 13413, ...}}`)

**If `successDetails` shows only one category (e.g. everything succeeded was `disabled`),
that's a strong signal the failures are concentrated in a specific kind of diff** (anything
that touches more than a disable flag) — chase that category next instead of grepping blind.

## Step 2 — Count log levels before reading any of them

```bash
grep -oE "^[0-9T:.-]+ [A-Z]+" pvp.log | awk '{print $2}' | sort | uniq -c
```

Individually-thrown `ERROR` lines (from `net.idauto.PolicyEngine` — "Stripping Diff due to
error while applying policy") are usually rare (single digits) even when thousands of
records fail. The bulk of failures show up as `WARN net.idauto.LDAPStoreStatsReporter -
Skipping Diff [...] because it could not be synchronized: [LDAPException(...)]` — one WARN
per failed record. Don't be misled by a low ERROR count into thinking the failure surface
is small.

## Step 3 — Bucket the WARN/ERROR lines by their trailing message, not by eyeballing JSON

Each failure line ends with the actual reason after the huge embedded JSON diff. Pull just
that tail:

```bash
grep "WARN\|ERROR" pvp.log | sed -E 's/.*(: \[LDAPException.*|: No username was mapped!)/\1/' | sort | uniq -c | sort -rn
```

This collapses 13,785 near-identical multi-KB lines down to one bucketed count per distinct
root cause (e.g. `LDAPException(resultCode=65 (object class violation) ...)` appearing
13,785 times vs. a handful of `No username was mapped!` `IllegalArgumentException`s).

## Step 4 — Parse one sample diff with Python, not by eye

The embedded diff JSON is too long to read raw (attribute-per-object dumps for every
`idautoPerson` field). Extract and parse it structurally:

```python
import json
line = open("sample_line.txt").read()
start = line.find("Skipping Diff [") + len("Skipping Diff [")
end = line.rfind("] because it could not be synchronized")
d = json.loads(line[start:end])
src, dst, mods = d.get("src") or {}, d.get("dst") or {}, d.get("mods", [])
```

`mods` is the actual list of attribute changes the pipeline tried to apply — that's where
the real signal is, not `src`/`dst` (full before/after attribute dumps).

To check whether a pattern holds across **every** failure (not just the sample), loop the
same parse over the whole file — this scales fine even at 1GB since you're only parsing
the isolated JSON substring per matching line, not the whole file into memory at once:

```python
for line in open("pvp.log", encoding="utf-8", errors="replace"):
    if "object class violation" not in line:
        continue
    # extract + json.loads the diff substring, inspect mods/src as above
```

## Known failure signature: broken username policy → `@username` literal leaks into mods

Seen in a Fulton `pvp.log` run where 13,785 of 14,481 staff updates failed:

- LDAP error: `resultCode=65 (object class violation) ... object class 'idautoPerson'
  requires attribute 'idautoPersonUserNameMV'`
- Every failing diff's `mods` contained `{"type":"REPLACE","attr":"idautoPersonUserNameMV","values":[]}`
  — the username policy rule cleared the required multi-valued username attribute.
- The **same** diffs also wrote the literal, unsubstituted string `@username` into other
  fields derived from it (`idautoPersonSAMAccountName`, `mail`, `idautoPersonExt2` — e.g.
  `"@username@fultonschools.org"`). `@username` is the **read-only pseudo-attribute** that
  holds the candidate username inside a policy rule (see `SKILL.md` § Policy
  Pseudo-Attributes) — its literal appearance in output means the username-generation
  expression itself failed to resolve to a value and something downstream just
  string-substituted the token name instead of the value.
- A handful of records (4, in this run) hit a harder failure earlier in the same policy
  chain: `java.lang.IllegalArgumentException: No username was mapped!` thrown from
  `net.idauto.idhub.provisioning.application.usernames.UsernameApplicator.apply` — the
  username policy produced no candidate at all for those records.
- Confirmed **not** a source-data gap: every failing record already had a valid
  `idautoPersonDistrictID`, `idautoPersonSAMAccountName`, and `idautoPersonExt1` (AD DN)
  from a prior sync — the policy was attempting to regenerate an already-existing username
  and breaking on that regeneration.
- Diagnostic tell for "which records actually succeeded": cross-check `successDetails` from
  Step 1 — in this run 100% of successes were `disabled`-only diffs, i.e. records whose diff
  never touched a username-derived attribute never hit the broken policy code path at all.

**When you see this signature**, the root cause lives in the customer's **username policy
MR file** (the `.mr` applying `idautoPersonUserNameMV` — see `patterns.md` § Username Policy
Patterns), not in an ingestion/publication rule and not in source data. Read that policy
rule's `when`/`incrementOnCollision` expression for what could cause it to resolve to a
null/failed username for records that already have one on file (e.g. a collision check
misfiring, a guard condition excluding already-provisioned records incorrectly, or a
downstream template that references `@username` where it should reference the resolved
`idautoPersonUserNameMV` value).
