import os
import tempfile

from app.nordeacsv import CsvFileOperator
import pytest
from pathlib import Path


def get_tests():
    return Path.home() / "."


@pytest.fixture(autouse=True)
def clear_files():
    try:
        os.remove(r"C:\Users\Olof\PycharmProjects\NordeaCsv\test_write.csv")
        os.remove(r"C:\Users\Olof\PycharmProjects\NordeaCsv\cash_flow.csv")
    except FileNotFoundError:
        print("Test bootstrap complete")
        pass

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

def test_to_base_csv():
    op = CsvFileOperator.bootstrap(r"C:\Users\Olof\PycharmProjects\NordeaCsv\nordea.csv", 1)
    d = op.to_base_csv()
    assert len(d) > 0


def test_gen_new_csv():
    op = CsvFileOperator.bootstrap(r"C:\Users\Olof\PycharmProjects\NordeaCsv\nordea.csv", 1)
    f = op.gen_new_csv()
    assert len(f) > 0


def test_delete_old_csv():
    op = CsvFileOperator.bootstrap(r"C:\Users\Olof\PycharmProjects\NordeaCsv\nordea.csv", 1)
    csv_file = r"C:\Users\Olof\PycharmProjects\NordeaCsv\not_here.csv"
    op.delete_old_csv(csv_file)
    assert os.path.exists(csv_file) is False

def test_delete_old_csv_2():
    with tempfile.NamedTemporaryFile() as csv_file:
        csv_file.write(b'Hello World')
        op = CsvFileOperator.bootstrap(r"C:\Users\Olof\PycharmProjects\NordeaCsv\nordea.csv", 1)
        op.delete_old_csv(csv_file.name)
        assert os.path.exists(csv_file.name) is False


def test_write_csv():
    op = CsvFileOperator.bootstrap(r"C:\Users\Olof\PycharmProjects\NordeaCsv\nordea.csv", 1)
    csv_file = r"C:\Users\Olof\PycharmProjects\NordeaCsv\test_write.csv"
    content = ["xxx", "yyy"]
    op.write_csv(csv_file)
    assert os.path.exists(csv_file)

# def test_to_cash_flow_csv(headers, content, datatypes):
def test_to_cash_flow_csv():
    op = CsvFileOperator.bootstrap(r"C:\Users\Olof\PycharmProjects\NordeaCsv\nordea.csv", 1)
    designated_file = r"C:\Users\Olof\PycharmProjects\NordeaCsv\cash_flow.csv"
    op.to_cash_flow_csv("Namn", designated_file)
    file_stat = os.stat(designated_file)
    size = file_stat.st_size
    assert os.path.exists(designated_file) and size > 0