#!/usr/bin/env python3
import sys

from pa1010d import PA1010D


if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <on/off>")
    sys.exit()

gps = PA1010D()

if sys.argv[1] == "on":
    gps.send_command("PMTK255,1")
else:
    gps.send_command("PMTK255,0")

result = gps.update()

print("OK" if result else "Uh oh!")
