#!/bin/sh
# Regenerates preview/*.png and docs/images/ (screens sheet, hero, demo GIF) from the exact
# 32x8 frames: the Subway layouts from the test suite, the stock Time/Date frames from
# tools/frames/ (made by tools/preview_clock.cpp), the overnight capture from preview/device/.
# Needs a firmware/ checkout (tools/setup-firmware.sh), cmake and Python with Pillow.
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
(cd "$root/firmware" && MTA_PREVIEW_DIR="$work" CXXFLAGS="${CXXFLAGS:--Wno-inconsistent-missing-override}" \
  python3 scripts/test_native.py -R mtafeed >/dev/null)
cp "$root"/tools/frames/*.png "$work"/
cp "$work/preview.txt" "$root/preview/preview.txt"
python3 "$root/tools/render_led.py" "$work"
