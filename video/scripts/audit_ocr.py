#!/usr/bin/env python3
"""Verify that essential judge-facing terms survive the final 1080p encode."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VIDEO = ROOT / "video"


def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def ocr_candidates(value: str) -> set[str]:
    """Return conservative candidates for common digit/letter OCR ambiguity."""
    normalized = compact(value)
    candidates = {normalized}
    if "1" in normalized:
        candidates.update({normalized.replace("1", "l"), normalized.replace("1", "i")})
    return candidates


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: audit_ocr.py VIDEO REPORT_DIR")
    source = Path(sys.argv[1])
    report_dir = Path(sys.argv[2])
    frames_dir = report_dir / "ocr"
    frames_dir.mkdir(parents=True, exist_ok=True)
    anchors = json.loads((VIDEO / "ocr-anchors.json").read_text(encoding="utf-8"))
    results: list[dict[str, object]] = []
    for index, anchor in enumerate(anchors, start=1):
        frame = frames_dir / f"{index:02d}-{compact(anchor['term'])}.png"
        subprocess.run(  # noqa: S603 - fixed binary and generated frame path
            [
                "/usr/bin/ffmpeg",
                "-v",
                "error",
                "-y",
                "-ss",
                str(anchor["second"]),
                "-i",
                str(source),
                "-frames:v",
                "1",
                "-vf",
                "scale=3840:2160:flags=lanczos",
                str(frame),
            ],
            check=True,
        )
        ocr = subprocess.run(  # noqa: S603 - fixed binary and generated frame path
            ["/usr/bin/tesseract", str(frame), "stdout", "-l", "eng", "--psm", "11"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        compact_ocr = compact(ocr)
        found = any(candidate in compact_ocr for candidate in ocr_candidates(str(anchor["term"])))
        results.append({**anchor, "found": found, "frame": frame.name})
    payload = {
        "status": "PASS" if all(item["found"] for item in results) else "FAIL",
        "terms": results,
    }
    (report_dir / "ocr-audit.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
