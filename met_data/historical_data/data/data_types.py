from collections import namedtuple
from enum import Enum


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
