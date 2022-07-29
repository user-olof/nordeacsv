import itertools

from src.actions.output import Output


class CsvDataFrame:
    def __init__(self, headers, content, datatypes, res=Output(), /):
        # used for calculations
        self.headers = headers
        self.content = content
        self.datatypes = datatypes
        # used for printing
        self.output = res

    @classmethod
    def bootstrap(cls, header, content, datatypes=None, /):
        # create the transpose of the content
        # maybe this can be moved to a later stage?
        return CsvDataFrame(header, content, datatypes)


    def group_by_header(self, key_name, /):
        key_index = self.headers.index(key_name)
        sorted_by_header = sorted(self.content, key=lambda x: x[key_index])
        group_by_header = {}

        # create iterator
        it = iter(sorted_by_header)
        for k, g in itertools.groupby(it, lambda x: x[key_index]):

            def sum_of_nums(column, dt, i):
                try:
                    if dt[i] == "float":
                        tmp = [float(s) for s in column]
                        yield sum(tmp)
                    if dt[i] == "int":
                        tmp = [int(s) for s in column]
                        yield sum(tmp)
                    else:
                        yield "NA"


                except AggDataConversionError as ex:
                    raise ex

            def generate_sum(group):
                index = 0
                for c in zip(*list(group)):
                    yield sum_of_nums(c, self.datatypes, index)
                    index += 1

            group_by_header.setdefault(k, [])
            for j in generate_sum(g):
                group_by_header[k].append(next(j))

        self.output = Output.create(self.headers, group_by_header, key_index)
        return group_by_header


class AggDataConversionError(ValueError):
    """ Data conversion error handling """