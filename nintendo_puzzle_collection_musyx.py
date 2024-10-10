import os
import sys
import shutil

USAGE = """Usage: nintendo_puzzle_collection_musyx.py <extracted_iso> <output_dir>

<extracted_iso> must be the path to a directory containing an exact replica of
the filesystem on the original game dise. Specifically, the following files are
required to be present from the game disc:

title/agb_title.samp
title/grand_staff.samp
title/Yoshi_title.samp
dr_test.samp
Dr_MARIO.plf
Dr_MARIO.rel
menu.plf
menu_relsamp.bin
PANEPON.plf
panepon.rel
panepon.samp
ycookie.bin

<output_dir> is the destination directory into which organized MusyX data will
be extracted.

This script only officially supports the version of the game with serial number
DL-DOL-GPZJ-JPN
"""

"""

  metadata format:

  output_dirname: {
    input_path: [
      (offset, size, output_name)
    ]
  }

  an offset and size of -1 indicates a 1:1 file copy of the input file

"""

meta = {
  "menu": {
    "/menu.plf": [
      # .samp file nowhere to be found ?
      (0x15B570, 0x194, "main_title.pool"),
      (0x15B704, 0x12C, "main_title.proj"),
      (0x15B830, 0x244, "main_title.sdir"),
      (0x15BD24, 0x2A8, "main_title.song"),
    ],

    "/menu_relsamp.bin": [
      (0x11DD20, 0x1C4, "gcpzls_se.pool"),
      (0x11DEE4, 0xB4, "gcpzls_se.proj"),
      (0x11DF98, 0x28C, "gcpzls_se.sdir"),

      (0x11E224, 0x21C0, "gcpzls.pool"),
      (0x1203E4, 0x268, "gcpzls.proj"),
      (0x12064C, 0xFC4, "gcpzls.sdir"),
      (0x121610, 0x1B2C, "gcpzls_00.song"),
      (0x12313C, 0x47A0, "gcpzls_01.song"),
      (0x1278DC, 0x1E58, "gcpzls_02.song"),

      (0x129734, 0x11B0, "grand_title.pool"),
      (0x12A8E4, 0x1A8, "grand_title.proj"),
      (0x12AA8C, 0xB8C, "grand_title.sdir"),
      (0x12B618, 0x3AF8, "grand_title_00.song"),
      (0x12F110, 0x339C, "grand_title_01.song"),

      (0x1324AC, 0x25E0, "grand_staff.pool"),
      (0x134A8C, 0x1D4, "grand_staff.proj"),
      (0x134C60, 0x1A74, "grand_staff.sdir"),
      (0x1366D4, 0x9938, "grand_staff.song"),
      
      (0x14000C, 0xA4, "agb_title.pool"),
      (0x1400B0, 0x110, "agb_title.proj"),
      (0x1401C0, 0xDC, "agb_title.sdir"),
      (0x14029C, 0x200, "agb_title_00.song"),
      (0x14049C, 0x19C, "agb_title_01.song"),
      
      (0x140638, 0x11AC, "Yoshi_title.pool"),
      (0x1417E4, 0x134, "Yoshi_title.proj"),
      (0x141918, 0x94C, "Yoshi_title.sdir"),
      (0x142264, 0x2124, "Yoshi_title.song"),

      (0x147BC0, 0x10CB38, "gcpzls.samp"),
      (0x254700, 0x19EC0, "gcpzls_se.samp"),
      (0x26E5C0, 0xC6348, "grand_title.samp"),
    ],

    "/title/grand_staff.samp": [
      (-1, -1, "grand_staff.samp"),
    ],

    "/title/agb_title.samp": [
      (-1, -1, "agb_title.samp"),
    ],

    "/title/Yoshi_title.samp": [
      (-1, -1, "Yoshi_title.samp"),
    ],
  },

  "panel_de_pon_debug": {
    "/panepon.samp": [
      (-1, -1, "panepon.samp"),
    ],

    "/PANEPON.plf": [
      (0xC4B70, 0x17380, "panepon.pool"),
      (0xDBEF0, 0x2CBC, "panepon.proj"),
      (0xDEBB0, 0x6F64, "panepon.sdir"),

      # Numeric prefixes in the filenames corresponds to the song's index in the
      # "songTbl" array in PANEPON.plf (which likely also corresponds to the
      # MIDI setup number).

      (0xE5B20, 0x2638, "08_cloud_01.song"),
      (0xE8160, 0x139C, "09_cloud_02.song"),
      (0xE9500, 0x35A0, "22_dragon_01.song"),
      (0xECAA0, 0x1A5C, "23_dragon_02.song"),
      (0xEE500, 0xC98, "34_ending.song"),
      (0xEF1A0, 0x3F18, "35_ending_easymode.song"),
      (0xF30C0, 0x28D0, "45_ending_frog.song"),
      (0xF5990, 0x534C, "53_ending_staff_credits.song"),
      (0xFACE0, 0x3AC8, "50_ending_whale_eyes.song"),
      (0xFE7B0, 0xC34, "54_ending_whale_gets_back_eyes.song"),
      (0xFF3F0, 0xDB18, "51_ending_which_photo.song"),
      (0x10CF10, 0x417C, "14_fire_01.song"),
      (0x111090, 0x2E60, "15_fire_02.song"),
      (0x113EF0, 0x1D90, "00_flower_01.song"),
      (0x115C80, 0xB44, "01_flower_02.song"),
      (0x1167D0, 0x1820, "28_goddess_01.song"),
      (0x117FF0, 0x8A8, "29_goddess_02.song"),
      (0x1188A0, 0xD90, "42_goddess_appear.song"),
      (0x119630, 0x424C, "12_green_01.song"),
      (0x11D880, 0x680, "13_green_02.song"),
      (0x11DF00, 0x33A8, "16_ice_01.song"),
      (0x1212B0, 0x96C, "17_ice_02.song"),
      (0x121C20, 0x1FE0, "38_intro_beginning.song"),
      (0x123C00, 0x5254, "49_intro_storm.song"),
      (0x128E60, 0x2874, "02_jewel_01.song"),
      (0x12B6E0, 0x93C, "03_jewel_02.song"),
      (0x12C020, 0x1994, "24_joker_01.song"),
      (0x12D9C0, 0x1A60, "25_joker_02.song"),
      (0x12F420, 0x15E8, "43_joker_apper.song"),
      (0x130A10, 0x158C, "41_keyload_part1.song"),
      (0x131FA0, 0x328, "39_keyroad_part2.song"),
      (0x1322D0, 0x1694, "52_keyroad_part3.song"),
      (0x133970, 0x167C, "20_lion_01.song"),
      (0x134FF0, 0xB4C, "21_lion_02.song"),
      (0x135B40, 0x1288, "10_moon_01.song"),
      (0x136DD0, 0x980, "11_moon_02.song"),
      (0x137750, 0x1C74, "46_obaba_01.song"),
      (0x1393D0, 0x1038, "47_obaba_02.song"),
      (0x13A410, 0x22C8, "32_opening.song"),
      (0x13C6E0, 0x1E60, "55_opening_skip.song"),
      (0x13E540, 0x1BAC, "18_prince_01.song"),
      (0x1400F0, 0x12BC, "19_prince_02.song"),
      (0x1413B0, 0x2180, "40_puzzle_edit.song"),
      (0x143530, 0x3CD0, "57_reserved1.song"),
      (0x147200, 0x3324, "58_reserved2.song"),
      (0x14A530, 0x2668, "56_reslut.song"),
      (0x14CBA0, 0x2C2C, "26_sanatos_01.song"),
      (0x14F7D0, 0xA7C, "27_sanatos_02.song"),
      (0x150250, 0x1C5C, "06_sea_01.song"),
      (0x151EB0, 0x12F8, "07_sea_02.song"),
      (0x1531B0, 0x2C14, "33_select.song"),
      (0x155DD0, 0x404C, "48_tutorial.song"),
      (0x159E20, 0x1E64, "04_water_01.song"),
      (0x15BC90, 0x1CB8, "05_water_02.song"),
      (0x15D950, 0x2F94, "30_whale_01.song"),
      (0x1608F0, 0x18BC, "31_whale_02.song"),
      (0x1621B0, 0x54C, "44_which_appear.song"),
      (0x162700, 0x5CC, "36_you_lose.song"),
      (0x162CD0, 0x1498, "37_you_win.song"),
    ],
  },

  "panel_de_pon_release": {
    "/panepon.samp": [
      (-1, -1, "panepon_00.samp"),
    ],

    "/panepon.rel": [
      (0x110750, 0x17390, "panepon_00.pool"),
      (0x127AE0, 0x2CBC, "panepon_00.proj"),
      (0x12A7A0, 0x6F64, "panepon_00.sdir"),

      # Numeric prefixes in the filenames corresponds to the song's index in the
      # "songTbl" array in PANEPON.plf (which likely also corresponds to the
      # MIDI setup number).

      (0x131710, 0x2638, "08_cloud_01.song"),
      (0x133D50, 0x139C, "09_cloud_02.song"),
      (0x1350F0, 0x35A0, "22_dragon_01.song"),
      (0x138690, 0x1A5C, "23_dragon_02.song"),
      (0x13A0F0, 0xE48, "34_ending.song"),
      (0x13AF40, 0x3F18, "35_ending_easymode.song"),
      (0x13EE60, 0x28D0, "45_ending_frog.song"),
      (0x141730, 0x534C, "53_ending_staff_credits.song"),
      (0x146A80, 0x3AC8, "50_ending_whale_eyes.song"),
      (0x14A550, 0xC34, "54_ending_whale_gets_back_eyes.song"),
      (0x14B190, 0xDB18, "51_ending_which_photo.song"),
      (0x158CB0, 0x417C, "14_fire_01.song"),
      (0x15CE30, 0x3154, "15_fire_02.song"),
      (0x15FF90, 0x1D90, "00_flower_01.song"),
      (0x161D20, 0xB44, "01_flower_02.song"),
      (0x162870, 0x1820, "28_goddess_01.song"),
      (0x164090, 0x8A8, "29_goddess_02.song"),
      (0x164940, 0xD90, "42_goddess_appear.song"),
      (0x1656D0, 0x3584, "12_green_01.song"),
      (0x168C60, 0x680, "13_green_02.song"),
      (0x1692E0, 0x33A8, "16_ice_01.song"),
      (0x16C690, 0x96C, "17_ice_02.song"),
      (0x16D000, 0x1FE0, "38_intro_beginning.song"),
      (0x16EFE0, 0x5264, "49_intro_storm.song"),
      (0x174250, 0x2874, "02_jewel_01.song"),
      (0x176AD0, 0x93C, "03_jewel_02.song"),
      (0x177410, 0x1994, "24_joker_01.song"),
      (0x178DB0, 0x1A60, "25_joker_02.song"),
      (0x17A810, 0x15E8, "43_joker_apper.song"),
      (0x17BE00, 0x158C, "41_keyload_part1.song"),
      (0x17D390, 0x328, "39_keyroad_part2.song"),
      (0x17D6C0, 0x1694, "52_keyroad_part3.song"),
      (0x17ED60, 0x167C, "20_lion_01.song"),
      (0x1803E0, 0xB4C, "21_lion_02.song"),
      (0x180F30, 0x1288, "10_moon_01.song"),
      (0x1821C0, 0x980, "11_moon_02.song"),
      (0x182B40, 0x1C74, "46_obaba_01.song"),
      (0x1847C0, 0x1038, "47_obaba_02.song"),
      (0x185800, 0x22A8, "32_opening.song"),
      (0x187AB0, 0x1E64, "55_opening_skip.song"),
      (0x189920, 0x1BAC, "18_prince_01.song"),
      (0x18B4D0, 0x12BC, "19_prince_02.song"),
      (0x18C790, 0x2180, "40_puzzle_edit.song"),
      (0x18E910, 0x3CD0, "57_reserved1.song"),
      (0x1925E0, 0x3324, "58_reserved2.song"),
      (0x195910, 0x2668, "56_reslut.song"),
      (0x197F80, 0x2C2C, "26_sanatos_01.song"),
      (0x19ABB0, 0xA7C, "27_sanatos_02.song"),
      (0x19B630, 0x1C5C, "06_sea_01.song"),
      (0x19D290, 0x12F8, "07_sea_02.song"),
      (0x19E590, 0x2C14, "33_select.song"),
      (0x1A11B0, 0x404C, "48_tutorial.song"),
      (0x1A5200, 0x1E64, "04_water_01.song"),
      (0x1A7070, 0x1CB8, "05_water_02.song"),
      (0x1A8D30, 0x2F94, "30_whale_01.song"),
      (0x1ABCD0, 0x1880, "31_whale_02.song"),
      (0x1AD550, 0x54C, "44_which_appear.song"),
      (0x1ADAA0, 0x5CC, "36_you_lose.song"),
      (0x1AE070, 0x1498, "37_you_win.song"),

      (0x1AF510, 0x1F0, "panepon_01.pool"),
      (0x1AF700, 0x78, "panepon_01.proj"),
      (0x1AF780, 0x124, "panepon_01.sdir"),
      (0x1AF8B0, 0xA5E8, "panepon_01.samp"),
    ],
  },

  "dr_mario_debug": {
    "/dr_test.samp": [
      (-1, -1, "dr_test.samp"),
    ],

    "/Dr_MARIO.plf": [
      (0x1375F0, 0xAE74, "dr_test.pool"),
      (0x142464, 0xED0, "dr_test.proj"),
      (0x143334, 0x3604, "dr_test.sdir"),

      # Numeric prefixes in the filenames corresponds to the song's index in the
      # "songTbl" array in Dr_MARIO.plf (which likely also corresponds to the
      # MIDI setup number).

      (0x17FED8, 0x5D58, "02_chil.song"),
      (0x185C30, 0x5D58, "03_chilf.song"),
      (0x18B988, 0xEF8, "14_end_a.song"),
      (0x18C880, 0x38A8, "15_end_b.song"),
      (0x190128, 0x208, "16_end_bs.song"),
      (0x190330, 0xB64, "17_end_c.song"),
      (0x190E94, 0x1FC, "18_end_cs.song"),
      (0x191090, 0x1648, "22_ending.song"),
      (0x1926D8, 0x3DF8, "00_fever.song"),
      (0x1964D0, 0x4130, "01_feverf.song"),
      (0x19A600, 0x19AC, "04_game_c.song"),
      (0x19BFAC, 0x1980, "05_game_cf.song"),
      (0x19D92C, 0x4B40, "06_game_d.song"),
      (0x1A246C, 0x4B40, "07_game_df.song"),
      (0x1A6FAC, 0x3448, "08_game_e.song"),
      (0x1AA3F4, 0x3448, "09_game_ef.song"),
      (0x1AD83C, 0x12BC, "10_game_opening.song"),
      (0x1AEAF8, 0x1164, "12_menu.song"),
      (0x1AFC5C, 0x16A4, "13_staff.song"),
      (0x1B1300, 0xBEC, "19_story_a.song"),
      (0x1B1EEC, 0xEF4, "20_story_b.song"),
      (0x1B2DE0, 0x810, "21_story_c.song"),
      (0x1B35F0, 0x47A0, "11_tile.song"),
      (0x1B7D90, 0x1684, "23_coffee.song"),
    ],
  },

  "dr_mario_release": {
    "/dr_test.samp": [
      (-1, -1, "dr_mario.samp"),
    ],

    "/Dr_MARIO.rel": [
      (0x1647D0, 0xAE74, "dr_mario.pool"),
      (0x16F644, 0xED0, "dr_mario.proj"),
      (0x170514, 0x3604, "dr_mario.sdir"),

      # Numeric prefixes in the filenames corresponds to the song's index in the
      # "songTbl" array in Dr_MARIO.plf (which likely also corresponds to the
      # MIDI setup number).

      (0x1AD0B8, 0x5D58, "02_chil.song"),
      (0x1B2E10, 0x5D58, "03_chilf.song"),
      (0x1B8B68, 0xEF8, "14_end_a.song"),
      (0x1B9A60, 0x38A8, "15_end_b.song"),
      (0x1BD308, 0x208, "16_end_bs.song"),
      (0x1BD510, 0xB64, "17_end_c.song"),
      (0x1BE074, 0x1FC, "18_end_cs.song"),
      (0x1BE270, 0x1648, "22_ending.song"),
      (0x1BF8B8, 0x3DF8, "00_fever.song"),
      (0x1C36B0, 0x4130, "01_feverf.song"),
      (0x1C77E0, 0x19AC, "04_game_c.song"),
      (0x1C918C, 0x1980, "05_game_cf.song"),
      (0x1CAB0C, 0x4B40, "06_game_d.song"),
      (0x1CF64C, 0x4B40, "07_game_df.song"),
      (0x1D418C, 0x3448, "08_game_e.song"),
      (0x1D75D4, 0x3448, "09_game_ef.song"),
      (0x1DAA1C, 0x12BC, "10_game_opening.song"),
      (0x1DBCD8, 0x1164, "12_menu.song"),
      (0x1DCE3C, 0x16A4, "13_staff.song"),
      (0x1DE4E0, 0xBEC, "19_story_a.song"),
      (0x1DF0CC, 0xEF4, "20_story_b.song"),
      (0x1DFFC0, 0x810, "21_story_c.song"),
      (0x1E07D0, 0x47A0, "11_tile.song"),
      (0x1E4F70, 0x1684, "23_coffee.song"),
    ],
  },

  "yoshi_no_cookie": {
    "/ycookie.bin": [
      (0x0, 0x200, "grp00.proj"),
      (0x200, 0x23E4, "grp00.pool"),
      (0x2600, 0x13FC, "grp00.sdir"),
      
      (0x3A00, 0x2D4, "grp01.proj"),
      (0x3CE0, 0xF38, "grp01.pool"),
      (0x4C20, 0x1204, "grp01.sdir"),
      
      (0x5E40, 0x994, "grp02.proj"),
      (0x67E0, 0x44A4, "grp02.pool"),
      (0xACA0, 0x217C, "grp02.sdir"),

      (0xCE20, 0x2248, "sng00.song"),
      (0xF080, 0x33A4, "sng01.song"),
      (0x12440, 0x25D0, "sng02.song"),
      (0x14A20, 0x2C10, "sng03.song"),
      (0x17640, 0x23F0, "sng04.song"),
      (0x19A40, 0x430, "sng05.song"),
      (0x19E80, 0x930, "sng06.song"),
      (0x1A7C0, 0x4C0, "sng07.song"),
      (0x1AC80, 0xFFC, "sng08.song"),
      (0x1BC80, 0x218C, "sng09.song"),
      (0x1DE20, 0x1DEC, "sng10.song"),
      (0x1FC20, 0x2668, "sng11.song"),
      (0x222A0, 0x2078, "sng12.song"),
      (0x24320, 0xA4C, "sng13.song"),
      (0x24D80, 0x6EC, "sng14.song"),
      (0x25480, 0xA84, "sng15.song"),
      (0x25F20, 0xCE8, "sng16.song"),
      (0x26C20, 0x2B54, "sng17.song"),
      (0x29780, 0x18A8, "sng18.song"),
      (0x2B040, 0x3464, "sng19.song"),
      (0x2E4C0, 0x3CBC, "sng20.song"),
      (0x32180, 0x369C, "sng21.song"),
      (0x35820, 0x3F94, "sng22.song"),
      (0x397C0, 0x2E8C, "sng23.song"),
      (0x3C660, 0x39B8, "sng24.song"),
      (0x40020, 0x1EF0, "sng25.song"),
      
      (0x41F20, 0x235C18, "grp00.samp"),
      (0x277B40, 0x1A9DD0, "grp01.samp"),
      (0x421920, 0x448978, "grp02.samp"),
    ],
  },
}

