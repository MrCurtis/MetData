from django.test import TestCase
from historical_data.models import (
        HistoricalData,
        create_or_update_data_point,
        region_mapper,
        month_mapper,
        value_type_mapper)
from historical_data.met_data_getter import  Month, Region, ValueType
from django.db.utils import IntegrityError


class HistoricalDataManagerTests(TestCase):

    def test_create_or_update__creates_if_no_entry_for_time_and_region_exists(self):
        create_or_update_data_point(
            region=Region.UK,
            year=1987,
            month=Month.MAY,
            value_type=ValueType.MAX_TEMP,
            value=123.45)

        try:
            entry = HistoricalData.objects.get(
                region=region_mapper[Region.UK],
                year=1987,
                month=month_mapper[Month.MAY])
        except HistoricalData.ObjectNotFound:
            self.fail("Did not create object")

        self.assertEqual(entry.max_temp, 123.45)

    def test_create_or_update__updates_if_entry_for_time_and_region_exists(self):
        create_or_update_data_point(
            region=Region.UK,
            year=1987,
            month=Month.MAY,
            value_type=ValueType.MAX_TEMP,
            value=123.45)
        create_or_update_data_point(
            region=Region.UK,
            year=1987,
            month=Month.MAY,
            value_type=ValueType.SUNSHINE,
            value=9.1)

        try:
            entry = HistoricalData.objects.get(
                region=region_mapper[Region.UK],
                year=1987,
                month=month_mapper[Month.MAY])
        except HistoricalData.ObjectNotFound:
            self.fail("Did not create object")
        except HistoricalData.MultipleObjectReturned:
            self.fail("Created multiple objects")

        self.assertEqual(entry.max_temp, 123.45)
        self.assertEqual(entry.sunshine, 9.1)

    # TODO - Tests for raising ValueError


class HistoricalDataTests(TestCase):

    # TODO -These tests should all assert something

    def test_can_create_data_point_with_all_value_types(self):
        historical_data = HistoricalData(
            year=2001,
            month=12,
            region=4,
            max_temp=23.4,
            min_temp=16.2,
            mean_temp=20.0,
            sunshine=23.1,
            rainfall=34.0)
        historical_data.save()

    def test_can_create_data_point_with_some_value_types_missing(self):
        historical_data = HistoricalData(
            year=1985,
            month=5,
            region=3,
            max_temp=21.4,
            min_temp=16.2,
            rainfall=32.0)
        historical_data.save()

    def test_cannot_create_data_point_without_year(self):
        try:
            historical_data = HistoricalData(
                month=3,
                region=1,
                max_temp=23.4,
                min_temp=16.2,
                mean_temp=20.0,
                sunshine=23.1,
                rainfall=34.0)
            historical_data.save()
        except IntegrityError:
            pass
        else:
            self.fail("Should not be able to create without year.")

    def test_cannot_create_data_point_without_month(self):
        try:
            historical_data = HistoricalData(
                year=2001,
                region=2,
                max_temp=23.4,
                min_temp=16.2,
                mean_temp=20.0,
                sunshine=23.1,
                rainfall=34.0)
            historical_data.save()
        except IntegrityError:
            pass
        else:
            self.fail("Should not be able to create without month.")

    def test_cannot_create_data_point_without_region(self):
        try:
            historical_data = HistoricalData(
                year=2001,
                month=4,
                max_temp=23.4,
                min_temp=16.2,
                mean_temp=20.0,
                sunshine=23.1,
                rainfall=34.0)
            historical_data.save()
        except IntegrityError:
            pass
        else:
            self.fail("Should not be able to create without region.")
