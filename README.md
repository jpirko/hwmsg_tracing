Hardware messages monitoring
--------------

It is possible to monitor all messages driver is sending down to hardware and
messages coming from hardware back to the driver. This is implemented
as a kernel tracepoint. The tracepoint name is `devlink:devlink_hwmsg`.

There is a simple python script called `devlink-hwmsg.py` that hooks up
on this tracepoint and converts events into PCAP output.
You can get it like this:

```
sw:~$ git clone https://github.com/jpirko/hwmsg_tracing.git
```

Then just use it from your desktop connecting it to Wireshark for easier
view like this:

```
desktop:~$ ssh sw sudo ~/hwmsg_tracing/devlink-hwmsg.py | sudo wireshark -k -i -
```

In case the `devlink-hwmsg.py` complains about missing `tracepoint` object,
you need to update `python-perf` package. For example like this:

```
sw:~$ sudo dnf install https://kojipkgs.fedoraproject.org//packages/kernel/4.8.0/0.rc7.git4.1.fc25/x86_64/python-perf-4.8.0-0.rc7.git4.1.fc25.x86_64.rpm -y
```

Also make sure that `devlink` module is loaded before you run the script.
