from io import StringIO
from os import linesep

from requests import get 
from pandas import read_csv

from historical_data.data.data_types import (
    DataPoint,
    Month,
    Region,
    ValueType)


def get_met_data(region, value_type):
    """Gets data from the met office website.
    
    Args:
      region: A region enum.
      value_type: A value type enum.

    Returns:
      A set of datapoints.
    """
    region_string = {
        Region.UK: "UK",
        Region.ENGLAND: "England",
        Region.SCOTLAND: "Scotland",
        Region.WALES: "Wales"}
    value_type_string = {
        ValueType.MAX_TEMP: "Tmax",
        ValueType.MIN_TEMP: "Tmin",
        ValueType.MEAN_TEMP: "Tmean",
        ValueType.SUNSHINE: "Sunshine",
        ValueType.RAINFALL: "Rainfall"}

    url = "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/datasets/{vty}/date/{reg}.txt".format(
        vty=value_type_string[value_type],
        reg=region_string[region])

    raw_data = _get_raw_data(url)
    pre_processed_data = _pre_process_data(raw_data)
    return _get_data(pre_processed_data, region, value_type)


def _get_raw_data(url):
    response = get(url)
    response.raise_for_status()
    return response.text


def _pre_process_data(input_text):
    return _replace_missing_entries_with_x(
        _remove_blurb(
            input_text))


def _remove_blurb(input_text):
    string_list = input_text.splitlines()

    empty_line_found=False
    while not empty_line_found:
        if string_list[0].strip() == "":
            empty_line_found = True
        string_list.pop(0)
    
    return linesep.join(string_list)


def _replace_missing_entries_with_x(input_text):
    string_list = input_text.splitlines()

    penultimate_string = string_list[-2]
    ultimate_string_as_list = list(string_list[-1])
    for index, character in enumerate(ultimate_string_as_list):
        if character == " " and penultimate_string[index] == ".":
            ultimate_string_as_list[index] = "X"
    string_list[-1] = "".join(ultimate_string_as_list)
    
    return linesep.join(string_list)


def _get_data(input_text, region=Region.UK, value_type=ValueType.MAX_TEMP):
    
    months = [
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC"]

    data_frame = read_csv(StringIO(input_text), delim_whitespace=True) 
    data_points = set()
    for index in range(len(data_frame)):
        for month in months:
            year = int(data_frame.at[index, "Year"])
            try:
                value = float(data_frame.at[index, month])
            except ValueError:
                pass
            else:
                data_points.add(
                    DataPoint(region, year, Month[month], value_type, value))

    return data_points
