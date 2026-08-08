#!/usr/bin/env python3
"""Fail the video build when narration, captions, and visuals drift apart."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VIDEO = ROOT / "video"
TIMELINE = json.loads((VIDEO / "timeline.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((VIDEO / "public/data/voiceover-manifest.json").read_text(encoding="utf-8"))
CAPTIONS = json.loads((VIDEO / "public/data/captions.json").read_text(encoding="utf-8"))
ANCHORS = json.loads((VIDEO / "semantic-anchors.json").read_text(encoding="utf-8"))


def tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+(?:-[a-z0-9_]+)*", value.lower())


def visual_text(shot: dict[str, object]) -> str:
    fields = ["eyebrow", "metric", "headline", "subhead", "badge"]
    values = [str(shot.get(field, "")) for field in fields]
    values.extend(str(item) for item in shot.get("bullets", []))
    return " ".join(values)


def shot_rows() -> dict[str, dict[str, object]]:
    fps = int(TIMELINE["fps"])
    rows: dict[str, dict[str, object]] = {}
    shot_count = 0
    for chapter in TIMELINE["chapters"]:
        cursor_ms = int(chapter["startMs"])
        for shot in chapter["shots"]:
            duration_ms = int(shot["duration"]) * 1000 / fps
            rows[str(shot["id"])] = {
                **shot,
                "chapter": chapter["id"],
                "startMs": cursor_ms,
                "endMs": cursor_ms + duration_ms,
            }
            cursor_ms += duration_ms
            shot_count += 1
        assert round(cursor_ms) == int(chapter["endMs"]), chapter["id"]
    assert shot_count == 34, shot_count
    assert int(TIMELINE["durationFrames"]) == 4740
    assert int(TIMELINE["durationSeconds"]) == 158
    return rows


def word_rows() -> dict[str, list[dict[str, object]]]:
    rows: dict[str, list[dict[str, object]]] = {}
    for scene in MANIFEST["scenes"]:
        chapter = str(scene["chapter"])
        sidecar = VIDEO / "public/audio/voiceover" / f"scene-{int(scene['id']):02d}.json"
        source = json.loads(sidecar.read_text(encoding="utf-8"))["captions"]
        start_ms = int(scene["startMs"])
        rows[chapter] = [
            {
                "tokens": tokens(str(item["text"])),
                "startMs": int(item["startMs"]) + start_ms,
                "endMs": int(item["endMs"]) + start_ms,
            }
            for item in source
            if tokens(str(item["text"]))
        ]
        chapter_row = next(item for item in TIMELINE["chapters"] if item["id"] == chapter)
        assert int(scene["startMs"]) >= int(chapter_row["startMs"])
        assert int(scene["endMs"]) <= int(chapter_row["endMs"])
    return rows


def find_spoken_start(words: list[dict[str, object]], phrase: str) -> int:
    flat: list[tuple[str, int]] = []
    for index, word in enumerate(words):
        flat.extend((token, index) for token in word["tokens"])
    target = tokens(phrase)
    for offset in range(len(flat) - len(target) + 1):
        if [value for value, _ in flat[offset : offset + len(target)]] == target:
            return int(words[flat[offset][1]]["startMs"])
    raise AssertionError(f"spoken anchor not found: {phrase}")


def check_caption_boundaries(words_by_chapter: dict[str, list[dict[str, object]]]) -> None:
    starts = {int(word["startMs"]) for words in words_by_chapter.values() for word in words}
    raw_ends: set[int] = set()
    for scene in MANIFEST["scenes"]:
        sidecar = VIDEO / "public/audio/voiceover" / f"scene-{int(scene['id']):02d}.json"
        start_ms = int(scene["startMs"])
        raw = json.loads(sidecar.read_text(encoding="utf-8"))["captions"]
        raw_ends.update(int(item["endMs"]) + start_ms for item in raw)
    for caption in CAPTIONS:
        assert 1 <= len(tokens(str(caption["text"]))) <= 7, caption["text"]
        assert min(abs(int(caption["startMs"]) - value) for value in starts) <= 100
        assert min(abs(int(caption["endMs"]) - value) for value in raw_ends) <= 100


def main() -> None:
    shots = shot_rows()
    words = word_rows()
    check_caption_boundaries(words)
    assert len(ANCHORS) >= 20
    results: list[dict[str, object]] = []
    for anchor in ANCHORS:
        shot = shots[str(anchor["shot"])]
        assert shot["chapter"] == anchor["chapter"], anchor
        assert str(anchor["visualContains"]).lower() in visual_text(shot).lower(), anchor
        spoken_ms = find_spoken_start(words[str(anchor["chapter"])], str(anchor["spoken"]))
        start_ms = float(shot["startMs"])
        end_ms = float(shot["endMs"])
        delta_ms = max(start_ms - spoken_ms, spoken_ms - end_ms, 0)
        assert delta_ms <= 250, {**anchor, "spokenMs": spoken_ms, "deltaMs": delta_ms}
        results.append({**anchor, "spokenMs": spoken_ms, "deltaMs": round(delta_ms)})
    print(
        json.dumps(
            {
                "status": "PASS",
                "durationSeconds": 158,
                "shots": len(shots),
                "captions": len(CAPTIONS),
                "semanticAnchors": len(results),
                "maxAnchorDeltaMs": max(item["deltaMs"] for item in results),
                "captionBoundaryToleranceMs": 100,
            }
        )
    )


if __name__ == "__main__":
    main()
