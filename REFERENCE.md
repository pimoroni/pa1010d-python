# Reference <!-- omit in toc -->

The PA1010D library communicates with the GPS over i2c, reading messages a byte at a time from a single register.

Messages are decoded using [pynmea2](https://github.com/Knio/pynmea2).

- [Getting Started](#getting-started)
  - [Installing (Stable)](#installing-stable)
  - [Installing (Unstable)](#installing-unstable)
- [Function Reference](#function-reference)
  - [Update](#update)
  - [Timestamp](#timestamp)
  - [Latitude & Longitude](#latitude--longitude)
  - [Altitude](#altitude)
  - [Number of Satellites](#number-of-satellites)
  - [GPS Fix Quality](#gps-fix-quality)
  - [Speed Over Ground](#speed-over-ground)

## Getting Started

The PA1010D Python library requires Python 3.4 or greater.

Most people should grab the code from GitHub and run our simple installer.

### Installing (Stable)

```
git clone https://github.com/pimoroni/pa1010d-python
cd pa1010d-python
sudo ./install.sh
```

This ensures any dependencies are installed and will copy examples into `~/Pimoroni/pa1010d/`

You can install just the pa1010d library from pypi by running:

```
sudo pip3 install pa1010d
```

### Installing (Unstable)

To install the library and dependencies directly from GitHub you can specify the `--unstable` flag on `./install.sh`:

```
git clone https://github.com/pimoroni/pa1010d-python
cd pa1010d-python
sudo ./install.sh --unstable
```

This will run `setup.py install` in the `library` directory instead of installing the library from pypi.

## Function Reference

In all cases you'll first need to initialise a PA1010D library instance like so:

```python
from pa1010d import PA1010D

gps = PA1010D()
```

### Update

The PA1010D GPS is read over i2c via a single register. To guarantee that `update` has actually retrieved new data, the update function will poll for new data until a specific sentence type is decoded or a timeout is reached.

```python
gps.update(wait_for="GGA", timeout=5)
```

By default the `update` function will wait 5 seconds for a "GGA" message, decoding and storing the information from any messages in the interim.

All positioning information is then read from properties.

### Timestamp

```python
gps.timestamp
```

The timestamp of the last GGA message decoded from the GPS

### Latitude & Longitude

```python
gps.latitude
gps.longitude
```

The latitude and longitude from the last decoded GGA message.

### Altitude

```python
gps.altitude
```

The altitude from the last decoded GGA message.

### Number of Satellites

```python
gps.num_sats
```

The number of satellites from the last decoded GGA message.

### GPS Fix Quality

```python
gps.gps_qual
```

The fix quality from the last decoded GGA message.

### Speed Over Ground

```python
gps.speed_over_ground
```

The speed over ground (in knots) from the last decoded RMC message.
