#!/usr/bin/env python3
"""Generate deterministic scene audio and word-timed captions with Edge TTS."""

from __future__ import annotations

import asyncio
import json
import re
import subprocess
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[2]
VIDEO = ROOT / "video"
AUDIO = VIDEO / "public" / "audio" / "voiceover"
DATA = VIDEO / "public" / "data"
VOICE = "en-US-AndrewMultilingualNeural"
RATE = "+18%"
CLOSING_RATE = "+70%"
PITCH = "-2Hz"
BOUNDARY = "WordBoundary"
TIMELINE = json.loads((VIDEO / "timeline.json").read_text(encoding="utf-8"))
TARGET_DURATION_MS = int(TIMELINE["durationSeconds"] * 1000)


def phrase_captions(captions: list[dict[str, object]]) -> list[dict[str, object]]:
    """Group exact word boundaries into phrases of no more than seven words."""
    normalized: list[dict[str, object]] = []
    for caption in captions:
        token = str(caption["text"]).strip()
        if not re.search(r"[A-Za-z0-9_]", token):
            if normalized:
                normalized[-1] = {
                    **normalized[-1],
                    "text": f"{str(normalized[-1]['text']).rstrip()}{token}",
                    "endMs": int(caption["endMs"]),
                }
            continue
        normalized.append({**caption, "text": token})

    phrases: list[dict[str, object]] = []
    group: list[dict[str, object]] = []
    for caption in normalized:
        group.append(caption)
        word = str(caption["text"]).strip()
        if len(group) < 7 and not word.endswith((".", "?", "!", ":", ";")):
            continue
        phrases.append(
            {
                "text": " " + " ".join(str(item["text"]).strip() for item in group),
                "startMs": int(group[0]["startMs"]),
                "endMs": int(group[-1]["endMs"]),
                "timestampMs": int(group[0]["startMs"]),
                "confidence": None,
            }
        )
        group = []
    if group:
        phrases.append(
            {
                "text": " " + " ".join(str(item["text"]).strip() for item in group),
                "startMs": int(group[0]["startMs"]),
                "endMs": int(group[-1]["endMs"]),
                "timestampMs": int(group[0]["startMs"]),
                "confidence": None,
            }
        )
    return phrases


def duration_ms(path: Path) -> int:
    result = subprocess.run(  # noqa: S603 - fixed ffprobe command and generated path
        [
            "/usr/bin/ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return round(float(result.stdout.strip()) * 1000)


async def generate_scene(index: int, text: str) -> tuple[Path, list[dict[str, object]]]:
    target = AUDIO / f"scene-{index:02d}.mp3"
    sidecar = AUDIO / f"scene-{index:02d}.json"
    scene_rate = CLOSING_RATE if index == 10 else RATE
    if target.stat().st_size > 1_000 if target.exists() else False:
        if sidecar.exists():
            cached = json.loads(sidecar.read_text(encoding="utf-8"))
            if (
                isinstance(cached, dict)
                and cached.get("voice") == VOICE
                and cached.get("rate") == scene_rate
                and cached.get("pitch") == PITCH
                and cached.get("boundary") == BOUNDARY
                and cached.get("text") == text
            ):
                return target, cached["captions"]

    for attempt in range(1, 5):
        temporary = target.with_suffix(".mp3.part")
        temporary.unlink(missing_ok=True)
        words: list[dict[str, object]] = []
        try:
            communicate = edge_tts.Communicate(
                text, VOICE, rate=scene_rate, pitch=PITCH, boundary=BOUNDARY
            )
            with temporary.open("wb") as audio_file:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_file.write(chunk["data"])
                    elif chunk["type"] in {"WordBoundary", "SentenceBoundary"}:
                        words.append(
                            {
                                "text": f" {chunk['text']}",
                                "startMs": round(chunk["offset"] / 10_000),
                                "endMs": round((chunk["offset"] + chunk["duration"]) / 10_000),
                                "timestampMs": round(chunk["offset"] / 10_000),
                                "confidence": None,
                            }
                        )
            if temporary.stat().st_size <= 1_000 or not words:
                raise RuntimeError("TTS returned an incomplete scene")
            temporary.replace(target)
            sidecar.write_text(
                json.dumps(
                    {
                        "voice": VOICE,
                        "rate": scene_rate,
                        "pitch": PITCH,
                        "boundary": BOUNDARY,
                        "text": text,
                        "captions": words,
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            return target, words
        except Exception:
            temporary.unlink(missing_ok=True)
            if attempt == 4:
                raise
            await asyncio.sleep(2**attempt)
    raise AssertionError("unreachable")


async def main() -> None:
    paragraphs = [
        value.strip()
        for value in (VIDEO / "narration.txt").read_text(encoding="utf-8").split("\n\n")
        if value.strip()
    ]
    AUDIO.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    chapters = TIMELINE["chapters"]
    if len(paragraphs) != len(chapters):
        raise SystemExit(
            f"Narration has {len(paragraphs)} paragraphs; timeline has {len(chapters)} chapters."
        )

    scene_rows: list[dict[str, object]] = []
    captions: list[dict[str, object]] = []
    speech_end_ms = 0

    for index, (paragraph, chapter) in enumerate(zip(paragraphs, chapters, strict=True), start=1):
        target, scene_words = await generate_scene(index, paragraph)
        scene_duration = duration_ms(target)
        start_ms = int(chapter["narrationStartMs"])
        end_ms = start_ms + scene_duration
        chapter_end_ms = int(chapter["endMs"])
        if end_ms > chapter_end_ms:
            raise SystemExit(
                f"Narration {index} ends at {end_ms / 1000:.3f}s, after "
                f"chapter {chapter['id']} ends at {chapter_end_ms / 1000:.3f}s."
            )
        for word in phrase_captions(scene_words):
            captions.append(
                {
                    **word,
                    "startMs": int(word["startMs"]) + start_ms,
                    "endMs": int(word["endMs"]) + start_ms,
                    "timestampMs": int(word["timestampMs"]) + start_ms,
                }
            )
        scene_rows.append(
            {
                "id": index,
                "chapter": chapter["id"],
                "audio": f"audio/voiceover/{target.name}",
                "startMs": start_ms,
                "endMs": end_ms,
                "durationMs": scene_duration,
                "rate": CLOSING_RATE if index == 10 else RATE,
                "text": paragraph,
            }
        )
        speech_end_ms = max(speech_end_ms, end_ms)
        await asyncio.sleep(0.75)

    if speech_end_ms > TARGET_DURATION_MS - 250:
        raise SystemExit(
            f"Voiceover ends at {speech_end_ms / 1000:.2f}s; closing hold is too short."
        )

    (DATA / "captions.json").write_text(
        json.dumps(captions, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (DATA / "voiceover-manifest.json").write_text(
        json.dumps(
            {
                "voice": VOICE,
                "rate": RATE,
                "closingRate": CLOSING_RATE,
                "pitch": PITCH,
                "boundary": BOUNDARY,
                "targetDurationMs": TARGET_DURATION_MS,
                "speechEndMs": speech_end_ms,
                "scenes": scene_rows,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "scenes": len(scene_rows),
                "captions": len(captions),
                "speech_end_seconds": round(speech_end_ms / 1000, 3),
            }
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
