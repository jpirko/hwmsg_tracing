#! /usr/bin/python

"""
Copyright 2016 Mellanox Technologies. All rights reserved.
Licensed under the GNU General Public License, version 2 as
published by the Free Software Foundation; see COPYING for details.
"""

__author__ = """
jiri@mellanox.com (Jiri Pirko)
"""

import perf
import sys
import os
import struct

class tracepoint(perf.evsel):
    def __init__(self, sys, name):
        config = perf.tracepoint(sys, name)
        perf.evsel.__init__(self, type = perf.TYPE_TRACEPOINT, config = config,
                            freq = 0, sample_period = 1, wakeup_events = 1,
                            sample_type = perf.SAMPLE_PERIOD | perf.SAMPLE_TID | perf.SAMPLE_CPU | perf.SAMPLE_RAW)

pcap_header = struct.pack("IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 0xffff, 0)

def pcap_packet_header(secs, usecs, pktlen):
    return struct.pack("IIII", secs, usecs, pktlen, pktlen)

def tlv_data(data_type, data):
    tlv_header = struct.pack("HH", data_type, len(data))
    return tlv_header + data

TLV_TYPE_BUS_NAME = 0
TLV_TYPE_DEV_NAME = 1
TLV_TYPE_OWNER_NAME = 2
TLV_TYPE_INCOMING = 3
TLV_TYPE_TYPE = 4
TLV_TYPE_BUF = 5

def main():
    tp = tracepoint("devlink", "devlink_hwmsg")
    cpus = perf.cpu_map()
    threads = perf.thread_map(-1)

    evlist = perf.evlist(cpus, threads)
    evlist.add(tp)
    evlist.open()
    evlist.mmap()
    
    sys.stdout = os.fdopen(1, "wb")
    sys.stdout.write(pcap_header)
    sys.stdout.flush()

    while True:
        try:
            evlist.poll(timeout = -1)
        except KeyboardInterrupt:
            break
        for cpu in cpus:
            event = evlist.read_on_cpu(cpu)
            if not event:
                continue

            if not isinstance(event, perf.sample_event):
                continue

            data = bytearray()
            data += tlv_data(TLV_TYPE_BUS_NAME, event.bus_name)
            data += tlv_data(TLV_TYPE_DEV_NAME, event.dev_name)
            data += tlv_data(TLV_TYPE_OWNER_NAME, event.owner_name)
            data += tlv_data(TLV_TYPE_INCOMING, struct.pack("B", event.incoming))
            data += tlv_data(TLV_TYPE_TYPE, struct.pack("H", event.type))
            data += tlv_data(TLV_TYPE_BUF, event.buf)
    
            sys.stdout.write(pcap_packet_header(0, 0, len(data)))
            sys.stdout.write(data)
            sys.stdout.flush()

if __name__ == '__main__':
    main()
