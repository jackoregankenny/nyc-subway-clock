#!/bin/sh
# Recreates firmware/: AWTRIX NG at the pinned upstream commit, with patches/*.patch applied as
# commits on a btrain branch. Then build with: cd firmware && pio run -e awtrix
#   UPSTREAM=<url or path>  clone from somewhere else (default: GitHub)
#   DEST=<dir>              put the checkout somewhere else (default: firmware/)
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
base=d51e266e529fa377e6e4af611c4d1f974633e513
upstream=${UPSTREAM:-https://github.com/Blueforcer/awtrix-ng.git}
dest=${DEST:-$root/firmware}
if [ -e "$dest" ]; then echo "$dest already exists; move it away first" >&2; exit 1; fi
git clone -q "$upstream" "$dest"
git -C "$dest" switch -q -C btrain "$base"
git -C "$dest" am -q --committer-date-is-author-date "$root"/patches/*.patch
git -C "$dest" log --oneline "$base..btrain"
