# 1 search headers.txt
# 2 if found: ask if the user wants to stick with pre-defined headers
# 3 if not: go to step 4
# 3 if not go to step
# 4 find headers in file
# 5 rely on the user to know that the first row are headers
# 6 suggest "str" and press enter or change to "float" or "int"
# 7 store result in headers.txt
# 8 format: name, headers
# 9 add header definition
import argparse
import errno
import importlib.abc
import os
import re
from abc import ABC
from typing import IO, Iterator
from contextlib import contextmanager
import resources

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources


class Resource:
    @classmethod
    def read(cls, path):
        try:
            # validate path
            os.stat(path)
            txt = pkg_resources.read_text(resources, path, encoding='utf-8')
            return txt
        except FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path) as ex:
            print(ex)

    @classmethod
    def write(cls, path, text, mode):
        try:
            # validate path
            os.stat(path)
            # write to resource file
            with open(path, encoding='utf-8', mode=mode) as f:
                f.write(text)
        except FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path) as ex:
            print(ex)


# class ReaderException(Exception):
#     """ Exception when reading a resource file """


# class Reader(importlib.abc.TraversableResources, ABC):
#
#     def __init__(self, mode: str):
#         self.file: IO = None
#         self.mode = mode
#
#     @classmethod
#     def create(cls, mode: str):
#         return Reader(mode)
#
#     def open_resource(self, resource: str) -> IO[bytes]:
#         try:
#             # get full path
#             path = self.resource_path(resource)
#             # validate path
#             os.stat(path)
#             # open file in read mode
#             self.file = open(path, self.mode)
#             return self.file
#         except FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path) as ex:
#             print(ex)
#         except IOError as ex:
#             print(ex)
#         except Exception as e:
#             print(e)
#
#     def resource_path(self, resource: str) -> str:
#         path = os.path.join(os.getcwd(), r"resources", resource)
#         return path
#
#     def is_resource(self, name: str) -> bool:
#         if name == "header.txt":
#             return True
#         else:
#             return False
#
#     def contents(self) -> Iterator[str]:
#         return "Not implemented"
#
#     # reads all the information in the reader.txt file
#     # get resource path
#     @contextmanager
#     def readable_file(self, resource: str) -> IO:
#         file = self.open_resource(resource)
#         try:
#             yield file
#         finally:
#             file.close()


class StorageUnit:
    def __init__(self, name):
        self.unit = {}
        self.name = name

    def name(self):
        return self.name

    def add(self, key: str, value: str):
        self.unit[key] = value

    def get_datatype(self, key: str) -> str:
        return self.unit[key]

    def all_headers(self) -> []:
        return self.unit.keys()


class DataTypeStorageException(Exception):
    """ Exception raised by StorageUnit name not found """


class DataTypeStorage:
    list_of_units = []

    @classmethod
    def _add(cls, unit: StorageUnit):
        if not cls.find_unit_by_csv_name(unit.name):
            cls.list_of_units.append(unit)

    @classmethod
    def create_unit_from_csv_name(cls, name) -> StorageUnit:
        try:
            if name is None:
                raise DataTypeStorageException
            # create new unit
            unit = StorageUnit(name)
            # add unit to storage
            cls._add(unit)
            # as a check, return the unit from the list
            return cls.find_unit_by_csv_name(unit.name)
        except DataTypeStorageException as ex:
            print(ex)

    @classmethod
    def find_unit_by_csv_name(cls, name):
        try:
            for unit in cls.list_of_units:
                if unit.name == name:
                    return unit
        except DataTypeStorageException("Unit does not exist") as ex:
            print(ex)


def get_resource_reading(resource: str, storage: DataTypeStorage, path_to_resources: str = None):
    """
    :param resource: file name
    :type resource: str
    :param storage: stored information in textfile header.txt about datatype mapping
    :type storage: DataTypeStorage
    :param path_to_resources: path to resource in the resource directory
    :type path_to_resources: str
    :return all text in file
    """
    # reader = Reader.create('r')
    # if reader.is_resource(resource) is False and path_to_resources is None:
    #     raise ReaderException

    # with reader.readable_file(resource) as f:
    with Resource.read(path_to_resources) as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            if "---" in lines[i]:
                i += 1
                if "# NAME:" in lines[i]:
                    # create new unit
                    i += 1
                    name = lines[i].replace('# ', '').replace('\n', '')
                    unit = storage.create_unit_from_csv_name(name)
                    i += 1
                    if "# HEADERS:" in lines[i]:
                        i += 1
                        while i < len(lines) and re.search('\\w+:\\w+', lines[i], flags=re.IGNORECASE) is not None:
                            cleaned_data = lines[i].replace('# ', '').replace('\n', '')
                            header, datatype = cleaned_data.split(':')
                            unit.add(header, datatype)
                            i += 1
            else:
                i += 1


class CommandPromptActionsException(Exception):
    """ Exception raised when trying to map headers and datatypes """


class CommandPromptActions:
    def __init__(self, resource):
        self.parser = None
        self.file = None
        self.datatypes = {}
        self.resource = resource

    @classmethod
    def create(cls, resource: str):
        return CommandPromptActions(resource)

    def start(self):
        self.parser = argparse.ArgumentParser(
            description="Convert CSV files from www.nordea.com into new standard CSV format")

    def set_csv(self):
        self.parser.add_argument('-f', '--file', required=True, type=str, help='Path to input file')
        args = self.parser.parse_args()
        self.file = os.path.abspath(args.file)

    def write_to_resource_file(self, header: str, datatype: str):
        # open the file in append mode to begin writing at EOF
        text = header.join(':').join(datatype).join('\n')
        Resource.write(self.file, text, 'a')

        # writer = Reader.create('a')
        # with writer.readable_file(self.resource) as w:
        #     w.write(header.join(':').join(datatype).join('\n'))

    def find_headers_in_csv(self) -> {int, list}:
        with open(self.file) as f:
            line = f.read()

        splitlines = line.splitlines()
        if len(splitlines) > 0:
            res = splitlines[0].split(';')
            n = len(res)
            return n, res
        return None

    def define_datatypes(self, column_names):
        i = 2
        while 0 < i:
            if i == 2:
                print("No datatypes were found in the configuration file. /"
                      "Would you like to set a new configuration for this .csv? (Y/N)")
                res = input()

            else:
                res = input("Would you like to set a new configuration for this .csv? (Y/N)")
            if res == 'Y' or res == 'y':
                for h in column_names:
                    print(h + ': str? ')
                    tmp = input()
                    if tmp == "":
                        self.datatypes[h] = "str"
                    elif tmp in ["float", "int", "str"]:
                        self.datatypes[h] = tmp
                    else:
                        raise CommandPromptActionsException("Datatype does not exist")
                    self.write_to_resource_file(h, self.datatypes[h])
                break
            if res == 'N' or res == 'y':
                break
            else:
                print("Wrong key. You have another {i} attempts.", i)
            i -= 1

    def set_datatypes(self) -> dict:
        (size, column_names) = self.find_headers_in_csv()
        if column_names is None:
            column_names = ["col" + str(i) for i in range(size)]
        self.define_datatypes(column_names)

        return self.datatypes

    def get_datatypes(self) -> dict:
        return self.datatypes

    def get_filepath(self) -> str:
        return self.file

    def print(self, string: str, /):
        print(string)

    def stop(self):
        input("New file has been generated in the root folder. Press Enter to exit ...")
        # Successful termination
