# RepairPilot video project

This Remotion project renders the 175-second competition demo from real
RepairPilot, DataHub, and GitHub captures plus verified JSON artifacts. The
complete editorial contract and 50-shot list are in [`../video-spec.md`](../video-spec.md).

## Rebuild

```bash
cd video
npm install
uv run --with edge-tts python scripts/generate_voiceover.py
npm run lint
npx remotion render RepairPilotDemo output/repairpilot-demo-raw.mp4 \
  --codec=h264 --crf=18 --pixel-format=yuv420p \
  --audio-codec=aac --audio-bitrate=192k \
  --browser-executable=/snap/bin/chromium
./scripts/normalize_audio.sh
./scripts/validate_video.sh
```

`--browser-executable` is used because the production build server is ARM64.
On x86 hosts, Remotion's managed Chrome may be used instead.

## Provenance

- UI screenshots and the browser recording come from the deployed public demo.
- DataHub pages use the original DataHub OSS UI and colors.
- The voice is generated with Microsoft Edge TTS, voice
  `en-US-AndrewMultilingualNeural`, from `narration.txt`.
- Interface tones are locally synthesized sine waves; no third-party music is
  included.
- All business data is synthetic; all technical execution shown is real.
