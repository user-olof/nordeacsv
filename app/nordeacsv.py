import argparse
import datetime

import itertools
from pathlib import Path

import errno
import os
import re

import sys
import numpy
from dateutil import parser

from app.cmd_prompt_actions import CommandPromptActions


class AggDataConversionError(ValueError):
    """ Data conversion error handling """


class Output:
    def __init__(self, columns=None, data=None, /):
        self.headers = columns
        self.content = data
    #
    # def headers(self):
    #     return self.columns
    #
    # def content(self):
    #     return self.data


class CsvDataFrame:
    def __init__(self, headers, content, datatypes, res=Output(), /):
        self.headers = headers
        self.content = content
        self.datatypes = datatypes
        self.output = res

    @classmethod
    def bootstrap(cls, header, content, datatypes=None, /):

        # create the transpose of the content
        # maybe this can be moved to a later stage?
        # t_content = [list(x) for x in zip(*content)]

        return CsvDataFrame(header, content, datatypes)

    # --- NOT USED NOW ---
    def set_default_datatypes(self, file_path: Path):
        # "DEPÅLIKVIDKONTO" "PLUSGIROKONTO"
        # "Bokföringsdag, Belopp ,Avsändare,Mottagare,Namn,Rubrik,Meddelande,Egna anteckningar,Saldo,Valuta"
        # "str, float, str, str, str, str, str, str, float, str"
        # if filename = use regex exp
        if re.match("DEPÅLIKVIDKONTO*", file_path.name) is not None:
            self.datatypes = ["str", "float", "str", "str", "str", "str", "str", "str", "float", "str"]
        elif re.match("PLUSGIROKONTO*", file_path.name) is not None:
            self.datatypes = ["str", "float", "str", "str", "str", "str", "str", "str", "float", "str"]
        elif re.match("nordea*", file_path.name) is not None:
            self.datatypes = ["str", "float", "str", "str", "str", "str", "str", "str", "float", "str"]
        elif self.datatypes is None:
            self.datatypes = ["str"] * len(self.headers)

    def group_by_header(self, key_name, /):
        # key_name = "Namn"
        key_index = self.headers.index(key_name)
        sorted_by_header = sorted(self.content, key=lambda x: x[key_index])
        group_by_header = {}

        # create iterator
        it = iter(sorted_by_header)
        for k, g in itertools.groupby(it, lambda x: x[key_index]):

            def sum_of_nums(column, dt, i):
                try:
                    # if dt[i] != "str":
                    #     tmp = [validate(s, dt[i]) for s in column]
                    #     yield sum(tmp)
                    if dt[i] == "float":
                        tmp = [float(s) for s in column]
                        yield sum(tmp)
                    if dt[i] == "int":
                        tmp = [int(s) for s in column]
                        yield sum(tmp)
                    else:
                        yield "NA"


                except AggDataConversionError as ex:
                    print(ex)

            def generate_sum(group):
                index = 0
                for c in zip(*list(group)):
                    yield sum_of_nums(c, self.datatypes, index)
                    index += 1

            group_by_header.setdefault(k, [])
            for j in generate_sum(g):
                group_by_header[k].append(next(j))

        self.output = Output(group_by_header.keys(), group_by_header.values())

        return group_by_header


class CsvFileOperatorException(Exception):
    """ Exception raised when generating the new csv file """


