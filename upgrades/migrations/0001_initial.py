# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table(u'upgrades_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('role', self.gf('django.db.models.fields.CharField')(default='R', max_length=1)),
            ('products', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('carriers', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('languages', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
            ('regions', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
        ))
        db.send_create_signal(u'upgrades', ['UserProfile'])

        # Adding model 'UpgradePathStatus'
        db.create_table(u'upgrades_upgradepathstatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='DRAFT', max_length=20)),
            ('created_on', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('modified_on', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'upgrades', ['UpgradePathStatus'])

        # Adding model 'UpgradePath'
        db.create_table(u'upgrades_upgradepath', (
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('bvs', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('pojo', self.gf('django.db.models.fields.TextField')(max_length=48000)),
        ))
        db.send_create_signal(u'upgrades', ['UpgradePath'])


    def backwards(self, orm):
        # Deleting model 'UserProfile'
        db.delete_table(u'upgrades_userprofile')

        # Deleting model 'UpgradePathStatus'
        db.delete_table(u'upgrades_upgradepathstatus')

        # Deleting model 'UpgradePath'
        db.delete_table(u'upgrades_upgradepath')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'upgrades.upgradepath': {
            'Meta': {'object_name': 'UpgradePath'},
            'bvs': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'pojo': ('django.db.models.fields.TextField', [], {'max_length': '48000'})
        },
        u'upgrades.upgradepathstatus': {
            'Meta': {'object_name': 'UpgradePathStatus'},
            'created_on': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_on': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'DRAFT'", 'max_length': '20'})
        },
        u'upgrades.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'carriers': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languages': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'products': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'regions': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'default': "'R'", 'max_length': '1'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['upgrades']