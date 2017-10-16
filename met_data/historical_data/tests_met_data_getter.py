from unittest import TestCase, main
from unittest import skip

from historical_data.met_data_getter import get_raw_data, remove_blurb, get_data, get_met_data
from historical_data.met_data_getter import DataPoint, Month, Region, ValueType

class GetTextTest(TestCase):

    def test_returns_correct_text(self):
        url = "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/datasets/Tmax/date/UK.txt"

        returned = get_raw_data(url)

        self.assertEqual("UK Maximum Temperature", returned[:len("UK Maximum Temperature")])

class RemoveBlurbTest(TestCase):

    def test_removes_blurb_from_top_of_file(self):
        url = "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/datasets/Tmax/date/UK.txt"
        input_text = get_raw_data(url)

        returned = remove_blurb(input_text)

        self.assertEqual(
            returned.splitlines()[0],
            "Year    JAN    FEB    MAR    APR    MAY    JUN    JUL    AUG    SEP    OCT    NOV    DEC     WIN    SPR    SUM    AUT     ANN")

    def test_adds_X_to_last_line_to_represent_missing_data(self):
        url = "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/datasets/Tmax/date/UK.txt"
        input_text = get_raw_data(url)

        returned = remove_blurb(input_text)

        expected_last_line = "2017    6.7    7.9   10.9   12.2   16.8   18.4   19.3   18.5   16.1     X      X      X     7.85  13.29  18.75"

        self.assertEqual(returned.splitlines()[-1], expected_last_line)


class GetDataTests(TestCase):

    def test_returns_correct_number_of_elements(self):
        expected_number = 108*12-3 # Number of years times number of months minus months not yet recorded.
        url = "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/datasets/Tmax/date/UK.txt"
        string_io = get_raw_data(url)
        formatted_string_io = remove_blurb(string_io)

        returned = get_data(formatted_string_io)

        self.assertEqual(len(returned), expected_number)

    def test_sample_of_entries_correct(self):
        expected_sample = {
            DataPoint(Region.UK, 1910, Month.JAN, ValueType.MAX_TEMP, 5.4),
            DataPoint(Region.UK, 1950, Month.MAY, ValueType.MAX_TEMP, 14.3),
            DataPoint(Region.UK, 1988, Month.NOV, ValueType.MAX_TEMP, 8.4),
            DataPoint(Region.UK, 2017, Month.SEP, ValueType.MAX_TEMP, 16.1)}
        # print(
            # {dp for dp in expected_sample if dp.year == 1950}        
        # )
        url = "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/datasets/Tmax/date/UK.txt"
        string_io = get_raw_data(url)
        formatted_string_io = remove_blurb(string_io)

        returned = get_data(formatted_string_io)

        self.assertIn(DataPoint(Region.UK, 1910, Month.JAN, ValueType.MAX_TEMP, 5.4), returned)
        self.assertIn(DataPoint(Region.UK, 1950, Month.MAY, ValueType.MAX_TEMP, 14.3), returned)
        self.assertIn(DataPoint(Region.UK, 1988, Month.NOV, ValueType.MAX_TEMP, 8.4), returned)
        self.assertTrue(expected_sample.issubset(returned))


class GetMetDataTests(TestCase):

    def test_gets_correct_data_for_uk_max_temp(self):
        expected_number = 108*12-3 # Number of years times number of months minus months not yet recorded.
        expected_sample = {
            DataPoint(Region.UK, 1910, Month.JAN, ValueType.MAX_TEMP, 5.4),
            DataPoint(Region.UK, 1950, Month.MAY, ValueType.MAX_TEMP, 14.3),
            DataPoint(Region.UK, 1988, Month.NOV, ValueType.MAX_TEMP, 8.4),
            DataPoint(Region.UK, 2017, Month.SEP, ValueType.MAX_TEMP, 16.1)}

        returned = get_met_data(Region.UK, ValueType.MAX_TEMP)

        self.assertEqual(len(returned), expected_number)
        self.assertTrue(expected_sample.issubset(returned))

    def test_gets_correct_data_for_scotish_sunshine(self):
        expected_number = 89*12-3 # Number of years times number of months minus months not yet recorded.
        expected_sample = {
            DataPoint(Region.SCOTLAND, 1929, Month.JAN, ValueType.SUNSHINE, 39.0),
            DataPoint(Region.SCOTLAND, 1945, Month.MAY, ValueType.SUNSHINE, 158.7),
            DataPoint(Region.SCOTLAND, 1987, Month.OCT, ValueType.SUNSHINE, 75.2),
            DataPoint(Region.SCOTLAND, 2017, Month.SEP, ValueType.SUNSHINE, 95.4)}

        returned = get_met_data(Region.SCOTLAND, ValueType.SUNSHINE)

        self.assertEqual(len(returned), expected_number)
        self.assertTrue(expected_sample.issubset(returned))

if __name__ == '__main__':
    main()
