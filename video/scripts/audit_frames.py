#!/usr/bin/env python3
"""Detect black frames and one-frame luma flashes in a rendered video."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: audit_frames.py VIDEO REPORT.json")
    source = Path(sys.argv[1])
    report = Path(sys.argv[2])
    result = subprocess.run(  # noqa: S603 - fixed binary and read-only media arguments
        [
            "/usr/bin/ffmpeg",
            "-v",
            "error",
            "-i",
            str(source),
            "-vf",
            "fps=30,scale=1:1:flags=area,format=gray",
            "-f",
            "rawvideo",
            "-",
        ],
        check=True,
        capture_output=True,
    )
    luma = list(result.stdout)
    black_frames = [index for index, value in enumerate(luma) if value <= 2]
    local_dips: list[dict[str, float | int]] = []
    local_spikes: list[dict[str, float | int]] = []
    for index in range(1, len(luma) - 1):
        before, value, after = luma[index - 1], luma[index], luma[index + 1]
        neighbor_floor = min(before, after)
        neighbor_ceiling = max(before, after)
        if neighbor_floor >= 70 and value <= neighbor_floor * 0.55:
            local_dips.append(
                {
                    "frame": index,
                    "second": round(index / 30, 3),
                    "before": before,
                    "value": value,
                    "after": after,
                }
            )
        if neighbor_ceiling <= 80 and value >= max(120, neighbor_ceiling * 1.75):
            local_spikes.append(
                {
                    "frame": index,
                    "second": round(index / 30, 3),
                    "before": before,
                    "value": value,
                    "after": after,
                }
            )
    payload = {
        "status": "PASS" if not black_frames and not local_dips and not local_spikes else "FAIL",
        "frames": len(luma),
        "blackFrames": len(black_frames),
        "singleFrameLumaDips": local_dips,
        "singleFrameLumaSpikes": local_spikes,
        "minimumLuma": min(luma),
        "maximumLuma": max(luma),
    }
    report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
