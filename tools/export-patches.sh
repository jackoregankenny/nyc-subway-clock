#!/bin/sh
# Writes the btrain branch of firmware/ as a patch series in patches/ (one file per commit, the
# commit messages kept), replacing what is there. Run after committing in firmware/.
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
base=d51e266e529fa377e6e4af611c4d1f974633e513
git -C "$root/firmware" rev-parse --verify -q btrain >/dev/null || { echo "firmware/ has no btrain branch" >&2; exit 1; }
mkdir -p "$root/patches"
find "$root/patches" -name '*.patch' -delete
git -C "$root/firmware" format-patch -q --binary --zero-commit --no-signature --no-numbered \
  -o "$root/patches" "$base..btrain"
ls "$root/patches"
