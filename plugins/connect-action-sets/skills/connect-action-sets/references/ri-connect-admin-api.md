# RapidIdentity Connect — Admin REST API for Action Sets

Action sets that manage Connect itself (trigger jobs, read/write files, kill processes) call the Connect admin REST API via `httpGET` / `httpPOST` using the Portal session's token.

## Authentication

Use `defineCloudPortalConnection` and pass `Authorization: Bearer {sessionPortal.token}` on every request.

```xml
<action name="defineCloudPortalConnection" outputVar="sessionPortal"/>
<action name="setVariable">
  <arg name="name" value="connectHeaders"/>
  <arg name="value" value="{&quot;Authorization&quot;:&quot;Bearer &quot; + sessionPortal.token, &quot;Accept&quot;:&quot;application/json&quot;, &quot;Content-Type&quot;:&quot;application/json&quot;}"/>
</action>
```

Base URL: `{sessionPortal.url}api/rest/admin/connect`

---

## Key Endpoints

### Trigger a Job (Run Now)

```xml
<action name="httpGET" outputVar="runResult">
  <arg name="url" value="sessionPortal.url + &quot;api/rest/admin/connect/runJob/&quot; + jobId"/>
  <arg name="headers" value="connectHeaders"/>
</action>
```

Response: `{"success":true,"message":"OK","httpStatus":200}`

---

### List Running Processes

```xml
<action name="httpGET" outputVar="processesResponse">
  <arg name="url" value="sessionPortal.url + &quot;api/rest/admin/connect/processes?project=&quot; + projectName"/>
  <arg name="headers" value="connectHeaders"/>
</action>
```

Response shape: `{ "processes": [{ "id": "2026-06-04/2026-06-04-14_55_18.706", "nodeId": "uuid", "status": "running", "action": {...}, "startTime": 1780584918706, "host": "pod/ip" }] }`

- `id` — composite key: `<date>/<date>-<time>.<ms>`
- `nodeId` — cluster node UUID

---

### Kill a Running Process

Uses `/api/rest/v2/` (not v1). Build the path from the `nodeId` and the two parts of the process `id`:

```xml
<action name="setVariable">
  <arg name="name" value="killUrl"/>
  <arg name="value" value="sessionPortal.url + &quot;api/rest/v2/admin/connect/processes/&quot; + process.nodeId + &quot;/&quot; + process.id"/>
</action>
<action name="httpDELETE" outputVar="killResult">
  <arg name="url" value="killUrl"/>
  <arg name="headers" value="connectHeaders"/>
</action>
```

Response: `{"success":true,"message":"OK","httpStatus":200}`

---

### List Jobs

```xml
<action name="httpGET" outputVar="jobsResponse">
  <arg name="url" value="sessionPortal.url + &quot;api/rest/admin/connect/jobs?project=&quot; + projectName"/>
  <arg name="headers" value="connectHeaders"/>
</action>
```

Response: `{ "jobs": [{ "id": "uuid", "name": "...", "disabled": false, "cronSpec": "0 * * * * ?", ... }] }`

---

### Read a File

```xml
<action name="httpGET" outputVar="fileContent">
  <arg name="url" value="sessionPortal.url + &quot;api/rest/admin/connect/fileContent/&quot; + filePath + &quot;?project=&quot; + projectName"/>
  <arg name="headers" value="connectHeaders"/>
</action>
```

Response body is the raw file text (`fileContent.data` — plain text, not JSON).

---

### Write a File

```xml
<action name="httpPOST" outputVar="writeResult">
  <arg name="url" value="sessionPortal.url + &quot;api/rest/admin/connect/files/&quot; + filePath + &quot;?project=&quot; + projectName"/>
  <arg name="headers" value="connectHeaders"/>
  <arg name="data" value="fileTextContent"/>
</action>
```

Response: XML node confirming the write (not JSON).

---

### List Action Sets (metadata only)

```xml
<action name="httpGET" outputVar="actionsResponse">
  <arg name="url" value="sessionPortal.url + &quot;api/rest/admin/connect/actions?project=&quot; + projectName + &quot;&amp;metaDataOnly=true&quot;"/>
  <arg name="headers" value="connectHeaders"/>
</action>
```

Response: `{ "actionDefs": [{ "id": "uuid", "name": "...", "version": N, ... }] }`

---

### Get / Save a Full Action Set

```
GET  {base}/actions/{id}          — returns full action set including nested actions tree
POST {base}/actions               — create (no id in body) or update (include id + version)
```

---

## Standard Response Envelope

Most write/delete operations return:
```json
{ "success": true, "message": "OK", "httpStatus": 200 }
```

Check `apiResponse.data.success` after every call and log `apiResponse.data.message` on failure.
