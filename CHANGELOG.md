# Changelog

All on AWTRIX NG 1.2.3 (`d51e266`).

## 1.0.0 (2026-11-13)

The first public release, after a few days on a real clock.

- **Up to three lines at one station.** Default `B,C,A` at 81 St–Museum of Natural History,
  downtown: B and C by day, the A overnight when it makes local stops. Lines in the same feed
  share one download.
- **Layouts:** numbers (all lines in time order, colored by line, no letters, left-aligned),
  bullets (two lines side by side) and turns (one line at a time). `N` for an arriving train.
- **MTA alerts:** a red dot while the MTA reports an unplanned disruption on one of the lines.
- **Off when dark:** the display switches off in a pitch-black room (default 1% light) and
  downloads pause until it's light again. New setting in the web UI's Brightness section.
- **Gzip downloads** through the ESP32's ROM inflater: about a fifth of the data.
- Fixed: a boot loop from 64-bit `printf` conversions, which the firmware's nano printf lacks.
- Fixed: gzip downloads failing their final check because the ROM inflater reads past the end
  of the data.

## 0.1 (2026-11-10)

- One line at any station, any of the 29 NYC subway routes, live from the MTA's GTFS-Realtime
  feeds, with no server in between.
- Streaming decoder with under 640 bytes of state; TLS verified against pinned roots.
- First-boot defaults: New York time, 12-hour clock, month/day dates, auto-brightness, sound off.
