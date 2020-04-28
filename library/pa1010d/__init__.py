__version__ = "0.0.1"

import time
import smbus


import pynmea2


PA1010D_ADDR = 0x10


class PA1010D():
    __slots__ = (
        "timestamp",
        "latitude",
        "longitude",
        "altitude",
        "num_sats",
        "gps_qual",
        "_i2c_addr",
        "_i2c"
    )

    def __init__(self, i2c_addr=PA1010D_ADDR):
        self._i2c_addr = i2c_addr
        self._i2c = smbus.SMBus(1)

        self.timestamp = None
        self.latitude = None
        self.longitude = None
        self.altitude = None
        self.num_sats = None
        self.gps_qual = None

    def _write_sentence(self, bytestring):
        """Write a sentence to the PA1010D device over i2c.

        We could- in theory- do this in one burst, but since smbus is limited to 32bytes,
        we would have to chunk the message and this is already one byte chunks anyway!

        """
        for char_index in bytestring:
            self._i2c.write_byte(self._i2c_addr, ord(char_index))

    def send_command(self, command, add_checksum=True):
        """Send a command string to the PA1010D.
        
        If add_checksum is True (the default) a NMEA checksum will automatically be computed and added.

        """
        # TODO replace with pynmea2 functionality
        if command.startswith("$"):
            command = command[1:]
        if command.endswith("*"):
            command = command[:-1]

        buf = bytearray()
        buf += b'$'
        buf += command
        if add_checksum:
            checksum = 0
            # bytes() is a real thing in Python 3
            # so `for char in commaud` iterates through char ordinals
            for char in command:
                checksum ^= char
            buf += b'*'  # Delimits checksum value
            buf += f"{checksum:02X}".encode("ascii")
        buf += b'\r\n'
        self._write_sentence(buf)

    def read_sentence(self, timeout=5):
        """Attempt to read an NMEA sentence from the PA1010D."""
        buf = []
        timeout += time.time()

        while time.time() < timeout:
            char = self._i2c.read_byte_data(self._i2c_addr, 0x00)

            if len(buf) == 0 and char != ord("$"):
                continue

            buf += [char]

            # Check for end of line
            if buf[-1] == ord("\n"):
                return bytearray(buf).decode("ascii")

        raise TimeoutError("Timeout waiting for readline")

    def update(self, wait_for="GGA", timeout=5):
        """Attempt to update from PA1010D.
        
        Returns true if a sentence has been successfully parsed.

        Returns false if an error has occured.

        Will wait 5 seconds for a GGA message by default.

        :param wait_for: Message type to wait for.
        :param timeout: Wait timeout in seconds

        """
        timeout += time.time()

        while time.time() < timeout:
            try:
                result = self.read_sentence()
            except TimeoutError:
                continue

            try:
                result = pynmea2.parse(result)
            except pynmea2.nmea.ParseError:
                continue

            if type(result) == pynmea2.GGA:
                if result.gps_qual is None:
                    self.num_sats = 0
                    self.gps_qual = 0
                else:
                    self.timestamp = result.timestamp
                    self.latitude = result.latitude
                    self.longitude = result.longitude
                    self.altitude = result.altitude
                    self.num_sats = result.num_sats
                    self.gps_qual = result.gps_qual
                if wait_for == "GGA":
                    return True

            elif type(result) == pynmea2.GSA:
                if wait_for == "GSA":
                    return True

            elif type(result) == pynmea2.RMC:
                if wait_for == "RMC":
                    return True

            elif type(result) == pynmea2.VTG:
                if wait_for == "VTG":
                    return True

            elif type(result) == pynmea2.GSV:
                if wait_for == "GSV":
                    return True

            else:
                raise RuntimeError(f"Unsupported message type {type(result)}")

        raise TimeoutError(f"Timeout waiting for {wait_for} message.")


if __name__ == "__main__":
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
