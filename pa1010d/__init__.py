import time

import pynmea2
import smbus2

__version__ = "0.0.4"

PA1010D_ADDR = 0x10

PPS_DISABLE = 0
PPS_AFTER_FIRST_FIX = 1
PPS_3D_FIX_ONLY = 2
PPS_3D_2D_FIX_ONLY = 3
PPS_ALWAYS = 4


class PA1010D:
    __slots__ = (
        "timestamp",
        "latitude",
        "longitude",
        "altitude",
        "lat_dir",
        "lon_dir",
        "geo_sep",
        "num_sats",
        "gps_qual",
        "speed_over_ground",
        "mode_fix_type",
        "pdop",
        "hdop",
        "vdop",
        "_i2c_addr",
        "_i2c",
        "_debug",
    )

    def __init__(self, i2c_addr=PA1010D_ADDR, debug=False):
        self._i2c_addr = i2c_addr
        self._i2c = smbus2.SMBus(1)

        self._debug = debug

        self.timestamp = None
        self.latitude = None
        self.longitude = None
        self.altitude = None
        self.num_sats = None
        self.gps_qual = None

        self.lat_dir = None
        self.lon_dir = None
        self.geo_sep = None

        self.pdop = None
        self.hdop = None
        self.vdop = None

        self.speed_over_ground = None
        self.mode_fix_type = None

    @property
    def data(self):
        return dict((slot, getattr(self, slot)) for slot in self.__slots__)

    def _write_sentence(self, bytestring):
        """Write a sentence to the PA1010D device over i2c.

        We could- in theory- do this in one burst, but since smbus is limited to 32bytes,
        we would have to chunk the message and this is already one byte chunks anyway!

        """
        for char_index in bytestring:
            self._i2c.write_byte(self._i2c_addr, char_index)

    def send_command(self, command, add_checksum=True):
        """Send a command string to the PA1010D.

        If add_checksum is True (the default) a NMEA checksum will automatically be computed and added.

        """
        if isinstance(command, bytes):
            command = command.encode("ascii")

        # TODO replace with pynmea2 functionality
        if command[0] == b"$":
            command = command[1:]
        if command[-1] == b"*":
            command = command[:-1]

        buf = bytearray()
        buf += b"$"
        buf += command
        if add_checksum:
            checksum = 0
            # bytes() is a real thing in Python 3
            # so `for char in commaud` iterates through char ordinals
            for char in command:
                checksum ^= char
            buf += b"*"  # Delimits checksum value
            buf += "{checksum:02X}".format(checksum=checksum).encode("ascii")
        buf += b"\r\n"
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
            # Should be a full \r\n since the GPS emits spurious newlines
            if buf[-2:] == [ord("\r"), ord("\n")]:
                # Remove line ending and spurious newlines from the sentence
                return bytearray(buf).decode("ascii").strip().replace("\n", "")

        raise TimeoutError("Timeout waiting for readline")

    def update(self, wait_for="GGA", timeout=5):
        """Attempt to update from PA1010D.

        Returns true if a sentence has been successfully parsed.

        Returns false if an error has occurred.

        Will wait 5 seconds for a GGA message by default.

        :param wait_for: Message type to wait for.
        :param timeout: Wait timeout in seconds

        """
        timeout += time.time()

        while time.time() < timeout:
            try:
                sentence = self.read_sentence()
            except TimeoutError:
                continue

            try:
                result = pynmea2.parse(sentence)
            except pynmea2.nmea.ParseError:
                if self._debug:
                    print("Parse error: {sentence}".format(sentence=sentence))
                continue

            # Time, position and fix
            if isinstance(result, pynmea2.GGA):
                if result.gps_qual is None:
                    self.num_sats = 0
                    self.gps_qual = 0
                else:
                    self.timestamp = result.timestamp
                    self.latitude = result.latitude
                    self.longitude = result.longitude
                    self.lat_dir = result.lat_dir
                    self.lon_dir = result.lon_dir
                    self.altitude = result.altitude
                    self.geo_sep = result.geo_sep
                    self.num_sats = result.num_sats
                    self.gps_qual = result.gps_qual
                if wait_for == "GGA":
                    return True

            # Geographic Lat/Lon (Loran holdover)
            elif isinstance(result, pynmea2.GLL):
                pass

            # GPS DOP and active satellites
            elif isinstance(result, pynmea2.GSA):
                self.mode_fix_type = result.mode_fix_type
                self.pdop = result.pdop
                self.hdop = result.hdop
                self.vdop = result.vdop
                if wait_for == "GSA":
                    return True

            # Position, velocity and time
            elif isinstance(result, pynmea2.RMC):
                self.speed_over_ground = result.spd_over_grnd
                if wait_for == "RMC":
                    return True

            # Track made good and speed over ground
            elif isinstance(result, pynmea2.VTG):
                if wait_for == "VTG":
                    return True

            # SVs in view, PRN, elevation, azimuth and SNR
            elif isinstance(result, pynmea2.GSV):
                if wait_for == "GSV":
                    return True

            # ProprietarySentence handles boot up output such as "$PMTK011,MTKGPS*08"
            elif isinstance(result, pynmea2.ProprietarySentence):
                # TODO If we implement sending commands *to* the GPS,
                # they should not be permitted until after receiving this sequence
                # $PMTK011,MTKGPS*08 Successful bootup
                # $PMTK010,001*2E    Startup
                # $PMTK010,002*2D    Wake from standby, normal operation
                print(sentence)
                return True

            else:
                # If native MTK support exists, check for those message types
                # requires merge and release of: https://github.com/Knio/pynmea2/pull/111
                # TODO Drop this special case when #111 is merged & released
                try:
                    if isinstance(result, (
                        pynmea2.types.proprietary.mtk.MTK011,
                        pynmea2.types.proprietary.mtk.MTK010
                    )):
                        return True
                except AttributeError:
                    pass
                raise RuntimeError("Unsupported message type {type} ({sentence})".format(type=type(result), sentence=sentence))

        raise TimeoutError("Timeout waiting for {wait_for} message.".format(wait_for=wait_for))

    def set_pps(self, mode, pulse_width=100):
        if mode not in (0, 1, 2, 3, 4):
            raise ValueError("Invalid PPS mode (0 to 4)")

        if pulse_width > 900 or pulse_width < 1:
            raise ValueError("Invalid PPS pulse_width (1 to 900ms)")

        self.send_command(f"PMTK285,{mode},{pulse_width}")


if __name__ == "__main__":
    gps = PA1010D()

    while True:
        result = gps.update()
        if result:
            print(f"""
Time:      {gps.timestamp}
Longitude: {gps.longitude: .5f} {gps.lon_dir}
Latitude:  {gps.latitude: .5f} {gps.lat_dir}
Altitude:  {gps.altitude}
Geoid_Sep: {gps.geo_sep}
Geoid_Alt: {float(gps.altitude) + -float(gps.geo_sep)}
Used Sats: {gps.num_sats}
Quality:   {gps.gps_qual}""")
        time.sleep(1.0)
