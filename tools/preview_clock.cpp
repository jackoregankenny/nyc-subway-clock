// B-train gift clock: renders upstream's own Time and Date apps with the gift's first-boot
// settings, so the preview shows the "ordinary clock" frames next to the Subway ones.
#include <cstdio>
#include <string>
#include "core/Settings.h"
#include "core/RuntimeState.h"
#include "core/apps/builtin/TimeApp.h"
#include "core/apps/builtin/DateApp.h"
#include "core/render/Canvas.h"
#include "media/AwtrixFontAdapter.h"
using namespace awtrix;
static void ppm(const Canvas& c, const std::string& path) {
  const int s = 12;
  std::FILE* f = std::fopen(path.c_str(), "wb");
  std::fprintf(f, "P6\n%d %d\n255\n", 34 * s, 10 * s);
  for (int py = 0; py < 10 * s; ++py)
    for (int px = 0; px < 34 * s; ++px) {
      const int x = px / s - 1, y = py / s - 1;
      uint32_t p = 0x0A0A0A;
      if (x >= 0 && y >= 0 && x < 32 && y < 8) {
        const int dx = px % s - s / 2, dy = py % s - s / 2;
        p = dx * dx + dy * dy <= (s * s) / 6 ? (c.getPixel(x, y) ? c.getPixel(x, y) : 0x161616) : 0x0A0A0A;
      }
      const unsigned char rgb[3] = {(unsigned char)(p >> 16), (unsigned char)(p >> 8), (unsigned char)p};
      std::fwrite(rgb, 1, 3, f);
    }
  std::fclose(f);
}
int main(int argc, char** argv) {
  const std::string dir = argc > 1 ? argv[1] : ".";
  Settings s;  // upstream defaults, then the gift's first-boot changes
  s.time24h = false; s.timeLeadingZero = false; s.dateOrder = kDateOrderMDY; s.dateSeparator = kDateSepSlash;
  RuntimeState rt;
  RenderCtx ctx;
  ctx.settings = &s; ctx.runtime = &rt; ctx.font = &awtrixFont(); ctx.fonts = &awtrixFontCatalog();
  ctx.hour = 18; ctx.minute = 23; ctx.second = 0; ctx.weekday = 2; ctx.mday = 10; ctx.month = 11; ctx.year = 2026;
  ctx.epochMs = 1794352980000LL; ctx.nowMs = 500000; ctx.shownSinceMs = 0;
  Canvas c(32, 8);
  TimeApp t; c.clear(); t.render(c, ctx); ppm(c, dir + "/clock_time.ppm");
  DateApp d; c.clear(); d.render(c, ctx); ppm(c, dir + "/clock_date.ppm");
  std::puts("ok");
}
