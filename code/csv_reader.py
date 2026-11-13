"""Read and validate the structure of an input CSV."""

import csv


class InputError(ValueError):
    """An input error with a file or row location for the CLI."""


def parse_rows(stream, expected_columns, filename="CSV"):
    reader = csv.reader(stream, strict=True)
    try:
        header = next(reader, None)
        if header is None:
            raise InputError(f"{filename}: missing header")
        if len(header) != len(expected_columns) or set(header) != set(expected_columns):
            expected = ", ".join(expected_columns)
            raise InputError(f"{filename}: header must contain these columns exactly once: {expected}")

        line = reader.line_num + 1
        for cells in reader:
            if len(cells) != len(header):
                raise InputError(f"{filename}: line {line}: expected {len(header)} fields, got {len(cells)}")
            row = dict(zip(header, cells))
            yield line, row
            line = reader.line_num + 1
    except csv.Error as error:
        raise InputError(f"{filename}: line {reader.line_num}: invalid CSV: {error}") from error


def read_rows(path, expected_columns):
    """Yield a source line number and a dictionary of raw field strings."""
    try:
        with open(path, encoding="utf-8-sig", newline="") as stream:
            for line, row in parse_rows(stream, expected_columns, str(path)):
                yield line, row
    except (OSError, UnicodeError) as error:
        raise InputError(f"{path}: could not read file: {error}") from error
