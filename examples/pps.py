#!/usr/bin/env python3
import sys

from pa1010d import PA1010D


if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <on/off>")
    sys.exit()

gps = PA1010D()

pulse_width = 100

if len(sys.argv) > 2:
    pulse_width = int(sys.argv[2])

if sys.argv[1] == "on":
    gps.send_command(f"PMTK285,4,{pulse_width}")
else:
    gps.send_command(f"PMTK285,0,{pulse_width}")

result = gps.update()

print("OK" if result else "Uh oh!")
