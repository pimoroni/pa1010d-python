# Pimoroni PA1010D GPS Breakout

[![Build Status](https://img.shields.io/github/actions/workflow/status/pimoroni/pa1010d-python/test.yml?branch=master)](https://github.com/pimoroni/pa1010d-python/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/pimoroni/pa1010d-python/badge.svg?branch=master)](https://coveralls.io/github/pimoroni/pa1010d-python?branch=master)
[![PyPi Package](https://img.shields.io/pypi/v/pa1010d.svg)](https://pypi.python.org/pypi/pa1010d)
[![Python Versions](https://img.shields.io/pypi/pyversions/pa1010d.svg)](https://pypi.python.org/pypi/pa1010d)

# Pre-requisites

You must enable:

* i2c: `sudo raspi-config nonint do_i2c 0`

You can optionally run `sudo raspi-config` or the graphical Raspberry Pi Configuration UI to enable interfaces.

# Installing

Stable library and dependencies from GitHub:

* `git clone https://github.com/pimoroni/pa1010d-python`
* `cd pa1010d-python`
* `sudo ./install.sh`

Latest/development library and dependencies from GitHub:

* `git clone https://github.com/pimoroni/pa1010d-python`
* `cd pa1010d-python`
* `sudo ./install.sh --unstable`

Stable (library only) from PyPi:

* Just run `python3 -m pip install pa1010d`

# Changelog

0.0.4
-----

* Fix read/write for Python 3.9

0.0.3
-----

* Add support for geoidal separation
* Add support for lat/long direction
* Require Python >= 3.6

0.0.2
-----

* Add support for disabling PPS LED
* Handle spurious newlines in sentences
* Add PDOP, VDOP and HDOP output
* Handle GLL messages

0.0.1
-----

* Initial Release
