# Skies of Arcadia (GC)
# Splits .info files into standard MusyX formats (pool, proj, sdir, song)

import os
import sys
import struct

def get_u16_be(buf, off=0):
    return struct.unpack(">H", buf[off:off+2])[0]

def main(argc=len(sys.argv), argv=sys.argv):
    if argc != 2:
        print("Usage: %s <infofile>" % argv[0])
        return 1

    infopath = os.path.realpath(argv[1])

    if not os.path.isfile(infopath):
        print("File path is invalid!")
        return 1

    stem = os.path.splitext(infopath)[0]

    with open(infopath, "rb") as info:
        infobuf = info.read()

    offset = 0

    offsets = []

    table_size = 4 * get_u16_be(infobuf, 0x00)

    while offset < table_size and get_u16_be(infobuf, offset) != 0:
        ckoff = 4 * get_u16_be(infobuf, offset)
        offsets.append(ckoff)
        offset += 2

    for idx in range( len(offsets) ):
        if idx <= 0:
            outpath = "%s.pool" % stem
        elif idx == 1:
            outpath = "%s.proj" % stem
        elif idx == 2:
            outpath = "%s.sdir" % stem
        else:
            if len(offsets) > 4:
                outpath = "%s_%02d.song" % (stem, idx-3)
            else:
                outpath = "%s.song" % stem

        ckoff = offsets[idx]

        if idx < len(offsets) - 1:
            cksize = offsets[idx+1] - ckoff
        else:
            cksize = len(infobuf) - ckoff

        with open(outpath, "wb") as outfile:
            outfile.write(infobuf[ckoff:ckoff+cksize])

    return 0

if __name__ == "__main__":
    main()