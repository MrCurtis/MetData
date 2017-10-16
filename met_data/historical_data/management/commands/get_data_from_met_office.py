from django.core.management.base import BaseCommand, CommandError

from historical_data.met_data_getter import Region, ValueType, get_met_data
from historical_data.models import create_or_update_data_point

class Command(BaseCommand):
    help = 'Gets historical meteorological data from the Met Office'

    def handle(self, *args, **options):
        for region in Region:
            for value_type in ValueType:
                data_points = get_met_data(region, value_type)
                for data_point in data_points:
                    create_or_update_data_point(*data_point)
    
        self.stdout.write(self.style.SUCCESS('Successfully got Met Office data'))
