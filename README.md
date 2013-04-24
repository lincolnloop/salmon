# salt-monitor

A multi-server monitoring system built on top of [Salt](http://www.saltstack.org) using Django.

The project is currently just a proof-of-concept. I'm interested in exploring its usefulness as both an alerting system like [monit](http://mmonit.com/monit/) and a monitoring system like [munin](http://munin-monitoring.org/) (perhaps using [Graphite's whisper datebase](http://graphite.readthedocs.org/en/latest/whisper.html)). 

![](http://cl.ly/image/2R1o2b0D1j1q/content.png)

## Installation

It's expected that you'll run this on the same server as the Salt master.

To bootstrap the project:

    virtualenv salt_monitor
    source salt_monitor/bin/activate
    cd path/to/salt_monitor/repository
    pip install -r requirements.pip
    pip install -e .
    cp salt_monitor/settings/local.py.example salt_monitor/settings/local.py
    manage.py syncdb --migrate

Fire up the development server with:

    manage.py runserver

Now login to the admin at `http://localhost:8000/admin/` to add some Salt targets to monitor. You can load some example data with the command `manage.py loaddata example_data`.

Once you have your targets defined, you can run `manage.py run_checks` periodically with `cron` and view the status at `http://localhost:8000`.

## Configuring Salt

For security reasons, you shouldn't run this as `root` on your server. Instead, use (or create) a less privileged user and modify your Salt master config to only provide access to the specific functions it needs to check. For example, you could create `/etc/salt/master.d/monitor_acl.conf` with the following contents:

    client_acl:
      youruser:
        - '.*':
          - test.ping
          - service.status
          - disk.usage

Be sure to restart the `salt-master` for configuration changes to take effect. For more details, read the docs on Salt's [`client_acl`](http://docs.saltstack.com/ref/configuration/master.html#std:conf_master-client_acl).
