"""PreToolUse hook on Read.

Three behaviors for XML files:

1. Minified/single-line XML (any line long enough for Read to truncate):
   deny the Read and point Claude at a pretty-printed sidecar copy under
   .claude/xml-pretty/. The sidecar carries an outline header (top-level
   elements + line numbers) so Claude can jump with offset/limit.

2. While pretty-printing, elements whose text is XML-escaped XML (Connect
   exports embed action XML inside attributes/CDATA) get an UNWRAPPED view
   inserted as a comment right after the element, so the actual logic is
   readable without manual unescaping.

3. JUnit test-result XML (build/test-results/**/TEST-*.xml): deny the Read
   and serve a compact pass/fail summary (failing tests + project-relevant
   stack frames) in the deny message instead of the verbose raw XML.

Sidecars are cached by content hash and regenerate when the original changes.
xml_grep_guard.py imports the shared helpers from this module.
"""

import hashlib
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

LONG_LINE = 1500              # bytes; Read truncates lines around 2000 chars
ET_SIZE_LIMIT = 10 * 1024 * 1024  # above this, use the regex splitter only
OUTLINE_MAX_DEPTH = 2         # indent levels included in the outline
OUTLINE_MAX_ENTRIES = 120
UNWRAP_MAX_VIEWS = 50
UNWRAP_MAX_CHARS = 100_000    # per unwrapped view
SUMMARY_MAX_CHARS = 6000
PROJECT_PACKAGE = os.environ.get("CONNECT_HOOKS_PROJECT_PACKAGE", "")
CACHE_DIRNAME = os.path.join(".claude", "xml-pretty")

MARKUP_RE = re.compile(r"<[A-Za-z_][\w.:-]*[\s>/]")


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def project_dir_of(hook_input: dict) -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or hook_input.get("cwd") or os.getcwd()


def is_sidecar(path: str, project_dir: str) -> bool:
    cache_dir = os.path.join(project_dir, CACHE_DIRNAME)
    return os.path.normcase(os.path.abspath(path)).startswith(
        os.path.normcase(os.path.abspath(cache_dir)))


def has_long_line(path: str) -> bool:
    with open(path, "rb") as f:
        for line in f:
            if len(line) > LONG_LINE:
                return True
    return False


# ---------------------------------------------------------------- pretty print

def looks_like_markup(text: str) -> bool:
    return bool(MARKUP_RE.search(text)) and ("</" in text or "/>" in text)


def decode_layers(text: str) -> str:
    """Peel extra layers of XML-escaping (&amp;lt; -> &lt; -> <) until real
    markup appears. The parser already peeled one layer for element text."""
    for _ in range(3):
        if MARKUP_RE.search(text) or "&lt;" not in text:
            return text
        text = (text.replace("&lt;", "<").replace("&gt;", ">")
                    .replace("&quot;", '"').replace("&apos;", "'")
                    .replace("&amp;", "&"))
    return text


def pretty_naive(text: str) -> str:
    """Split tags onto lines and indent by tag nesting. Approximate, but every
    line stays readable. Used for malformed/oversized XML and unwrapped views."""
    text = re.sub(r">\s*<", ">\n<", text)
    out = []
    depth = 0
    for raw in text.split("\n"):
        line = raw.strip()
        if line.startswith("</"):
            depth = max(depth - 1, 0)
        out.append("  " * depth + line)
        if (line.startswith("<")
                and not line.startswith(("</", "<?", "<!--", "<!"))
                and not line.endswith("/>")
                and not re.search(r"</[A-Za-z_][\w.:-]*>$", line)):
            depth += 1
    return "\n".join(out)


def insert_unwrapped_views(root: ET.Element) -> None:
    """After each leaf element whose text is escaped XML, insert a comment
    holding the decoded content pretty-printed. Comments can't contain '--'."""
    views = 0
    for parent in root.iter():
        inserted = 0
        for idx, child in enumerate(list(parent)):
            if views >= UNWRAP_MAX_VIEWS:
                return
            if len(child) or not child.text or not isinstance(child.tag, str):
                continue
            decoded = decode_layers(child.text.strip())
            if not looks_like_markup(decoded):
                continue
            if len(decoded) > UNWRAP_MAX_CHARS:
                decoded = decoded[:UNWRAP_MAX_CHARS] + "\n... [unwrapped view truncated] ..."
            body = pretty_naive(decoded).replace("--", "- -")
            comment = ET.Comment(
                "\nUNWRAPPED (decoded) escaped XML from the preceding <%s> element:\n%s\n"
                % (child.tag, body))
            parent.insert(idx + 1 + inserted, comment)
            inserted += 1
            views += 1


def pretty_via_et(text: str) -> str:
    for _event, (prefix, uri) in ET.iterparse(io.StringIO(text), events=("start-ns",)):
        ET.register_namespace(prefix, uri)
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True, insert_pis=True))
    root = ET.fromstring(text, parser=parser)
    insert_unwrapped_views(root)
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode")


# ------------------------------------------------------------------- sidecars

