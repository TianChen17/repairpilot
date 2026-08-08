#!/usr/bin/env python3
"""Generate deterministic scene audio and word-timed captions with Edge TTS."""

from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[2]
VIDEO = ROOT / "video"
AUDIO = VIDEO / "public" / "audio" / "voiceover"
DATA = VIDEO / "public" / "data"
VOICE = "en-US-AndrewMultilingualNeural"
RATE = "+18%"
PITCH = "-2Hz"
GAP_MS = 350
TARGET_DURATION_MS = 175_000
PREFERRED_START_MS = [
    650,
    13_200,
    21_500,
    33_500,
    44_700,
    56_500,
    73_800,
    91_000,
    101_300,
    114_300,
    135_200,
    151_200,
    162_000,
    168_000,
]


def phrase_captions(captions: list[dict[str, object]]) -> list[dict[str, object]]:
    """Split sentence boundaries into readable caption phrases."""
    phrases: list[dict[str, object]] = []
    for caption in captions:
        words = str(caption["text"]).split()
        groups = [words[offset : offset + 7] for offset in range(0, len(words), 7)]
        start_ms = int(caption["startMs"])
        end_ms = int(caption["endMs"])
        total_words = max(len(words), 1)
        consumed = 0
        for group in groups:
            group_start = start_ms + round((end_ms - start_ms) * consumed / total_words)
            consumed += len(group)
            group_end = start_ms + round((end_ms - start_ms) * consumed / total_words)
            phrases.append(
                {
                    "text": " " + " ".join(group),
                    "startMs": group_start,
                    "endMs": group_end,
                    "timestampMs": group_start,
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
    if target.stat().st_size > 1_000 if target.exists() else False:
        if sidecar.exists():
            cached = json.loads(sidecar.read_text(encoding="utf-8"))
            if (
                isinstance(cached, dict)
                and cached.get("voice") == VOICE
                and cached.get("rate") == RATE
                and cached.get("pitch") == PITCH
                and cached.get("text") == text
            ):
                return target, cached["captions"]

    for attempt in range(1, 5):
        temporary = target.with_suffix(".mp3.part")
        temporary.unlink(missing_ok=True)
        words: list[dict[str, object]] = []
        try:
            communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
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
                        "rate": RATE,
                        "pitch": PITCH,
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

    scene_rows: list[dict[str, object]] = []
    captions: list[dict[str, object]] = []
    cursor_ms = 650

    for index, paragraph in enumerate(paragraphs, start=1):
        target, scene_words = await generate_scene(index, paragraph)
        scene_duration = duration_ms(target)
        cursor_ms = max(cursor_ms, PREFERRED_START_MS[index - 1])
        for word in phrase_captions(scene_words):
            captions.append(
                {
                    **word,
                    "startMs": int(word["startMs"]) + cursor_ms,
                    "endMs": int(word["endMs"]) + cursor_ms,
                    "timestampMs": int(word["timestampMs"]) + cursor_ms,
                }
            )
        scene_rows.append(
            {
                "id": index,
                "audio": f"audio/voiceover/{target.name}",
                "startMs": cursor_ms,
                "durationMs": scene_duration,
                "text": paragraph,
            }
        )
        cursor_ms += scene_duration + GAP_MS
        await asyncio.sleep(0.75)

    if cursor_ms > TARGET_DURATION_MS - 1_500:
        raise SystemExit(f"Voiceover ends at {cursor_ms / 1000:.2f}s; regenerate at a faster rate.")

    (DATA / "captions.json").write_text(
        json.dumps(captions, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (DATA / "voiceover-manifest.json").write_text(
        json.dumps(
            {
                "voice": VOICE,
                "rate": RATE,
                "pitch": PITCH,
                "targetDurationMs": TARGET_DURATION_MS,
                "speechEndMs": cursor_ms - GAP_MS,
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
                "speech_end_seconds": round((cursor_ms - GAP_MS) / 1000, 3),
            }
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
