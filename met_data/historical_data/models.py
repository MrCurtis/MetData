from collections import defaultdict
from django.db import models
from django.core.validators import MinLengthValidator

from historical_data.met_data_getter import Region, Month, ValueType

region_mapper = {
    Region.UK: "uk",
    Region.ENGLAND: "england",
    Region.SCOTLAND: "scotland",
    Region.WALES: "wales"}

month_mapper = {
    Month.JAN: 1,
    Month.FEB: 2,
    Month.MAR: 3,
    Month.APR: 4,
    Month.MAY: 5,
    Month.JUN: 6,
    Month.JUL: 7,
    Month.AUG: 8,
    Month.SEP: 9,
    Month.OCT: 10,
    Month.NOV: 11,
    Month.DEC: 12}

value_type_mapper = {
    ValueType.MAX_TEMP: "max_temp",
    ValueType.MIN_TEMP: "min_temp",
    ValueType.MEAN_TEMP: "mean_temp",
    ValueType.SUNSHINE: "sunshine",
    ValueType.RAINFALL: "rainfall"}


def get_time_series(value_type, regions):
    """Gets time series data.

    Args:
      value_type: A valid ValueType enum.
      regions: An iterable of Region enums.

    Returns:
      A dictionary representing the time-series for the given value type
      and regions. The dictionary will have the following form:
        {
          "value_type": "<value_type>"
          "labels": ["<date_1>", "<date_2>",...,"<date_n>"],
          "series": [{
            "name": "<region_name_1>",
            "data": [<value_1>, <value_2>,...,<value_n>]
          },{
            "name": "<region_name_2>",
            "data": [<value_1>, <value_2>,...,<value_n>]
          },{
            ...
          },{
            "name": "<region_name_m>",
            "data": [<value_1>, <value_2>,...,<value_n>]
          }]}
    """
    value_type_to_title_mapper = {
        ValueType.MAX_TEMP: "Maximum Temperature",
        ValueType.MIN_TEMP: "Minimum Temperature",
        ValueType.MEAN_TEMP: "Mean Temperature",
        ValueType.SUNSHINE: "Sunshine",
        ValueType.RAINFALL: "Rainfall"}

    month_to_lable_string_mapper = {
        1: "JAN",
        2: "FEB",
        3: "MAR",
        4: "APR",
        5: "MAY",
        6: "JUN",
        7: "JUL",
        8: "AUG",
        9: "SEP",
        10: "OCT",
        11: "NOV",
        12: "DEC"}

    region_to_name_mapper = {
        Region.UK: "UK",
        Region.ENGLAND: "England",
        Region.SCOTLAND: "Scotland",
        Region.WALES: "Wales"}

    entries = HistoricalData.objects\
        .filter(region__in=[region_mapper[region] for region in regions])\
        .filter(value_type=value_type_mapper[value_type])

    potential_max = potential_min = (entries[0].year, entries[0].month)
    dd = defaultdict(lambda: defaultdict(lambda: None))
    for entry in entries:
        potential_min = min((entry.year, entry.month), potential_min)
        potential_max = max((entry.year, entry.month), potential_max)
        dd[(entry.year, entry.month)][entry.region] = entry.value

    year_month_tuples = _create_list_of_tuples(potential_min, potential_max)

    labels = [str(year)+"-"+month_to_lable_string_mapper[month] for year, month in year_month_tuples]

    series = []
    for region in regions:
        d = {
            "name": region_to_name_mapper[region],
            "data": [dd[t][region_mapper[region]] for t in year_month_tuples]}
        series.append(d)

    return {
        "value_type": value_type_to_title_mapper[value_type],
        "labels": labels,
        "series": series}
    

def _create_list_of_tuples(smallest, largest):
    l = []
    curr = smallest
    while curr <= largest:
        l.append(curr)
        if curr[1] >= 12:
            curr = (curr[0]+1, 1)
        else:
            curr = (curr[0], curr[1]+1)
    return l


def create_or_update_data_point(
        region,
        year,
        month,
        value_type,
        value):
    """Stores a datapoint to the database.

    Args:
      region: A valid region as specified by a Region Enum.
      year: A year as specified by ant int.
      month: A valid month as specified by a Month Enum.
      value_type: A valid value_type as specified by a ValueType Enum.
      value:  float.

    Raises:
      ValueError if invalid arguments given.
    """
    try:
        region_key = region_mapper[region]
    except KeyError:
        raise ValueError(
                "Argument: {} is not a valid region enum".format(region))
    try:
        month_key = month_mapper[month]
    except KeyError:
        raise ValueError(
                "Argument: {} is not a valid month enum".format(month))
    try:
        value_type_key = value_type_mapper[value_type]
    except KeyError:
        raise ValueError(
                "Argument: {} is not a valid value_type enum".format(value_type))

    try:
        entry = HistoricalData.objects.get(
            region=region_key,
            year=year,
            month=month_key,
            value_type=value_type_key)
    except HistoricalData.DoesNotExist:
        entry = HistoricalData.objects.create(
            region=region_key,
            year=year,
            month=month_key,
            value_type=value_type_key,
            value=value)
    else:
        entry.value=value
    entry.save()


class HistoricalData(models.Model):
    """Models a single data point.

    Fields:
      year: Integer representing a year.
      month: Integer representing the month of the year. (January is 1, Febuary
        is 2, etc.)
      region: Integer representing a region - as returned by the
        region-mapper.
      value_type: Integer representing a value_type - as returned by the
        value-type-mapper 
      value: Float.
    """
    _non_empty_string = MinLengthValidator(1)
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    region = models.CharField(max_length=20, validators=[_non_empty_string])
    value_type = models.CharField(max_length=20, validators=[_non_empty_string])
    value = models.FloatField()

    def save(self, *args, **kwargs):
        self.clean_fields()
        super().save(*args, **kwargs)
