import os
import tempfile
import time

from src.nordeacsv.nordeacsv import CsvFileOperator
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


@pytest.fixture
def resources_test_csv():
    cwd = os.getcwd()
    fullpath = os.path.join(cwd, 'resources', 'test.csv')
    return fullpath


@pytest.fixture
def resources_not_here_csv():
    cwd = os.getcwd()
    fullpath = os.path.join(cwd, 'resources', 'not_here.csv')
    return fullpath


@pytest.fixture
def resources_test_write_csv():
    cwd = os.getcwd()
    fullpath = os.path.join(cwd, 'test_write.csv')
    return fullpath


@pytest.fixture
def resources_cash_flow_csv():
    cwd = os.getcwd()
    fullpath = os.path.join(cwd, 'cash_flow.csv')
    return fullpath


@pytest.fixture
def cwd():
    return os.getcwd()


@pytest.fixture(autouse=True)
def remove_test_write_csv(resources_test_write_csv):
    clear_files(resources_test_write_csv)
    # clear_files(r"C:\Users\Olof\PycharmProjects\NordeaCsv\test_nordeacsv\test_write.csv")


@pytest.fixture(autouse=True)
def remove_cash_flow_csv(resources_test_write_csv):
    clear_files(resources_test_write_csv)
    # clear_files(r"C:\Users\Olof\PycharmProjects\NordeaCsv\test_nordeacsv\cash_flow.csv")


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
def csvfileoperator(test_datatypes, resources_test_csv):
    return CsvFileOperator.bootstrap(resources_test_csv, test_datatypes)


@pytest.fixture
def test_bootstrap(test_datatypes, resources_test_csv):
    op = CsvFileOperator.bootstrap(resources_test_csv, test_datatypes)
    assert type(op) is CsvFileOperator


def test_validate(csvfileoperator):
    item = ''
    datatype = "float"
    val = csvfileoperator.__validate__(item, datatype)
    assert type(val) is float


def test_gen_new_csv(csvfileoperator):
    f = csvfileoperator.gen_new_csv("new_empty.csv")
    assert len(f) > 0


def test_delete_old_csv(csvfileoperator, resources_not_here_csv):
    csvfileoperator.delete_old_csv(resources_not_here_csv)
    assert hasattr(resources_not_here_csv, 'delete') is False


def test_delete_old_csv_2(csvfileoperator):
    with tempfile.TemporaryDirectory() as csv_dir:
        csv_file = os.path.join(str(csv_dir), 'HelloWorld.csv')
        with open(csv_file, 'w', encoding="utf-8") as f:
            f.write('Hello World')

        csvfileoperator.delete_old_csv(csv_file)
    assert os.path.exists(csv_file) is False


def test_write_output_to_csv(csvfileoperator, resources_test_write_csv):
    # csv_file = r"C:\Users\Olof\PycharmProjects\NordeaCsv\test_nordeacsv\test_write.csv"
    csvfileoperator.frame.output.content = [["xxx", "aaa"], ["yyy", "bbb"]]
    csvfileoperator.write_output_to_csv(resources_test_write_csv)
    assert os.path.exists(resources_test_write_csv)


def test_write_output_to_csv_2(csvfileoperator, resources_test_write_csv):
    # csv_file = r"C:\Users\Olof\PycharmProjects\NordeaCsv\test_nordeacsv\test_write.csv"
    csvfileoperator.frame.output.headers = ["header1", "header2"]
    csvfileoperator.frame.output.content = [["xxx", "aaa"], ["yyy", "bbb"]]
    csvfileoperator.write_output_to_csv(resources_test_write_csv)
    assert os.path.exists(resources_test_write_csv)


# def test_to_cash_flow_csv(headers, content, datatypes):
def test_to_cash_flow_csv(csvfileoperator, content, headers, datatypes, resources_cash_flow_csv):
    csvfileoperator.frame.content = content
    csvfileoperator.frame.headers = headers
    csvfileoperator.frame.datatypes = datatypes
    # designated_file = r"C:\Users\Olof\PycharmProjects\NordeaCsv\test_nordeacsv\cash_flow.csv"
    csvfileoperator.to_cash_flow_csv("Namn", resources_cash_flow_csv)
    file_stat = os.stat(resources_cash_flow_csv)
    size = file_stat.st_size
    assert os.path.exists(resources_cash_flow_csv) and size > 0