def verify_game_dir(input_dirpath):
  for output_dirname in meta:
    for input_relpath in meta[output_dirname]:
      abspath = os.path.join(input_dirpath, input_relpath.lstrip("\\/"))
      if not os.path.isfile(abspath):
        return False
  return True

def main(argc=len(sys.argv), argv=sys.argv):
  if argc != 3:
    print(USAGE)
    return 1

  root_input_dir = os.path.realpath(argv[1])
  root_output_dir = os.path.realpath(argv[2])

  if not verify_game_dir(root_input_dir):
    print(USAGE)
    return 1

  try:
    root_output_dir = os.path.join(root_output_dir, "musyx_data")
    if not os.path.isdir(root_output_dir):
      os.makedirs(root_output_dir)
  except:
    sys.exit("Fatal error creating output directories!")

  print("Extracting:")
  
  for output_dirname in meta:
    output_dirpath = os.path.join(root_output_dir, output_dirname)
    if not os.path.isdir(output_dirpath):
      os.makedirs(output_dirpath)
    for input_relpath in meta[output_dirname]:
      input_abspath = os.path.join(root_input_dir, input_relpath.lstrip("\\/"))
      for offset, size, output_filename in meta[output_dirname][input_relpath]:
        output_path = os.path.join(output_dirpath, output_filename)
        print("%s ... " % output_path, end="")
        if offset == -1 and size == -1:
          shutil.copyfile(input_abspath, output_path)
        else:
          with open(input_abspath, "rb") as fi:
            fi.seek(offset)
            with open(output_path, "wb") as fo:
              fo.write(fi.read(size))
        print("OK")

  return 0

if __name__ == "__main__":
  main()
