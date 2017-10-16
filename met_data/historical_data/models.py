from django.db import models

from historical_data.met_data_getter import Region, Month, ValueType

region_mapper = {
    Region.UK: 1,
    Region.ENGLAND: 2,
    Region.SCOTLAND: 3,
    Region.WALES: 4}

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

    entry, _ = HistoricalData.objects.get_or_create(
        region=region_key,
        year=year,
        month=month_key)
    setattr(entry, value_type_key, value)
    entry.save()


class HistoricalData(models.Model):
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    region = models.PositiveSmallIntegerField()
    max_temp = models.FloatField(null=True)
    min_temp = models.FloatField(null=True)
    mean_temp = models.FloatField(null=True)
    sunshine = models.FloatField(null=True)
    rainfall = models.FloatField(null=True)
