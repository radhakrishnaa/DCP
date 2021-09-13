def create_extra_key(server):
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
    return result


def get_one_extra_key(server):
    result = server.api('GET', 'extra_key')
    if not result:
        return create_extra_key(server)
    return result[0]


def create_extra_value_by_test_number(test_number, extra_key_id):
    extra_value_to_be_create = {
        'value': '300300-test-{}'.format(test_number),
        'name': 'retail-test-{}'.format(test_number),
        'comment': 'test creating extra val 300300-test-{}'.format(test_number),
        'extra_key_id': extra_key_id,
    }
    return extra_value_to_be_create


def post_extra_value(server, extra_value_to_be_create):
    return server.api('POST', 'extra_value', extra_value_to_be_create)


def test_create_extra_value(server):
    # Get extra key to relation with the extra value
    extra_key_to_relation = get_one_extra_key(server)

    # Create extra value object to be use in test
    extra_value_to_be_create = create_extra_value_by_test_number(
        '01', extra_key_to_relation['id'])

    # Post the extra value object to save extra value in server
    result = post_extra_value(server, extra_value_to_be_create)

    # Compare object that was post with object that was return of request
    assert result is not None
    assert result['value'] == extra_value_to_be_create['value']
    assert result['name'] == extra_value_to_be_create['name']
    assert result['comment'] == extra_value_to_be_create['comment']


def test_list_one_extra_value(server):
    # Get extra key to relation with the extra value
    extra_key_to_relation = get_one_extra_key(server)

    # Create extra value object to be use in test
    extra_value_to_be_create = create_extra_value_by_test_number(
        '02', extra_key_to_relation['id'])

    # Post the extra value object
    result = post_extra_value(server, extra_value_to_be_create)

    # Check if object was saved successfully and get id for next test
    assert result is not None
    id_to_be_listed = result['id']

    # Make the request and execute the GET
    uri = 'extra_value/%s' % id_to_be_listed
    result = server.api('GET', uri)

    assert result is not None
    assert result['value'] == extra_value_to_be_create['value']
    assert result['name'] == extra_value_to_be_create['name']
    assert result['comment'] == extra_value_to_be_create['comment']


def test_list_all_extra_value(server):
    # Get extra key to relation with the extra value
    extra_key_to_relation = get_one_extra_key(server)

    # Create extra value object to be use in test
    extra_value_to_be_create = create_extra_value_by_test_number(
        '03', extra_key_to_relation['id'])

    # Post the extra value object
    result = post_extra_value(server, extra_value_to_be_create)

    assert result is not None

    # Get all extra values in server
    result = server.api('GET', 'extra_value')

    assert result is not None
    found = False
    for result_item in result:
        if result_item['value'] != extra_value_to_be_create['value']:
            continue
        assert result_item['name'] == extra_value_to_be_create['name']
        assert result_item['comment'] == extra_value_to_be_create['comment']
        found = True
    assert found


def test_update_extra_value(server):
    # Get extra key to relation with the extra value
    extra_key_to_relation = get_one_extra_key(server)

    # Create extra value object to be use in test
    extra_value = create_extra_value_by_test_number(
        '04', extra_key_to_relation['id'])

    # Post the extra value object
    result = post_extra_value(server, extra_value)

    # Get id to be used in update test
    assert result is not None
    id_to_be_updated = result['id']

    # Change the property that will be updated
    extra_value['value'] = '300300-test04-update'

    # Make the request and execute PUT
    uri = 'extra_value/%s' % id_to_be_updated
    result = server.api('PUT', uri, extra_value)

    assert result is not None
    assert result['id'] == id_to_be_updated
    assert result['value'] == extra_value['value']


def test_delete_extra_value(server):
    # Get all extra values used in test to be delete
    results = server.api('GET', 'extra_value')

    # Make the delete request for each extra value created in all tests
    for result in results:
        id_to_be_deleted = result['id']
        uri = 'extra_value/%s' % id_to_be_deleted
        server.api('DELETE', uri)

    results = server.api('GET', 'extra_value')
    assert results == []
