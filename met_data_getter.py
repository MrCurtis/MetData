from io import StringIO
from os import linesep
from collections import namedtuple
from enum import Enum

import numpy
from pandas import read_csv

DataPoint = namedtuple("DataPoint", "region year month value_type value")

class Month(Enum):
    JAN = 1
    FEB = 2
    MAR = 3
    APR = 4
    MAY = 5
    JUN = 6
    JUL = 7
    AUG = 8
    SEP = 9
    OCT = 10
    NOV = 11
    DEC = 12

class Region(Enum):
    UK = 1
    ENGLAND = 2
    SCOTLAND = 3
    WALES = 4

class ValueType(Enum):
    MAX_TEMP = 1
    MIN_TEMP = 2
    MEAN_TEMP = 3
    SUNSHINE = 4
    RAINFALL = 5

from requests import get 
import pandas

def get_raw_data(url):
    """Gets the raw data text file.

    Arg:
      url: The url of the text file.

    Raises:
      HttpError if request is not successful.

    Returns:
      A file-like object containing the text file.
    """
    response = get(url)
    response.raise_for_status()
    return response.text

def remove_blurb(input_text):
    """Strips non-data from file.

    Arg:
      A file like object. 

    Returns:
      A file-like object with: 
        - all lines up to and including the first blank line removed.
        - "X" characters added to represent cells for missing months in the
          final row.
    """
    string_list = input_text.splitlines()

    empty_line_found=False
    while not empty_line_found:
        if string_list[0].strip() == "":
            empty_line_found = True
        string_list.pop(0)

    penultimate_string = string_list[-2]
    ultimate_string_as_list = list(string_list[-1])
    for index, character in enumerate(ultimate_string_as_list):
        if character == " " and penultimate_string[index] == ".":
            ultimate_string_as_list[index] = "X"
    string_list[-1] = "".join(ultimate_string_as_list)
    
    return linesep.join(string_list)

def get_data(input_text, region=Region.UK, value_type=ValueType.MAX_TEMP):
    
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

def get_met_data(region, value_type):
    """Gets data from the met office website.
    
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

    raw_data = get_raw_data(url)
    pre_processed_data = remove_blurb(raw_data)
    return get_data(pre_processed_data, region, value_type)
