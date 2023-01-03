from types import ModuleType

from ..core import (
    ConstExpr,
    EUDVariable,
    EUDVArray,
    IsEUDVariable,
    SeqCompute,
    SetTo,
    SetVariables,
    f_bitlshift,
)
from ..core.variable.eudv import IsRValue
from ..ctrlstru import EUDElse, EUDEndIf, EUDIf
from ..eudlib import EUDArray
from ..maprw import EUDOnStart
from ..utils import (
    ExprProxy,
    FlattenList,
    List2Assignable,
    TriggerScopeError,
    ep_warn,
    isUnproxyInstance,
)
from .epsimp import EPSLoader


def _RELIMP(path, mod_name):  # relative path import
    import importlib.util
    import inspect
    import pathlib

    p = pathlib.Path(inspect.getabsfile(inspect.currentframe())).parent
    for s in path.split("."):
        if s == "":
            p = p.parent
        else:
            p = p / s
    try:
        spec = importlib.util.spec_from_file_location(mod_name, p / (mod_name + ".py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except FileNotFoundError:
        loader = EPSLoader(mod_name, str(p / (mod_name + ".eps")))
        spec = importlib.util.spec_from_loader(mod_name, loader)
        module = loader.create_module(spec)
        loader.exec_module(module)
    return module


def _IGVA(vList, exprListGen):
    def _():
        exprList = exprListGen()
        SetVariables(vList, exprList)

    EUDOnStart(_)


def _CGFW(exprf, retn):
    try:
        return exprf()
    except (TriggerScopeError, NameError):
        rets = [ExprProxy(None) for _ in range(retn)]

        def _():
            vals = exprf()
            for ret, val in zip(rets, vals):
                ret._value = val

        EUDOnStart(_)
        return rets


def _ARR(items):  # EUDArray initialization
    k = EUDArray(len(items))
    for i, item in enumerate(items):
        k[i] = item
    return k


def _VARR(items):  # EUDVArray initialization
    k = EUDVArray(len(items))()
    for i, item in enumerate(items):
        k[i] = item
    return k


def _SRET(v, klist):
    return List2Assignable([v[k] for k in klist])


def _SV(dL, sL):
    [d << s for d, s in zip(FlattenList(dL), FlattenList(sL))]


class _ATTW:  # attribute write
    def __init__(self, obj, attrName):
        self.obj = obj
        self.attrName = attrName

    def __lshift__(self, r):
        if isinstance(self.obj, ModuleType):
            ov = getattr(self.obj, self.attrName)
            if IsEUDVariable(ov):
                ov << r
                return
            ep_warn("Try to shadow module variable")
        setattr(self.obj, self.attrName, r)

    def __iadd__(self, v):
        try:
            self.obj.iaddattr(self.attrName, v)
        except AttributeError:
            ov = getattr(self.obj, self.attrName)
            ov += v
            setattr(self.obj, self.attrName, ov)
        return self

    def __isub__(self, v):
        try:
            self.obj.isubattr(self.attrName, v)
        except AttributeError:
            ov = getattr(self.obj, self.attrName)
            ov -= v
            setattr(self.obj, self.attrName, ov)
        return self

    def __imul__(self, v):
        try:
            self.obj.imulattr(self.attrName, v)
        except AttributeError:
            ov = getattr(self.obj, self.attrName)
            ov *= v
            setattr(self.obj, self.attrName, ov)
        return self

    def __ifloordiv__(self, v):
        try:
            self.obj.ifloordivattr(self.attrName, v)
        except AttributeError:
            ov = getattr(self.obj, self.attrName)
            ov //= v
            setattr(self.obj, self.attrName, ov)
        return self

    def __imod__(self, v):
        try:
            self.obj.imodattr(self.attrName, v)
        except AttributeError:
            ov = getattr(self.obj, self.attrName)
            ov %= v
            setattr(self.obj, self.attrName, ov)
        return self

    def __ilshift__(self, v):
        try:
            self.obj.ilshiftattr(self.attrName, v)
        except AttributeError:
            ov = getattr(self.obj, self.attrName)
            ov <<= v
            setattr(self.obj, self.attrName, ov)
        return self

    def __irshift__(self, v):
        try:
            self.obj.irshiftattr(self.attrName, v)
        except AttributeError:
            ov = getattr(self.obj, self.attrName)
            ov >>= v
            setattr(self.obj, self.attrName, ov)
        return self

    def __ipow__(self, v):
        try:
            self.obj.ipowattr(self.attrName, v)
        except AttributeError:
            ov = getattr(self.obj, self.attrName)
            ov **= v
            setattr(self.obj, self.attrName, ov)
        return self

    def __iand__(self, v):
        try:
            self.obj.iandattr(self.attrName, v)
        except AttributeError:
            ov = getattr(self.obj, self.attrName)
            ov &= v
            setattr(self.obj, self.attrName, ov)
        return self

    def __ior__(self, v):
        try:
            self.obj.iorattr(self.attrName, v)
        except AttributeError:
            ov = getattr(self.obj, self.attrName)
            ov |= v
            setattr(self.obj, self.attrName, ov)
        return self

    def __ixor__(self, v):
        try:
            self.obj.ixorattr(self.attrName, v)
        except AttributeError:
            ov = getattr(self.obj, self.attrName)
            ov ^= v
            setattr(self.obj, self.attrName, ov)
        return self


class _ARRW:  # array write
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index

    def __lshift__(self, r):
        isUnproxyInstance
        if not IsEUDVariable(self.obj) and not isUnproxyInstance(self.obj, ConstExpr):
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
    def __init__(self, obj, attrName):
        self.obj = obj
        self.attrName = attrName

    def __eq__(self, k):
        try:
            return self.obj.eqattr(self.attrName, k)
        except AttributeError:
            return getattr(self.obj, self.attrName) == k

    def __ne__(self, k):
        try:
            return self.obj.neattr(self.attrName, k)
        except AttributeError:
            return getattr(self.obj, self.attrName) != k

    def __le__(self, k):
        try:
            return self.obj.leattr(self.attrName, k)
        except AttributeError:
            return getattr(self.obj, self.attrName) <= k

    def __lt__(self, k):
        try:
            return self.obj.ltattr(self.attrName, k)
        except AttributeError:
            return getattr(self.obj, self.attrName) < k

    def __ge__(self, k):
        try:
            return self.obj.geattr(self.attrName, k)
        except AttributeError:
            return getattr(self.obj, self.attrName) >= k

    def __gt__(self, k):
        try:
            return self.obj.gtattr(self.attrName, k)
        except AttributeError:
            return getattr(self.obj, self.attrName) > k


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


def _L2V(l):  # logic to value
    ret = EUDVariable()
    if EUDIf()(l):
        ret << 1
    if EUDElse()():
        ret << 0
    EUDEndIf()
    return ret


def _LVAR(vs):
    ret, ops = [], []
    for v in FlattenList(vs):
        if IsEUDVariable(v) and IsRValue(v):
            ret.append(v.makeL())
        else:
            nv = EUDVariable()
            ret.append(nv)
            ops.append((nv, SetTo, v))
    if ops:
        SeqCompute(ops)
    return List2Assignable(ret)


def _LSH(l, r):
    if IsEUDVariable(l):
        return f_bitlshift(l, r)
    else:
        return l << r
