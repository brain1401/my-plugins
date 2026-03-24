#!/usr/bin/env python3
"""세션당 1회 한국어 주석 규칙 리마인드 (PostToolUse hook)."""

import json
import os
import sys
from pathlib import Path

CODE_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".py", ".java", ".go", ".rs",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".kt", ".swift",
}


def get_file_paths(data: dict) -> list[str]:
    """Write/Edit/MultiEdit에서 편집된 파일 경로 추출."""
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
    session_id = data.get("session_id", "unknown")

    # 코드 파일 편집 여부 확인
    file_paths = get_file_paths(data)
    if not any(is_code_file(fp) for fp in file_paths):
        sys.exit(0)

    # 세션당 1회 체크
    state_file = Path(f"/tmp/claude_comments_reminded_{session_id}")
    if state_file.exists():
        sys.exit(0)

    # 상태 저장
    state_file.touch()

    # rules.md 읽어서 systemMessage로 출력
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    rules_path = Path(plugin_root) / "hooks" / "rules.md"

    if rules_path.exists():
        rules_content = rules_path.read_text(encoding="utf-8")
    else:
        rules_content = "복잡한 로직에 한국어 주석을 추가하세요."

    output = json.dumps({"systemMessage": rules_content}, ensure_ascii=False)
    print(output)
    sys.exit(0)


if __name__ == "__main__":
    main()
