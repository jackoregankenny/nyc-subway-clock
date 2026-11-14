# Development

## Two repositories

- **This repo**: docs, tools, previews, and the firmware change as a patch series in `patches/`.
- **The firmware**: a clone of [AWTRIX NG](https://github.com/Blueforcer/awtrix-ng) at `d51e266`
  (v1.2.3, 2026-11-03), with the change as commits on a `btrain` branch. It lives in `firmware/`
  and keeps upstream's history, so moving to a new upstream release is a rebase. This repo ignores
  `firmware/`. The branch is also on GitHub:
  [jackoregankenny/awtrix-ng, branch `btrain`](https://github.com/jackoregankenny/awtrix-ng/tree/btrain).

`patches/` and the `btrain` branch are the same thing; a rebuild from the patches gives the branch's
tree byte for byte.

```bash
tools/setup-firmware.sh
```

That clones AWTRIX NG into `firmware/` and applies the series. After committing in `firmware/`,
refresh the series and commit it here:

```bash
tools/export-patches.sh
```

## Build

Install PlatformIO once (with [uv](https://docs.astral.sh/uv/), or pip):

```bash
uv tool install platformio
```

```bash
cd firmware && pio run -e awtrix
```

The app image is `firmware/.pio/build/awtrix/firmware.bin`: upload it in the web UI
(System → Maintenance → Firmware update), or from a terminal:

```bash
curl -F "firmware=@firmware/.pio/build/awtrix/firmware.bin;filename=firmware-awtrix-ng.bin" http://CLOCK-IP/update
```

The full USB image (bootloader, partitions, app, written at `0x0`):

```bash
cd firmware && uv run --no-project --with esptool==4.8.1 python scripts/factory_image.py --env awtrix --flash-size 4MB -o ../build/awtrix-ng-subway-usb-4mb.bin
```

The image uses 89.5% of a 1,728 KB app slot, so OTA updates keep working.

## Test

The host tests build with CMake and run in seconds. On macOS with Apple clang, one upstream header
needs a warning switched off:

```bash
cd firmware && CXXFLAGS="-Wno-inconsistent-missing-override" python3 scripts/test_native.py -j 6
```

Everything passes except two upstream tests, `test_devicecapabilities` and `test_iconsource`.
They fail the same way on pristine upstream on a Mac (libc++ versus libstdc++ differences) and
pass with GCC. Only this project's suites:

```bash
cd firmware && CXXFLAGS="-Wno-inconsistent-missing-override" python3 scripts/test_native.py -R "mtafeed|subwayscript|brightnesspolicy"
```

What they cover:

- **`test_mtafeed`**: the decoder against real MTA snapshots in `test/fixtures/` (the expected
  values come from Google's reference decoder), every chunk size, malformed input, the 2 MB cap;
  the alerts mask at several moments; gunzip (including an inflater that reads ahead like the ROM
  one, and damaged streams); arrival rules and DST; every layout's pixels (never clipped, the
  alert pixel always free); a check that device code has no 64-bit `printf` conversions.
- **`test_subwayscript`**: the Subway script in the real Berry VM against stub natives: settings,
  defaults, what it passes to the firmware.
- **`test_brightnesspolicy`**: dark-off, with its hold time and hysteresis.

Against the live feeds (needs clang++ and uv):

```bash
tools/crosscheck.sh
```

## Previews

The 32×8 layouts are drawn by `src/core/transit/SubwayView.h`, which the tests also run on the
host. Set `MTA_PREVIEW_DIR` and `test_mtafeed` writes each state as a PPM plus an ASCII board
(`preview.txt`), so you can check a layout change without a clock:

```bash
cd firmware && MTA_PREVIEW_DIR=../preview CXXFLAGS="-Wno-inconsistent-missing-override" python3 scripts/test_native.py -R mtafeed
```

On a clock, `GET /api/v1/display/screen` returns the current 32×8 frame as JSON.

The images in these docs (`preview/*.png`, `docs/images/`) are rendered from those exact frames
by one script, so they always match the code:

```bash
tools/render-docs-images.sh
```

## Where things are

| Piece | Files (in `firmware/`) |
|---|---|
| Decoder | `src/core/transit/GtfsRtDecoder.*` |
| Arrival rules | `src/core/transit/ArrivalBoard.h` |
| Routes, feeds, colors | `src/core/transit/Routes.h` |
| Layouts | `src/core/transit/SubwayView.h` |
| Gunzip framing | `src/core/transit/Gunzip.h` (portable), `src/system/RomInflater.h` (ESP32 ROM) |
| Fetch task, script natives | `src/system/MtaFeedService.*`, pinned roots in `src/system/MtaRoots.h` |
| The Subway app | `src/system/SubwayScript.h` (Berry source; bump `kSubwayScriptVersion` to replace installed copies) |
| First-boot defaults | `src/system/GiftDefaults.*` (versioned, so new defaults apply once to existing clocks) |
| Dark-off | `src/core/sensing/BrightnessPolicy.*`, setting `darkOffLevel` |
| Hooks into AWTRIX NG | `src/main.cpp` (8 lines) |

The Subway app's log line comes from `subway_status()`; the clock's log is at `/api/v1/logs`.

## ESP32 lessons

Things that cost time, so they don't again:

- **No 64-bit `printf`.** The firmware links newlib's nano printf, which has no `%lld`; one
  shifted the arguments, a `%s` read NULL and the clock boot-looped. Use `%ld` with `long`. The
  tests fail on any `ll`, `j` or `z` conversion in the device sources.
- **`HTTPClient` adds `Accept-Encoding: identity`** to every HTTP/1.1 request, before your own
  headers, and the MTA obeys the first one. Put yours on the `User-Agent` line.
- **The ROM tinfl reads ahead** up to 4 bytes past the DEFLATE end and doesn't return them. Read
  the gzip trailer from the last 8 bytes of the input.
- **Float settings must be positive** in AWTRIX NG's settings schema; use an int when 0 means "off".
- **Flash at 115200 baud.** The TC001's USB-serial link drops out at 460800 and above.

## Moving to a new AWTRIX NG release

```bash
cd firmware && git fetch origin --tags && git rebase --onto <new tag> d51e266 btrain
```

Then update the base hash in `tools/setup-firmware.sh` and `tools/export-patches.sh`, run the
tests, build, try it on a clock, and export the patches.

## Releases

A release attaches the two images (`awtrix-ng-subway-usb-4mb.bin`, `awtrix-ng-subway-ota.bin`)
with their SHA-256 hashes, and tags both repos with the same version.
