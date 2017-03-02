# Silent Hill 3 sd.bin extractor / re-builder

import os
import sys
import struct

def read_u32_le(f):
    return struct.unpack("<I", f.read(4))[0]

def write_u32_le(f, x):
    f.write(struct.pack("<I", x))

def extract(fin, dst, sector, size):
    with open(dst, "wb") as fout:
        fin.seek(sector * 2048)
        fout.write(fin.read(size))

def insert(fout, src):
    size = os.path.getsize(src)
    outbuf = bytearray(size + (2048 - (size % 2048)) if size % 2048 else size)
    with open(src, "rb") as fin:
        outbuf[:size] = fin.read(size)
    fout.write(outbuf)

def get_file_arg(message, real=True):
    x = ''
    while not os.path.isfile(x):
        x = input(message).strip('"')
    return os.path.realpath(x)

def get_dir_arg(message, real=True):
    x = ''
    while not os.path.isdir(x):
        x = input(message).strip('"')
    return os.path.realpath(x)

def get_lit_arg(valid_list, message, lowercase=True):
    x = ''
    while x not in valid_list:
        x = input(message)
        if lowercase:
            x = x.lower()
    return x

mode = get_lit_arg(['b','e'], "Enter 'e' to extract, 'b' to build: ")

if mode == 'e':
    bin_path = get_file_arg("Enter path to sd.bin: ")
    if not os.access(bin_path, os.R_OK):
        input("Cannot open sd.bin")
        sys.exit(1)

    sd_stem = os.path.splitext(bin_path)[0]

    with open(bin_path, "rb") as bin:
        if bin.read(0x10) != b"TYOSD v-1.01\x03\x00\x00\x00":
            input("Unexpected ID in main header of sd.bin")
            sys.exit(1)

        tdsect = read_u32_le(bin)
        tdsize = read_u32_le(bin)
        hdsect = read_u32_le(bin)
        hdsize = read_u32_le(bin)
        bdsect = read_u32_le(bin)
        bdsize = read_u32_le(bin)

        extract(bin, "%s.TD" % sd_stem, tdsect, tdsize)
        print("Extracted: sd.TD")

        extract(bin, "%s.HD" % sd_stem, hdsect, hdsize)
        print("Extracted: sd.HD")

        extract(bin, "%s.BD" % sd_stem, bdsect, bdsize)
        print("Extracted: sd.BD")

elif mode == 'b':
    basedir = get_dir_arg("Enter path to directory containing sd.TD, sd.HD and sd.BD: ")

    td_path = os.path.join(basedir, "sd.TD")
    if not os.access(td_path, os.R_OK):
        input("Cannot open sd.TD")
        sys.exit(1)

    hd_path = os.path.join(basedir, "sd.HD")
    if not os.access(hd_path, os.R_OK):
        input("Cannot open sd.HD")
        sys.exit(1)

    bd_path = os.path.join(basedir, "sd.BD")
    if not os.access(bd_path, os.R_OK):
        input("Cannot open sd.BD")
        sys.exit(1)

    bin_path = os.path.join(basedir, "sd.bin")
    if not os.access(bin_path, os.W_OK):
        input("Cannot create/open sd.bin")
        sys.exit(1)

    with open(bin_path, "wb") as bin:
        bin.write(b"TYOSD v-1.01\x03\x00\x00\x00")

        bin.seek(2048)

        tdsect = bin.tell() // 2048
        tdsize = os.path.getsize(td_path)
        insert(bin, td_path)

        hdsect = bin.tell() // 2048
        hdsize = os.path.getsize(hd_path)
        insert(bin, hd_path)

        bdsect = bin.tell() // 2048
        bdsize = os.path.getsize(bd_path)
        insert(bin, bd_path)

        bin.seek(0x10)

        write_u32_le(bin, tdsect)
        write_u32_le(bin, tdsize)
        write_u32_le(bin, hdsect)
        write_u32_le(bin, hdsize)
        write_u32_le(bin, bdsect)
        write_u32_le(bin, bdsize)

input("All done.")
