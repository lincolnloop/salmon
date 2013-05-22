from optparse import make_option

from django.core.management.base import BaseCommand

from salmon.apps.monitor.tests import generate_sample_data


class Command(BaseCommand):
    help = "Run Salt monitor checks"
    option_list = BaseCommand.option_list + (
        make_option('--point_number',
                    action='store_true',
                    dest='point_numbers',
                    default=1000,
                    help='Number of results you want to create.'),
        make_option('--interval',
                    action='store_true',
                    dest='interval',
                    default=5,
                    help='Interval in minutes between each result'))

    def handle(self, *args, **options):
        print("Generating sample data ....")
        print("This operation will take few seconds.")
        generate_sample_data(options["point_numbers"], options["interval"])
