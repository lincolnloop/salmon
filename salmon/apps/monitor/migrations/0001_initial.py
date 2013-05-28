# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Check'
        db.create_table(u'monitor_check', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('target', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('function', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'monitor', ['Check'])

        # Adding model 'Minion'
        db.create_table(u'monitor_minion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'monitor', ['Minion'])

        # Adding model 'Result'
        db.create_table(u'monitor_result', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('check', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['monitor.Check'])),
            ('minion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['monitor.Minion'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('result', self.gf('django.db.models.fields.TextField')()),
            ('result_type', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('failed', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'monitor', ['Result'])


    def backwards(self, orm):
        # Deleting model 'Check'
        db.delete_table(u'monitor_check')

        # Deleting model 'Minion'
        db.delete_table(u'monitor_minion')

        # Deleting model 'Result'
        db.delete_table(u'monitor_result')


    models = {
        u'monitor.check': {
            'Meta': {'object_name': 'Check'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'function': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'target': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'monitor.minion': {
            'Meta': {'object_name': 'Minion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'monitor.result': {
            'Meta': {'object_name': 'Result'},
            'check': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['monitor.Check']"}),
            'failed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['monitor.Minion']"}),
            'result': ('django.db.models.fields.TextField', [], {}),
            'result_type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }

    complete_apps = ['monitor']