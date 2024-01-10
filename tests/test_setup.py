def test_setup(smbus):
    import pa1010d

    gps = pa1010d.PA1010D()
    del gps


def test_send_command(smbus):
    import pa1010d

    gps = pa1010d.PA1010D()
    gps.send_command("$TEST")
    gps.send_command("$TEST*")
    gps.send_command("$TEST*".encode("ascii"))


def test_recv_command(smbus):
    import pa1010d

    gps = pa1010d.PA1010D()
    assert gps.update() is True