def build_outline(body_lines: list) -> list:
    """[(1-based body line, description)] for shallow elements."""
    entries = []
    tag_re = re.compile(r"^(\s*)<([A-Za-z_][\w.:-]*)\b([^>]*)")
    attr_re = re.compile(r'\b(?:name|label|id)="([^"]*)"')
    in_comment = False
    for i, line in enumerate(body_lines, start=1):
        if in_comment:
            if "-->" in line:
                in_comment = False
            continue
        if line.lstrip().startswith("<!--") and "-->" not in line:
            in_comment = True
            continue
        m = tag_re.match(line)
        if not m:
            continue
        indent = len(m.group(1)) // 2
        if indent > OUTLINE_MAX_DEPTH:
            continue
        desc = "  " * indent + "<" + m.group(2) + ">"
        attr = attr_re.search(m.group(3))
        if attr:
            desc += ' "' + attr.group(1) + '"'
        entries.append((i, desc))
        if len(entries) >= OUTLINE_MAX_ENTRIES:
            entries.append((i, "... outline truncated ..."))
            break
    return entries


def make_sidecar_text(original_path: str, body: str) -> str:
    body_lines = body.split("\n")
    outline = build_outline(body_lines)
    # Header layout: open + 3 note lines + "OUTLINE:" + entries + closing "-->"
    header_len = 5 + len(outline) + 1
    header = [
        "<!-- PRETTY-PRINTED COPY (generated by xml_read_guard hook) of:",
        "     " + original_path,
        "     Line numbers in this outline refer to THIS file - use Read offset/limit to jump.",
        "     For Edit/Write, target the ORIGINAL file above; whitespace here will NOT match it.",
        "OUTLINE:",
    ]
    for body_line, desc in outline:
        header.append("  line %d: %s" % (body_line + header_len, desc))
    header.append("-->")
    return "\n".join(header + body_lines) + "\n"


def ensure_sidecar(path: str, project_dir: str) -> str:
    """Return the path of an up-to-date pretty-printed sidecar for `path`,
    generating it (and dropping stale versions) if needed."""
    cache_dir = os.path.join(project_dir, CACHE_DIRNAME)
    with open(path, "rb") as f:
        raw = f.read()
    digest = hashlib.sha1(raw).hexdigest()[:10]
    base = os.path.basename(path)
    sidecar = os.path.join(cache_dir, "%s.%s.xml" % (base, digest))
    if os.path.isfile(sidecar):
        return sidecar

    text = raw.decode("utf-8", errors="replace")
    pretty = None
    if len(raw) <= ET_SIZE_LIMIT:
        try:
            pretty = pretty_via_et(text)
        except ET.ParseError:
            pretty = None
    if pretty is None:
        pretty = pretty_naive(text)
    os.makedirs(cache_dir, exist_ok=True)
    for old in os.listdir(cache_dir):
        if old.startswith(base + ".") and old != os.path.basename(sidecar):
            try:
                os.remove(os.path.join(cache_dir, old))
            except OSError:
                pass
    with open(sidecar, "w", encoding="utf-8", newline="\n") as f:
        f.write(make_sidecar_text(path, pretty))
    return sidecar


def long_line_deny_reason(original_path: str, sidecar: str) -> str:
    return (
        "This XML file has lines over %d chars; Read would truncate them. "
        "A pretty-printed copy with an outline header (element -> line number) is at: %s "
        "- Read that instead, and use its outline with offset/limit to jump to sections. "
        "IMPORTANT: for Edit/Write, target the original file (%s); exact text/whitespace "
        "in the pretty copy will NOT match the original, so re-grab exact snippets from "
        "the original (e.g. Grep -o) before editing." % (LONG_LINE, sidecar, original_path)
    )


# --------------------------------------------------------------- junit summary

def looks_like_junit_report(path: str) -> bool:
    norm = path.replace("\\", "/").lower()
    return "test-results" in norm or os.path.basename(path).startswith("TEST-")


def summarize_junit(path: str) -> str:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return None
    if root.tag not in ("testsuite", "testsuites"):
        return None
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    lines = []
    for s in suites:
        lines.append("suite %s: tests=%s failures=%s errors=%s skipped=%s time=%ss" % (
            s.get("name", "?"), s.get("tests", "?"), s.get("failures", "?"),
            s.get("errors", "?"), s.get("skipped", "?"), s.get("time", "?")))
        for tc in s.iter("testcase"):
            label = "%s.%s" % (tc.get("classname", ""), tc.get("name", ""))
            for kind in ("failure", "error"):
                for node in tc.findall(kind):
                    msg = (node.get("message") or "").strip().replace("\n", " ")
                    lines.append("  %s %s: %s" % (kind.upper(), label, msg[:300]))
                    trace = [t.strip() for t in (node.text or "").strip().splitlines() if t.strip()]
                    keep = [t for t in trace if PROJECT_PACKAGE in t][:4] or trace[:3]
                    lines.extend("    " + t for t in keep)
            if tc.find("skipped") is not None:
                lines.append("  SKIPPED %s" % label)
    summary = "\n".join(lines)
    if len(summary) > SUMMARY_MAX_CHARS:
        summary = summary[:SUMMARY_MAX_CHARS] + "\n... [summary truncated] ..."
    return summary


# ----------------------------------------------------------------------- main

def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Read":
        return
    path = (data.get("tool_input") or {}).get("file_path") or ""
    if not path.lower().endswith(".xml") or not os.path.isfile(path):
        return
    project_dir = project_dir_of(data)
    if is_sidecar(path, project_dir):
        return

    if looks_like_junit_report(path):
        summary = summarize_junit(path)
        if summary is not None:
            deny(
                "JUnit test-result XML - raw XML withheld to save context; summary:\n"
                + summary
                + "\n(For full stack traces, Grep this file or read it with Bash.)"
            )

    if not has_long_line(path):
        return
    sidecar = ensure_sidecar(path, project_dir)
    deny(long_line_deny_reason(path, sidecar))


if __name__ == "__main__":
    main()
