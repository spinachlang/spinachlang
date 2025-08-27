"""list of exit codes"""

from enum import IntEnum


class ExitCode(IntEnum):
    """list of exit codes"""

    OK = 0
    FILE_NOT_FOUND = 2
    INVALID_INPUT = 3
    READ_ERROR = 4
    WRITE_ERROR = 6
