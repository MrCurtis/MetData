from os import path
from unittest import TestCase, main
from unittest import skip

import responses

from historical_data.data.met_data_getter import get_met_data
from historical_data.data.met_data_getter import DataPoint, Month, Region, ValueType

FIXTURES_DIR = path.join(path.dirname(__file__), "test_fixtures")


class GetMetDataTests(TestCase):

    @responses.activate
    def test_gets_correct_data_for_uk_max_temp(self):
        with open(path.join(FIXTURES_DIR, "uk_max_temp.txt")) as data:
            responses.add(
                responses.GET,
                "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/datasets/Tmax/date/UK.txt",
                body=data.read(),
                status=200)
        expected_number = 108*12-2 # Number of years times number of months minus months not yet recorded.
        expected_sample = {
            DataPoint(Region.UK, 1910, Month.JAN, ValueType.MAX_TEMP, 5.4),
            DataPoint(Region.UK, 1950, Month.MAY, ValueType.MAX_TEMP, 14.3),
            DataPoint(Region.UK, 1988, Month.NOV, ValueType.MAX_TEMP, 8.4),
            DataPoint(Region.UK, 2017, Month.OCT, ValueType.MAX_TEMP, 14.3)}

        returned = get_met_data(Region.UK, ValueType.MAX_TEMP)

        self.assertEqual(len(returned), expected_number)
        self.assertTrue(expected_sample.issubset(returned))

    @responses.activate
    def test_gets_correct_data_for_scotish_sunshine(self):
        with open(path.join(FIXTURES_DIR, "scotland_sunshine.txt")) as data:
            responses.add(
                responses.GET,
                "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/datasets/Sunshine/date/Scotland.txt",
                body=data.read(),
                status=200)
        expected_number = 89*12-2 # Number of years times number of months minus months not yet recorded.
        expected_sample = {
            DataPoint(Region.SCOTLAND, 1929, Month.JAN, ValueType.SUNSHINE, 39.0),
            DataPoint(Region.SCOTLAND, 1945, Month.MAY, ValueType.SUNSHINE, 158.7),
            DataPoint(Region.SCOTLAND, 1987, Month.OCT, ValueType.SUNSHINE, 75.2),
            DataPoint(Region.SCOTLAND, 2017, Month.OCT, ValueType.SUNSHINE, 56.5)}

        returned = get_met_data(Region.SCOTLAND, ValueType.SUNSHINE)

        self.assertEqual(len(returned), expected_number)
        self.assertTrue(expected_sample.issubset(returned))
