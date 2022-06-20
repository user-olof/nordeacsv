import itertools
import pytest
from src.nordeacsv.nordeacsv import CsvDataFrame


@pytest.fixture
def headers():
    return ["Belopp", "Namn"]


@pytest.fixture
def content():
    return [["-47333", "aaa"],
            ["-7962", "aaa"],
            ["-246263", "bbb"],
            ["-4.2", "ccc"],
            ["250000", "ddd"],
            ["50000", "ddd"],
            ["-7962", "aaa"],
            ["-11.9", "eee"],
            ["-15188", "fff"]]


@pytest.fixture
def datatypes():
    return ["float", "str"]

@pytest.fixture
def csvdataframe(headers, content, datatypes):
    return CsvDataFrame.bootstrap(headers, content, datatypes)

def test_bootstrap(headers, content, datatypes):
    frame = CsvDataFrame.bootstrap(headers, content, datatypes)
    return type(frame) is CsvDataFrame

def test_slicing_content(content):
    output = [list(x) for x in zip(*content)]
    assert output is not None


def test_groupby_header(headers, content, datatypes):
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

    assert group_by_header["ddd"][0] == 300000


def test_groupby_header_2(csvdataframe):
    group_by_header = csvdataframe.group_by_header("Namn")
    assert group_by_header["ddd"][0] == 300000


