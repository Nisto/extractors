# Lost Kingdoms (GC)
# Splits .pps files into standard MusyX formats (pool, proj, sdir, song)

import os
import sys
import struct

def get_u32_be(buf, off):
  return struct.unpack(">I", buf[off:off+4])[0]

def dump_file(path, buf):
  with open(path, "wb") as f:
    f.write(buf)

def extract(in_path):
  with open(in_path, "rb") as pps:
    ppsbuf = pps.read()

  if get_u32_be(ppsbuf, 0x04) == 3:
    pool_off = get_u32_be(ppsbuf, 0x08)
    proj_off = get_u32_be(ppsbuf, 0x0C)
    sdir_off = get_u32_be(ppsbuf, 0x10)

    stem = os.path.splitext(in_path)[0]

    dump_file("%s.pool" % stem, ppsbuf[pool_off:proj_off])
    dump_file("%s.proj" % stem, ppsbuf[proj_off:sdir_off])
    dump_file("%s.sdir" % stem, ppsbuf[sdir_off:len(ppsbuf)])
  else:
    input("Number at 0x04 != 0x03 in file %s" % in_path)

def main(argc=len(sys.argv), argv=sys.argv):
  if argc < 2:
    print("Usage: %s <pps_file|pps_dir> [...]" % argv[0])
    return 1

  for arg in argv[1:]:
    full_path = os.path.realpath(arg)
    if os.path.isfile(arg):
      extract(full_path)
    elif os.path.isdir(arg):
      for filename in os.listdir(arg):
        if os.path.splitext(filename)[1].lower() == ".pps":
          extract( os.path.join(full_path, filename) )
    else:
      input("Not a path to a file or directory: %s" % arg)

  return 0

if __name__ == "__main__":
  main()