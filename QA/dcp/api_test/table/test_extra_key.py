def test_create_extra_key(server):
    extra_key_to_be_create = {
        'code': 'mcc-mnc-test-01',
        'name': 'mcc-mnc-test-01',
        'comment': 'test creating mcc-mnc-test-01',
    }
    result = server.api('POST', 'extra_key', extra_key_to_be_create)

    assert result is not None
    assert result['code'] == extra_key_to_be_create['code']
    assert result['name'] == extra_key_to_be_create['name']
    assert result['comment'] == extra_key_to_be_create['comment']


def test_list_one_extra_key(server):
    extra_key_to_be_create = {
        'code': 'mcc-mnc-test-02',
        'name': 'mcc-mnc-test-02',
        'comment': 'test creating mcc-mnc-test-02',
    }
    result = server.api('POST', 'extra_key', extra_key_to_be_create)

    assert result is not None
    id_to_be_listed = result['id']

    uri = 'extra_key/%s' % id_to_be_listed
    result = server.api('GET', uri)

    assert result is not None
    assert result['code'] == extra_key_to_be_create['code']
    assert result['name'] == extra_key_to_be_create['name']
    assert result['comment'] == extra_key_to_be_create['comment']


def test_list_all_extra_key(server):
    extra_key_to_be_create = {
        'code': 'mcc-mnc-test-03',
        'name': 'mcc-mnc-test-03',
        'comment': 'test creating mcc-mnc-test-03',
    }
    result = server.api('POST', 'extra_key', extra_key_to_be_create)

    assert result is not None

    result = server.api('GET', 'extra_key')

    assert result is not None
    found = False
    for result_item in result:
        if result_item['code'] != extra_key_to_be_create['code']:
            continue
        assert result_item['name'] == extra_key_to_be_create['name']
        assert result_item['comment'] == extra_key_to_be_create['comment']
        found = True
    assert found


def test_update_extra_key(server):
    extra_key_to_be_create = {
        'code': 'mcc-mnc-test-04',
        'name': 'mcc-mnc-test-04',
        'comment': 'test creating mcc-mnc-test-04',
    }
    result = server.api('POST', 'extra_key', extra_key_to_be_create)

    assert result is not None
    id_to_be_updated = result['id']

    extra_key_to_be_update = {
        'code': 'mcc-mnc-test-05',
        'name': 'mcc-mnc-test-05',
        'comment': 'test creating mcc-mnc-test-05',
    }
    uri = 'extra_key/%s' % id_to_be_updated
    result = server.api('PUT', uri, extra_key_to_be_update)

    assert result is not None
    assert result['id'] == id_to_be_updated
    assert result['code'] == extra_key_to_be_update['code']
    assert result['name'] == extra_key_to_be_update['name']
    assert result['comment'] == extra_key_to_be_update['comment']


def test_delete_extra_key(server):
    results = server.api('GET', 'extra_key')

    for result in results:
        id_to_be_deleted = result['id']
        uri = 'extra_key/%s' % id_to_be_deleted
        server.api('DELETE', uri)

    results = server.api('GET', 'extra_key')
    assert results == []
