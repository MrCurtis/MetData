from django.test import TestCase
from historical_data.models import (
        HistoricalData,
        create_or_update_data_point,
        get_time_series,
        region_mapper,
        month_mapper,
        value_type_mapper)
from historical_data.met_data_getter import  Month, Region, ValueType
from historical_data.met_data_getter import  DataPoint
from django.db.utils import IntegrityError


class GetTimeSeriesTests(TestCase):

    def test_returns_with_correct_value_type(self):
        expected_value_type = "Rainfall"
        data_points = {
            DataPoint(Region.WALES, 1234, Month.MAY, ValueType.RAINFALL, 23.5),        
            DataPoint(Region.WALES, 1234, Month.JUN, ValueType.RAINFALL, 22.5)}
        for dp in data_points:
            create_or_update_data_point(*dp)

        returned = get_time_series(ValueType.RAINFALL, {Region.WALES, Region.ENGLAND})

        self.assertEqual(returned["value_type"], expected_value_type)

    def test_labels_contains_every_month_between_earliest_and_latest_for_value_type(self):
        expected_labels = [
            "1913-MAY",
            "1913-JUN",
            "1913-JUL",
            "1913-AUG",
            "1913-SEP",
            "1913-OCT",
            "1913-NOV",
            "1913-DEC",
            "1914-JAN",
            "1914-FEB",
            "1914-MAR"]

        data_points = {
            DataPoint(Region.WALES, 1912, Month.MAY, ValueType.SUNSHINE, 45.5),        
            DataPoint(Region.WALES, 1913, Month.MAY, ValueType.RAINFALL, 23.5),        
            DataPoint(Region.WALES, 1913, Month.JUN, ValueType.RAINFALL, 22.5),
            DataPoint(Region.ENGLAND, 1913, Month.AUG, ValueType.RAINFALL, 22.5),
            DataPoint(Region.ENGLAND, 1913, Month.SEP, ValueType.RAINFALL, 22.5),
            DataPoint(Region.ENGLAND, 1913, Month.DEC, ValueType.RAINFALL, 22.5),
            DataPoint(Region.ENGLAND, 1914, Month.FEB, ValueType.RAINFALL, 22.5),
            DataPoint(Region.ENGLAND, 1914, Month.MAR, ValueType.RAINFALL, 22.5)}
        for dp in data_points:
            create_or_update_data_point(*dp)

        returned = get_time_series(ValueType.RAINFALL, {Region.WALES, Region.ENGLAND})

        self.assertEqual(returned["labels"], expected_labels)

    def test_returns_only_series_for_requested_regions(self):
        expected_regions = {"Wales", "Scotland"}

        data_points = {
            DataPoint(Region.WALES, 1913, Month.MAY, ValueType.RAINFALL, 23.5),        
            DataPoint(Region.WALES, 1913, Month.JUN, ValueType.RAINFALL, 22.5)}
        for dp in data_points:
            create_or_update_data_point(*dp)

        returned = get_time_series(ValueType.RAINFALL, {Region.WALES, Region.SCOTLAND})
        returned_regions = {x["name"] for x in returned["series"]}

        self.assertEqual(returned_regions, expected_regions)

    def test_returns_correst_value_series_filling_missing_data_with_none(self):
        expected_value_series = [
            None, None, None, 14.3, 12.8, None, None, 22.5, None, 32.5, None]

        data_points = {
            DataPoint(Region.WALES, 1912, Month.MAY, ValueType.SUNSHINE, 45.5),        
            DataPoint(Region.WALES, 1913, Month.MAY, ValueType.MAX_TEMP, 23.5),        
            DataPoint(Region.WALES, 1913, Month.JUN, ValueType.MAX_TEMP, 22.5),
            DataPoint(Region.ENGLAND, 1913, Month.AUG, ValueType.MAX_TEMP, 14.3),
            DataPoint(Region.ENGLAND, 1913, Month.SEP, ValueType.MAX_TEMP, 12.8),
            DataPoint(Region.ENGLAND, 1913, Month.DEC, ValueType.MAX_TEMP, 22.5),
            DataPoint(Region.ENGLAND, 1914, Month.FEB, ValueType.MAX_TEMP, 32.5),
            DataPoint(Region.WALES, 1914, Month.MAR, ValueType.MAX_TEMP, 24.5)}
        for dp in data_points:
            create_or_update_data_point(*dp)

        returned = get_time_series(ValueType.MAX_TEMP, {Region.WALES, Region.ENGLAND})
        returned_value_series = [x["data"] for x in returned["series"] if x["name"] == "England"][0]

        self.assertEqual(expected_value_series, returned_value_series)

class CreateOrUpdateDataPointTests(TestCase):

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
