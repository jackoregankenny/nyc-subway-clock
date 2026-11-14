#include <cstdio>
#include <fstream>
#include <iterator>
#include <string>
#include "core/transit/GtfsRtDecoder.h"
int main(int argc, char** argv) {
  std::ifstream in(argv[1], std::ios::binary);
  std::string f((std::istreambuf_iterator<char>(in)), std::istreambuf_iterator<char>());
  awtrix::transit::GtfsRtDecoder d; d.begin(argv[2], argv[3], 0, 0);
  for (size_t i = 0; i < f.size(); i += 1460) d.feed((const uint8_t*)f.data() + i, std::min<size_t>(1460, f.size() - i));
  d.finish();
  std::printf("%s", d.error() == awtrix::transit::DecodeError::None ? "" : "ERR ");
  for (size_t i = 0; i < d.count(); ++i) std::printf("%lld ", (long long)d.at(i));
  std::printf("\n");
}
