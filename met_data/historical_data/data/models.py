from django.db import models
from django.core.validators import MinLengthValidator

from historical_data.data.met_data_getter import Region, Month, ValueType

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
