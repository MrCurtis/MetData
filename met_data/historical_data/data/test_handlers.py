from django.test import TestCase
from historical_data.data.handlers import (
    create_or_update_data_point,
    get_time_series)
from historical_data.data.models import (
    HistoricalData,
    region_mapper,
    month_mapper,
    value_type_mapper)
from historical_data.data.met_data_getter import  Month, Region, ValueType
from historical_data.data.met_data_getter import  DataPoint


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

    def test_creates_if_no_entry_for_time_region_and_data_type_exists(self):
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
                month=month_mapper[Month.MAY],
                value_type=value_type_mapper[ValueType.MAX_TEMP])
        except HistoricalData.ObjectNotFound:
            self.fail("Did not create object")

        self.assertEqual(entry.value, 123.45)

    def test_creates_if_datapoint_varies_from_existing_by_year(self):
        year_1 = 1982
        value_1 = 12.5
        year_2 = 1999
        value_2 = 45.0
        create_or_update_data_point(
            region=Region.UK,
            year=year_1,
            month=Month.MAY,
            value_type=ValueType.MAX_TEMP,
            value=value_1)
        create_or_update_data_point(
            region=Region.UK,
            year=year_2,
            month=Month.MAY,
            value_type=ValueType.MAX_TEMP,
            value=value_2)
        expected = {
            (year_1, value_1),
            (year_2, value_2)}

        entries = HistoricalData.objects.filter(
            region=region_mapper[Region.UK],
            month=month_mapper[Month.MAY],
            value_type=value_type_mapper[ValueType.MAX_TEMP])
        returned = {
            (entry.year, entry.value) for entry in entries}

        self.assertEqual(returned, expected)

    def test_creates_if_datapoint_varies_from_existing_by_month(self):
        month_1 = Month.MAY
        value_1 = 2.4
        month_2 = Month.JUN
        value_2 = 6.34
        create_or_update_data_point(
            region=Region.UK,
            year=1980,
            month=month_1,
            value_type=ValueType.MAX_TEMP,
            value=value_1)
        create_or_update_data_point(
            region=Region.UK,
            year=1980,
            month=month_2,
            value_type=ValueType.MAX_TEMP,
            value=value_2)
        expected = {
            (month_mapper[month_1], value_1),
            (month_mapper[month_2], value_2)}

        entries = HistoricalData.objects.filter(
            region=region_mapper[Region.UK],
            year=1980,
            value_type=value_type_mapper[ValueType.MAX_TEMP])
        returned = {
            (entry.month, entry.value) for entry in entries}

        self.assertEqual(returned, expected)

    def test_creates_if_datapoint_varies_from_existing_by_region(self):
        region_1 = Region.UK
        value_1 = 9.2
        region_2 = Region.WALES
        value_2 = 5.2
        create_or_update_data_point(
            region=region_1,
            year=1980,
            month=Month.MAY,
            value_type=ValueType.MAX_TEMP,
            value=value_1)
        create_or_update_data_point(
            region=region_2,
            year=1980,
            month=Month.MAY,
            value_type=ValueType.MAX_TEMP,
            value=value_2)
        expected = {
            (region_mapper[region_1], value_1),
            (region_mapper[region_2], value_2)}

        entries = HistoricalData.objects.filter(
            year=1980,
            month=month_mapper[Month.MAY],
            value_type=value_type_mapper[ValueType.MAX_TEMP])
        returned = {
            (entry.region, entry.value) for entry in entries}

        self.assertEqual(returned, expected)

    def test_creates_if_datapoint_varies_from_existing_by_value_type(self):
        value_type_1 = ValueType.MAX_TEMP
        value_1 = 45.1
        value_type_2 = ValueType.MIN_TEMP
        value_2 = 4.1
        create_or_update_data_point(
            region=Region.UK,
            year=1980,
            month=Month.MAY,
            value_type=value_type_1,
            value=value_1)
        create_or_update_data_point(
            region=Region.UK,
            year=1980,
            month=Month.MAY,
            value_type=value_type_2,
            value=value_2)
        expected = {
            (value_type_mapper[value_type_1], value_1),
            (value_type_mapper[value_type_2], value_2)}

        entries = HistoricalData.objects.filter(
            region=region_mapper[Region.UK],
            year=1980,
            month=month_mapper[Month.MAY])
        returned = {
            (entry.value_type, entry.value) for entry in entries}

        self.assertEqual(returned, expected)

    def test_updates_if_datapoint_varies_from_existing_by_value_only(self):
        initial_value = 23.
        new_value = 56.7

        create_or_update_data_point(
            region=Region.UK,
            year=1980,
            month=Month.MAY,
            value_type=ValueType.MAX_TEMP,
            value=initial_value)
        create_or_update_data_point(
            region=Region.UK,
            year=1980,
            month=Month.MAY,
            value_type=ValueType.MAX_TEMP,
            value=new_value)

        try:
            entry = HistoricalData.objects.get(
                region=region_mapper[Region.UK],
                year=1980,
                value_type=value_type_mapper[ValueType.MAX_TEMP],
                month=month_mapper[Month.MAY])
        except HistoricalData.MultipleObjectsReturned:
            self.fail("Created multiple objects")

        self.assertEqual(entry.value, new_value)


