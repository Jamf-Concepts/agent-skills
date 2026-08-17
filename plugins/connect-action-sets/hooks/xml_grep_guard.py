"""PreToolUse hook on Grep.

A content-mode Grep against a minified/single-line XML file returns the entire
file as one "matching line" - a context bomb. When the Grep targets such a
file (and isn't already using -o), deny it and point at the pretty-printed
sidecar (real line numbers) or suggest -o for exact-text extraction.

Only fires when Grep's path is a specific .xml file; directory-wide greps are
left alone (tool-result truncation caps the damage there).
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xml_read_guard as xrg


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Grep":
        return
    ti = data.get("tool_input") or {}
    if ti.get("output_mode") != "content" or ti.get("-o"):
        return
    path = ti.get("path") or ""
    if not path.lower().endswith(".xml") or not os.path.isfile(path):
        return
    project_dir = xrg.project_dir_of(data)
    if xrg.is_sidecar(path, project_dir):
        return
    if not xrg.has_long_line(path):
        return

    sidecar = xrg.ensure_sidecar(path, project_dir)
    xrg.deny(
        "This XML file has lines over %d chars, so a content-mode Grep would return "
        "entire multi-KB lines. Either (a) Grep the pretty-printed copy at %s instead "
        "- it has real line numbers and an outline header - or (b) re-run this Grep on "
        "the original with \"-o\": true to get only the matched text (useful for grabbing "
        "exact snippets to Edit the original file)." % (xrg.LONG_LINE, sidecar)
    )


if __name__ == "__main__":
    main()