class CsvFileOperator:
    def __init__(self, file_path: Path, header: [], content: [[]], /):
        self.file_path = file_path
        self.frame = CsvDataFrame.bootstrap(header, content)
        self.status = "LOADED"

    @classmethod
    def bootstrap(cls, file_as_string: str, datatypes: dict, /):
        try:
            os.stat(file_as_string)
        except FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_as_string):
            sys.exit(1)

        file_path = Path(file_as_string)

        # bootstrap CsvDataFrame
        content = []
        with file_path.open() as f:
            try:
                h = f.readline()
                h = re.sub(",", ".", h)
                h = re.sub(";", ",", h)
                headers = h.split(',')
                for line in f.readlines():
                    line = re.sub(",", ".", line)
                    line = re.sub(";", ",", line)
                    # #remove spaces from e.g. " 125.5 "
                    # l = re.sub("\s[0-9]+\s", )
                    line = line.split(',')
                    if isinstance(line, list) is False:
                        raise CsvFileOperatorException("Line split did not execute successfully")

                    # get data types
                    map_items = map(cls.__validate__, line, datatypes)
                    content = list(map_items)
                    if len(content) == 0:
                        raise CsvFileOperatorException("The list of validated data is empty")
                    # content.append(line)
                    # content.append(items)
                    # content = [items]
            except CsvFileOperatorException as ex:
                print(ex)
        return CsvFileOperator(file_path, headers, content)

    @classmethod
    def __validate__(cls, item, datatypes):


        if datatypes == "float":
            validated = (float(item), 0.0)[len(item) == 0]
        elif datatypes == "int":
            validated = (int(item), 0)[len(item) == 0]
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
                print(ex)
                raise ex

    def write_csv(self, designated_file, /):
        try:
            f = open(designated_file, 'w')
        except FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), designated_file) as ex:
            print(ex)
            raise ex
        except OSError as ex:
            print("Could not open file")
            raise ex

        with f:
            f.write(self.frame.headers)
            for line in self.frame.content:
                f.write(line)

        if os.path.isfile(designated_file):
            self.status = "GENERATED"
        else:
            raise CsvFileOperatorException("File has not been generated successfully")

    # def to_base_csv(self):
    #     # generate doc
    #     content = []
    #     with open(self.file_path.absolute()) as f:
    #         for line in f.readlines():
    #             line = re.sub(",", ".", line)
    #             line = re.sub(";", ",", line)
    #             content.append(line)
    #
    #     return content

    def to_cash_flow_csv(self, key_name, designated_file, /):
        # guess the datatypes
        # self.frame.set_default_datatypes(self.file_path)
        self.frame.group_by_header(key_name)
        self.write_output_to_csv(designated_file)

    def write_output_to_csv(self, designated_file, /):
        try:
            f = open(designated_file, 'w')
        except FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), designated_file) as ex:
            print(ex)
            raise ex
        except OSError as ex:
            print("Could not open file")
            raise ex

        with f:
            tmp = ','.join(self.frame.output.headers)
            f.write(tmp)
            for line in self.frame.output.content:
                tmp = ','.join(line)
                f.write(tmp + '\n')

        if os.path.isfile(designated_file):
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            self.status = "OUTPUT_GENERATED_" + current_time
        else:
            raise CsvFileOperatorException("File has not been generated successfully")

        # with open(designated_file, 'w') as f:
        #     tmp = ','.join(self.frame.output.headers)
        #     f.write(tmp)
        #     for line in self.frame.output.content:
        #         tmp = ','.join(line)
        #         f.write(tmp + '\n')
        # except Exception as err:
        #     print("Writing failed: ", err)


def main():
    # parser = argparse.ArgumentParser(description="Convert CSV files from www.nordea.com into new standard CSV format")
    # parser.add_argument('-f', '--file', required=True, type=str, help='Path to input file')
    # args = parser.parse_args()
    actions = CommandPromptActions.create("header.txt")
    actions.start()
    actions.set_csv()
    datatypes = actions.set_datatypes()

    # datatypes = actions.get_datatypes()
    file_as_string = actions.get_filepath()

    op = CsvFileOperator.bootstrap(file_as_string, datatypes)
    csv = op.gen_new_csv("SUCCESS.csv")
    op.delete_old_csv(csv)
    op.write_csv(csv)

    op.to_cash_flow_csv("Namn", csv)

    actions.stop()


if __name__ == '__main__':
    main()
