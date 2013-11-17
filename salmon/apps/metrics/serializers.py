import logging
from django.utils.timezone import now
from rest_framework import serializers

from . import models

logger = logging.getLogger(__name__)


class MetricSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source='source.name', required=False)
    value = serializers.FloatField(source='latest_value')
    timestamp = serializers.DateTimeField(source='last_updated',
                                          required=False)

    class Meta:
        model = models.Metric
        fields = ('source', 'name', 'value', 'timestamp')

    def restore_object(self, attrs, instance=None):
        kwargs = {'name': attrs['name']}
        if 'source.name' in attrs:
            source, created = models.Source.objects.get_or_create(
                name=attrs['source.name'])
            if created:
                logger.debug('Created source: %s', source.name)
            kwargs['source_id'] = source.pk
        try:
            instance = self.opts.model.objects.get(**kwargs)
        except self.opts.model.DoesNotExist:
            instance = self.opts.model(**kwargs)
        instance.latest_value = attrs['latest_value']
        instance.last_updated = attrs.get('timestamp', now())
        return instance

    def save_object(self, obj, **kwargs):
        if 'force_insert' in kwargs:
            del(kwargs['force_insert'])
        super(MetricSerializer, self).save_object(obj, **kwargs)
        obj.add_latest_to_archive()
