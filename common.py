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
