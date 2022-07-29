import errno
import os
import re
import sys
from pathlib import Path

from src.actions.csv_data_frame import CsvDataFrame
from src.actions.enum_file import FileStatus


class CsvFileOperatorException(Exception):
    """ Exception raised when generating the new csv file """


class CsvFileOperator:
    def __init__(self, file_path: Path, header: [], content: [[]], /):
        self.file_path = file_path
        self.frame = CsvDataFrame.bootstrap(header, content)
        self.status = FileStatus.LOADED

    @classmethod
    def bootstrap(cls, file_as_string: str, datatypes: dict, /):
        try:
            os.stat(file_as_string)
        except FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_as_string):
            sys.exit(1)

        file_path = Path(file_as_string)

        # bootstrap CsvDataFrame
        with file_path.open(encoding='utf-8-sig') as f:
            try:
                h = f.readline()
                h = char_replace(h, ',', '.')
                h = char_replace(h, ';', ',')
                h = char_replace(h, '\n', '')
                headers = h.split(',')
                for line in f.readlines():
                    line = char_replace(line, ',', '.')
                    line = char_replace(line, ';', ',')
                    line = char_replace(line, '\n', '')
                    # #remove spaces from e.g. " 125.5 "
                    # l = re.sub("\s[0-9]+\s", )
                    line = line_split(line, ',')

                    # get data types
                    map_items = map(cls.__validate__, line, datatypes)
                    content = list(map_items)
                    if len(content) == 0:
                        raise CsvFileOperatorException("The list of validated data is empty")
            except CsvFileOperatorException as ex:
                print(ex)
        return CsvFileOperator(file_path, headers, content)

    @classmethod
    def __validate__(cls, item: str, datatype: str):

        if datatype == "float":
            if len(item) == 0:
                validated = 0.0
            else:
                validated = float(item)
        elif datatype == "int":
            if len(item) == 0:
                validated = 0
            else:
                validated = int(item)
        else:
            validated = ''

        return validated

    def gen_new_csv(self, name: str):
        # here we could check the name is valid
        abs_path = str(self.file_path.absolute())
        list = abs_path.split('\\')
        list.pop()
        list.append(name)
        csv_file = "\\".join(list)
        return csv_file

    def delete_old_csv(self, designated_file, /):
        if os.path.isfile(designated_file):
            try:
                os.remove(designated_file)
            except FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), designated_file) as ex:
                raise ex


    def to_cash_flow_csv(self, key_name, designated_file, /):
        self.frame.group_by_header(key_name)
        self.write_output_to_csv(designated_file)


    def write_output_to_csv(self, designated_file, /):
        try:
            f = open(designated_file, 'w')
        except FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), designated_file) as ex:
            raise ex
        except OSError("Could not open file") as ex:
            raise ex

        with f:
            if type(self.frame.output.datatypes) is list:
                if len(self.frame.output.datatypes) > 0:
                    tmp = ','.join(str(e) for e in self.frame.output.datatypes)
                    f.write(tmp + '\n')
            if type(self.frame.output.content) is list:
                for line in self.frame.output.content:
                    if len(line) > 0:
                        tmp = ','.join(str(e) for e in line)
                        f.write(tmp + '\n')

        if os.path.isfile(designated_file):
            self.status = FileStatus.GENERATED
        else:
            self.status = FileStatus.NOT_FOUND
            raise CsvFileOperatorException("File has not been generated successfully")

    def file_status(self) -> str:
        if self.status == FileStatus.LOADED:
            msg = "File information is loaded into the CsvDataFrame"
        elif self.status == FileStatus.GENERATED:
            msg = "New file has been generated in the root folder"
        elif self.status == FileStatus.NOT_FOUND:
            msg = "No new file has been generated"
        return msg


def char_replace(line: str, old_char: str, new_char: str):
    try:
        line = re.sub(old_char, new_char, line)
        return line
    except CsvFileOperatorException("Substituting character: " + old_char + " to: " + new_char + " has failed") as ex:
        raise ex


def line_split(line: str, separator: str):
    try:
        line = line.split(separator)
        if len(line) == 0:
            raise CsvFileOperatorException("Line split generated an empty list")
        return line
    except CsvFileOperatorException("Line split has failed for separator: " + separator) as ex:
        raise ex