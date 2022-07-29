from enum import Enum


class FileStatus(Enum):
    NOT_FOUND = 0
    LOADED = 1
    GENERATED = 2