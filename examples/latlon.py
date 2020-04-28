#!/usr/bin/env python3
import time

from pa1010d import PA1010D


gps = PA1010D()

while True:
    result = gps.update()
    if result:
        print(f"""
T: {gps.timestamp}
N: {gps.longitude}
E: {gps.latitude}
Alt: {gps.altitude}
Sats: {gps.num_sats}
Qual: {gps.gps_qual}
""")
    time.sleep(1.0)
