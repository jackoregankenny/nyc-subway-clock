#!/bin/sh
# Fetches all eight MTA subway feeds and compares this repo's C++ decoder with Google's
# gtfs-realtime-bindings for one stop on every line. Needs clang++ and uv. Dev-only.
set -eu
here=$(cd "$(dirname "$0")" && pwd); fw="$here/../firmware"; work=$(mktemp -d)
for f in gtfs gtfs-ace gtfs-bdfm gtfs-g gtfs-jz gtfs-nqrw gtfs-l gtfs-si; do
  curl -sSf -H 'Accept-Encoding: identity' -o "$work/$f.pb" "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2F$f"
done
clang++ -std=gnu++17 -O2 -I "$fw/src" "$here/crosscheck_decode.cpp" "$fw/src/core/transit/GtfsRtDecoder.cpp" -o "$work/cdecode"
pass=0; fail=0
while read -r feed route stop; do
  c=$("$work/cdecode" "$work/$feed.pb" "$route" "$stop")
  r=$(uv run -q --no-project --with gtfs-realtime-bindings python -I "$here/crosscheck_reference.py" "$work/$feed.pb" "$route" "$stop")
  if [ "$c" = "$r" ]; then pass=$((pass+1)); echo "ok   $route $stop"; else fail=$((fail+1)); echo "DIFF $route $stop c=[$c] r=[$r]"; fi
done <<LIST
gtfs 1 127S
gtfs 2 127N
gtfs 3 127S
gtfs 4 631S
gtfs 5 631N
gtfs 6 631S
gtfs 6X 601S
gtfs 7 725S
gtfs 7X 725N
gtfs GS 902S
gtfs-ace A A27S
gtfs-ace C A21N
gtfs-ace E A27N
gtfs-ace H H04N
gtfs-bdfm B A21S
gtfs-bdfm D D14S
gtfs-bdfm F F14N
gtfs-bdfm M F14S
gtfs-bdfm FS S01N
gtfs-g G G22S
gtfs-jz J J27N
gtfs-l L L03S
gtfs-nqrw N R16S
gtfs-nqrw Q R16N
gtfs-nqrw R R16S
gtfs-nqrw W R16N
gtfs-si SI S31N
LIST
rm -rf "$work"
echo "pass=$pass fail=$fail"; [ "$fail" -eq 0 ]
