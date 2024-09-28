# Source: https://github.com/PaddlePaddle/PaddleSOT/blob/7a2a7f4bdb998ccbec6a386ed69be54d996e923e/sot/opcode_translator/executor/pycode_generator.py#L149-L332

import sys
import types
from collections.abc import Callable, Iterator
from dis import Instruction, get_instructions
from typing import Any


def get_pycode_attributes() -> list[str]:
    """
    Returns a list of attribute names for PyCodeObject.
    NOTE(SigureMo): The order should consistent with signature specified in code_doc
    3.8: https://github.com/python/cpython/blob/3.8/Objects/codeobject.c#L416-L421
    3.10: https://github.com/python/cpython/blob/3.10/Objects/codeobject.c#L523-L543
    3.11: https://github.com/python/cpython/blob/3.11/Objects/codeobject.c#L1494-L1516

    Returns:
        list[str]: The attribute names for PyCodeObject.
    """
    pycode_attributes = [
        "co_argcount",
        "co_posonlyargcount",
        "co_kwonlyargcount",
        "co_nlocals",
        "co_stacksize",
        "co_flags",
        "co_code",
        "co_consts",
        "co_names",
        "co_varnames",
        "co_filename",
        "co_name",
    ]
    if sys.version_info >= (3, 11):
        pycode_attributes.append("co_qualname")
    pycode_attributes.append("co_firstlineno")
    if sys.version_info >= (3, 10):
        pycode_attributes.append("co_linetable")
    else:
        pycode_attributes.append("co_lnotab")
    if sys.version_info >= (3, 11):
        pycode_attributes.append("co_exceptiontable")
    pycode_attributes += [
        "co_freevars",
        "co_cellvars",
    ]
    return pycode_attributes


PYCODE_ATTRIBUTES = get_pycode_attributes()


def gen_code_options(code: types.CodeType) -> dict[str, Any]:
    """
    Generates a dictionary of code options for the given code object.

    Args:
        code (types.CodeType): The code object.

    Returns:
        dict[str, any]: The code options.
    """
    code_options = {}
    for k in PYCODE_ATTRIBUTES:
        val = getattr(code, k)
        if isinstance(val, tuple):
            val = list(val)
        code_options[k] = val

    return code_options


def gen_new_opcode(
    code_object: types.CodeType,
    code_options: dict[str, Any],
    keys: list[str],
    ep_lineno_map: Callable[[int], int],
) -> types.CodeType:
    """
    Generates a new code object with the given instructions, code options, and keys.

    Args:
        code_object (types.CodeType): The original CodeType for instructions.
        code_options (dict[str, any]): The code options for the new code object.
        keys (list[str]): The keys to specify the order of code options.
        ep_lineno_map (Callable[[int], int]): The function to convert line number.

    Returns:
        types.CodeType: The new code object.
    """
    ep_firstlineno = ep_lineno_map(code_options["co_firstlineno"])
    linetable = assemble(
        get_instructions(code_object),
        ep_firstlineno,
        ep_lineno_map,
    )
    if sys.version_info >= (3, 10):
        # Python deprecated co_lnotab in 3.10, use co_linetable instead
        # https://peps.python.org/pep-0626/
        code_options["co_linetable"] = linetable
    else:
        code_options["co_lnotab"] = linetable
    code_options["co_firstlineno"] = ep_firstlineno
    code_options["co_nlocals"] = len(code_options["co_varnames"])
    # TODO: should we generate or empty 3.11 exception table?
    # if sys.version_info >= (3, 11):
    #     code_options["co_exceptiontable"] = bytes([])
    for key, val in code_options.items():
        if isinstance(val, list):
            code_options[key] = tuple(val)
    # code_options is a dict, use keys to make sure the input order
    return types.CodeType(*[code_options[k] for k in keys])


def assemble(
    instructions: Iterator[Instruction],
    firstlineno: int,
    ep_lineno_map: Callable[[int], int],
) -> bytes:
    """
    Assembles a list of instructions into lnotab.

    Args:
        instructions (Iterator[Instruction]): The list of instructions.
        firstlineno (int): The starting line number.
        ep_lineno_map (Callable[[int], int]): The function to convert line number.

    Returns:
        bytes: The assembled lnotab.
    """
    code: list[int] = []
    linetable = []
    ep_firstlineno = firstlineno

    calc_linetable, update_cursor = create_linetable_calculator(ep_firstlineno)

    for instr in instructions:
        # set linetable, Python 3.11 need to set linetable for each instruction
        if instr.starts_line is not None or sys.version_info >= (3, 11):
            ep_lineno: int | None
            if instr.starts_line is not None:
                ep_lineno = ep_lineno_map(instr.starts_line)
            else:
                ep_lineno = None
            linetable.extend(calc_linetable(ep_lineno, len(code)))
            update_cursor(ep_lineno, len(code))

        # get bytecode
        arg = instr.arg or 0
        code.extend((instr.opcode, arg & 0xFF))
        # fill CACHE
        for _ in range(get_instruction_size(instr) // 2 - 1):
            code.extend((0, 0))

    if sys.version_info >= (3, 11):
        # End hook for Python 3.11
        linetable.extend(calc_linetable(None, len(code)))
    elif sys.version_info >= (3, 10):
        # End hook for Python 3.10
        linetable.extend(calc_linetable(0, len(code)))

    return bytes(linetable)


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
        result: list[int] = []

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
        result: list[int] = []
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
        line_offset = starts_line - cur_lineno if starts_line is not None else 0
        byte_offset = (code_length - cur_bytecode) // 2
        return _encode_bytecode_to_entries_py311(line_offset, byte_offset)

    if sys.version_info >= (3, 11):
        return calc_linetable_py311, update_cursor
    elif sys.version_info >= (3, 10):
        return calc_linetable_py310, update_cursor
    else:
        return calc_lnotab, update_cursor
