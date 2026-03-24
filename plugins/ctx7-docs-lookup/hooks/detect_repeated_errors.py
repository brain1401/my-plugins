#!/usr/bin/env python3
"""반복 에러 감지 후 ctx7 공식 문서 참조 리마인드 (PostToolUse hook)."""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

ERROR_PATTERNS = re.compile(
    r"(?i)\b(error|exception|traceback|FAILED|panic)\b"
)

# 정규화 시 제거할 패턴 (파일 경로, 줄 번호, 숫자값)
NORMALIZE_PATTERNS = [
    re.compile(r"(/[\w./-]+)"),          # 파일 경로
    re.compile(r"\b\d+\b"),              # 숫자값 (줄 번호 포함)
    re.compile(r"0x[0-9a-fA-F]+"),       # 16진수 주소
]


def extract_error_signature(text: str) -> str | None:
    """에러 메시지에서 정규화된 시그니처 해시 생성."""
    if not ERROR_PATTERNS.search(text):
        return None

    # 에러 타입/클래스 + 첫 번째 줄 추출
    lines = text.strip().splitlines()
    error_lines = [
        line.strip() for line in lines
        if ERROR_PATTERNS.search(line)
    ]

    if not error_lines:
        return None

    # 첫 번째 에러 줄만 사용
    signature = error_lines[0]

    # 정규화 (경로, 숫자 제거)
    for pattern in NORMALIZE_PATTERNS:
        signature = pattern.sub("", signature)

    # 공백 정규화
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

    # 에러 시그니처 생성
    signature = extract_error_signature(str(tool_result))
    if signature is None:
        sys.exit(0)

    # 세션별 에러 추적 파일
    tracking_path = Path(f"/tmp/claude_error_tracking_{session_id}.json")

    if tracking_path.exists():
        tracking = json.loads(tracking_path.read_text(encoding="utf-8"))
    else:
        tracking = {}

    # 카운트 업데이트
    count = tracking.get(signature, 0) + 1
    tracking[signature] = count
    tracking_path.write_text(
        json.dumps(tracking, ensure_ascii=False), encoding="utf-8"
    )

    # 2회 미만이면 스킵
    if count < 2:
        sys.exit(0)

    # 2회 이상: rules.md 주입 + 카운터 리셋
    tracking[signature] = 0
    tracking_path.write_text(
        json.dumps(tracking, ensure_ascii=False), encoding="utf-8"
    )

    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    rules_path = Path(plugin_root) / "hooks" / "rules.md"

    if rules_path.exists():
        rules_content = rules_path.read_text(encoding="utf-8")
    else:
        rules_content = "동일 오류 반복 감지. ctx7으로 공식 문서를 확인하세요."

    output = json.dumps({"systemMessage": rules_content}, ensure_ascii=False)
    print(output)
    sys.exit(0)


if __name__ == "__main__":
    main()
