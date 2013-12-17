salmon
======

.. image:: https://secure.travis-ci.org/lincolnloop/salmon.png?branch=master
   :target: http://travis-ci.org/lincolnloop/salmon

.. image:: https://coveralls.io/repos/lincolnloop/salmon/badge.png?branch=master
   :target: https://coveralls.io/r/lincolnloop/salmon?branch=master

A simple monitoring system built on top of Django.

The intent is to serve both as an alerting system like `monit <http://mmonit.com/monit/>`_  and a monitoring system like `munin <http://munin-monitoring.org/>`_ (using `Graphite's whisper database <http://graphite.readthedocs.org/en/latest/whisper.html>`_).

The original release of Salmon was coupled to `Salt <http://docs.saltstack.com/>`_ and designed to monitor servers (**Sal** t **Mon** itor). As of v0.2.0, the system has been decoupled from Salt and ingests data via a simple HTTP interface.


.. image:: http://cl.ly/image/3s340i0W0N06/content.png

.. image:: https://cloudup.com/chXR0xnFtkf+

Installation
-------------

To bootstrap the project::

    virtualenv salmon
    source salmon/bin/activate
    pip install salmon
    salmon init
    salmon upgrade
    salmon collectstatic

Fire up the web server with::

    salmon start

Sending Metrics to Salmon
-------------------------

Metrics are sent in as JSON over HTTP. The format for a single metric::

    {
        "source": "test.example.com",
        "name": "load",
        "value": 0.1
    }

Multiple metrics can be sent as an array::

    [
        {"source": "test.example.com", "name": "load", "value": 0.1},
        {"source": "multi.example.com", "name": "cpu", "value": 55.5}
    ]

The API endpoint is ``/api/v1/metric/``. If your Salmon server lives at http://salmon.example.com, you can ``POST`` to ``http://salmon.example.com/api/v1/metric/``. Pass in your API key as found in ``~/.salmon/conf.py`` for authentication. Using Curl, it would look something like this::

    curl -i --user "<API_KEY>:" \
         -H "Content-Type: application/json" \
         -X POST \
         -d '{"source": "test.example.com", "name": "load", "value": 0.1}' \
         http://salmon.example.com/api/v1/metric/


Using Salt
^^^^^^^^^^

1. Setup the `salt-stats <https://github.com/lincolnloop/salt-stats>`_ states on your master or just grab the `salmon returner <https://github.com/lincolnloop/salt-stats/blob/master/salt/_returners/salmon_return.py>`_
2. Add the path to your Salmon install and API key (found in ``~/.salmon/conf.py``) to your Salt Pillar. (`salmon pillar example <https://github.com/lincolnloop/salt-stats/blob/master/salt/_returners/salmon_return.py#L10-L12>`_)
3. Add a `schedule` pillar. (`schedule pillar example <https://gist.github.com/ipmb/8009715>`_)
4. Run ``salt '*' saltutil.sync_all``

*Note:* To use Salt's ``ps`` module, `psutil <https://code.google.com/p/psutil/>`_ must be installed on
the minions. Ubuntu provides a ``python-psutil`` package or it can be installed via ``pip install psutil``.
