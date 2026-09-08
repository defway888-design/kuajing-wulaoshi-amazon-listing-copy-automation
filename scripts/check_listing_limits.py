#!/usr/bin/env python3
"""Validate deterministic limits for a finalized Amazon Listing payload.

Read UTF-8 JSON from a file path or stdin (use '-'). Required keys:
title, highlight (or legacy highlights), bullets, and search_terms.
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any


DEFAULT_LIMITS = {
    "title_max": 74,
    "bullet_max": 200,
    "highlight_max": 125,
    "st_max_bytes": 250,
}


def load_payload(source: str) -> dict[str, Any]:
    raw = sys.stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object.")
    return value


def require_text(
    payload: dict[str, Any], key: str, errors: list[str], *, allow_empty: bool = False
) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        errors.append(f"{key} must be a string.")
        return ""
    if not allow_empty and not value.strip():
        errors.append(f"{key} cannot be empty.")
    return value


def read_highlight(payload: dict[str, Any], errors: list[str]) -> str:
    if "highlight" in payload:
        return require_text(payload, "highlight", errors)
    if "highlights" in payload:
        value = payload.get("highlights")
        if isinstance(value, str):
            if not value.strip():
                errors.append("highlights cannot be empty.")
            return value
        errors.append("highlights must be a string.")
        return ""
    errors.append("highlight must be provided as a string.")
    return ""


def read_bullets(payload: dict[str, Any], errors: list[str]) -> list[str]:
    value = payload.get("bullets")
    if not isinstance(value, list):
        errors.append("bullets must be an array of exactly five strings.")
        return []
    if len(value) != 5:
        errors.append(f"bullets must contain exactly five items; received {len(value)}.")
    bullets: list[str] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, str):
            errors.append(f"bullets[{index}] must be a string.")
            bullets.append("")
        else:
            if not item.strip():
                errors.append(f"bullets[{index}] cannot be empty.")
            bullets.append(item)
    return bullets


def has_unicode_punctuation(value: str) -> bool:
    return any(unicodedata.category(char).startswith("P") for char in value)


def read_bool(payload: dict[str, Any], key: str, default: bool, errors: list[str]) -> bool:
    value = payload.get(key, default)
    if not isinstance(value, bool):
        errors.append(f"{key} must be true or false when provided.")
        return default
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Amazon Listing bullets, title, highlight, and ST limits."
    )
    parser.add_argument("payload", help="UTF-8 JSON path, or - to read JSON from stdin")
    parser.add_argument(
        "--fail-on-error", action="store_true", help="Return exit code 2 when validation fails"
    )
    args = parser.parse_args()

    try:
        payload = load_payload(args.payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 2

    errors: list[str] = []
    title = require_text(payload, "title", errors)
    highlight = read_highlight(payload, errors)
    bullets = read_bullets(payload, errors)
    search_terms = require_text(payload, "search_terms", errors, allow_empty=True)

    limits = dict(DEFAULT_LIMITS)
    custom_limits = payload.get("limits", {})
    if not isinstance(custom_limits, dict):
        errors.append("limits must be an object when provided.")
    else:
        for key in DEFAULT_LIMITS:
            if key in custom_limits:
                value = custom_limits[key]
                if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                    limits[key] = value
                else:
                    errors.append(f"limits.{key} must be a non-negative integer.")

    space_separated = read_bool(payload, "space_separated", True, errors)
    require_title_divider = read_bool(
        payload, "require_title_divider", space_separated, errors
    )

    title_chars = len(title)
    highlight_chars = len(highlight)
    bullet_chars = [len(item) for item in bullets]
    st_bytes = len(search_terms.encode("utf-8"))

    if title_chars > limits["title_max"]:
        errors.append(
            f"title has {title_chars} Unicode code points; maximum is {limits['title_max']}."
        )
    if "\n" in title or "\r" in title:
        errors.append("title must be one line.")
    if require_title_divider and title.count(" - ") != 1:
        errors.append("title must contain exactly one required ' - ' divider.")

    for index, count in enumerate(bullet_chars, start=1):
        if count > limits["bullet_max"]:
            errors.append(
                f"bullets[{index}] has {count} Unicode code points; maximum is "
                f"{limits['bullet_max']}."
            )
        if index <= len(bullets) and ("\n" in bullets[index - 1] or "\r" in bullets[index - 1]):
            errors.append(f"bullets[{index}] must be one line.")

    if highlight_chars > limits["highlight_max"]:
        errors.append(
            f"highlight has {highlight_chars} Unicode code points; maximum is "
            f"{limits['highlight_max']}."
        )
    if "\n" in highlight or "\r" in highlight:
        errors.append("highlight must be one line.")
    if highlight.rstrip().endswith((".", "。")):
        errors.append("highlight cannot end with a full stop.")

    if st_bytes > limits["st_max_bytes"]:
        errors.append(
            f"search_terms uses {st_bytes} UTF-8 bytes; maximum is {limits['st_max_bytes']}."
        )
    if "\n" in search_terms or "\r" in search_terms:
        errors.append("search_terms must be one line.")
    if has_unicode_punctuation(search_terms):
        errors.append("search_terms cannot contain punctuation.")

    repeated_tokens: list[str] = []
    if space_separated and search_terms:
        if search_terms != search_terms.strip() or "  " in search_terms or "\t" in search_terms:
            errors.append(
                "space-separated search_terms must use one ASCII space between tokens and no edge space."
            )
        tokens = [token.casefold() for token in search_terms.split(" ") if token]
        seen: set[str] = set()
        for token in tokens:
            if token in seen and token not in repeated_tokens:
                repeated_tokens.append(token)
            seen.add(token)
        if repeated_tokens:
            errors.append(
                "search_terms has repeated exact tokens: " + ", ".join(repeated_tokens) + "."
            )

    result = {
        "valid": not errors,
        "count_method": (
            "Unicode code points for bullets/title/highlight; UTF-8 bytes for search_terms"
        ),
        "title": {
            "characters": title_chars,
            "maximum": limits["title_max"],
            "divider_required": require_title_divider,
            "divider_count": title.count(" - "),
        },
        "bullets": {
            "count": len(bullets),
            "characters": bullet_chars,
            "maximum_each": limits["bullet_max"],
        },
        "highlight": {"characters": highlight_chars, "maximum": limits["highlight_max"]},
        "search_terms": {"utf8_bytes": st_bytes, "maximum": limits["st_max_bytes"]},
        "repeated_exact_tokens": repeated_tokens,
        "manual_checks_required": [
            "five-counted-keyword title prefix and brand/category inclusion",
            "trusted-root deduplication",
            "highlight semantic non-repetition with title",
            "keyword frequency, density, stopwords, morphology, and Flesch readability",
        ],
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if errors and args.fail_on_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
