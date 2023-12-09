# Copyright (c) 2022 Alessandro Molina
# https://github.com/amol-/linetable/blob/main/linetable/linetable.py


from .varint import generate_signed_varint, read_signed_varint, read_varint


def generate_linetable(pairs, firstlineno=1, use_bytecode_offset=False):
    return b"".join(
        _generate_linetable(pairs, firstlineno, use_bytecode_offset)
    )


def _generate_linetable(pairs, firstlineno, use_bytecode_offset):
    pairs = iter(pairs)  # will do nothing if it's already an iterator.

    cur_line = firstlineno
    cur_entry = next(pairs)
    while cur_entry:
        try:
            next_entry = next(pairs)
        except StopIteration:
            next_entry = None

        length, start_line, *more = cur_entry
        if more:
            end_line, start_col, end_col = more
        else:
            end_line, start_col, end_col = start_line, None, None

        if use_bytecode_offset:
            # We don't have the length,
            # but we have the byte code offsets from dis.findlinestarts()
            length = _linetable_length(length, next_entry)

        if start_line is not None:
            line_delta = start_line - cur_line
            cur_line = end_line

        if start_line is None:
            code = 15
            yield _new_linetable_entry(code, length).to_bytes(
                1, byteorder="little"
            )
        elif start_col is None:
            code = 13
            yield _new_linetable_entry(code, length).to_bytes(
                1, byteorder="little"
            )
            for b in generate_signed_varint(line_delta):
                yield b.to_bytes(1, byteorder="little")
        elif line_delta == 0 and (end_col - start_col) < 15:
            # short form, same line as before and near columns.
            code = start_col // 8
            yield _new_linetable_entry(code, length).to_bytes(
                1, byteorder="little"
            )
            yield (((start_col % 8) << 4) | (end_col - start_col)).to_bytes(
                1, byteorder="little"
            )
        elif line_delta <= 2 and start_col <= 255 and end_col <= 255:
            # New line form
            code = 10 + line_delta
            print(line_delta)
            yield _new_linetable_entry(code, length).to_bytes(
                1, byteorder="little"
            )
            yield start_col.to_bytes(1, byteorder="little")
            yield end_col.to_bytes(1, byteorder="little")
        else:
            raise NotImplementedError()

        cur_entry = next_entry


def _new_linetable_entry(code, length):
    # 8 bits entry made of:
    # -----------------
    # 7 | 6 - 3 | 2 - 0
    # 1 |  code | length-1
    print((1 << 7) | (code << 3) | (length - 1))
    return (1 << 7) | (code << 3) | (length - 1)


def _linetable_length(bc_start, next_entry):
    length = 1
    if next_entry:
        # Each bytecode entry is 2 bytes,
        # so compute the offset in bytes between two bytecode entries
        # and then divide by 2 to get the number of entries.
        length = (next_entry[0] - bc_start) // 2
    return length


def parse_linetable(linetable, firstlineno=1):
    line = firstlineno
    it = iter(linetable)
    while True:
        try:
            first_byte = next(it)
        except StopIteration:
            return
        code = (first_byte >> 3) & 15
        length = (first_byte & 7) + 1
        if code == 15:
            yield (length, None, None, None, None)
        elif code == 14:
            line_delta = read_signed_varint(it)
            line += line_delta
            end_line = line + read_varint(it)
            col = read_varint(it)
            if col == 0:
                col = None
            else:
                col -= 1
            end_col = read_varint(it)
            if end_col == 0:
                end_col = None
            else:
                end_col -= 1
            yield (length, line, end_line, col, end_col)
        elif code == 13:  # No column
            line_delta = read_signed_varint(it)
            line += line_delta
            yield (length, line, line, None, None)
        elif code in (10, 11, 12):  # new line
            line_delta = code - 10
            line += line_delta
            column = next(it)
            end_column = next(it)
            yield (length, line, line, column, end_column)
        elif 0 <= code < 10:  # short form
            second_byte = next(it)
            column = code << 3 | (second_byte >> 4)
            yield (length, line, line, column, column + (second_byte & 15))
        else:
            raise NotImplementedError()
