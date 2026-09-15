"""PostToolUse hook on Edit|Write.

After any edit to an .xml file, re-parse it. If the file is no longer
well-formed, exit 2 so the parse error is fed straight back to Claude and gets
fixed immediately instead of surfacing later as a confusing downstream failure.

Skips the .claude/xml-pretty/ sidecar cache (reading aids, never authoritative).
"""

import json
import os
import sys
import xml.etree.ElementTree as ET


def main() -> None:
    data = json.load(sys.stdin)
    path = (data.get("tool_input") or {}).get("file_path") or ""
    if not path.lower().endswith(".xml") or not os.path.isfile(path):
        return
    if "/.claude/xml-pretty/" in path.replace("\\", "/"):
        return

    with open(path, "rb") as f:
        raw = f.read()
    try:
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True, insert_pis=True))
        ET.fromstring(raw, parser=parser)
    except ET.ParseError as e:
        sys.stderr.write(
            "XML well-formedness check failed for %s: %s. "
            "The edit was applied but left the file malformed - fix it before moving on.\n"
            % (path, e)
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
