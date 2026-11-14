# FAQ

### Does it need a server, an account or an API key?

No. The clock downloads the MTA's public real-time feeds directly over HTTPS. The MTA doesn't
require a key for the subway feeds. Nothing else is involved apart from an NTP time server.

### How accurate are the times?

They're the MTA's own predictions, the same data behind the countdown clocks in stations and the
MTA's app. The clock rounds down to whole minutes, like those do, and counts down by itself
between downloads, so it's never more than about 30 seconds behind the feed. Expect the same
occasional surprises the station clocks have: a train that sits, or one that skips your stop.

### Why is a line missing?

A line only shows when it has trains predicted at your platform. At 81 St the A stops only late
at night, so with `B,C,A` the A appears overnight and drops out by day. The same goes for
weekend and night service changes. If a line never appears, check the log for
`route not in this feed` or `stop not in this feed` (see the
[troubleshooting table](USER_GUIDE.md#troubleshooting)).

### Why do two lines have the same color?

The colors are the MTA's: lines on the same trunk share one (A, C and E are all blue; B, D, F and
M are all orange). If two of your lines share a color and you need to tell them apart, use the
**bullets** or **turns** layout, which show letters.

### Which stations work?

All 496 subway stations, including the Staten Island Railway, with up to three lines each. Look
yours up in [STATIONS.md](STATIONS.md). Buses, LIRR, Metro-North and PATH aren't supported.

### How much data does it use?

About 6–7 MB an hour while the display is on, with the default three lines and alerts on. That's
two gzipped feeds every 30 seconds (about 10–30 KB each) and the alerts every 5 minutes (about
90 KB). With the display off or the room dark, nothing at all.

### Does it phone home or collect anything?

No. Apart from the MTA's feed servers and NTP, the clock contacts nothing. There's no analytics,
and no account to sign in to.

### Can I still use the other AWTRIX features?

Yes. It's AWTRIX NG with one app added: the time, date, sensors, notifications, custom apps,
scripts, MQTT and the web UI all work as usual. See the
[AWTRIX NG documentation](https://github.com/Blueforcer/awtrix-ng).

### What happens if I update to an official AWTRIX NG release?

The clock keeps working, but the Subway screen stops: the official release doesn't contain the
native part the app needs. Install this project's update file again to get it back.

### Does it work on other clocks?

It's built for the Ulanzi TC001 (classic ESP32, 32×8). AWTRIX NG also runs on other hardware,
but this project is only built and tested for the TC001.

### Can I sell clocks with this on them?

No. AWTRIX NG's license, PolyForm Noncommercial 1.0.0, allows noncommercial use only, and this
project is under the same license. Giving one as a present is fine.

### Is this an official MTA product?

No. It uses the MTA's public data under the MTA's developer terms, and isn't affiliated with or
endorsed by the MTA.
