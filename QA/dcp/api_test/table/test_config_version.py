import logging
import random
from __init__ import needs_publish

logger = logging.getLogger(__name__)

TEST_COMMENT = 'test_config_version automatic test'


@needs_publish
def test_change_setting(server):
    # get server default cloud
    user = server.api('GET', 'currentuser')
    assert 'cloud' in user
    cloud = user['cloud']
    assert cloud != 'prod'
    logger.info('default cloud %s', cloud)

    # get a test config_set
    config_sets = server.api('GET', 'config_set', {
        'like.category_id.name': 'Checkin',
        'like.hwtype': 'test',
        'like.carrier': 'test',
        'max': 1,

    })
    assert type(config_sets) is list
    assert len(config_sets) == 1
    config_set = config_sets[0]

    logger.debug('returned config set: %r' % config_set)

    # get the uncommitted version for that config_set
    config_versions = server.api('GET', 'config_version', {
        'eq.config_set_id': config_set['id'],
    })

    config_version = None
    for version_item in config_versions:
        if version_item['committed'] is None:
            config_version = version_item
    assert config_version is not None

    # set new setting value
    new_setting_value = '%d' % (random.random() * 10**12)
    logger.info('new setting value %s', new_setting_value)

    data = {
        'comment': TEST_COMMENT,
        'settings': {
            'dummy.abandoned.checkin': new_setting_value,
        },
    }
    server.api('PUT', 'config_version/%d/settings' % config_version['id'], data)
    server.api('PUT', 'config_version/%d/commit' % config_version['id'], data)
    server.api('PUT', 'config_version/%d/approve' % config_version['id'], data)
    server.api('PUT', 'config_version/%d/publish' % config_version['id'], {
        'comment': TEST_COMMENT,
    })

    # test if value was defined correctly
    ret = server.api('GET', 'livequery', {
        'carrier': config_set['carrier'],
        'hwtype': config_set['hwtype'],
        'region': config_set['region'],
        'env': cloud,
    })

    assert 'settings' in ret
    assert 'dummy.abandoned.checkin' in ret['settings']
    assert ret['settings']['dummy.abandoned.checkin'] == new_setting_value
