#!/usr/bin/env python3
"""Validate deterministic Listing limits from a UTF-8 JSON payload.

Read JSON from a file path or stdin (use '-'). Expected keys are title,
highlights, search_terms, optional limits, and optional space_separated.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_LIMITS = {
    "title_max": 74,
    "highlights_min": 124,
    "highlights_max": 125,
    "st_max_bytes": 250,
}


def load_payload(source: str) -> dict[str, Any]:
    raw = sys.stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object.")
    return value


def require_text(payload: dict[str, Any], key: str, errors: list[str]) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        errors.append(f"{key} must be a string.")
        return ""
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Amazon Listing title, highlight and ST limits.")
    parser.add_argument("payload", help="UTF-8 JSON path, or - to read JSON from stdin")
    parser.add_argument("--fail-on-error", action="store_true", help="Return exit code 2 when validation fails")
    args = parser.parse_args()

    try:
        payload = load_payload(args.payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 2

    errors: list[str] = []
    title = require_text(payload, "title", errors)
    highlights = require_text(payload, "highlights", errors)
    search_terms = require_text(payload, "search_terms", errors)
    limits = dict(DEFAULT_LIMITS)
    custom_limits = payload.get("limits", {})
    if not isinstance(custom_limits, dict):
        errors.append("limits must be an object when provided.")
    else:
        for key in DEFAULT_LIMITS:
            if key in custom_limits:
                if (
                    isinstance(custom_limits[key], int)
                    and not isinstance(custom_limits[key], bool)
                    and custom_limits[key] >= 0
                ):
                    limits[key] = custom_limits[key]
                else:
                    errors.append(f"limits.{key} must be a non-negative integer.")

    if limits["highlights_min"] > limits["highlights_max"]:
        errors.append("highlights_min cannot exceed highlights_max.")

    title_chars = len(title)
    highlight_chars = len(highlights)
    st_bytes = len(search_terms.encode("utf-8"))

    if title_chars > limits["title_max"]:
        errors.append(f"title has {title_chars} Unicode code points; maximum is {limits['title_max']}.")
    if not limits["highlights_min"] <= highlight_chars <= limits["highlights_max"]:
        errors.append(
            f"highlights has {highlight_chars} Unicode code points; required range is "
            f"{limits['highlights_min']} to {limits['highlights_max']}.")
    if st_bytes > limits["st_max_bytes"]:
        errors.append(f"search_terms uses {st_bytes} UTF-8 bytes; maximum is {limits['st_max_bytes']}.")
    if "\n" in title or "\r" in title:
        errors.append("title must be one line.")
    if any(ch in highlights for ch in "\r\n.。"):
        errors.append("highlights cannot contain a full stop or line break.")
    if "\n" in search_terms or "\r" in search_terms:
        errors.append("search_terms must be one line.")
    if re.search(r"[,，.;。；\-‐‑‒–—]", search_terms):
        errors.append("search_terms cannot contain comma, full stop, semicolon, or hyphen punctuation.")

    space_separated = payload.get("space_separated", True)
    if not isinstance(space_separated, bool):
        errors.append("space_separated must be true or false when provided.")
        space_separated = True
    repeated_tokens: list[str] = []
    if space_separated and search_terms:
        if search_terms != search_terms.strip() or "  " in search_terms or "\t" in search_terms:
            errors.append("space-separated search_terms must use one ASCII space between tokens and no edge space.")
        tokens = [token.casefold() for token in search_terms.split(" ") if token]
        seen: set[str] = set()
        for token in tokens:
            if token in seen and token not in repeated_tokens:
                repeated_tokens.append(token)
            seen.add(token)
        if repeated_tokens:
            errors.append("search_terms has repeated exact tokens: " + ", ".join(repeated_tokens) + ".")

    result = {
        "valid": not errors,
        "count_method": "Unicode code points for title/highlights; UTF-8 bytes for search_terms",
        "title": {"characters": title_chars, "maximum": limits["title_max"]},
        "highlights": {
            "characters": highlight_chars,
            "minimum": limits["highlights_min"],
            "maximum": limits["highlights_max"],
        },
        "search_terms": {"utf8_bytes": st_bytes, "maximum": limits["st_max_bytes"]},
        "repeated_exact_tokens": repeated_tokens,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if errors and args.fail_on_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
