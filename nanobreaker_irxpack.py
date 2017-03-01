# Nanobreaker irxpack.bin extractor

import os
import sys
import struct

namemap = {
    "Sound_Device_Library" : "libsd",
    "sdr_driver"           : "sdrdrv",
    "cdvd_st_driver"       : "cdvdstm",
    "libsmf2_driver"       : "libsmf2",
    "sdstr3_driver"        : "sdstr3",
}

OFF_COUNT = 0x00
OFF_SZTBL = 0x04

def get_u32_le(buf, off):
    return struct.unpack("<I", buf[off:off+4])[0]

def get_c_str(buf, off):
    end = off

    while buf[end] != 0:
        end += 1

    return buf[off:end].decode("ASCII")

def main(argc=len(sys.argv), argv=sys.argv):
    if argc != 2:
        print("Usage: %s <irxpack.bin>" % argv[0])
        return 1

    inpath = os.path.realpath(argv[1])
    os.chdir( os.path.dirname(inpath) )

    with open(inpath, "rb") as bin:
        buf = bin.read()

    irxcount = get_u32_le(buf, OFF_COUNT)
    offset = OFF_SZTBL + irxcount * 4

    for i in range(irxcount):
        offset = ((offset - 1) & ~0xF) + 0x10
        size = get_u32_le(buf, OFF_SZTBL+i*4)
        name = get_c_str(buf, offset+0x8E)

        if name in namemap:
            name = namemap[name]

        with open("%s.irx" % name, "wb") as irx:
            irx.write(buf[offset:offset+size])

        offset += size

if __name__ == "__main__":
    main()