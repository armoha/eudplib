# Copyright (c) 2022 Alessandro Molina
# https://github.com/amol-/linetable/blob/main/linetable/varint.py


def read_varint(it):
    b = next(it)
    val = b & 63
    shift = 0
    while b & 64:
        b = next(it)
        shift += 6
        val |= (b & 63) << shift
    return val


def read_signed_varint(it):
    uval = read_varint(it)
    if uval & 1:
        return -(uval >> 1)
    else:
        return uval >> 1


def generate_varint(n):
    if n == 0:
        yield 0
    while n:
        if n > 63:
            yield n & 63 | 64
        else:
            yield n & 63
        n = n >> 6


def generate_signed_varint(s):
    if s < 0:
        return generate_varint(((-s) << 1) | 1)
    else:
        return generate_varint(s << 1)
