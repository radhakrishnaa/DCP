def assert_valid_carrier(carrier):
    assert 'comment' in carrier
    assert 'old_code' in carrier
    assert 'code' in carrier
    assert 'id' in carrier
    assert 'name' in carrier

    assert isinstance(carrier['code'], basestring)
    assert isinstance(carrier['name'], basestring)
    assert isinstance(carrier['id'], int)


def test_list(server):
    carriers = server.api('GET', 'carrier', {
        'max': 20,
    })
    for carrier in carriers:
        assert_valid_carrier(carrier)

    assert len(carriers) is 20
