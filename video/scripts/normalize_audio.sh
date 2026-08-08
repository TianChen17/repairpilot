#!/usr/bin/env bash
set -euo pipefail

video_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
input=${1:-"$video_root/output/repairpilot-demo-raw.mp4"}
output=${2:-"$video_root/output/repairpilot-demo.mp4"}
analysis_file=$(mktemp /tmp/repairpilot-loudness-XXXXXX.txt)
normalized_audio=$(mktemp /tmp/repairpilot-normalized-XXXXXX.m4a)
trap 'rm -f "$analysis_file" "$normalized_audio"' EXIT

ffmpeg -hide_banner -i "$input" \
  -map 0:a:0 \
  -af 'loudnorm=I=-16:TP=-1.3:LRA=7:print_format=json' \
  -f null - 2>"$analysis_file"

analysis=$(sed -n '/^{/,/^}/p' "$analysis_file")
input_i=$(jq -r '.input_i' <<<"$analysis")
input_tp=$(jq -r '.input_tp' <<<"$analysis")
input_lra=$(jq -r '.input_lra' <<<"$analysis")
input_thresh=$(jq -r '.input_thresh' <<<"$analysis")
target_offset=$(jq -r '.target_offset' <<<"$analysis")

ffmpeg -hide_banner -loglevel error -i "$input" \
  -map 0:a:0 \
  -af "loudnorm=I=-16:TP=-1.3:LRA=7:measured_I=$input_i:measured_TP=$input_tp:measured_LRA=$input_lra:measured_thresh=$input_thresh:offset=$target_offset:linear=true:print_format=summary" \
  -ar 48000 -c:a aac -b:a 192k -y "$normalized_audio"

# Video is copied byte-for-byte from the single CRF 14 Remotion encode. Only
# the separately normalized AAC stream is remuxed, so UI pixels are not encoded
# a second time.
ffmpeg -hide_banner -loglevel error \
  -i "$input" -i "$normalized_audio" \
  -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a copy \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -movflags +faststart -y "$output"

echo "normalized_video=$output video_codec=copy"
