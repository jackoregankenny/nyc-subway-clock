# User guide

Everything the Subway clock shows and every setting it has. For flashing a clock, see
[INSTALL.md](INSTALL.md).

## Reading the screen

The clock rotates through its apps (Time, Subway, and whatever else you switch on). The Subway
screen looks like this with the default layout:

| You see | It means |
|---|---|
| `3   7   12   25`, in orange and blue | Trains in 3, 7, 12 and 25 minutes, soonest first. Each number is in its line's color: orange B, blue A or C, and so on |
| `N` | A train arriving now (under a minute) |
| `12 MIN` | Only one train is predicted |
| A red dot, top right | The MTA reports delays, suspensions or other unplanned trouble on one of your lines. Planned work and service notices don't count |
| A gray `- -` | No live times right now: no internet, or the MTA's feed is down or out of date. The clock never shows an old countdown |
| No Subway screen at all | Nothing is running on your lines at your station (late at night, say), so it skips its turn |

A line that isn't stopping drops out by itself. At 81 St the B and C run in the daytime and the A
stops there only late at night, so with `B,C,A` you see B and C by day and the A overnight, with no
schedule to set.

Times are minutes, rounded down, like the MTA's own countdown clocks. They count down on the clock
between downloads, so they stay right between updates.

### Other layouts

Set **Layout** in the app's settings:

- **numbers** (default): all lines' next trains in time order, colored, no letters. At most four fit.
- **bullets**: two lines side by side, each with its round line bullet and the next train.
- **turns**: one line at a time, with its bullet and next two trains, switching every 5 seconds.

With a single line, every layout shows the bullet and the next two trains, e.g. `●B 4 · 11`.

## Settings

Open the clock's address in a browser (it scrolls across the display at start-up, and your
router lists it as `awtrixng-…`). Go to **Apps**, then the gear icon next to **Subway**.

| Setting | Default | What it does |
|---|---|---|
| Lines | `B,C,A` | Up to three lines at the station, separated by commas. Any of `1`–`7`, `A`–`Z` (as the MTA names them), `GS`, `FS`, `H` (shuttles), `SI`, `6X`, `7X`, `FX` |
| Station ID | `A21` | The station's ID from [STATIONS.md](STATIONS.md). `A21` is 81 St–Museum of Natural History |
| Direction | `S` | `N` or `S`. The station list says what each means at your station (at 81 St, S is downtown) |
| Layout | numbers | See above |
| Red dot for MTA alerts | on | Downloads the MTA's alerts every 5 minutes for the red dot |
| Show when live times are unavailable | on | Off: skip the screen instead of showing `- -` |
| Time on screen | 10 s | How long the Subway screen stays up in the rotation |

**Advanced**, for when something changes on the MTA's side:

| Setting | Default | What it does |
|---|---|---|
| Feed URL | empty | Empty: the clock picks the right MTA feed for each line. Only set it if the MTA moves its feeds |
| Refresh every | 30 s | How often each feed is downloaded |
| Old after | 120 s | Times from a feed older than this are never shown |
| Verify the MTA certificate | on | Leave on. Only switch it off if the log says the TLS check fails because the MTA changed its certificate authority |

In **Settings → Brightness**, **Off when dark** (default 1%) switches the display off after 30
seconds below that light level, and pauses all downloads until it's light again. Set it to 0 to
keep the display on in the dark.

## Buttons

- **Left / right:** previous / next screen.
- **Middle, double press:** display off and on.
- **Middle, held while plugging in:** Wi-Fi setup mode (see below).

## Wi-Fi

The clock needs a 2.4 GHz network with no login page.

- **First time, or it can't find its network:** after about 15 seconds it opens its own network,
  `awtrixng-…` (no password). Join it from your phone; a setup page opens (or go to
  `192.168.4.1`). Pick your network, type the password, save.
- **Switching networks while the old one still works:** unplug it, hold the **middle** button,
  plug it back in and keep holding about a second until it says `SETUP`. Then as above.
- **Don't use factory reset for Wi-Fi.** It isn't needed and it erases your settings. (The Subway
  app and its defaults come back by themselves, but your own changes are gone.)

## Updates

Updates for this project are uploaded in the web UI: **System → Maintenance → Firmware update**
([INSTALL.md](INSTALL.md)). **Don't use "Check for updates" there**: it installs the official
AWTRIX NG, which has no Subway support.

## Troubleshooting

The clock's web UI has a **log** (Console). The Subway app writes one line whenever its state
changes, for example:

```
B A21S live 4 11 | feed age 12s | last ok 31204B 1800ms || C A21S live 7 19 | ...
```

| Problem | Look for | Fix |
|---|---|---|
| Always `- -` | `last fail net …` | The clock has no internet. Check the Wi-Fi network has no login page |
| Always `- -` | `last fail http 4…` / `5…` | The MTA's server refused or failed. Usually passes; if not for hours, check the MTA's developer site for changed feed URLs |
| The screen never appears | `route not in this feed` | A typo in Lines, or a Feed URL that doesn't match the line. Clear Feed URL |
| The screen never appears | `stop not in this feed` | Wrong Station ID, or the station ID is missing its direction. Check STATIONS.md |
| The screen never appears | `no_arrivals` | Nothing is running there right now. Normal late at night or during service changes |
| Times look a minute off | — | Both the clock and the MTA round down, at slightly different moments |
| The display goes dark in a dim room | — | Lower **Off when dark**, or set it to 0 |
