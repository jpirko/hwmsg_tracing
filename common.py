"""
Copyright 2016, 2018 Mellanox Technologies. All rights reserved.
Licensed under the GNU General Public License, version 2 as
published by the Free Software Foundation; see COPYING for details.
"""

import struct
import sys

def pcap_header_out(f = sys.stdout):
    LINKTYPE_USER15 = 162
    pcap_header = struct.pack("IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 0xffff,
                              LINKTYPE_USER15)
    f.write(pcap_header)
    f.flush()

def normalize_ba(ba):
    if (isinstance(ba, str)):
        ba = bytearray(ba + "\0")
    return ba

class Tag:
    def __init__(self, tag, encoder):
        self._tag = tag
        self._encoder = encoder

    def tag(self):
        return self._tag

    def encode(self, v):
        return self._encoder(v)

tlv_bus_name =    Tag(0, normalize_ba)
tlv_dev_name =    Tag(1, normalize_ba)
tlv_driver_name = Tag(2, normalize_ba)
tlv_incoming =    Tag(3, lambda v: struct.pack("?", v))
tlv_type =        Tag(4, lambda v: struct.pack("H", v))
tlv_buf =         Tag(5, lambda v: v)
