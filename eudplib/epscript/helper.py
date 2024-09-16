from types import ModuleType

from ..collections import EUDArray
from ..core import (
    ConstExpr,
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
    f_bitlshift,
)
from ..ctrlstru import EUDElse, EUDEndIf, EUDIf
from ..maprw import EUDOnStart
from ..memio import f_setcurpl2cpcache
from ..utils import (
    EPD,
    ExprProxy,
    FlattenList,
    List2Assignable,
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


def _RELIMP(path, mod_name):  # noqa: N802
    """relative path import"""
    import importlib
    import inspect
    import pathlib
    import sys

    abs_path = pathlib.Path(inspect.getabsfile(inspect.currentframe().f_back))
    pathsplit = path.split(".")
    if len(path) + 1 == len(pathsplit):  # path == '.' * len(path)
        pathsplit = pathsplit[1:]
    for s in pathsplit:
        if s == "":
            abs_path = abs_path.parent
        else:
            abs_path = abs_path / s

    abs_path = abs_path / mod_name
    abs_import = None
    # test if relative import can be converted to absolute import
    for parent in sys.path:
        try:
            abs_import = abs_path.relative_to(parent)
        except ValueError:
            continue
        else:
            break
    if abs_import is None:
        raise ImportError("attempted relative import beyond top-level package")
    else:
        return importlib.import_module(str(abs_import).replace("\\", "."))


def _TYGV(types, expr_list_gen):  # noqa: N802
    PushTriggerScope()
    init_start = NextTrigger()
    values = expr_list_gen()
    var_list = []
    for ty, value in zip(types, values):
        is_eudvar = IsEUDVariable(value)
        is_untyped = ty is None or issubclass(ty, EUDVariable)
        if not is_untyped:
            value = ty.cast(value)
        if not is_eudvar:
            value = EUDVariable(value)
            if not is_untyped:
                value = ty.cast(value)
        var_list.append(value)
    nptr = Forward()
    SetNextTrigger(nptr)
    PopTriggerScope()

    def _init_global_var() -> None:
        nonlocal nptr
        SetNextTrigger(init_start)
        nptr << NextTrigger()

    EUDOnStart(_init_global_var)
    return List2Assignable(var_list)


def _TYSV(types, vs):  # noqa: N802
    var_list = []
    for ty, v in zip(types, vs):
        is_untyped = ty is None or issubclass(ty, EUDVariable)
        if not is_untyped:
            v = ty.cast(v)
        value = EUDVariable(v)
        if not is_untyped:
            value = ty.cast(value)
        var_list.append(value)
    return List2Assignable(var_list)


def _TYLV(types, vs):  # noqa: N802
    from ..core.variable.eudv import _yield_and_check_rvalue

    ret, ops = [], []
    for ty, v_and_is_rvalue in zip(types, _yield_and_check_rvalue(vs, 1)):
        is_untyped = ty is None or issubclass(ty, EUDVariable)
        v, is_rvalue = v_and_is_rvalue
        is_eudvar = IsEUDVariable(v)
        if is_eudvar and is_rvalue:
            nv = v.makeL()
        else:
            if not is_untyped:
                v = ty.cast(v)
            nv = EUDVariable()
            ops.append((nv, SetTo, v))
        if not is_untyped:
            nv = ty.cast(nv)
        ret.append(nv)
    if ops:
        SeqCompute(ops)
    return List2Assignable(ret)


def _CGFW(exprf, retn):  # noqa: N802
    PushTriggerScope()
    start = NextTrigger()
    try:
        rets = exprf()
    except NameError:
        rets = [ExprProxy(None) for _ in range(retn)]

        def _init_global_const():
            vals = exprf()
            for ret, val in zip(rets, vals):
                ret._value = val

        EUDOnStart(_init_global_const)
    end = Forward()
    SetNextTrigger(end)
    PopTriggerScope()

    def _init():
        nonlocal end
        SetNextTrigger(start)
        end << NextTrigger()

    EUDOnStart(_init)
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
