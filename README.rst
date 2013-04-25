salmon
======

A multi-server monitoring system built on top of `Salt <http://www.saltstack.org>`_ using Django.

The project currently isn't much more than proof-of-concept. I'm interested in exploring its usefulness as both an alerting system like `monit <http://mmonit.com/monit/>`_ and a monitoring system like `munin <http://munin-monitoring.org/>`_ (perhaps using `Graphite's whisper database <http://graphite.readthedocs.org/en/latest/whisper.html>`_). 

.. image:: http://cl.ly/image/3s340i0W0N06/content.png

Installation
-------------

It's expected that you'll run this on the same server as the Salt master.

To bootstrap the project::

    virtualenv salmon
    source salmon/bin/activate
    pip install salmon
    salmon init
    salmon upgrade

Fire up the web server with::

    salmon start

Now create a config file for your checks. There is a `commented example in the repo <https://github.com/lincolnloop/salmon/blob/master/salmon/settings/example/checks.yaml>`_. Store this in the same directory as your ``conf.py`` file (default: ``~/.salmon/checks.yaml``).

Once you have your checks defined, you can run ``manage.py run_checks`` periodically with ``cron`` and view the status at ``http://localhost:9000``.

Configuring Salt
----------------

For security reasons, you shouldn't run this as ``root`` on your server. Instead, use (or create) a less privileged user and modify your Salt master config to only provide access to the specific functions it needs to check. For example, you could create ``/etc/salt/master.d/monitor_acl.conf`` with the following contents::

    client_acl:
      youruser:
        - '.*':
          - test.ping
          - service.status
          - disk.usage
          - 'ps.*'
          - file.check_hash

Be sure to restart the ``salt-master`` for configuration changes to take effect. For more details, read the docs on Salt's `client_acl <http://docs.saltstack.com/ref/configuration/master.html#std:conf_master-client_acl>`_.
