from django.test import TestCase
from historical_data.data.models import HistoricalData
from historical_data.data.met_data_getter import  Month, Region, ValueType
from historical_data.data.met_data_getter import  DataPoint
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError


class HistoricalDataTests(TestCase):

    def test_can_create_data_point_when_all_fields_specified(self):
        historical_data = HistoricalData(
            year=2001,
            month=12,
            region="wales",
            value_type="max_temp",
            value=34.5)
        historical_data.save()

    def test_cannot_create_data_point_without_value_type(self):
        try:
            historical_data = HistoricalData(
                year=1967,
                month=3,
                region="uk",
                value=19.43)
            historical_data.save()
        except (IntegrityError, ValidationError):
            pass
        else:
            self.fail("Should not be able to create without value type.")

    def test_cannot_create_data_point_without_value(self):
        try:
            historical_data = HistoricalData(
                year=1967,
                month=3,
                region="uk",
                value_type="max_temp")
            historical_data.save()
        except (IntegrityError, ValidationError):
            pass
        else:
            self.fail("Should not be able to create without value.")

    def test_cannot_create_data_point_without_year(self):
        try:
            historical_data = HistoricalData(
                month=3,
                region="uk",
                value_type="mean_temp",
                value=4.2)
            historical_data.save()
        except (IntegrityError, ValidationError):
            pass
        else:
            self.fail("Should not be able to create without year.")

    def test_cannot_create_data_point_without_month(self):
        try:
            historical_data = HistoricalData(
                year=2001,
                region="england",
                value_type="mean_temp",
                value=4.2)
            historical_data.save()
        except (IntegrityError, ValidationError):
            pass
        else:
            self.fail("Should not be able to create without month.")

    def test_cannot_create_data_point_without_region(self):
        try:
            historical_data = HistoricalData(
                year=2001,
                month=4,
                value_type="mean_temp",
                value=4.2)
            historical_data.save()
        except (IntegrityError, ValidationError):
            pass
        else:
            self.fail("Should not be able to create without region.")
