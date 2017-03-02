# World Soccer: Winning Eleven 5 sound / VFS extractor
# Only supports SLPM-62053

import os
import sys
import struct

EXE_PATH = "SLPM_620.53"

FS_DIR_OFF = 0x17ADD0
FS_EXT_OFF = 0x17AE10
FS_TOC_OFF = 0x17CA50
FS_TOC_CNT = 719
TOC_ENT_SZ = 48

SD_TOC_OFF = 0x227B60
SD_TOC_CNT = 8918
SD_ENT_SZ  = 8
SD_ST_SECT = 70566

# for the headerless Sony ADPCM data;
# these are in the main executable
# (function 0x205220)

# sample_rates = {
#     0x2A8: 22050,
#     0x2A9: 22050,
#     0x2AA: 22050,
# 
#     # ??? seems like the function
#     # just returns on 0x22C5, but
#     # this is probably correct
#     0x22C5: 44100,
# 
#     0x22C6: 44100,
#     0x22C7: 44100,
#     0x22C8: 44100,
#     0x22C9: 44100,
#     0x22CA: 44100,
#     0x22CB: 44100,
#     0x22CC: 44100,
#     0x22CD: 44100,
#     0x22CE: 44100,
#     0x22CF: 44100,
# }

class ISOFS_IMAGE:
    #
    # DISCLAIMER:
    # Only supports reading the ISO filesystem / track (first track probably)
    # on NON-mixed-mode disk images.
    # -- Nisto
    #
    def __init__(self, path):
        self.path = path

        self.f = open(self.path, "rb")

        self.toc = {}

        self.f.seek(16 * 2352)
        pvd_raw = self.f.read(2352)

        self.f.seek(16 * 2048)
        pvd_user = self.f.read(2048)

        if self.is_raw_sector(pvd_raw) and self.is_pvd(pvd_raw[0x10:0x810]):
            #
            # Standard CD-ROM
            #
            pvd = pvd_raw[0x10:0x810]
            self.is_raw = 1
            self.is_xa = 0
            self.sector_size = 2352
            self.user_start = 0x10
            if pvd_raw[0x0F] == 1:
                self.user_size = 2048
                self.user_end = 0x810
            elif pvd_raw[0x0F] == 2:
                self.user_size = 2336
                self.user_end = 0x930
        elif self.is_raw_sector(pvd_raw) and self.is_pvd(pvd_raw[0x18:0x818]):
            #
            # CD-ROM XA
            #
            pvd = pvd_raw[0x18:0x818]
            self.is_raw = 1
            self.is_xa = 1
            self.sector_size = 2352
            self.user_start = 0x18
            # size of User Data is 2048 if Form 1, or 2324 if Form 2, and the
            # Form may vary across a track, so a global size / end offset of
            # the User Data doesn't really make sense for CD-ROM XA
            self.user_size = None
            self.user_end = None
        elif self.is_pvd(pvd_user):
            #
            # CD / DVD / ... (User Data only)
            #
            pvd = pvd_user
            self.is_raw = 0
            self.is_xa = 0
            self.sector_size = 2048
            self.user_start = 0x00
            self.user_size = 2048
            self.user_end = 2048
        else:
            print("Unrecognized disk image format")
            sys.exit(1)

        root_dr = self.drparse(pvd[0x9C:0xBE])

        self.seek_user(root_dr["lba"])

        root_dir = self.read_user(root_dr["size"])

        self.dirparse(root_dir)

    def is_raw_sector(self, buf):
        sync = buf[0x00:0x0C]
        if sync != b"\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00":
            return 0

        mm = buf[0x0C]
        if (mm>>4) & 0x0F > 9 or mm & 0x0F > 9:
            return 0

        ss = buf[0x0D]
        if (ss>>4) & 0x0F > 5 or ss & 0x0F > 9:
            return 0

        ff = buf[0x0E]
        if (ff>>4) & 0x0F > 7 or ff & 0x0F > 9 \
        or ((ff>>4) & 0x0F == 7 and ff & 0x0F > 4):
            return 0

        mode = buf[0x0F]
        if mode > 2:
            return 0

        return 1

    def is_pvd(self, buf):
        if len(buf) != 2048:
            return 0

        if buf[0x00:0x06] != b"\x01CD001":
            return 0

        return 1

    def set_xa(self, subcode):
        if subcode & 0b100000 == 0:
            self.user_size = 2048
            self.user_end = 0x818
        else:
            self.user_size = 2324
            self.user_end = 0x92C

    def read_user(self, size):
        usrbuf = b""
        if self.is_raw:
            offset_in_sector = self.f.tell() % self.sector_size
            if offset_in_sector != 0:
                if offset_in_sector < self.user_start:
                    self.f.seek(-offset_in_sector, os.SEEK_CUR)
                else:
                    if self.is_xa:
                        self.f.seek(-offset_in_sector, os.SEEK_CUR)
                        tmpbuf = self.f.read(offset_in_sector)
                        self.set_xa(tmpbuf[0x12])

                    if offset_in_sector < self.user_end:
                        user_remain = self.user_end - offset_in_sector

                        if size < user_remain:
                            return self.f.read(size)

                        usrbuf += self.f.read(user_remain)

                        size -= user_remain

                        self.f.seek(self.sector_size - (offset_in_sector + user_remain), os.SEEK_CUR)
                    else:
                        self.f.seek(self.sector_size - offset_in_sector, os.SEEK_CUR)

            if self.is_xa:
                while size > 0:
                    sectbuf = self.f.read(self.sector_size)
                    self.set_xa(sectbuf[0x12])
                    if size >= self.user_size:
                        usrbuf += sectbuf[self.user_start:self.user_end]
                        size -= self.user_size
                    else:
                        usrbuf += sectbuf[self.user_start:self.user_start+size]
                        self.f.seek(-self.sector_size + self.user_start + size, os.SEEK_CUR)
                        size = 0
            else:
                while size > 0:
                    if size >= self.user_size:
                        sectbuf = self.f.read(self.sector_size)
                        size -= self.user_size
                    else:
                        sectbuf = self.f.read(self.user_start + size)
                        size = 0
                    usrbuf += sectbuf[self.user_start:self.user_end]
        else:
            while size > 0:
                if size >= self.user_size:
                    usrbuf += self.f.read(self.user_size)
                    size -= self.user_size
                else:
                    usrbuf += self.f.read(size)
                    size = 0

        return usrbuf

    def seek_user(self, sectors, bytes=0):
        if self.is_xa:
            self.f.seek(sectors * self.sector_size)
            while bytes > 0:
                header = self.f.read(self.user_start)
                self.set_xa(header[0x12])
                if bytes >= self.user_size:
                    self.f.seek(self.sector_size - self.user_start, os.SEEK_CUR)
                    bytes -= self.user_size
                else:
                    self.f.seek(bytes, os.SEEK_CUR)
                    bytes = 0
        else:
            if self.is_raw and bytes > 0:
                sectors += bytes // self.user_size
                bytes = self.user_start + (bytes % self.user_size)
            self.f.seek(sectors * self.sector_size + bytes)

    def extract_user(self, lba, bytes, outpath):
        self.seek_user(lba)
        todo_size = bytes
        with open(outpath, "wb") as outfile:
            while todo_size > 0:
                read_size = min(2048, todo_size)
                buf = self.read_user(read_size)
                outfile.write(buf)
                todo_size -= read_size

    def drparse(self, drbuf):
        dr_size = get_u8(drbuf, 0x00)
        lba = get_u32_le(drbuf, 0x02)
        size = get_u32_le(drbuf, 0x0A)
        flags = get_u8(drbuf, 0x19)
        name_len = get_u8(drbuf, 0x20)
        name = drbuf[0x21 : 0x21 + name_len].decode("ASCII")

        if name == "\x00":
            name = '.'
        elif name == "\x01":
            name = '..'
        else:
            name = name.rsplit(';', 1)[0]

        return {"lba":lba, "size":size, "flags":flags, "name":name}

    def dirparse(self, dirbuf, dirname=''):
        i = 0
        subdirs = []
        while i < len(dirbuf) and dirbuf[i] > 0:
            dr_len = dirbuf[i]

            record = self.drparse(dirbuf[i:i+dr_len])

            if record["flags"] & 0b10 != 0 and record["name"] != '.' and record["name"] != '..':
                subdirs.append(record)
            elif record["flags"] & 0b10 == 0:
                self.toc[os.path.join('', dirname, record["name"]).replace(os.sep, '/')] = record
                self.toc[os.path.join('/', dirname, record["name"]).replace(os.sep, '/')] = record
                self.toc[os.path.join('./', dirname, record["name"]).replace(os.sep, '/')] = record

            i += dr_len

        for record in subdirs:
            self.seek_user(record["lba"])
            dirbuf = self.read_user(record["size"])
            self.dirparse(dirbuf, os.path.join(dirname, record["name"]))

