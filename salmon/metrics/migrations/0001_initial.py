# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Source'
        db.create_table(u'metrics_source', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'metrics', ['Source'])

        # Adding model 'Metric'
        db.create_table(u'metrics_metric', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['metrics.Source'], null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('latest_value', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('alert_operator', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('alert_value', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('alert_triggered', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display_as', self.gf('django.db.models.fields.CharField')(default='float', max_length=20)),
        ))
        db.send_create_signal(u'metrics', ['Metric'])

        # Adding unique constraint on 'Metric', fields ['source', 'name']
        db.create_unique(u'metrics_metric', ['source_id', 'name'])


    def backwards(self, orm):
        # Removing unique constraint on 'Metric', fields ['source', 'name']
        db.delete_unique(u'metrics_metric', ['source_id', 'name'])

        # Deleting model 'Source'
        db.delete_table(u'metrics_source')

        # Deleting model 'Metric'
        db.delete_table(u'metrics_metric')


    models = {
        u'metrics.metric': {
            'Meta': {'unique_together': "(('source', 'name'),)", 'object_name': 'Metric'},
            'alert_operator': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'alert_triggered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'alert_value': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'display_as': ('django.db.models.fields.CharField', [], {'default': "'float'", 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'latest_value': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['metrics.Source']", 'null': 'True'})
        },
        u'metrics.source': {
            'Meta': {'object_name': 'Source'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['metrics']