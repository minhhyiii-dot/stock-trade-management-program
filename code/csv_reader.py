import csv


class InputError(ValueError):

def parse_rows(stream, expected_columns, filename="CSV"):
    reader = csv.reader(stream, strict=True)
    try:
        header = next(reader, None) # take the first row as header, if None or different from expected_column then raise error
        if header is None:
            raise InputError(f"{filename}: missing header")
        if len(header) != len(expected_columns) or set(header) != set(expected_columns):
            expected = ", ".join(expected_columns)
            raise InputError(f"{filename}: header must contain these columns exactly once: {expected}")

        line = reader.line_num + 1 # basically the same with line = 2
        for cells in reader: # loop for every row in csv, finally yield line and row
            if len(cells) != len(header):
                raise InputError(f"{filename}: line {line}: expected {len(header)} fields, got {len(cells)}")
            row = dict(zip(header, cells))
            yield line, row
            line = reader.line_num + 1
    except csv.Error as error:
        raise InputError(f"{filename}: line {reader.line_num}: invalid CSV: {error}") from error


def read_rows(path, expected_columns):

    try:
        with open(path, encoding="utf-8-sig", newline="") as stream:
            for line, row in parse_rows(stream, expected_columns, str(path)):
                yield line, row # take the verified output from parse
    except (OSError, UnicodeError) as error:
        raise InputError(f"{path}: could not read file: {error}") from error