def get_u8(buf, off):
    return struct.unpack("B", buf[off:off+1])[0]

def get_u16_le(buf, off):
    return struct.unpack("<H", buf[off:off+2])[0]

def get_u32_le(buf, off):
    return struct.unpack("<I", buf[off:off+4])[0]

def get_c_string(buf, off):
    end = off

    while buf[end] != 0:
        end += 1

    return buf[off:end].decode("ASCII")

def vfs_ex(disk, elfbuf):

    outdir = "%s - vfs" % os.path.splitext(disk.path)[0]

    e_phoff  = get_u32_le(elfbuf, 0x1C)
    p_offset = get_u32_le(elfbuf, e_phoff+0x04)
    p_vaddr  = get_u32_le(elfbuf, e_phoff+0x08)

    offset = FS_TOC_OFF

    for i in range(FS_TOC_CNT):

        fsEntry = elfbuf[offset:offset+TOC_ENT_SZ]

        dirPathIdx   = get_u32_le(fsEntry, 0x00)
        dirPathAddr  = get_u32_le(elfbuf, FS_DIR_OFF + dirPathIdx*4)
        dirPathOff   = p_offset + dirPathAddr - p_vaddr
        dirPath      = get_c_string(elfbuf, dirPathOff)

        fileNameAddr = get_u32_le(fsEntry, 0x04)
        fileNameOff  = p_offset + fileNameAddr - p_vaddr
        fileName     = get_c_string(elfbuf, fileNameOff)

        extIdx       = get_u32_le(fsEntry, 0x08)
        extAddr      = get_u32_le(elfbuf, FS_EXT_OFF + extIdx*4)
        extOff       = p_offset + extAddr - p_vaddr
        ext          = get_c_string(elfbuf, extOff)

        cdStartSect  = get_u32_le(fsEntry, 0x10)
        cdEndSect    = get_u32_le(fsEntry, 0x18)
        cdSectCnt    = get_u32_le(fsEntry, 0x20)
        byteSize     = get_u32_le(fsEntry, 0x28)

        outsubdir = os.path.join(outdir, dirPath)

        if not os.path.isdir(outsubdir):
            os.makedirs(outsubdir)

        vfs_path = dirPath + fileName + ext

        outpath = os.path.join(outdir, vfs_path)

        disk.extract_user(cdStartSect, byteSize, outpath)

        print("extracted: %s" % vfs_path)

        offset += TOC_ENT_SZ

