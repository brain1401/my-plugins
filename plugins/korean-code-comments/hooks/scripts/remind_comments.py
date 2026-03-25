#!/usr/bin/env python3
"""Once-per-session Korean comment rules reminder (PostToolUse hook)."""

import json
import os
import sys
import uuid
from pathlib import Path

CODE_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".py", ".java", ".go", ".rs",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".kt", ".swift",
}


def get_file_paths(data: dict) -> list[str]:
    """Extract edited file paths from Write/Edit tool input."""
    tool_input = data.get("tool_input", {})

    # Write, Edit
    file_path = tool_input.get("file_path")
    if file_path:
        return [file_path]

    # MultiEdit
    files_to_edit = tool_input.get("files_to_edit", [])
    return [f.get("file_path", "") for f in files_to_edit if f.get("file_path")]


def is_code_file(file_path: str) -> bool:
    return Path(file_path).suffix.lower() in CODE_EXTENSIONS


def main() -> None:
    data = json.load(sys.stdin)
    session_id = data.get("session_id") or uuid.uuid4().hex

    # Check if edited file is a code file
    file_paths = get_file_paths(data)
    if not any(is_code_file(fp) for fp in file_paths):
        sys.exit(0)

    # Once-per-session check
    state_file = Path(f"/tmp/claude_comments_reminded_{session_id}")
    if state_file.exists():
        sys.exit(0)

    # Save state
    state_file.touch()

    # Read rules.md and output as systemMessage
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    rules_path = Path(plugin_root) / "hooks" / "rules.md"

    if rules_path.exists():
        rules_content = rules_path.read_text(encoding="utf-8")
    else:
        rules_content = "Add Korean comments to complex logic sections."

    output = json.dumps({"systemMessage": rules_content}, ensure_ascii=False)
    print(output)
    sys.exit(0)


if __name__ == "__main__":
    main()
