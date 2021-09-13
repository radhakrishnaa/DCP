# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):

        if db.backend_name == 'mysql':
            try:
                db.execute('SET storage_engine=INNODB')
            except Exception:
                db.execute('SET default_storage_engine=INNODB')

        # Adding model 'ExtraKey'
        db.create_table('extra_key', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
        ))
        db.send_create_signal(u'api', ['ExtraKey'])

        # Adding model 'ExtraValue'
        db.create_table('extra_value', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('extra_key_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.ExtraKey'], db_column='extra_key_id')),
        ))
        db.send_create_signal(u'api', ['ExtraValue'])


    def backwards(self, orm):
        # Deleting model 'ExtraKey'
        db.delete_table('extra_key')

        # Deleting model 'ExtraValue'
        db.delete_table('extra_value')


    models = {
        u'api.carrier': {
            'Meta': {'ordering': "['code']", 'object_name': 'Carrier', 'db_table': "'carrier'"},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'old_code': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'})
        },
        u'api.cloudenv': {
            'Meta': {'ordering': "['order', 'short_name']", 'object_name': 'CloudEnv', 'db_table': "'cloud_env'"},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'env_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        u'api.configset': {
            'Meta': {'ordering': "['category_id', 'hwtype_id', 'carrier_id', 'region_id']", 'unique_together': "(('category_id', 'hwtype_id', 'carrier_id', 'region_id', 'delta_name'),)", 'object_name': 'ConfigSet', 'db_table': "'config_set'"},
            'carrier_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Carrier']", 'null': 'True', 'db_column': "'carrier_id'", 'blank': 'True'}),
            'category_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.SettingCategory']", 'db_column': "'category_id'"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'delta_name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'fallback_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.ConfigSet']", 'null': 'True', 'db_column': "'fallback_id'", 'blank': 'True'}),
            'hwtype_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Hwtype']", 'null': 'True', 'db_column': "'hwtype_id'", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'region_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Region']", 'null': 'True', 'db_column': "'region_id'", 'blank': 'True'})
        },
        u'api.configsetting': {
            'Meta': {'object_name': 'ConfigSetting', 'db_table': "'config_setting'"},
            'config_version_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.ConfigVersion']", 'db_column': "'config_version_id'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'setting_value_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.SettingValue']", 'db_column': "'setting_value_id'"})
        },
        u'api.configversion': {
            'Meta': {'object_name': 'ConfigVersion', 'db_table': "'config_version'"},
            'approved': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'approver_id': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'config_version_approver'", 'null': 'True', 'db_column': "'approver_id'", 'to': u"orm['api.User']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'committed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'committer_id': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'config_version_committer'", 'null': 'True', 'db_column': "'committer_id'", 'to': u"orm['api.User']"}),
            'config_set_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.ConfigSet']", 'db_column': "'config_set_id'"}),
            'fallback_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.ConfigVersion']", 'null': 'True', 'db_column': "'fallback_id'", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_edited': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_editor_id': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'config_version_last_editor'", 'null': 'True', 'db_column': "'last_editor_id'", 'to': u"orm['api.User']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'publisher_id': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'config_version_publisher'", 'null': 'True', 'db_column': "'publisher_id'", 'to': u"orm['api.User']"}),
            'setting_value': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['api.SettingValue']", 'null': 'True', 'through': u"orm['api.ConfigSetting']", 'blank': 'True'}),
            'version_number': ('django.db.models.fields.IntegerField', [], {})
        },
        u'api.envtransform': {
            'Meta': {'ordering': "['order', 'env_pat']", 'object_name': 'EnvTransform', 'db_table': "'env_transform'"},
            'carrier_region_pat': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'env_pat': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'hwtype_pat': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'setting_name_pat': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'value_pat': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'value_sub': ('django.db.models.fields.CharField', [], {'max_length': '8000', 'null': 'True', 'blank': 'True'})
        },
        u'api.extrakey': {
            'Meta': {'ordering': "['code']", 'object_name': 'ExtraKey', 'db_table': "'extra_key'"},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'api.extravalue': {
            'Meta': {'object_name': 'ExtraValue', 'db_table': "'extra_value'"},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'extra_key_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.ExtraKey']", 'db_column': "'extra_key_id'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'api.hwtype': {
            'Meta': {'ordering': "['code']", 'object_name': 'Hwtype', 'db_table': "'hwtype'"},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'marketing_name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'model_number': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'})
        },
        u'api.region': {
            'Meta': {'ordering': "['code']", 'object_name': 'Region', 'db_table': "'region'"},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'api.settingcategory': {
            'Meta': {'ordering': "['name']", 'object_name': 'SettingCategory', 'db_table': "'setting_category'"},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'})
        },
        u'api.settingdef': {
            'Meta': {'ordering': "['group', 'order', 'display_name']", 'object_name': 'SettingDef', 'db_table': "'setting_def'"},
            'category_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.SettingCategory']", 'db_column': "'category_id'"}),
            'datatype': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rules': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'short_help': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'})
        },
        u'api.settingvalue': {
            'Meta': {'object_name': 'SettingValue', 'db_table': "'setting_value'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'setting_def_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.SettingDef']", 'db_column': "'setting_def_id'"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '8000', 'null': 'True', 'blank': 'True'})
        },
        u'api.user': {
            'Meta': {'ordering': "['username']", 'object_name': 'User', 'db_table': "'user'"},
            'admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'approver': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'editor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publisher': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        }
    }

    complete_apps = ['api']