def sound_ex(disk, elfbuf):

    # the respective VFS file is /data/sound/we5.cat

    outdir = "%s - sound" % os.path.splitext(disk.path)[0]

    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    offset = SD_TOC_OFF

    for i in range(SD_TOC_CNT):
        sector = get_u32_le(elfbuf, offset+0x00)
        size = get_u32_le(elfbuf, offset+0x04)

        disk.seek_user(SD_ST_SECT + sector)

        id = disk.read_user(4)
        if id == b"SdDt":
            ext = "TD"
        elif id == b"IECS":
            ext = "HD"
        else:
            ext = "BD"

        outname = "SD_%04X.%s" % (i, ext)

        outpath = os.path.join(outdir, outname)

        disk.extract_user(SD_ST_SECT + sector, size, outpath)
    
        print("extracted: %s" % outname)

        offset += SD_ENT_SZ

def main(argc=len(sys.argv), argv=sys.argv):
    if argc != 2:
        print("Usage: %s <disk>" % argv[0])
        return 1

    in_path = os.path.realpath(argv[1])

    disk = ISOFS_IMAGE(in_path)

    disk.seek_user(disk.toc[EXE_PATH]["lba"])

    elfbuf = disk.read_user(disk.toc[EXE_PATH]["size"])

    vfs_ex(disk, elfbuf)

    sound_ex(disk, elfbuf)

if __name__ == "__main__":
    main()