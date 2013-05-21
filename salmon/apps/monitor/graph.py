from datetime import datetime
import os
import whisper

from django.conf import settings


class WhisperDatabase(object):
    def __init__(self, name):
        self.name = name
        self.path = self.get_db_path(name)

    def get_db_path(self, name):
        return os.path.join(settings.SALMON_WHISPER_DB_PATH, name)


    def get_or_create(self):
        if not os.path.exists(self.path):
            archives = [whisper.parseRetentionDef(settings.ARCHIVES)]
            whisper.create(self.path, archives,
                           xFilesFactor=settings.XFILEFACTOR,
                           aggregationMethod=settings.AGGREGATION_METHOD)


    def _floatify(self, value):
        """
        This method try to convert a value to a float
        """
        if isinstance(value, float):
            return value
        elif isinstance(value, int):
            return float(value)
        elif isinstance(value, str) or isinstance(value, unicode):
            try:
                return float(value)
            except ValueError as err:
                # the value might be a %, remove the sign and try again
                return float(value.replace("%", ""))

    def update(self, value):
        value = self._floatify(value)
        self._update([(datetime.now().strftime("%s"), value)])

    def _update(self, datapoints):
        """
        This method store in the datapoints in the current database.

            :datapoints: is a list of tupple with the epoch timestamp and value
                 [(1368977629,10)]
        """
        if len(datapoints) == 1:
          timestamp,value = datapoints[0]
          whisper.update(self.path, value, timestamp)
        else:
          whisper.update_many(self.path, datapoints)



