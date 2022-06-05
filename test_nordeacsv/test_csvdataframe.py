import itertools

import pytest
import numpy as np
from dateutil.parser import parser

from app.nordeacsv import CsvDataFrame, CsvFileOperator


@pytest.fixture
def headers():
    return ["Belopp", "Namn"]


@pytest.fixture
def content():
    return [["-47333", "SKATTEVERKET"],
            ["-7962", "SKATTEVERKET"],
            ["-246263", "GARANTITAK I KUMLA AB"],
            ["-4.2", "PRIS ENL SPEC"],
            ["250000", "FÄNSBODA AB"],
            ["50000", "FÄNSBODA AB"],
            ["-7962", "SKATTEVERKET"],
            ["-11.9", "PRIS ENL SPEC"],
            ["-15188", "JA:S BILSERVICE"]]


@pytest.fixture
def datatypes():
    return ["float", "str"]


def test_slicing_content(content):
    output = [list(x) for x in zip(*content)]
    assert output is not None


def test_bootstrap():
    frame = CsvDataFrame.bootstrap(headers, content, datatypes)
    assert frame is not None


class nested_iterator(object):
    def __init__(self, nested_list=[[]]):
        self.res = []
        self.index = 0

        # flatten the list
        def get_val(nested_list):
            for item in nested_list:
                if isinstance(item, str):
                    self.res.append(item)
                else:
                    self.get_val(item)

        self.get_val(nested_list)

    def next(self, ):
        self.index += 1
        return self.res[self.index - 1]

    def hasNext(self):
        if self.index == len(self.res):
            return False
        return True


def test_groupby_header(headers, content, datatypes):
    # frame = CsvDataFrame.bootstrap(header, content)
    # Mapping of datapoints - on demand
    def convert_datatype(datatype, datapoint):
        match datatype:
            case "float":
                return float(datapoint)
            case "int":
                return int(datapoint)
            case "datetime":
                return parser.parse(datapoint)
            case _:
                return str(datapoint)

    key_name = "Namn"
    # sort by "Namn"
    index = headers.index(key_name)
    sorted_by_header = sorted(content, key=lambda x: x[index])
    group_by_header = {}

    # create iterator
    it = iter(sorted_by_header)
    for k, g in itertools.groupby(it, lambda x: x[index]):
        # --- solution 1 ---
        val = 0
        for l in list(g):
            dt_index = 0
            for dt in datatypes:
                if dt_index is not index:
                    tmp = convert_datatype(dt, l[dt_index])
                    val = val + tmp
                dt_index += 1

        group_by_header[k] = val
        # --- end solution 1 ---

    assert len(group_by_header) > 0


def test_groupby_header_2(headers, content, datatypes):
    key_name = "Namn"
    # sort by "Namn"
    key_index = headers.index(key_name)
    sorted_by_header = sorted(content, key=lambda x: x[key_index])
    group_by_header = {}

    # create iterator
    it = iter(sorted_by_header)
    for k, g in itertools.groupby(it, lambda x: x[key_index]):
        def sum_of_nums(column, dt, i):
            if dt[i] == "float":
                tmp = [float(s) for s in column]
                yield sum(tmp)
            if dt[i] == "int":
                tmp = [int(s) for s in column]
                yield sum(tmp)
            else:
                yield "NA"

        def generate_sum(group):
            index = 0
            for c in zip(*list(group)):
                yield sum_of_nums(c, datatypes, index)
                index += 1

        group_by_header.setdefault(k, [])
        for j in generate_sum(g):
            group_by_header[k].append(next(j))

    assert group_by_header["FÄNSBODA AB"][0] == 300000


def test_groupby_header_3(headers, content, datatypes):
    frame = CsvDataFrame.bootstrap(headers, content, datatypes)
    group_by_header = frame.group_by_header("Namn")
    assert group_by_header["FÄNSBODA AB"][0] == 300000


