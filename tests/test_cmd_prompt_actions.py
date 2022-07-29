import os
import pytest
from src.actions.cmd_prompt_actions import get_resource_reading, DataTypeStorage, DataTypeStorageException, \
    CommandPromptActions, Resource


@pytest.fixture
def resource():
    return "header.txt"


# @pytest.fixture
# def reader():
#     return Reader.create('r')


@pytest.fixture
def storage():
    return DataTypeStorage()


# @pytest.fixture
# def writer():
#     return Reader.create('w')


# def test_open_resource(resource, reader):
#     file = reader.open_resource(resource)
#     assert file is not None


def test_readable_file(resource):
    text = Resource.read(resource)
    assert type(text) is list
    # with reader.readable_file(resource) as f:
    #     line = f.read()
    #     assert type(line) is str


# This test checks if there are two identical file names. See header.txt
def test_get_resource_reading(resource, storage):
    try:
        # fullpath = os.path.join(os.getcwd(), "resources", resource)
        get_resource_reading(resource, storage)
        # get_resource_reading(resource, storage, fullpath)
    except DataTypeStorageException as ex:
        print(ex)
    unit = storage.find_unit_by_csv_name("test.csv")
    assert unit.name == "test.csv" and len(storage.list_of_units) == 1


def test_find_headers(resource):
    cwd = os.getcwd()
    fullpath = os.path.join(cwd, 'resources', 'test.csv')
    # fullpath = r'C:\Users\Olof\PycharmProjects\NordeaCsv\nordea.csv'
    actions = CommandPromptActions.create(resource)
    actions.file = fullpath
    (size, headers) = actions.find_headers_in_csv()
    assert len(headers) > 0 and size > 0


@pytest.mark.skip(reason="OSError: pytest: reading from stdin while output is captured!  Consider using `-s`.")
def test_define_datatypes(resource):
    column_names = ["col1", "col2", "col3"]
    actions = CommandPromptActions.create(resource)
    # mocking creation of full path to resource
    actions.file = r"C:\Users\Olof\PycharmProjects\NordeaCsv\tests\resources\header.txt"
    actions.define_datatypes(column_names)
    assert len(actions.datatypes) == 3
