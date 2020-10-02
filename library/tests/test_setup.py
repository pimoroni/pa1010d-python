def test_setup(smbus):
    import pa1010d

    gps = pa1010d.PA1010D()
    del gps
