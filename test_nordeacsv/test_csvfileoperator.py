import os
import tempfile
import time

from app.nordeacsv import CsvFileOperator
import pytest
from pathlib import Path


def get_tests():
    return Path.home() / "."


# @pytest.fixture
def clear_files(file: str):
    try:
        # dont try files we cannot find
        if os.path.isfile(file):
            os.remove(file)
            print(file + " removed\n")
    except FileNotFoundError(file + " not found\n") as ex:
        pass


@pytest.fixture(autouse=True)
def remove_test_write_csv():
    clear_files(r"C:\Users\Olof\PycharmProjects\NordeaCsv\test_nordeacsv\test_write.csv")


@pytest.fixture(autouse=True)
def remove_cash_flow_csv():
    clear_files(r"C:\Users\Olof\PycharmProjects\NordeaCsv\test_nordeacsv\cash_flow.csv")


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
def test_datatypes():
    # change first datatype to be "datetime". Currently, there is no support
    return ["str", "float", "str", "str", "str", "str", "str", "str", "float", "str"]


@pytest.fixture
def csvfileoperator(test_datatypes):
    return CsvFileOperator.bootstrap(r"C:\Users\Olof\PycharmProjects\NordeaCsv\test_nordeacsv\resources\test.csv", \
                                     test_datatypes)


def test_bootstrap(test_datatypes):
    op = CsvFileOperator.bootstrap(r"C:\Users\Olof\PycharmProjects\NordeaCsv\test_nordeacsv\resources\test.csv", \
                                   test_datatypes)
    assert type(op) is CsvFileOperator


def test_validate(csvfileoperator):
    item = ''
    datatype = "float"
    val = csvfileoperator.__validate__(item, datatype)
    assert type(val) is float


def test_gen_new_csv(csvfileoperator):
    f = csvfileoperator.gen_new_csv("new_empty.csv")
    assert len(f) > 0


def test_delete_old_csv(csvfileoperator):
    csv_file = r"C:\Users\Olof\PycharmProjects\NordeaCsv\not_here.csv"
    csvfileoperator.delete_old_csv(csv_file)
    assert os.path.exists(csv_file) is False


def test_delete_old_csv_2(csvfileoperator):
    with tempfile.NamedTemporaryFile() as csv_file:
        csv_file.write(b'Hello World')
        csvfileoperator.delete_old_csv(csv_file.name)
        assert os.path.exists(csv_file.name) is False


def test_write_output_to_csv(csvfileoperator):
    csv_file = r"C:\Users\Olof\PycharmProjects\NordeaCsv\test_nordeacsv\test_write.csv"
    csvfileoperator.frame.output.content = [["xxx", "aaa"], ["yyy", "bbb"]]
    csvfileoperator.write_output_to_csv(csv_file)
    assert os.path.exists(csv_file)


def test_write_output_to_csv_2(csvfileoperator):
    csv_file = r"C:\Users\Olof\PycharmProjects\NordeaCsv\test_nordeacsv\test_write.csv"
    csvfileoperator.frame.output.headers = ["header1", "header2"]
    csvfileoperator.frame.output.content = [["xxx", "aaa"], ["yyy", "bbb"]]
    csvfileoperator.write_output_to_csv(csv_file)
    assert os.path.exists(csv_file)


# def test_to_cash_flow_csv(headers, content, datatypes):
def test_to_cash_flow_csv(csvfileoperator, content, headers, datatypes):
    csvfileoperator.frame.content = content
    csvfileoperator.frame.headers = headers
    csvfileoperator.frame.datatypes = datatypes
    designated_file = r"C:\Users\Olof\PycharmProjects\NordeaCsv\test_nordeacsv\cash_flow.csv"
    csvfileoperator.to_cash_flow_csv("Namn", designated_file)
    file_stat = os.stat(designated_file)
    size = file_stat.st_size
    assert os.path.exists(designated_file) and size > 0
