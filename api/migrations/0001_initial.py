# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Region'
        db.create_table('region', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('api', ['Region'])

        # Adding model 'Carrier'
        db.create_table('carrier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('api', ['Carrier'])

        # Adding model 'Hwtype'
        db.create_table('hwtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('internal_name', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('marketing_name', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
        ))
        db.send_create_signal('api', ['Hwtype'])

        # Adding model 'SettingCategory'
        db.create_table('setting_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
        ))
        db.send_create_signal('api', ['SettingCategory'])

        # Adding model 'SettingDef'
        db.create_table('setting_def', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.SettingCategory'], db_column='category_id')),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('datatype', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('short_help', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('api', ['SettingDef'])

        # Adding model 'SettingValue'
        db.create_table('setting_value', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('setting_def_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.SettingDef'], db_column='setting_def_id')),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=8000, null=True, blank=True)),
        ))
        db.send_create_signal('api', ['SettingValue'])

        # Adding model 'ConfigSet'
        db.create_table('config_set', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('region_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Region'], null=True, db_column='region_id', blank=True)),
            ('carrier_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Carrier'], null=True, db_column='carrier_id', blank=True)),
            ('hwtype_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Hwtype'], null=True, db_column='hwtype_id', blank=True)),
            ('category_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.SettingCategory'], db_column='category_id')),
            ('fallback_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.ConfigSet'], null=True, db_column='fallback_id', blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
        ))
        db.send_create_signal('api', ['ConfigSet'])

        # Adding model 'User'
        db.create_table('user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('editor', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('approver', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('publisher', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('api', ['User'])

        # Adding model 'ConfigVersion'
        db.create_table('config_version', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('config_set_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.ConfigSet'], db_column='config_set_id')),
            ('last_editor_id', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='config_version_last_editor', null=True, db_column='last_editor_id', to=orm['api.User'])),
            ('last_edited', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('committer_id', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='config_version_committer', null=True, db_column='committer_id', to=orm['api.User'])),
            ('committed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('approver_id', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='config_version_approver', null=True, db_column='approver_id', to=orm['api.User'])),
            ('approved', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('publisher_id', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='config_version_publisher', null=True, db_column='publisher_id', to=orm['api.User'])),
            ('published', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('fallback_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.ConfigVersion'], null=True, db_column='fallback_id', blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
        ))
        db.send_create_signal('api', ['ConfigVersion'])

        # Adding model 'ConfigSetting'
        db.create_table('config_setting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('config_version_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.ConfigVersion'], db_column='config_version_id')),
            ('setting_value_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.SettingValue'], db_column='setting_value_id')),
        ))
        db.send_create_signal('api', ['ConfigSetting'])


    def backwards(self, orm):
        # Deleting model 'Region'
        db.delete_table('region')

        # Deleting model 'Carrier'
        db.delete_table('carrier')

        # Deleting model 'Hwtype'
        db.delete_table('hwtype')

        # Deleting model 'SettingCategory'
        db.delete_table('setting_category')

        # Deleting model 'SettingDef'
        db.delete_table('setting_def')

        # Deleting model 'SettingValue'
        db.delete_table('setting_value')

        # Deleting model 'ConfigSet'
        db.delete_table('config_set')

        # Deleting model 'User'
        db.delete_table('user')

        # Deleting model 'ConfigVersion'
        db.delete_table('config_version')

        # Deleting model 'ConfigSetting'
        db.delete_table('config_setting')


    models = {
        'api.carrier': {
            'Meta': {'ordering': "['code']", 'object_name': 'Carrier', 'db_table': "'carrier'"},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'api.config_set': {
            'Meta': {'ordering': "['hwtype_id', 'carrier_id', 'region_id']", 'object_name': 'ConfigSet', 'db_table': "'config_set'"},
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
            'version_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'api.hwtype': {
            'Meta': {'ordering': "['code']", 'object_name': 'Hwtype', 'db_table': "'hwtype'"},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'marketing_name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'})
        },
        'api.region': {
            'Meta': {'ordering': "['code']", 'object_name': 'Region', 'db_table': "'region'"},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'short_help': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
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