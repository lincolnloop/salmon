# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Metric.transform'
        db.add_column(u'metrics_metric', 'transform',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Metric.transform'
        db.delete_column(u'metrics_metric', 'transform')


    models = {
        u'metrics.metric': {
            'Meta': {'unique_together': "(('source', 'name'),)", 'object_name': 'Metric'},
            'alert_operator': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'alert_triggered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'alert_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'display_as': ('django.db.models.fields.CharField', [], {'default': "'float'", 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_counter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'latest_value': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['metrics.Source']", 'null': 'True'}),
            'transform': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'metrics.source': {
            'Meta': {'object_name': 'Source'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['metrics']