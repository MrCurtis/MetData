from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from django.template import loader

from historical_data.data import (
    get_time_series,
    DataPoint,
    Month,
    Region,
    ValueType)

def index(request):
    template = loader.get_template("historical_data/index.html")
    return HttpResponse(template.render({}, request))

def time_series(request, value_type_string, regions_string):
    try:
        value_type = _get_value_type(value_type_string)
        regions = _get_regions(regions_string)
    except KeyError:
        return HttpResponseNotFound()
    time_series = get_time_series(value_type, regions)
    return JsonResponse(time_series)

def _get_value_type(value_type_string):
    string_value_mapper = {
        "maxtemp": ValueType.MAX_TEMP,
        "mintemp": ValueType.MIN_TEMP,
        "meantemp": ValueType.MEAN_TEMP,
        "sunshine": ValueType.SUNSHINE,
        "rainfall": ValueType.RAINFALL}
    return string_value_mapper[value_type_string]

def _get_regions(regions_string):
    string_region_mapper = {
        "uk": Region.UK,
        "england": Region.ENGLAND,
        "scotland": Region.SCOTLAND,
        "wales": Region.WALES}
    return { string_region_mapper[s] for s in regions_string.split("-") }
