from unittest.mock import patch, call
from functools import reduce

from django.test import TestCase
from django.core.management import call_command
from django.utils.six import StringIO

from historical_data.data import Month, DataPoint, Region, ValueType


COMMAND_LOCATION = "historical_data.management.commands.get_data_from_met_office"


class GetDataFromMetOfficeTests(TestCase):

    @patch(COMMAND_LOCATION+".create_or_update_data_point")
    @patch(COMMAND_LOCATION+".get_met_data")
    def test_gets_and_persists_all_datapoints(
            self,
            mock_get_met_data,
            mock_create_or_update_data_point):

        def _mock_get_met_data(region, value_type):
            return frozenset({
                DataPoint(region, 1984, Month.MAY, value_type, 123),
                DataPoint(region, 1985, Month.JUN, value_type, 456)})

        mock_get_met_data.side_effect = _mock_get_met_data

        expected_calls = map(
            lambda x: call(*x),
            reduce(
                lambda x, y: x.union(y),
                {_mock_get_met_data(r, vt) for r in Region for vt in ValueType},
                set()))

        call_command("get_data_from_met_office", stdout=StringIO())

        mock_create_or_update_data_point.assert_has_calls(
            expected_calls,
            any_order=True)

    @patch(COMMAND_LOCATION+".create_or_update_data_point")
    @patch(COMMAND_LOCATION+".get_met_data")
    def test_prints_success_message(
            self,
            mock_get_met_data,
            mock_create_or_update_data_point):
        out = StringIO()
        mock_get_met_data.return_value = \
                {DataPoint(Region.UK, 1984, Month.MAY, ValueType.MAX_TEMP, 123)}

        call_command("get_data_from_met_office", stdout=out)

        self.assertIn("Successfully got Met Office data.", out.getvalue())

