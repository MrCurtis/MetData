from unittest.mock import patch
from django.test import TestCase, Client
from historical_data.met_data_getter import ValueType, Region

class TimeSeriesViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    @patch("historical_data.views.get_time_series")
    def test_success(self, mock_get_time_series):
        mock_get_time_series.return_value = {"key": 123}
        response = self.client.get("/time-series/mintemp/scotland-england")

        self.assertEqual(response.status_code, 200)

    @patch("historical_data.views.get_time_series")
    def test_calls_get_time_series_with_correct_arguments(self, mock_get_time_series):
        mock_get_time_series.return_value = {"key": 123}
        response = self.client.get("/time-series/maxtemp/scotland-england")

        mock_get_time_series.assert_called_with(ValueType.MAX_TEMP, {Region.SCOTLAND, Region.ENGLAND})

    @patch("historical_data.views.get_time_series")
    def test_returns_json_response(self, mock_get_time_series):
        mock_get_time_series.return_value = {"key": 123}
        response = self.client.get("/time-series/maxtemp/scotland-england")

        self.assertEqual(response.content, b"{\"key\": 123}")

    @patch("historical_data.views.get_time_series")
    def test_returns_404_if_value_type_misformed(self, mock_get_time_series):
        mock_get_time_series.return_value = {"key": 123}
        response = self.client.get("/time-series/temax/scotland-england")

        self.assertEqual(response.status_code, 404)

    @patch("historical_data.views.get_time_series")
    def test_returns_404_if_regions_misformed(self, mock_get_time_series):
        mock_get_time_series.return_value = {"key": 123}
        response = self.client.get("/time-series/tempmax/scotnd-england")

        self.assertEqual(response.status_code, 404)
