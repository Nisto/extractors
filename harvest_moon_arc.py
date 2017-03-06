# Harvest Moon (GC) sound arc extractor

import os
import sys
import struct

if sys.version_info[0] > 2:
    xrange = range

def read_u32_be(f):
    try:
        buf = f.read(4)
    except EnvironmentError:
        sys.exit("ERROR: Read error at 0x%08X" % f.tell())
    return struct.unpack(">I", buf)[0]

def main(argc=len(sys.argv), argv=sys.argv):
    if argc < 2:
        print("Usage: %s <file.arc> [<file.arc> ...]" % argv[0])
        return 1

    for i in xrange(1, argc):
        if os.path.isfile(argv[i]) is not True:
            print("ERROR: Invalid file path: %s" % argv[i])
            continue

        path_in = os.path.realpath(argv[i])
        dir_in = os.path.dirname(path_in)
        basename = os.path.splitext(os.path.basename(path_in))[0]

        with open(path_in, "rb") as arc:
            arc.seek(0x30)

            pool_offset = read_u32_be(arc)
            pool_size = read_u32_be(arc)
            arc.seek(4, os.SEEK_CUR)

            proj_offset = read_u32_be(arc)
            proj_size = read_u32_be(arc)
            arc.seek(4, os.SEEK_CUR)

            sdir_offset = read_u32_be(arc)
            sdir_size = read_u32_be(arc)
            arc.seek(4, os.SEEK_CUR)

            song_offset = read_u32_be(arc)
            song_size = read_u32_be(arc)
            arc.seek(4, os.SEEK_CUR)

            arc.seek(pool_offset)
            with open(os.path.join(dir_in, basename+".pool"), "wb") as pool:
                pool.write(arc.read(pool_size))

            arc.seek(proj_offset)
            with open(os.path.join(dir_in, basename+".proj"), "wb") as proj:
                proj.write(arc.read(proj_size))

            arc.seek(sdir_offset)
            with open(os.path.join(dir_in, basename+".sdir"), "wb") as sdir:
                sdir.write(arc.read(sdir_size))

            arc.seek(song_offset)
            with open(os.path.join(dir_in, basename+".song"), "wb") as song:
                song.write(arc.read(song_size))

    print("No more files to process.")

    return 0

if __name__=="__main__":
    main()
