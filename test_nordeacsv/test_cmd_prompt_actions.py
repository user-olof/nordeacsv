import os
import tempfile

import pytest

from app.cmd_prompt_actions import Reader, get_resource_reading, DataTypeStorage, DataTypeStorageException, \
    CommandPromptActions


@pytest.fixture
def resource():
    return "header.txt"


@pytest.fixture
def reader():
    return Reader.create('r')


@pytest.fixture
def storage():
    return DataTypeStorage()


@pytest.fixture
def writer():
    return Reader.create('w')


def test_open_resource(resource, reader):
    file = reader.open_resource(resource)
    assert file is not None


def test_readable_file(resource, reader):
    with reader.readable_file(resource) as f:
        line = f.read()
        assert type(line) is str


# This test checks if there are two identical file names. See header.txt
def test_get_resource_reading(resource, storage):
    try:
        fullpath = os.path.join(os.getcwd(), "resources", "header.txt")
        get_resource_reading(resource, storage, fullpath)
    except DataTypeStorageException as ex:
        print(ex)
    unit = storage.find_unit_by_csv_name("test.csv")
    assert unit.name == "test.csv" and len(storage.list_of_units) == 1


def test_find_headers():
    cwd = os.getcwd()
    fullpath = os.path.join(cwd, 'nordea.csv')
    # fullpath = r'C:\Users\Olof\PycharmProjects\NordeaCsv\nordea.csv'
    actions = CommandPromptActions.create("header.txt")
    actions.file = fullpath
    headers = actions.find_headers()
    assert len(headers) > 0
