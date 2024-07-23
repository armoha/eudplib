#!/usr/bin/python
from types import ModuleType

from ..core import (
    ConstExpr,
    EUDCreateVariables,
    EUDVariable,
    EUDVArray,
    Forward,
    IsEUDVariable,
    NextTrigger,
    PopTriggerScope,
    PushTriggerScope,
    SeqCompute,
    SetNextTrigger,
    SetTo,
    SetVariables,
    f_bitlshift,
)
from ..ctrlstru import EUDElse, EUDEndIf, EUDIf
from ..eudlib import EUDArray, f_setcurpl2cpcache
from ..maprw import EUDOnStart
from ..utils import (
    EPD,
    ExprProxy,
    FlattenList,
    List2Assignable,
    TriggerScopeError,
    ep_assert,
    ep_warn,
    isUnproxyInstance,
)


def _RELIMP(path, mod_name, _cache={}):  # relative path import  # noqa: N802
    import importlib.util
    import inspect
    import pathlib

    from .epsimp import EPSLoader

    p = pathlib.Path(inspect.getabsfile(inspect.currentframe().f_back))
    pathsplit = path.split(".")
    if len(path) + 1 == len(pathsplit):  # path == '.' * len(path)
        pathsplit = pathsplit[1:]
    for s in pathsplit:
        if s == "":
            p = p.parent
        else:
            p = p / s

    abs_path = p / mod_name
    if abs_path in _cache:
        return _cache[abs_path]

    def py_module(mod_name, p):
        spec = importlib.util.spec_from_file_location(
            mod_name, p / (mod_name + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def eps_module(mod_name, p):
        loader = EPSLoader(mod_name, str(p / (mod_name + ".eps")))
        spec = importlib.util.spec_from_loader(mod_name, loader)
        module = loader.create_module(spec)
        loader.exec_module(module)
        return module

    try:
        module = py_module(mod_name, p)
    except FileNotFoundError:
        try:
            module = eps_module(mod_name, p)
        except FileNotFoundError:
            item_name = mod_name
            mod_name = p.name
            p = p.parent
            abs_path = p / mod_name
            if abs_path in _cache:
                module = _cache[abs_path]
            else:
                try:
                    module = py_module(mod_name, p)
                except FileNotFoundError:
                    module = eps_module(mod_name, p)
                _cache[abs_path] = module
            return getattr(module, item_name)
    _cache[abs_path] = module
    return module


def _IGVA(var_count, expr_list_gen):  # noqa: N802
    try:
        var_list = List2Assignable([EUDVariable(x) for x in expr_list_gen()])
    except (TriggerScopeError, NameError):
        var_list = EUDCreateVariables(var_count)

        def _() -> None:
            expr_list = expr_list_gen()
            SetVariables(var_list, expr_list)

        EUDOnStart(_)
    return var_list


def _CGFW(exprf, retn):  # noqa: N802
    PushTriggerScope()
    start = NextTrigger()
    try:
        rets = exprf()
    except NameError:
        rets = [ExprProxy(None) for _ in range(retn)]

        def _():
            vals = exprf()
            for ret, val in zip(rets, vals):
                ret._value = val

        EUDOnStart(_)
    end = Forward()
    SetNextTrigger(end)
    PopTriggerScope()

    def _():
        nonlocal end
        SetNextTrigger(start)
        end << NextTrigger()

    EUDOnStart(_)
    return rets


def _ARR(items):  # EUDArray initialization  # noqa: N802
    k = EUDArray(len(items))
    for i, item in enumerate(items):
        k[i] = item
    return k


def _VARR(items):  # EUDVArray initialization  # noqa: N802
    k = EUDVArray(len(items))()
    for i, item in enumerate(items):
        k[i] = item
    return k


def _SRET(v, klist):  # noqa: N802
    return List2Assignable([v[k] for k in klist])


def _SV(d_list, s_list):  # noqa: N802
    [d << s for d, s in zip(FlattenList(d_list), FlattenList(s_list))]


class _ATTW:  # attribute write
    def __init__(self, obj, attr_name):
        self.obj = obj
        self.attr_name = attr_name

    def __lshift__(self, r):
        if isinstance(self.obj, ModuleType):
            ov = getattr(self.obj, self.attr_name)
            if IsEUDVariable(ov):
                ov << r
                return
            ep_warn("Try to shadow module variable")
        setattr(self.obj, self.attr_name, r)

    def __iadd__(self, v):
        try:
            self.obj.iaddattr(self.attr_name, v)
        except AttributeError:
            ov = getattr(self.obj, self.attr_name)
            ov += v
            setattr(self.obj, self.attr_name, ov)
        return self

    def __isub__(self, v):
        try:
            self.obj.isubattr(self.attr_name, v)
        except AttributeError:
            ov = getattr(self.obj, self.attr_name)
            ov -= v
            setattr(self.obj, self.attr_name, ov)
        return self

    def __imul__(self, v):
        try:
            self.obj.imulattr(self.attr_name, v)
        except AttributeError:
            ov = getattr(self.obj, self.attr_name)
            ov *= v
            setattr(self.obj, self.attr_name, ov)
        return self

    def __ifloordiv__(self, v):
        try:
            self.obj.ifloordivattr(self.attr_name, v)
        except AttributeError:
            ov = getattr(self.obj, self.attr_name)
            ov //= v
            setattr(self.obj, self.attr_name, ov)
        return self

    def __imod__(self, v):
        try:
            self.obj.imodattr(self.attr_name, v)
        except AttributeError:
            ov = getattr(self.obj, self.attr_name)
            ov %= v
            setattr(self.obj, self.attr_name, ov)
        return self

    def __ilshift__(self, v):
        try:
            self.obj.ilshiftattr(self.attr_name, v)
        except AttributeError:
            ov = getattr(self.obj, self.attr_name)
            ov <<= v
            setattr(self.obj, self.attr_name, ov)
        return self

    def __irshift__(self, v):
        try:
            self.obj.irshiftattr(self.attr_name, v)
        except AttributeError:
            ov = getattr(self.obj, self.attr_name)
            ov >>= v
            setattr(self.obj, self.attr_name, ov)
        return self

    def __ipow__(self, v):
        try:
            self.obj.ipowattr(self.attr_name, v)
        except AttributeError:
            ov = getattr(self.obj, self.attr_name)
            ov **= v
            setattr(self.obj, self.attr_name, ov)
        return self

    def __iand__(self, v):
        try:
            self.obj.iandattr(self.attr_name, v)
        except AttributeError:
            ov = getattr(self.obj, self.attr_name)
            ov &= v
            setattr(self.obj, self.attr_name, ov)
        return self

    def __ior__(self, v):
        try:
            self.obj.iorattr(self.attr_name, v)
        except AttributeError:
            ov = getattr(self.obj, self.attr_name)
            ov |= v
            setattr(self.obj, self.attr_name, ov)
        return self

    def __ixor__(self, v):
        try:
            self.obj.ixorattr(self.attr_name, v)
        except AttributeError:
            ov = getattr(self.obj, self.attr_name)
            ov ^= v
            setattr(self.obj, self.attr_name, ov)
        return self


class _ARRW:  # array write
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index

    def __lshift__(self, r):
        isUnproxyInstance
        if not IsEUDVariable(self.obj) and not isUnproxyInstance(
            self.obj, ConstExpr
        ):
            # maybe Python collections
            ov = self.obj[self.index]
            if IsEUDVariable(ov):
                ov << r
                return
        self.obj[self.index] = r

    def __iadd__(self, v):
        try:
            self.obj.iadditem(self.index, v)
        except AttributeError:
            ov = self.obj[self.index]
            ov += v
            self.obj[self.index] = ov
        return self

    def __isub__(self, v):
        try:
            self.obj.isubitem(self.index, v)
        except AttributeError:
            ov = self.obj[self.index]
            ov -= v
            self.obj[self.index] = ov
        return self

    def __imul__(self, v):
        try:
            self.obj.imulitem(self.index, v)
        except AttributeError:
            ov = self.obj[self.index]
            ov *= v
            self.obj[self.index] = ov
        return self

    def __ifloordiv__(self, v):
        try:
            self.obj.ifloordivitem(self.index, v)
        except AttributeError:
            ov = self.obj[self.index]
            ov //= v
            self.obj[self.index] = ov
        return self

    def __imod__(self, v):
        try:
            self.obj.imoditem(self.index, v)
        except AttributeError:
            ov = self.obj[self.index]
            ov %= v
            self.obj[self.index] = ov
        return self

    def __ilshift__(self, v):
        try:
            self.obj.ilshiftitem(self.index, v)
        except AttributeError:
            ov = self.obj[self.index]
            ov <<= v
            self.obj[self.index] = ov
        return self

    def __irshift__(self, v):
        try:
            self.obj.irshiftitem(self.index, v)
        except AttributeError:
            ov = self.obj[self.index]
            ov >>= v
            self.obj[self.index] = ov
        return self

    def __ipow__(self, v):
        try:
            self.obj.ipowitem(self.index, v)
        except AttributeError:
            ov = self.obj[self.index]
            ov **= v
            self.obj[self.index] = ov
        return self

    def __iand__(self, v):
        try:
            self.obj.ianditem(self.index, v)
        except AttributeError:
            ov = self.obj[self.index]
            ov &= v
            self.obj[self.index] = ov
        return self

    def __ior__(self, v):
        try:
            self.obj.ioritem(self.index, v)
        except AttributeError:
            ov = self.obj[self.index]
            ov |= v
            self.obj[self.index] = ov
        return self

    def __ixor__(self, v):
        try:
            self.obj.ixoritem(self.index, v)
        except AttributeError:
            ov = self.obj[self.index]
            ov ^= v
            self.obj[self.index] = ov
        return self


class _ATTC:  # attribute comparison
    def __init__(self, obj, attr_name):
        self.obj = obj
        self.attr_name = attr_name

    def __eq__(self, k):
        try:
            return self.obj.eqattr(self.attr_name, k)
        except AttributeError:
            return getattr(self.obj, self.attr_name) == k

    def __ne__(self, k):
        try:
            return self.obj.neattr(self.attr_name, k)
        except AttributeError:
            return getattr(self.obj, self.attr_name) != k

    def __le__(self, k):
        try:
            return self.obj.leattr(self.attr_name, k)
        except AttributeError:
            return getattr(self.obj, self.attr_name) <= k

    def __lt__(self, k):
        try:
            return self.obj.ltattr(self.attr_name, k)
        except AttributeError:
            return getattr(self.obj, self.attr_name) < k

    def __ge__(self, k):
        try:
            return self.obj.geattr(self.attr_name, k)
        except AttributeError:
            return getattr(self.obj, self.attr_name) >= k

    def __gt__(self, k):
        try:
            return self.obj.gtattr(self.attr_name, k)
        except AttributeError:
            return getattr(self.obj, self.attr_name) > k


class _ARRC:  # array comparison
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index

    def __eq__(self, k):
        try:
            return self.obj.eqitem(self.index, k)
        except AttributeError:
            return self.obj[self.index] == k

    def __ne__(self, k):
        try:
            return self.obj.neitem(self.index, k)
        except AttributeError:
            return self.obj[self.index] != k

    def __le__(self, k):
        try:
            return self.obj.leitem(self.index, k)
        except AttributeError:
            return self.obj[self.index] <= k

    def __lt__(self, k):
        try:
            return self.obj.ltitem(self.index, k)
        except AttributeError:
            return self.obj[self.index] < k

    def __ge__(self, k):
        try:
            return self.obj.geitem(self.index, k)
        except AttributeError:
            return self.obj[self.index] >= k

    def __gt__(self, k):
        try:
            return self.obj.gtitem(self.index, k)
        except AttributeError:
            return self.obj[self.index] > k


def _L2V(logic):  # noqa: N802, logic to value
    ret = EUDVariable()
    if EUDIf()(logic):
        ret << 1
    if EUDElse()():
        ret << 0
    EUDEndIf()
    return ret


def _LVAR(vs):  # noqa: N802
    import sys

    from ..core.variable.eudv import _yield_and_check_rvalue

    ret, ops = [], []
    if sys.version_info >= (3, 11):
        refcount = 3
    else:
        refcount = 4
    for v, is_rvalue in _yield_and_check_rvalue(vs, refcount):
        if IsEUDVariable(v) and is_rvalue:
            ret.append(v.makeL())
        else:
            nv = EUDVariable()
            ret.append(nv)
            ops.append((nv, SetTo, v))
    if ops:
        SeqCompute(ops)
    return List2Assignable(ret)


def _LSH(lhs, r):  # noqa: N802
    if IsEUDVariable(lhs):
        return f_bitlshift(lhs, r)
    else:
        return lhs << r


def _ALL(actions):  # noqa: N802
    from ..trigger.tpatcher import actpt, apply_patch_table

    ep_assert(len(actions) == 2)
    apply_patch_table(EPD(actions[1]), actions[1], actpt)
    f_setcurpl2cpcache([], actions)
