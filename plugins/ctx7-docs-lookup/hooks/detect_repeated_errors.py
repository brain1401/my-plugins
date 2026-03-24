#!/usr/bin/env python3
"""Detect repeated errors and remind to consult official docs via ctx7 (PostToolUse hook)."""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

ERROR_PATTERNS = re.compile(
    r"(?i)\b(error|exception|traceback|FAILED|panic)\b"
)

# Patterns to strip during normalization (file paths, line numbers, numeric values)
NORMALIZE_PATTERNS = [
    re.compile(r"(/[\w./-]+)"),          # file paths
    re.compile(r"\b\d+\b"),              # numeric values (incl. line numbers)
    re.compile(r"0x[0-9a-fA-F]+"),       # hex addresses
]


def extract_error_signature(text: str) -> str | None:
    """Generate a normalized signature hash from error message."""
    if not ERROR_PATTERNS.search(text):
        return None

    # Extract error type/class + first error line
    lines = text.strip().splitlines()
    error_lines = [
        line.strip() for line in lines
        if ERROR_PATTERNS.search(line)
    ]

    if not error_lines:
        return None

    # Use only the first error line
    signature = error_lines[0]

    # Normalize (strip paths, numbers)
    for pattern in NORMALIZE_PATTERNS:
        signature = pattern.sub("", signature)

    # Normalize whitespace
    signature = re.sub(r"\s+", " ", signature).strip()

    if not signature:
        return None

    return hashlib.sha256(signature.encode()).hexdigest()


def main() -> None:
    data = json.load(sys.stdin)
    session_id = data.get("session_id", "unknown")
    tool_result = data.get("tool_result", "")

    if isinstance(tool_result, dict):
        tool_result = json.dumps(tool_result)

    # Generate error signature
    signature = extract_error_signature(str(tool_result))
    if signature is None:
        sys.exit(0)

    # Per-session error tracking file
    tracking_path = Path(f"/tmp/claude_error_tracking_{session_id}.json")

    if tracking_path.exists():
        tracking = json.loads(tracking_path.read_text(encoding="utf-8"))
    else:
        tracking = {}

    # Update count
    count = tracking.get(signature, 0) + 1
    tracking[signature] = count
    tracking_path.write_text(
        json.dumps(tracking, ensure_ascii=False), encoding="utf-8"
    )

    # Skip if count < 2
    if count < 2:
        sys.exit(0)

    # Count >= 2: inject rules.md + reset counter
    tracking[signature] = 0
    tracking_path.write_text(
        json.dumps(tracking, ensure_ascii=False), encoding="utf-8"
    )

    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    rules_path = Path(plugin_root) / "hooks" / "rules.md"

    if rules_path.exists():
        rules_content = rules_path.read_text(encoding="utf-8")
    else:
        rules_content = "Repeated error detected. Consult official docs via ctx7."

    output = json.dumps({"systemMessage": rules_content}, ensure_ascii=False)
    print(output)
    sys.exit(0)


if __name__ == "__main__":
    main()
