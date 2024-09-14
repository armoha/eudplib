# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import string

from eudplib import core as c
from eudplib import utils as ut
from eudplib.localize import _

from .cpprint import PColor, PName, eprint_all, f_cpstr_print, f_eprintln
from .dbstr import DBString
from .eudprint import epd2s, f_dbstr_print, hptr, ptr2s


class _EUDFormatter(string.Formatter):
    def __init__(self):
        self.last_number = 0

    def vformat(self, format_string, args, kwargs):
        used_args = set()
        result, _ = self._eudformat(format_string, args, kwargs, used_args, 2)
        self.check_unused_args(used_args, args, kwargs)
        return result

    def _eudformat(
        self,
        format_string,
        args,
        kwargs,
        used_args,
        recursion_depth,
        auto_arg_index=0,
    ):
        if recursion_depth < 0:
            raise ValueError(_("Max string recursion exceeded"))
        result = []
        for literal_text, field_name, format_spec, conversion in self.parse(
            format_string
        ):
            # output the literal text
            if literal_text:
                result.append(literal_text)

            # if there's a field, output it
            if field_name is not None:
                # this is some markup, find the object and do the formatting

                # fmt: off
                # handle arg indexing when empty field_names are given.
                if field_name == "":
                    if auto_arg_index is False:
                        raise ValueError(_("cannot switch from manual field specification to automatic field numbering"))  # noqa: E501
                    field_name = str(auto_arg_index)
                    auto_arg_index += 1
                elif field_name.isdigit():
                    if auto_arg_index:
                        raise ValueError(_("cannot switch from manual field specification to automatic field numbering"))  # noqa: E501
                    # disable auto arg incrementing, if it gets
                    # used later on, then an exception will be raised
                    auto_arg_index = False

                # fmt: on
                # given the field_name, find the object it references
                #  and the argument it came from
                obj, arg_used = self.get_field(field_name, args, kwargs)
                used_args.add(arg_used)

                # do any conversion on the resulting object
                obj = self.convert_field(obj, conversion)

                # expand the format spec, if needed
                format_spec, auto_arg_index = self._vformat(
                    format_spec,
                    args,
                    kwargs,
                    used_args,
                    recursion_depth - 1,
                    auto_arg_index=auto_arg_index,
                )

                # format the object and append to the result
                result.append(self.eudformat_field(obj, format_spec))

        return result, auto_arg_index

    def eudformat_field(self, value, format_spec):
        if format_spec.endswith("s"):
            if c.IsConstExpr(value):
                try:
                    if value % 4 == 0:
                        return epd2s(ut.EPD(value))
                except TypeError:
                    return ptr2s(value)
            return ptr2s(value)
        elif format_spec.endswith("t"):
            return epd2s(value)
        elif format_spec.endswith("x") or format_spec.endswith("X"):
            return hptr(value)
        elif format_spec.endswith("c"):
            return PColor(value)
        elif format_spec.endswith("n"):
            return PName(value)
        else:
            types = (c.Db, ptr2s, epd2s, hptr, c.EUDVariable, DBString)
            for t in types:
                if ut.isUnproxyInstance(value, t):
                    return value
            if c.IsConstExpr(value):
                return value
        return format(value, format_spec)

    def get_value(self, key, args, kwargs):
        if key == "":
            key = self.last_number
            self.last_number += 1
        return super().get_value(key, args, kwargs)


def _format_args(format_string, *args):
    formatter = _EUDFormatter()
    return formatter.format(format_string, *args)


def f_sprintf(dst, format_string, *args, EOS=True, encoding="UTF-8"):  # noqa: N803
    fmtargs = _format_args(format_string, *args)
    return f_dbstr_print(dst, *fmtargs, EOS=EOS, encoding=encoding)


def f_sprintf_cp(format_string, *args, EOS=True, encoding="UTF-8"):  # noqa: N803
    fmtargs = _format_args(format_string, *args)
    f_cpstr_print(*fmtargs, EOS=EOS, encoding=encoding)


def f_eprintf(format_string, *args):
    fmtargs = _format_args(format_string, *args)
    f_eprintln(*fmtargs)


def f_eprintAll(format_string, *args):  # noqa: N802
    fmtargs = _format_args(format_string, *args)
    eprint_all(*fmtargs)
