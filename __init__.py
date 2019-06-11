"""Decode EDID information
"""

import struct
import subprocess
from collections import namedtuple
import csv
import os
import os.path
import string

DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILENAME = os.path.join(DIR, 'pnp_ids.csv')
PNP_IDS = {}

with open(CSV_FILENAME, 'r') as file:
    reader = csv.reader(file)
    for line in reader:
        PNP_IDS[line[0]] = line[1]

class EDID:
    """Extended Display Identification Data
    """
    @staticmethod
    def manufacturer_from_raw(raw):
        """Get the manufacture from raw data
        """
        id = EDID.id_from_raw(raw)
        return EDID.manufacturer_from_id(id)

    @staticmethod
    def manufacturer_from_id(id):
        """Get the manufacture from the manufacture id
        """
        return PNP_IDS.get(id, "Unknown")

    @staticmethod
    def id_from_raw(raw):
        """Get the manufacture id from raw data
        """
        tmp = [(raw >> 10) & 31, (raw >> 5) & 31, raw & 31]
        return "".join(string.ascii_uppercase[n-1] for n in tmp)

    @staticmethod
    def hex2bytes(hex):
        """Convert string of hexidecimal to bytes
        """
        numbers = []
        for i in range(0, len(hex), 2):
            pair = hex[i:i+2]
            numbers.append(int(pair, 16))
        return bytes(numbers)

    _STRUCT_FORMAT = (
        ">"     # big-endian
        "8s"    # constant header (8 bytes)
        "H"     # manufacturer id (2 bytes)
        "H"     # product id (2 bytes)
        "I"     # serial number (4 bytes)
        "B"     # manufactoring week (1 byte)
        "B"     # manufactoring year (1 byte)
        "B"     # edid version (1 byte)
        "B"     # edid revision (1 byte)
        "B"     # video input type (1 byte)
        "B"     # horizontal size in cm (1 byte)
        "B"     # vertical size in cm (1 byte)
        "B"     # display gamma (1 byte)
        "B"     # supported features (1 byte)
        "10s"   # color characteristics (10 bytes)
        "H"     # supported timings (2 bytes)
        "B"     # reserved timing (1 byte)
        "16s"   # EDID supported timings (16 bytes)
        "18s"   # detailed timing block 1 (18 bytes)
        "18s"   # detailed timing block 2 (18 bytes)
        "18s"   # detailed timing block 3 (18 bytes)
        "18s"   # detailed timing block 4 (18 bytes)
        "B"     # extension flag (1 byte)
        "B"     # checksum (1 byte)
    )

    _TIMINGS = {
        0: {"width":1280, "height": 1024, "refresh_rate": 75.},
        1: {"width":1024, "height":  768, "refresh_rate": 75.},
        2: {"width":1024, "height":  768, "refresh_rate": 72.},
        3: {"width":1024, "height":  768, "refresh_rate": 60.},
        4: {"width":1024, "height":  768, "refresh_rate": 87.},
        5: {"width": 832, "height":  624, "refresh_rate": 75.},
        6: {"width": 800, "height":  600, "refresh_rate": 75.},
        7: {"width": 800, "height":  600, "refresh_rate": 70.},
        8: {"width": 800, "height":  600, "refresh_rate": 60.},
        9: {"width": 800, "height":  600, "refresh_rate": 56.},
        10:{"width": 640, "height":  480, "refresh_rate": 75.},
        11:{"width": 640, "height":  480, "refresh_rate": 72.},
        12:{"width": 640, "height":  480, "refresh_rate": 67.},
        13:{"width": 640, "height":  480, "refresh_rate": 60.},
        14:{"width": 720, "height":  400, "refresh_rate": 88.},
        15:{"width": 720, "height":  400, "refresh_rate": 70.}
    }

    _ASPECT_RATIOS = {
        0b00: (16, 10), # was 1:1 prior to EDID 1.3
        0b01: (4, 3),
        0b10: (5, 4),
        0b11: (16, 9),
    }

    _DIGITAL_BIT_DEPTHS = {
        # _XXX____
        0b00000000: 0,
        0b00010000: 6,
        0b00100000: 8,
        0b00110000: 10,
        0b01000000: 12,
        0b01010000: 14,
        0b01100000: 16,
        0b01110000: 0
    }

    _DIGITAL_VIDEO_INTERFACES = {
        # ____XXXX
        0b00000000: "undefined",
        0b00000001: "HDMIa",
        0b00000010: "HDMIb",
        0b00000100: "MDDI",
        0b00000101: "DisplayPort"
    }

    _DIGITAL_DISPLAY_TYPES = {
        # ___XX___
        0b00000000: "RGB 4:4:4",
        0b00001000: "RGB 4:4:4 + YCrCb 4:4:4",
        0b00010000: "RGB 4:4:4 + YCrCb 4:2:2",
        0b00011000: "RGB 4:4:4 + YCrCb 4:4:4 + YCrCb 4:2:2"
    }

    _ANALOG_DISPLAY_TYPES = {
        # ___XX___
        0b00000000: "Monochrome or grayscale",
        0b00001000: "RGB Color",
        0b00010000: "Non-RGB Color",
        0b00011000: "undefined"
    }

    _ANALOG_SYNC_LEVELS = {
        # _XX_____
        0b00000000: "+0.700/−0.300 V",
        0b00100000: "+0.714/−0.286 V",
        0b01000000: "+1.000/−0.400 V",
        0b01100000: "+0.700/-0.000 V"
    }

    _RawEdid = namedtuple(
        "RawEdid", (
            "header", "manu_id", "prod_id", "serial_no", "manu_week", "manu_year", "edid_version",
            "edid_revision", "input_type", "width", "height", "gamma", "features", "color",
            "timings_supported", "timings_reserved", "timings_edid", "timing_1", "timing_2",
            "timing_3", "timing_4", "extension", "checksum"
        )
    )

    def __init__(self, bytes=None):
        if bytes is not None:
            self._parse_edid(bytes)

    def _parse_edid(self, bytes):
        if struct.calcsize(self._STRUCT_FORMAT) != 128:
            raise ValueError("Wrong edid size.")

        if sum(map(int, bytes)) % 256 != 0:
            raise ValueError("Checksum mismatch.")

        tuple = struct.unpack(self._STRUCT_FORMAT, bytes)
        raw_edid = self._RawEdid(*tuple)

        if raw_edid.header != b'\x00\xff\xff\xff\xff\xff\xff\x00':
            raise ValueError("Invalid header.")

        self.raw = bytes
        self.manufacturer = EDID.manufacturer_from_raw(raw_edid.manu_id)
        self.manufacturer_id = EDID.id_from_raw(raw_edid.manu_id)
        self.product_id = raw_edid.prod_id
        self.year = raw_edid.manu_year + 1990
        self.edid_version = "%d.%d" % (raw_edid.edid_version, raw_edid.edid_revision)
        if (raw_edid.input_type & 0b10000000):
            self.type = "digital"
            self.bit_depth = self._DIGITAL_BIT_DEPTHS[raw_edid.input_type & 0b01110000]
            self.video_interface = self._DIGITAL_VIDEO_INTERFACES[raw_edid.input_type & 0b00001111]
            self.display_type = self._DIGITAL_DISPLAY_TYPES[raw_edid.features & 0b00011000]
        else:
            self.type = "analog"
            self.sync_levels = self._ANALOG_SYNC_LEVELS[raw_edid.input_type & 0b01100000]
            self.black_to_black_setup_expected = bool(raw_edid.input_type & 0b00010000)
            self.separate_sync = bool(raw_edid.input_type & 0b00001000)
            self.composite_sync_supported = bool(raw_edid.input_type & 0b00000100)
            self.sync_on_green_supported = bool(raw_edid.input_type & 0b00000010)
            self.vsync_must_be_serrated = bool(raw_edid.input_type & 0b00000001)
            self.display_type = self._ANALOG_DISPLAY_TYPES[raw_edid.features & 0b00011000]
        self.width = float(raw_edid.width)
        self.height = float(raw_edid.height)
        self.gamma = (raw_edid.gamma + 100) / 100
        self.dpms_standby = bool(raw_edid.features & 0b10000000)
        self.dpms_suspend = bool(raw_edid.features & 0b01000000)
        self.dpms_activeoff = bool(raw_edid.features & 0b00100000)

        self.resolutions = []
        for i in range(16):
            bit = raw_edid.timings_supported & i
            if bit:
                self.resolutions.append(self._TIMINGS[16-i])

        for i in range(8):
            bytes = raw_edid.timings_edid[2*i:2*i+2]
            if bytes == b'\x01\x01':
                continue
            byte1, byte2 = bytes
            x_res = 8*(int(byte1)+31)
            aspect_ratio = self._ASPECT_RATIOS[(byte2>>6) & 0b11]
            y_res = int(x_res * aspect_ratio[1]/aspect_ratio[0])
            rate = (int(byte2) & 0b00111111) + 60.0
            self.resolutions.append({
                "width": x_res,
                "height": y_res,
                "refresh_rate": rate
            })

        self.name = None
        self.serial = None

        for bytes in (raw_edid.timing_1, raw_edid.timing_2, raw_edid.timing_3, raw_edid.timing_4):
            if bytes[0:2] == b'\x00\x00': # "other" descriptor
                type = bytes[3]
                if type in (0xFF, 0xFE, 0xFC):
                    buffer = bytes[5:]
                    buffer = buffer.partition(b"\x0a")[0]
                    text = buffer.decode("cp437")
                    if type == 0xFF:
                        self.serial = text
                    elif type == 0xFC:
                        self.name = text

        if not self.serial:
            self.serial = raw_edid.serial_no

    def get_edid(self):
        """What does this do?
        """
        ret = {}
        for name in dir(self):
            if not name.startswith("_"): # ignore "private" members
                value = getattr(self, name)
                if not callable(value): # ignore callable items
                    ret[name] = value
        return ret

    def __repr__(self):
        """Representation of the object
        """
        clsname = self.__class__.__name__
        attributes = []
        for name in dir(self):
            if not name.startswith("_"): # ignore "private" members
                value = getattr(self, name)
                if not callable(value): # ignore callable items
                    attributes.append("\t%s=%r" % (name, value))
        return "%s(\n%s\n)" % (clsname, ", \n".join(attributes))

if __name__ == "__main__":
    pass
