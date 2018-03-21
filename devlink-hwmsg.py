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
                            sample_type = perf.SAMPLE_PERIOD | perf.SAMPLE_TID |
                            perf.SAMPLE_CPU | perf.SAMPLE_RAW |
                            perf.SAMPLE_TIME)

LINKTYPE_USER15 = 162
pcap_header = struct.pack("IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 0xffff,
                          LINKTYPE_USER15)

def pcap_packet_header(secs, usecs, pktlen):
    return struct.pack("IIII", secs, usecs, pktlen, pktlen)

def tlv_data(data_type, data):
    tlv_header = struct.pack("HH", data_type, len(data))
    return tlv_header + data

TLV_TYPE_BUS_NAME = 0
TLV_TYPE_DEV_NAME = 1
TLV_TYPE_DRIVER_NAME = 2
TLV_TYPE_INCOMING = 3
TLV_TYPE_TYPE = 4
TLV_TYPE_BUF = 5

def pcap_header_out():
    sys.stdout.write(pcap_header)
    sys.stdout.flush()

def normalize_ba(ba):
    if (isinstance(ba, str)):
        ba = bytearray(ba + "\0")
    return ba

def event_out(event):
    data = bytearray()
    data += tlv_data(TLV_TYPE_BUS_NAME, normalize_ba(event.bus_name))
    data += tlv_data(TLV_TYPE_DEV_NAME, normalize_ba(event.dev_name))
    data += tlv_data(TLV_TYPE_DRIVER_NAME, normalize_ba(event.driver_name))
    data += tlv_data(TLV_TYPE_INCOMING, struct.pack("B", event.incoming))
    data += tlv_data(TLV_TYPE_TYPE, struct.pack("H", event.type))
    data += tlv_data(TLV_TYPE_BUF, normalize_ba(event.buf))

    secs = event.sample_time / 1000000000
    usecs = (event.sample_time % 1000000000) / 1000
    sys.stdout.write(pcap_packet_header(secs, usecs, len(data)))
    sys.stdout.write(data)
    sys.stdout.flush()

def main():
    sys.stdout = os.fdopen(1, "wb")

    tp = tracepoint("devlink", "devlink_hwmsg")
    cpus = perf.cpu_map()
    threads = perf.thread_map(-1)

    evlist = perf.evlist(cpus, threads)
    evlist.add(tp)
    evlist.open()
    evlist.mmap()

    pcap_header_out()

    while True:
        try:
            evlist.poll(timeout = -1)
        except KeyboardInterrupt:
            break
        for cpu in cpus:
            while True:
                event = evlist.read_on_cpu(cpu)
                if not event:
                    break
                if not isinstance(event, perf.sample_event):
                    continue
                event_out(event)

if __name__ == '__main__':
    main()
