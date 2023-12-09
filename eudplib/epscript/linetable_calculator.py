# Source: https://github.com/PaddlePaddle/PaddleSOT/blob/7a2a7f4bdb998ccbec6a386ed69be54d996e923e/sot/opcode_translator/executor/pycode_generator.py#L149-L332

import sys


def to_byte(num):
    """
    Converts a negative number to an unsigned byte.

    Args:
        num (int): The number to convert.

    Returns:
        int: The converted unsigned byte.
    """
    if num < 0:
        num += 256
    return num


# Cache for some opcodes, it's for Python 3.11+
# https://github.com/python/cpython/blob/3.11/Include/internal/pycore_opcode.h#L41-L53
PYOPCODE_CACHE_SIZE = {
    "BINARY_SUBSCR": 4,
    "STORE_SUBSCR": 1,
    "UNPACK_SEQUENCE": 1,
    "STORE_ATTR": 4,
    "LOAD_ATTR": 4,
    "COMPARE_OP": 2,
    "LOAD_GLOBAL": 5,
    "BINARY_OP": 1,
    "LOAD_METHOD": 10,
    "PRECALL": 1,
    "CALL": 4,
}


def get_instruction_size(instr) -> int:
    cache_size = 0
    if sys.version_info >= (3, 11):
        cache_size = PYOPCODE_CACHE_SIZE.get(instr.opname, 0)
    return 2 * (cache_size + 1)


def create_linetable_calculator(firstlineno: int):
    """
    Creates a line table calculator function.

    Args:
        firstlineno (int): The starting line number.

    Returns:
        Callable: The line table calculator function.
    """
    cur_lineno = firstlineno
    cur_bytecode = 0
    line_offset = 0  # For Python 3.10

    def update_cursor(starts_line: int | None, code_length: int):
        nonlocal cur_lineno, cur_bytecode
        cur_bytecode = code_length
        if starts_line is not None:
            cur_lineno = starts_line

    def calc_lnotab(starts_line: int, code_length: int):
        """
        Calculates the lnotab for Python 3.8 and 3.9.
        https://github.com/python/cpython/blob/3.9/Objects/lnotab_notes.txt

        Args:
            starts_line (int): The line number where the instruction starts.
            code_length (int): The length of the code.

        Returns:
            list[int]: The lnotab.
        """
        nonlocal cur_lineno, cur_bytecode
        line_offset = starts_line - cur_lineno
        byte_offset = code_length - cur_bytecode
        result = []

        while line_offset or byte_offset:
            line_offset_step = min(max(line_offset, -128), 127)
            byte_offset_step = min(max(byte_offset, 0), 255)
            result.extend((byte_offset_step, to_byte(line_offset_step)))
            line_offset -= line_offset_step
            byte_offset -= byte_offset_step
        return result

    def calc_linetable_py310(starts_line: int, code_length: int):
        """
        Calculates the linetable for Python 3.10.
        https://github.com/python/cpython/blob/3.10/Objects/lnotab_notes.txt

        Args:
            starts_line (int): The line number where the instruction starts.
            code_length (int): The length of the code.

        Returns:
            list[int]: The linetable.
        """
        nonlocal cur_lineno, cur_bytecode, line_offset
        byte_offset = code_length - cur_bytecode
        result = []
        while line_offset or byte_offset:
            line_offset_step = min(max(line_offset, -127), 127)
            byte_offset_step = min(max(byte_offset, 0), 254)
            result.extend((byte_offset_step, to_byte(line_offset_step)))
            line_offset -= line_offset_step
            byte_offset -= byte_offset_step
        line_offset = starts_line - cur_lineno
        return result

    def _encode_varint(num: int):
        """
        Encode unsigned integer into variable-length format.
        """
        continue_flag = 0b01 << 6
        stop_flag = 0b00 << 6
        while num >= 0x40:
            yield (num & 0x3F) | continue_flag
            num >>= 6
        yield num | stop_flag

    def _encode_svarint(num: int):
        """
        Encode signed integer into variable-length format.
        """
        unsigned_value = (((-num) << 1) | 1) if num < 0 else (num << 1)
        yield from _encode_varint(unsigned_value)

    def _encode_bytecode_to_entries_py311(line_offset: int, byte_offset: int):
        if not byte_offset:
            return []
        if 0 < byte_offset <= 8:
            entry_head = 0b1_1101_000 | (byte_offset - 1)
            return [entry_head, *list(_encode_svarint(line_offset))]
        return [
            *_encode_bytecode_to_entries_py311(line_offset, 8),
            *_encode_bytecode_to_entries_py311(line_offset, byte_offset - 8),
        ]

    def calc_linetable_py311(starts_line: int | None, code_length: int):
        """
        Calculates the linetable for Python 3.11.
        https://github.com/python/cpython/blob/3.11/Objects/locations.md

        Args:
            starts_line (int): The line number where the instruction starts.
            code_length (int): The length of the code.

        Returns:
            list[int]: The linetable.
        """
        nonlocal cur_lineno, cur_bytecode
        line_offset = (
            starts_line - cur_lineno if starts_line is not None else 0
        )
        byte_offset = (code_length - cur_bytecode) // 2
        return _encode_bytecode_to_entries_py311(line_offset, byte_offset)

    if sys.version_info >= (3, 11):
        return calc_linetable_py311, update_cursor
    elif sys.version_info >= (3, 10):
        return calc_linetable_py310, update_cursor
    else:
        return calc_lnotab, update_cursor
