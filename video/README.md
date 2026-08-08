# RepairPilot video project

This Remotion project renders the 158-second, 34-shot judge demo from real
RepairPilot, DataHub, and GitHub captures plus verified JSON artifacts. The
single source of timing truth is [`timeline.json`](timeline.json); the complete
editorial contract is in [`../video-spec.md`](../video-spec.md).

## Rebuild

```bash
cd video
npm install
uv run --with edge-tts python scripts/generate_voiceover.py
npm run lint
npm run render
./scripts/normalize_audio.sh
./scripts/validate_video.sh
```

The renderer emits PNG intermediate frames and performs one CRF 14 H.264 encode.
Audio is normalized separately and remuxed with `-c:v copy`, so browser text is
not encoded twice. Validation checks 46 semantic anchors, word-boundary caption
timing, format, loudness, black/flash frames, and the separate 34-shot manual
review record.

## Provenance

- UI screenshots and the browser recording come from the deployed public demo.
- UI stills are lossless 3840×2160 PNG captures with no Ken Burns scaling.
- DataHub pages use the original DataHub OSS UI and colors.
- The voice is generated with Microsoft Edge TTS, voice
  `en-US-AndrewMultilingualNeural`, from `narration.txt`.
- Interface tones are locally synthesized sine waves; no third-party music is
  included.
- All business data is synthetic; all technical execution shown is real.
