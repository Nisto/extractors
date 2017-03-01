import os
import sys
import struct

def get_u32_le(buf, off=0):
    return struct.unpack("<I", buf[off:off+4])[0]

def main(argc=len(sys.argv), argv=sys.argv):
    if argc != 2:
        input("Usage: %s <trg.bin>" % argv[0])
        return 1

    bin_path = os.path.realpath(argv[1])

    if not os.access(bin_path, os.R_OK):
        input("Cannot open %s" % bin_path)
        return 1

    bin_stem = os.path.splitext(bin_path)[0]

    with open(bin_path, "rb") as bin:

        bin.seek(0x0C)

        num_files = get_u32_le( bin.read(4) )
        num_groups = num_files // 3

        table = bin.read(num_files * 8)
        tableoff = 0

        for groupnum in range(num_groups):

            for i in range(3):

                sect = get_u32_le(table, tableoff+0x00)
                size = get_u32_le(table, tableoff+0x04)

                bin.seek(sect * 2048)

                id = bin.read(4)

                if id == b"SdDt":
                    ext = "TD"
                elif id == b"IECS":
                    ext = "HD"
                else:
                    ext = "BD"

                outpath = "%s_%04d.%s" % (bin_stem, groupnum, ext)

                with open(outpath, "wb") as fo:

                    fo.write( id + bin.read(size - 4) )

                print("Extracted: %s" % outpath)

                tableoff += 8

    input("All done.")

if __name__=="__main__":
    main()