# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import functools

from ... import utils as ut
from ...localize import _
from ...utils.blockstru import BlockStruManager, set_blockstru_manager
from .. import allocator as ac
from .. import rawtrigger as bt
from .. import variable as ev
from .trace.tracetool import _eud_trace_pop, _eud_trace_push

_current_compiled_func = None
_current_trigger_count = 0


def _update_func_trigger_count():
    global _current_trigger_count
    current_counter = bt.GetTriggerCounter()
    added_trigger_count = current_counter - _current_trigger_count

    if _current_compiled_func:
        _current_compiled_func._triggerCount += added_trigger_count
    _current_trigger_count = current_counter


def _set_current_compiled_func(func):
    global _current_compiled_func

    last_compiled_func = _current_compiled_func
    _update_func_trigger_count()
    _current_compiled_func = func
    return last_compiled_func


class EUDFuncN:
    def __init__(self, argn, callerfunc, bodyfunc, *, traced):
        """EUDFuncN

        :param callerfunc: Function to be wrapped.
        :param argn: The number of arguments got by callerfunc
        :param bodyfunc: Where function should return to
        """

        if bodyfunc is None:
            bodyfunc = callerfunc

        if isinstance(argn, int):
            self._argn = argn
            self._arginits = [(0, bt.SetTo, 0, None)] * argn
        elif all(
            isinstance(initvals, tuple) and len(initvals) == 4 for initvals in argn
        ):
            self._argn = len(argn)
            self._arginits = argn
        else:
            raise ut.EPError(f"Invalid argn: {argn}")
        self._retn = None
        self._callerfunc = callerfunc
        self._bodyfunc = bodyfunc
        functools.update_wrapper(self, bodyfunc)
        self._fstart = None
        self._fend = None
        self._nptr = None
        self._fargs = None
        self._frets = None
        self._triggerCount = None
        self._traced = traced

    def size(self):
        if not self._fstart:
            self._create_func_body()

        return self._triggerCount

    def _create_func_body(self):
        self._triggerCount = 0
        last_compiled_func = _set_current_compiled_func(self)

        # Add return point
        self._fend = ac.Forward()

        # Prevent double compilication
        ut.ep_assert(self._fstart is None)

        # Initialize new namespace
        f_bsm = BlockStruManager()
        prev_bsm = set_blockstru_manager(f_bsm)
        bt.PushTriggerScope()

        self._create_func_args()

        fstart = bt.NextTrigger()
        self._fstart = fstart

        if self._traced:
            _eud_trace_push()

        final_rets = self._callerfunc(*self._fargs)
        if final_rets is not None:
            self._add_return(ut.Assignable2List(final_rets), False)

        if not self._fend.IsSet():
            self._fend << bt.NextTrigger()
        if self._traced:
            _eud_trace_pop()
        if self._retn is None or self._retn == 0:
            self._fend = bt.RawTrigger()
            self._nptr = self._fend + 4
        else:
            fend_trgs = ut.FlattenList(ev.VProc(self._frets, []))
            self._fend = fend_trgs[0]
            self._nptr = fend_trgs[-1]._actions[-1] + 20

        bt.PopTriggerScope()

        # Finalize
        if not f_bsm.empty():
            raise ut.EPError(
                _("Block start/end mismatch inside function")
                + f": {', '.join(name for name, _data in f_bsm._blockstru)}"
            )
        set_blockstru_manager(prev_bsm)

        # No return -> set return count to 0
        if self._retn is None:
            self._retn = 0
        _set_current_compiled_func(last_compiled_func)

    def _create_func_args(self):
        if self._fargs is None:
            self._fargs = []
            for initvals in self._arginits:
                if initvals[3] is None:
                    argv = ev.EUDXVariable(*initvals[:3])
                else:
                    argv = ev.EUDXVariable(*initvals)
                self._fargs.append(argv)

    def _add_return(self, retv, needjump):
        retv = ut.FlattenList(retv)
        if self._frets is None:
            self._frets = [ev.EUDVariable() for _ in retv]
            self._retn = len(retv)

        ut.ep_assert(
            len(retv) == len(self._frets),
            _("Number of returned values should be constant.")
            + _(" (From function %s)").format(self._bodyfunc.__name__),
        )

        var_assigns, const_assigns = list(), list()
        for fret, ret in zip(self._frets, retv):
            if ev.IsEUDVariable(ret):
                var_assigns.append((fret, bt.SetTo, ret))
            else:
                const_assigns.append((fret, bt.SetTo, ret))
        if len(var_assigns) <= 2:
            ev.SeqCompute(const_assigns + var_assigns)
        else:
            ev.NonSeqCompute(const_assigns + var_assigns)

        if needjump:
            bt.SetNextTrigger(self._fend)

    def _call_with_last_args(self, *, ret=None):
        if self._fstart is None:
            self._create_func_body()

        fcallend = ac.Forward()

        # SeqCompute gets faster when const-assignments are in front of
        # variable assignments.
        if ret is None:
            ret = ev.EUDCreateVariables(self._retn)
        ret = ut.FlattenList(ret)
        ut.ep_assert(
            len(ret) == self._retn,
            _("Return number mismatch : ")
            + "len(%s) != %d" % (repr(ret), self._retn),
        )
        next_ptr_assignment = [(ut.EPD(self._nptr), bt.SetTo, fcallend)]
        if self._retn >= 1:
            for fret, retv in zip(self._frets, ret):
                try:
                    retv = ut.EPD(retv.getValueAddr())
                except AttributeError:
                    pass
                next_ptr_assignment.append(
                    (ut.EPD(fret.getDestAddr()), bt.SetTo, retv)
                )

        ev.SeqCompute(next_ptr_assignment)
        bt.SetNextTrigger(self._fstart)

        fcallend << bt.NextTrigger()

        if self._frets is not None:
            for retv in ret:
                try:
                    retv.makeR()
                except AttributeError:
                    pass
            return ut.List2Assignable(ret)

    def __call__(self, *args, ret=None):
        if self._fstart is None:
            self._create_func_body()

        ut.ep_assert(
            len(args) == self._argn,
            _("Argument number mismatch : ")
            + "len(%s) != %d" % (repr(args), self._argn),
        )

        fcallend = ac.Forward()

        # SeqCompute gets faster when const-assignments are in front of
        # variable assignments.
        if ret is None:
            ret = ev.EUDCreateVariables(self._retn)
        ret = ut.FlattenList(ret)
        ut.ep_assert(
            len(ret) == self._retn,
            _("Return number mismatch : ")
            + "len(%s) != %d" % (repr(ret), self._retn),
        )
        next_ptr_assignment = [(ut.EPD(self._nptr), bt.SetTo, fcallend)]
        if self._retn >= 1:
            for fret, retv in zip(self._frets, ret):
                try:
                    retv = ut.EPD(retv.getValueAddr())
                except AttributeError:
                    pass
                next_ptr_assignment.append(
                    (ut.EPD(fret.getDestAddr()), bt.SetTo, retv)
                )
        var_assigns, const_assigns = list(), list()
        for farg, arg in zip(self._fargs, args):
            if ev.IsEUDVariable(arg):
                var_assigns.append((farg, bt.SetTo, arg))
            else:
                const_assigns.append((farg, bt.SetTo, arg))
        if len(var_assigns) <= 2:
            ev.SeqCompute(next_ptr_assignment + const_assigns + var_assigns)
        else:
            ev.NonSeqCompute(next_ptr_assignment + const_assigns + var_assigns)
        bt.SetNextTrigger(self._fstart)

        fcallend << bt.NextTrigger()

        if self._frets is not None:
            for retv in ret:
                try:
                    retv.makeR()
                except AttributeError:
                    pass
            return ut.List2Assignable(ret)


def EUDReturn(*args):  # noqa: N802
    _current_compiled_func._add_return(args, True)
