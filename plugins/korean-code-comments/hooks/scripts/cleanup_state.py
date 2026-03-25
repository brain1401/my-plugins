#!/usr/bin/env python3
"""SessionEnd hook: clean up once-per-session state file."""

import json
import sys
from pathlib import Path


def main() -> None:
    data = json.load(sys.stdin)
    session_id = data.get("session_id", "")

    if not session_id:
        sys.exit(0)

    state_file = Path(f"/tmp/claude_comments_reminded_{session_id}")
    if state_file.exists():
        state_file.unlink()

    sys.exit(0)


if __name__ == "__main__":
    main()
