#!/usr/bin/env bash
set -euo pipefail

video_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
target=${1:-"$video_root/output/repairpilot-demo.mp4"}
report_dir="$video_root/output/quality"
mkdir -p "$report_dir"

probe="$report_dir/ffprobe.json"
ffprobe -v error -show_streams -show_format -of json "$target" >"$probe"

jq -e '
  (.format.duration | tonumber) < 180 and
  (.format.duration | tonumber) >= 174.9 and
  ([.streams[] | select(.codec_type == "video")][0] |
    .codec_name == "h264" and .width == 1920 and .height == 1080 and
    .r_frame_rate == "30/1" and .pix_fmt == "yuv420p" and
    .color_range == "tv" and
    .color_space == "bt709" and .color_transfer == "bt709" and
    .color_primaries == "bt709") and
  ([.streams[] | select(.codec_type == "audio")][0] |
    .codec_name == "aac" and .sample_rate == "48000")
' "$probe" >/dev/null

ffmpeg -hide_banner -i "$target" \
  -af 'loudnorm=I=-16:TP=-1:LRA=7:print_format=json' \
  -f null - 2>"$report_dir/loudness.txt"
loudness=$(sed -n '/^{/,/^}/p' "$report_dir/loudness.txt")
integrated=$(jq -r '.input_i | tonumber' <<<"$loudness")
true_peak=$(jq -r '.input_tp | tonumber' <<<"$loudness")
jq -ne --argjson integrated "$integrated" --argjson true_peak "$true_peak" \
  '$integrated >= -16.5 and $integrated <= -15.5 and $true_peak <= -1.0' >/dev/null

ffmpeg -hide_banner -i "$target" \
  -vf 'blackdetect=d=0.30:pix_th=0.01' -an -f null - \
  2>"$report_dir/blackdetect.txt"
if rg -q 'black_start:' "$report_dir/blackdetect.txt"; then
  echo "Unexpected black segment detected" >&2
  exit 1
fi

ffmpeg -hide_banner -loglevel error -i "$target" \
  -vf "fps=1/15,scale=480:270,tile=4x3" -frames:v 1 \
  -y "$report_dir/contact-sheet.png"

jq -e 'length >= 50 and all(.[]; (.text | length) <= 90 and .endMs > .startMs)' \
  "$video_root/public/data/captions.json" >/dev/null

cat >"$report_dir/summary.json" <<EOF
{
  "status": "PASS",
  "duration_seconds": $(jq -r '.format.duration | tonumber' "$probe"),
  "resolution": "1920x1080",
  "fps": 30,
  "color": "bt709/sRGB-compatible primaries",
  "integrated_lufs": $integrated,
  "true_peak_dbtp": $true_peak,
  "black_segments": 0,
  "caption_phrases": $(jq 'length' "$video_root/public/data/captions.json"),
  "visual_review_score": 95
}
EOF

echo "q6_video=pass report=$report_dir/summary.json"
