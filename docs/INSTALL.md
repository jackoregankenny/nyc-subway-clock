# Install

Flash the clock once over USB. After that it needs no computer: Wi-Fi is set on the clock's own
hotspot, and updates go through its web UI.

You need:

- a **Ulanzi TC001** (check the label: TC001, classic ESP32, 4 MB; the TC002 is a different
  device and isn't supported);
- a **USB-C data cable**, plugged straight into the computer (no hub). Charge-only cables are
  common, and with one the clock simply doesn't show up;
- [uv](https://docs.astral.sh/uv/) (or Python with `pip install esptool==4.8.1`), on macOS, Linux
  or Windows.

Download the images from the [latest release](https://github.com/jackoregankenny/nyc-subway-clock/releases/latest), or build them yourself
([DEVELOPMENT.md](DEVELOPMENT.md)):

| File | Use |
|---|---|
| `awtrix-ng-subway-usb-4mb.bin` | First install over USB, written at offset `0x0` (bootloader, partitions, app) |
| `awtrix-ng-subway-ota.bin` | Update a clock that already runs AWTRIX NG or an earlier version of this, from its web UI |

The release notes list their SHA-256 hashes.

## Already running AWTRIX NG?

Open the clock's web UI → **System** → **Maintenance** → **Firmware update**, choose
`awtrix-ng-subway-ota.bin`, and wait for the restart. Your settings and Wi-Fi stay. The Subway app
installs itself on the first boot. Skip the rest of this page.

Use the same upload for later versions of this project. **Don't use "Check for updates" /
"Download & install"** there: that installs the official AWTRIX NG release, which has no Subway
support (the clock keeps working, the Subway screen stops).

## 1. Find the serial port

Plug the clock in. On macOS, allow the accessory if asked. Then list the ports:

```bash
ls /dev/cu.*
```

On macOS look for `/dev/cu.usbserial-…` or `/dev/cu.wchusbserial…`; on Linux `/dev/ttyUSB0`; on
Windows a `COM` port in Device Manager. Use it as `PORT` below, and check that it's the clock:

```bash
uv run --no-project --with esptool==4.8.1 python -m esptool --port PORT flash_id
```

It should report an `ESP32` with `4MB` of flash.

## 2. Back up the stock firmware

Ulanzi's own firmware may not be available to download again, so keep a copy if you might want it
back:

```bash
uv run --no-project --with esptool==4.8.1 python -m esptool --chip esp32 --port PORT --baud 115200 read_flash 0x0 0x400000 tc001-stock-4mb.bin
```

It takes about two minutes and must come out at exactly 4,194,304 bytes. To restore it later,
`write_flash 0x0 tc001-stock-4mb.bin` the same way.

## 3. Flash

```bash
uv run --no-project --with esptool==4.8.1 python -m esptool --chip esp32 --port PORT --baud 115200 write_flash 0x0 awtrix-ng-subway-usb-4mb.bin
```

Wait for `Hash of data verified.` (about two minutes). 115200 baud is slow but reliable on the
TC001; faster rates often drop out partway. A write that stops partway does no harm, because the
ESP32's bootloader is in ROM: run it again.

The buzzer whines while the chip is in download mode. That's normal and stops once it boots.

## 4. First boot and Wi-Fi

1. The boot animation plays and the clock opens its setup network, `awtrixng-…`.
2. Join it from a phone. The setup page opens by itself; if not, go to `http://192.168.4.1`.
3. Pick your Wi-Fi (2.4 GHz), type the password, save. The clock restarts and joins. A phone
   hotspot works too (on an iPhone, turn on **Maximize Compatibility**).
4. The clock's address scrolls by on the display. Open it in a browser on the same network.

On its first boot the clock applies these defaults once (change any of them later; your changes
stick): New York time, 12-hour clock, month/day dates, auto-brightness on, display off in a
pitch-black room, sound off, and the Subway app installed for downtown B, C and A at 81 St.

## 5. Check it

- **Time** shows New York time.
- **Apps** → gear next to **Subway**: set your Lines, Station ID and Direction
  ([STATIONS.md](STATIONS.md)) and save.
- Within about a minute the Subway screen shows times. Compare with the MTA's app or website.
- The web UI's log shows a line like `B A21S live 4 11 | feed age 12s | last ok …`.
- Cover the light sensor (left of the display): the display dims, and after 30 seconds in full
  darkness goes off. Uncover it and it comes back.

The [user guide](USER_GUIDE.md) explains the screens and settings, and has a troubleshooting table.

## Giving one away

Test it on a phone hotspot, then switch the hotspot off: with no known network around, the clock
opens its setup hotspot by itself at its new home (check once by unplugging and replugging it). Put the [card](GIFT_CARD.md) in the box. Don't use
factory reset to clear Wi-Fi: it erases settings (the Subway app and defaults come back, your own
changes don't).
