# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Carrier.comment'
        db.add_column('carrier', 'comment',
                      self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Hwtype.model_number'
        db.add_column('hwtype', 'model_number',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Hwtype.comment'
        db.add_column('hwtype', 'comment',
                      self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True),
                      keep_default=False)


        # Changing field 'ConfigVersion.version_number'
        db.alter_column('config_version', 'version_number', self.gf('django.db.models.fields.IntegerField')(default=0))
        # Adding field 'Region.comment'
        db.add_column('region', 'comment',
                      self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True),
                      keep_default=False)

        # Adding field 'SettingDef.group'
        db.add_column('setting_def', 'group',
                      self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True),
                      keep_default=False)

        # Adding field 'SettingDef.order'
        db.add_column('setting_def', 'order',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'SettingDef.rules'
        db.add_column('setting_def', 'rules',
                      self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True),
                      keep_default=False)


        # Changing field 'SettingDef.short_help'
        db.alter_column('setting_def', 'short_help', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True))
        # Adding unique constraint on 'ConfigSet', fields ['hwtype_id', 'category_id', 'region_id', 'carrier_id']
        db.create_unique('config_set', ['hwtype_id', 'category_id', 'region_id', 'carrier_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ConfigSet', fields ['hwtype_id', 'category_id', 'region_id', 'carrier_id']
        db.delete_unique('config_set', ['hwtype_id', 'category_id', 'region_id', 'carrier_id'])

        # Deleting field 'Carrier.comment'
        db.delete_column('carrier', 'comment')

        # Deleting field 'Hwtype.model_number'
        db.delete_column('hwtype', 'model_number')

        # Deleting field 'Hwtype.comment'
        db.delete_column('hwtype', 'comment')


        # Changing field 'ConfigVersion.version_number'
        db.alter_column('config_version', 'version_number', self.gf('django.db.models.fields.IntegerField')(null=True))
        # Deleting field 'Region.comment'
        db.delete_column('region', 'comment')

        # Deleting field 'SettingDef.group'
        db.delete_column('setting_def', 'group')

        # Deleting field 'SettingDef.order'
        db.delete_column('setting_def', 'order')

        # Deleting field 'SettingDef.rules'
        db.delete_column('setting_def', 'rules')


        # Changing field 'SettingDef.short_help'
        db.alter_column('setting_def', 'short_help', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    models = {
        'api.carrier': {
            'Meta': {'ordering': "['code']", 'object_name': 'Carrier', 'db_table': "'carrier'"},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'api.config_set': {
            'Meta': {'ordering': "['category_id', 'hwtype_id', 'carrier_id', 'region_id']", 'unique_together': "(('category_id', 'hwtype_id', 'carrier_id', 'region_id'),)", 'object_name': 'ConfigSet', 'db_table': "'config_set'"},
            'carrier_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.Carrier']", 'null': 'True', 'db_column': "'carrier_id'", 'blank': 'True'}),
            'category_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.SettingCategory']", 'db_column': "'category_id'"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'fallback_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.ConfigSet']", 'null': 'True', 'db_column': "'fallback_id'", 'blank': 'True'}),
            'hwtype_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.Hwtype']", 'null': 'True', 'db_column': "'hwtype_id'", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'region_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.Region']", 'null': 'True', 'db_column': "'region_id'", 'blank': 'True'})
        },
        'api.config_setting': {
            'Meta': {'object_name': 'ConfigSetting', 'db_table': "'config_setting'"},
            'config_version_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.ConfigVersion']", 'db_column': "'config_version_id'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'setting_value_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.SettingValue']", 'db_column': "'setting_value_id'"})
        },
        'api.config_version': {
            'Meta': {'object_name': 'ConfigVersion', 'db_table': "'config_version'"},
            'approved': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'approver_id': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'config_version_approver'", 'null': 'True', 'db_column': "'approver_id'", 'to': "orm['api.User']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'committed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'committer_id': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'config_version_committer'", 'null': 'True', 'db_column': "'committer_id'", 'to': "orm['api.User']"}),
            'config_set_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.ConfigSet']", 'db_column': "'config_set_id'"}),
            'fallback_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.ConfigVersion']", 'null': 'True', 'db_column': "'fallback_id'", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_edited': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_editor_id': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'config_version_last_editor'", 'null': 'True', 'db_column': "'last_editor_id'", 'to': "orm['api.User']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'publisher_id': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'config_version_publisher'", 'null': 'True', 'db_column': "'publisher_id'", 'to': "orm['api.User']"}),
            'setting_value': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['api.SettingValue']", 'null': 'True', 'through': "orm['api.ConfigSetting']", 'blank': 'True'}),
            'version_number': ('django.db.models.fields.IntegerField', [], {})
        },
        'api.hwtype': {
            'Meta': {'ordering': "['code']", 'object_name': 'Hwtype', 'db_table': "'hwtype'"},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'marketing_name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'model_number': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'})
        },
        'api.region': {
            'Meta': {'ordering': "['code']", 'object_name': 'Region', 'db_table': "'region'"},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'api.setting_category': {
            'Meta': {'ordering': "['name']", 'object_name': 'SettingCategory', 'db_table': "'setting_category'"},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'})
        },
        'api.setting_def': {
            'Meta': {'ordering': "['display_name']", 'object_name': 'SettingDef', 'db_table': "'setting_def'"},
            'category_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.SettingCategory']", 'db_column': "'category_id'"}),
            'datatype': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rules': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'short_help': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'})
        },
        'api.setting_value': {
            'Meta': {'object_name': 'SettingValue', 'db_table': "'setting_value'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'setting_def_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.SettingDef']", 'db_column': "'setting_def_id'"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '8000', 'null': 'True', 'blank': 'True'})
        },
        'api.user': {
            'Meta': {'ordering': "['username']", 'object_name': 'User', 'db_table': "'user'"},
            'admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'approver': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'editor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publisher': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        }
    }

    complete_apps = ['api']