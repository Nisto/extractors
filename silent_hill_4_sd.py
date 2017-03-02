# Silent Hill 4 sd.bin extractor

import os
import sys
import struct

def read_u32_le(f):
    return struct.unpack("<I", f.read(4))[0]

def extract(fin, dst, sector, size):
    with open(dst, "wb") as fout:
        fin.seek(sector * 2048)
        fout.write(fin.read(size))

def main(argc=len(sys.argv), argv=sys.argv):
    if argc != 2:
        input("Usage: %s <sd.bin>" % argv[0])
        return 1

    bin_path = os.path.realpath(argv[1])

    if not os.access(bin_path, os.R_OK):
        input("Cannot open sd.bin")
        sys.exit(1)

    sd_stem = os.path.splitext(bin_path)[0]

    with open(bin_path, "rb") as bin:
        bin.seek(0x10)

        hdsect = read_u32_le(bin)
        hdsize = read_u32_le(bin)
        bdsect = read_u32_le(bin)
        bdsize = read_u32_le(bin)
        tdsect = read_u32_le(bin)
        tdsize = read_u32_le(bin)

        extract(bin, "%s.HD" % sd_stem, hdsect, hdsize)
        print("Extracted: sd.HD")

        extract(bin, "%s.BD" % sd_stem, bdsect, bdsize)
        print("Extracted: sd.BD")

        extract(bin, "%s.TD" % sd_stem, tdsect, tdsize)
        print("Extracted: sd.TD")

    input("All done.")

if __name__=="__main__":
    main()