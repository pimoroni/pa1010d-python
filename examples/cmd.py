#!/usr/bin/env python3
import sys
import time

from pa1010d import PA1010D

"""
Run raw commands against the PA1010D GPS and return the responses.

Eg:
    PMTK605 = Query Firmware Release Info
    PMTK430 = Query Datum
    PMTK414 = Query NMEA Output Frequency
    PMTK400 = Query Update Rate
    PMTK225,<1 or 0> = Enable/Disable PPS
"""


def timeout(err=None, timeout=5.0):
    if err is None:
        err = "Timed out!"
    t_start = time.time()
    while time.time() - t_start < timeout:
        yield
    raise TimeoutError(err)


responses = {}

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <command>")
    sys.exit()

command = sys.argv[1]
response = responses.get(command, f"$PMTK{int(command[4:]) + 100}")

gps = PA1010D()

gps.update()

gps.send_command(sys.argv[1])

if response:
    print(f"Waiting for {response}...")
    for t in timeout("Timed out waiting for command response."):
        message = gps.read_sentence()
        if message.startswith(response):
            print(message)
            break
