"""
sentry.management.commands.start
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from django.core.management import call_command
from django.core.management.base import NoArgsCommand

from optparse import make_option
import sys

from salmon.core.server import SalmonHTTPServer


class Command(NoArgsCommand):
    help = 'Starts the web service'

    option_list = NoArgsCommand.option_list + (
        make_option('--debug',
            action='store_true',
            dest='debug',
            default=False),
        make_option('--noupgrade',
            action='store_false',
            dest='upgrade',
            default=True),
        make_option('--workers', '-w',
            dest='workers',
            type=int,
            default=None),
    )

    def handle(self, address=None, upgrade=True, **options):

        if address:
            if ':' in address:
                host, port = address.split(':', 1)
                port = int(port)
            else:
                host = address
                port = None
        else:
            host, port = None, None

        if upgrade:
            # Ensure we perform an upgrade before starting any service
            print "Performing upgrade before service startup..."
            call_command('migrate', verbosity=0)


        server = SalmonHTTPServer(
            debug=options.get('debug'),
            host=host,
            port=port,
            workers=options.get('workers'),
        )

        # remove command line arguments to avoid optparse failures with service code
        # that calls call_command which reparses the command line, and if --noupgrade is supplied
        # a parse error is thrown
        sys.argv = sys.argv[:1]

        print "Running web service"
        server.run()
