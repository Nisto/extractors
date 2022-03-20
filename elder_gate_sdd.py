import os
import sys
import struct

def get_u32_le(buf, off=0):
  return struct.unpack("<I", buf[off:off+4])[0]

def get_u16_le(buf, off=0):
  return struct.unpack("<H", buf[off:off+2])[0]

class SDD:
  def __init__(self, filename):
    with open(filename, "rb") as f:
      self.name = f.name
      self.buffer = f.read()
      self.size = len(self.buffer)
      self.offset = 0
      self.seq_num = 0
      self.num_kdt_extracted = 0
      self.num_vab_extracted = 0

def calc_num_tones_in_program(tone_table, program_index):
  num_tones = 0
  offset = program_index * 0x200
  for i in range(16):
    sample_num = get_u16_le(tone_table, offset+0x16)
    if sample_num != 0:
      num_tones += 1
    offset += 0x20
  return num_tones

def calc_avg_volume_of_instrument(instrument, num_tones):
  volume_sum = 0
  offset = 0
  for i in range(num_tones):
    volume_sum += instrument[offset+0x02]
    offset += 0x10
  return volume_sum // num_tones

def calc_avg_pan_of_instrument(instrument, num_tones):
  pan_sum = 0
  offset = 0
  for i in range(num_tones):
    pan_sum += instrument[offset+0x03]
    offset += 0x10
  return pan_sum // num_tones

def generate_program_table(tone_table, num_programs):
  program_table = bytearray()

  for program_index in range(128):
    vol, pan, num_tones, mode, prio = (0, 0, 0, 0, 0)

    if program_index < num_programs:
      num_tones = calc_num_tones_in_program(tone_table, program_index)
      instrument_ofs = program_index * 0x200
      instrument = tone_table[instrument_ofs:instrument_ofs+0x200]
      vol = calc_avg_volume_of_instrument(instrument, num_tones)
      pan = calc_avg_pan_of_instrument(instrument, num_tones)

    program_table += bytearray(
      [
        num_tones, vol, prio, mode, pan,
        0xFF, 0x00,0x00, 0xFF,0xFF,0xFF,0xFF, 0xFF,0xFF,0xFF,0xFF
      ]
    )

  return program_table

def parse_pbav(sdd):
  size = get_u32_le(sdd.buffer, sdd.offset+0x0C)
  payload_offset = sdd.offset + 0x00
  with open("%s.VAB" % (os.path.realpath(sdd.name)), "wb") as vab:
    if sdd.buffer[sdd.offset:sdd.offset+4] == b"pBAV":
      # write standard VAB data as-is
      vab.write(sdd.buffer[sdd.offset:sdd.offset+size])
    else:
      # manually write header magic (PBAV -> pBAV)
      vab.write(b"pBAV")
      # write the rest of the main header
      vab.write(sdd.buffer[sdd.offset+0x04:sdd.offset+0x20])
      # write program table
      num_programs = get_u16_le(sdd.buffer, sdd.offset+0x12)
      tone_table = sdd.buffer[sdd.offset+0x20:sdd.offset+0x20+num_programs*0x200]
      program_table = generate_program_table(tone_table, num_programs)
      vab.write(program_table)
      # write the rest of the VAB data
      vab.write(sdd.buffer[sdd.offset+0x20:sdd.offset+size])
  sdd.num_vab_extracted += 1
  sdd.offset = payload_offset
  return payload_offset + size

def parse_kdt1(sdd):
  size = get_u32_le(sdd.buffer, sdd.offset+0x04)
  payload_offset = sdd.offset + 0x00
  with open("%s_%d.KDT" % (os.path.realpath(sdd.name), sdd.seq_num), "wb") as kdt:
    kdt.write(sdd.buffer[sdd.offset:sdd.offset+size])
  sdd.num_kdt_extracted += 1
  sdd.offset = payload_offset
  return payload_offset + size

def parse_kdt2(sdd):
  size = get_u32_le(sdd.buffer, sdd.offset+0x04)
  sdd.seq_num = get_u32_le(sdd.buffer, sdd.offset+0x08)
  unk0C = get_u32_le(sdd.buffer, sdd.offset+0x0C)
  payload_offset = sdd.offset + 0x10
  sdd.offset = payload_offset
  parse_next(sdd)
  return payload_offset + size

def parse_tsdb(sdd):
  size = get_u32_le(sdd.buffer, sdd.offset+0x04)
  num_kdt_chunks = get_u32_le(sdd.buffer, sdd.offset+0x08)
  payload_offset = sdd.offset + 0x0C
  sdd.offset = payload_offset
  for kdt_num in range(num_kdt_chunks):
    parse_next(sdd)
  return payload_offset + size

def parse_kcet(sdd):
  size = get_u32_le(sdd.buffer, sdd.offset+0x04)
  payload_offset = sdd.offset + 0x08
  sdd.offset = payload_offset
  parse_next(sdd)
  return payload_offset + size

parsers = {
  b"KCET": parse_kcet,
  b"TSDB": parse_tsdb,
  b"KDT2": parse_kdt2,
  b"KDT1": parse_kdt1,
  b"PBAV": parse_pbav,
  b"pBAV": parse_pbav,
}

def parse_sdd(sdd):
  while parse_next(sdd):
    continue

def parse_next(sdd):
  while sdd.offset + 4 <= len(sdd.buffer):
    magic = sdd.buffer[sdd.offset:sdd.offset+4]
    if magic in parsers:
      end_offset = parsers[magic](sdd)
      sdd.offset = end_offset
      return True
    else:
      sdd.offset += 4
  return False

def main(argc=len(sys.argv), argv=sys.argv):
  if argc < 2:
    print("Usage: %s <SDD>" % argv[0])
    return 1

  sdd = SDD(argv[1])

  parse_sdd(sdd)

  print("Extraction summary for: %s" % sdd.name)
  print("  KDT: %d" % sdd.num_kdt_extracted)
  print("  VAB: %d" % sdd.num_vab_extracted)

  return 0

if __name__ == "__main__":
  main()
