# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Target'
        db.create_table(u'monitor_target', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'monitor', ['Target'])

        # Adding model 'Function'
        db.create_table(u'monitor_function', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'monitor', ['Function'])

        # Adding model 'Check'
        db.create_table(u'monitor_check', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('target', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['monitor.Target'])),
            ('function', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['monitor.Function'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('last_run', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True)),
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
        ))
        db.send_create_signal(u'monitor', ['Result'])


    def backwards(self, orm):
        # Deleting model 'Target'
        db.delete_table(u'monitor_target')

        # Deleting model 'Function'
        db.delete_table(u'monitor_function')

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
            'function': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['monitor.Function']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_run': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['monitor.Target']"})
        },
        u'monitor.function': {
            'Meta': {'object_name': 'Function'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'monitor.minion': {
            'Meta': {'object_name': 'Minion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'monitor.result': {
            'Meta': {'object_name': 'Result'},
            'check': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['monitor.Check']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['monitor.Minion']"}),
            'result': ('django.db.models.fields.TextField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'monitor.target': {
            'Meta': {'object_name': 'Target'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['monitor']