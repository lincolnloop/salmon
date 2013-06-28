from datetime import datetime
import os
import whisper

from django.conf import settings


class WhisperDatabase(object):
    def __init__(self, name):
        self.name = name
        self.path = self.get_db_path(name)
        if not os.path.exists(self.path):
            self._create()

    def get_db_path(self, name):
        return os.path.join(settings.SALMON_WHISPER_DB_PATH, name)

    def _create(self):
        """Create the Whisper file on disk"""
        if not os.path.exists(settings.SALMON_WHISPER_DB_PATH):
            os.makedirs(settings.SALMON_WHISPER_DB_PATH)
        archives = [whisper.parseRetentionDef(retentionDef)
                    for retentionDef in settings.ARCHIVES.split(",")]
        whisper.create(self.path, archives,
                       xFilesFactor=settings.XFILEFACTOR,
                       aggregationMethod=settings.AGGREGATION_METHOD)

    def update(self, timestamp, value):
        self._update([(timestamp.strftime("%s"), value)])

    def _update(self, datapoints):
        """
        This method store in the datapoints in the current database.

            :datapoints: is a list of tupple with the epoch timestamp and value
                 [(1368977629,10)]
        """
        if len(datapoints) == 1:
            timestamp, value = datapoints[0]
            whisper.update(self.path, value, timestamp)
        else:
            whisper.update_many(self.path, datapoints)

    def fetch(self, from_time, until_time=None):
        """
        This method fetch data from the database according to the period
        given

        fetch(path, fromTime, untilTime=None)

        fromTime is an datetime
        untilTime is also an datetime, but defaults to now.

        Returns a tuple of (timeInfo, valueList)
        where timeInfo is itself a tuple of (fromTime, untilTime, step)

        Returns None if no data can be returned
        """
        until_time = until_time or datetime.now()
        time_info, values = whisper.fetch(self.path,
                                          from_time.strftime('%s'),
                                          until_time.strftime('%s'))
        # build up a list of (timestamp, value)
        start_time, end_time, step = time_info
        current = start_time
        times = []
        while current <= end_time:
            times.append(current)
            current += step
        return zip(times, values)
