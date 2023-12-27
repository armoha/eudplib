use crate::allocator::rlocint::{PyRlocInt, RlocInt, DivFloor};
use crate::types::EXPRPROXY;
use pyo3::exceptions::{PyAttributeError, PyRuntimeError, PyValueError};
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyInt, PyNone, PyString, PyTuple};

#[derive(Clone, Debug)]
pub(crate) struct ConstExpr {
    baseobj: PyObject,
    offset: i32,
    rlocmode: i32,
}

impl ConstExpr {
    pub(crate) fn new(baseobj: PyObject, offset: i32, rlocmode: i32) -> Self {
        Self {
            baseobj,
            offset,
            rlocmode,
        }
    }
}

/// Class for general expression with rlocints.
#[derive(Clone)]
#[pyclass(
    frozen,
    subclass,
    name = "ConstExpr",
    module = "eudplib.core.allocator"
)]
pub struct PyConstExpr(pub(crate) ConstExpr);

#[pymethods]
impl PyConstExpr {
    #[new]
    #[pyo3(signature = (baseobj, offset=0, rlocmode=4))]
    fn new(baseobj: PyObject, offset: i32, rlocmode: i32) -> PyResult<Self> {
        Ok(Self(ConstExpr::new(baseobj, offset, rlocmode)))
    }

    #[allow(non_snake_case)]
    fn Evaluate(&self, py: Python) -> PyResult<PyRlocInt> {
        let rlocint = if self.0.rlocmode == 0 {
            RlocInt::new(self.0.offset, 0)
        } else {
            self.0
                .baseobj
                .call_method0(py, intern!(py, "Evaluate"))?
                .extract::<PyRlocInt>(py)?
                .0
                * self.0.rlocmode
                / 4
                + self.0.offset
        };
        Ok(PyRlocInt(rlocint))
    }

    fn __repr__(&self) -> String {
        format!("{:?}", self.0)
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn __int__(&self, py: Python) -> PyResult<i32> {
        if self.0.rlocmode == 0 && self.0.baseobj.is_none(py) {
            Ok(self.0.offset)
        } else {
            Err(PyValueError::new_err(
                "int(ConstExpr) failed because ConstExpr has baseobj",
            ))
        }
    }

    fn __add__(slf: PyRef<Self>, py: Python, rhs: i64) -> Self {
        let offset = slf.0.offset + rhs as i32;
        let rlocmode = slf.0.rlocmode;
        Self(ConstExpr {
            baseobj: if rlocmode != 0 && slf.0.baseobj.is_none(py) {
                slf.into_py(py)
            } else {
                slf.0.baseobj.clone_ref(py)
            },
            offset,
            rlocmode,
        })
    }

    fn __radd__(slf: PyRef<Self>, py: Python, rhs: i64) -> Self {
        Self::__add__(slf, py, rhs)
    }

    fn __sub__(slf: PyRef<Self>, py: Python, rhs: i64) -> Self {
        let offset = slf.0.offset - rhs as i32;
        let rlocmode = slf.0.rlocmode;
        Self(ConstExpr {
            baseobj: if rlocmode != 0 && slf.0.baseobj.is_none(py) {
                slf.into_py(py)
            } else {
                slf.0.baseobj.clone_ref(py)
            },
            offset,
            rlocmode,
        })
    }

    fn __rsub__(slf: PyRef<Self>, py: Python, rhs: i64) -> Self {
        let offset = rhs as i32 - slf.0.offset;
        let rlocmode = -slf.0.rlocmode;
        Self(ConstExpr {
            baseobj: if rlocmode != 0 && slf.0.baseobj.is_none(py) {
                slf.into_py(py)
            } else {
                slf.0.baseobj.clone_ref(py)
            },
            offset,
            rlocmode,
        })
    }

    fn __mul__(slf: PyRef<Self>, py: Python, rhs: i32) -> Self {
        let offset = slf.0.offset * rhs;
        let rlocmode = slf.0.rlocmode * rhs;
        Self(ConstExpr {
            baseobj: if rlocmode != 0 && slf.0.baseobj.is_none(py) {
                slf.into_py(py)
            } else if rlocmode == 0 {
                PyNone::get(py).into()
            } else {
                slf.0.baseobj.clone_ref(py)
            },
            offset,
            rlocmode,
        })
    }

    fn __rmul__(slf: PyRef<Self>, py: Python, rhs: i32) -> Self {
        Self::__mul__(slf, py, rhs)
    }

    fn __floordiv__(slf: PyRef<Self>, py: Python, rhs: i32) -> PyResult<Self> {
        if slf.0.rlocmode != 0 && slf.0.rlocmode % rhs != 0 {
            return Err(PyValueError::new_err("Address not divisible"));
        }
        let offset = DivFloor::div_floor(&slf.0.offset, rhs);
        let rlocmode = DivFloor::div_floor(&slf.0.rlocmode, rhs);
        Ok(Self(ConstExpr {
            baseobj: if rlocmode != 0 && slf.0.baseobj.is_none(py) {
                slf.into_py(py)
            } else {
                slf.0.baseobj.clone_ref(py)
            },
            offset,
            rlocmode,
        }))
    }

    fn __mod__(&self, rhs: i32) -> PyResult<i32> {
        if self.0.rlocmode != 4 || 4 % rhs != 0 {
            return Err(PyValueError::new_err("Address not divisible"));
        }
        Ok(DivFloor::rem_floor(&self.0.offset, rhs))
    }

    fn __divmod__(slf: PyRef<Self>, py: Python, rhs: i32) -> PyResult<(Self, i32)> {
        if slf.0.rlocmode != 4 || 4 % rhs != 0 {
            return Err(PyValueError::new_err("Address not divisible"));
        }
        let (offset, modulo) = slf.0.offset.divrem_floor(rhs);
        let rlocmode = slf.0.rlocmode / rhs;
        Ok((
            Self(ConstExpr {
                baseobj: if rlocmode != 0 && slf.0.baseobj.is_none(py) {
                    slf.into_py(py)
                } else {
                    slf.0.baseobj.clone_ref(py)
                },
                offset,
                rlocmode,
            }),
            modulo,
        ))
    }

    fn __neg__(&self) -> Self {
        Self(ConstExpr {
            baseobj: self.0.baseobj.clone(),
            offset: -self.0.offset,
            rlocmode: -self.0.rlocmode,
        })
    }

    fn _is_aligned_ptr(&self) -> bool {
        self.0.rlocmode == 4 && self.0.offset % 4 == 0
    }

    fn _is_epd(&self) -> bool {
        self.0.rlocmode == 1
    }
}

/// Class for forward definition.
#[pyclass(extends = PyConstExpr, module = "eudplib.core.allocator")]
pub struct Forward {
    expr: PyObject,
}

#[pymethods]
impl Forward {
    #[new]
    fn new(py: Python) -> (Self, PyConstExpr) {
        let expr = ConstExpr::new(PyNone::get(py).into(), 0, 4);
        (
            Self {
                expr: PyNone::get(py).into(),
            },
            PyConstExpr(expr),
        )
    }

    #[getter]
    fn get_expr(&self) -> PyResult<PyObject> {
        Ok(self.expr.clone())
    }

    fn __lshift__(&mut self, py: Python, expr: PyObject) -> PyResult<PyObject> {
        if !self.expr.is_none(py) {
            return Err(PyAttributeError::new_err(
                "Reforwarding without reset is not allowed",
            ));
        }
        if expr.is_none(py) {
            return Err(PyValueError::new_err("Cannot forward to None"));
        }
        let mut expr = expr.as_ref(py);
        let exprproxy = EXPRPROXY.get(py)?;
        while expr.is_instance(exprproxy)? {
            expr = expr.getattr(intern!(py, "_value"))?;
        }
        let expr: Py<PyAny> = if let Ok(offset) = expr.extract::<i32>() {
            PyConstExpr(ConstExpr::new(PyNone::get(py).into(), offset, 0)).into_py(py)
        } else {
            expr.into_py(py)
        };
        self.expr = expr.clone();
        Ok(expr)
    }

    #[allow(non_snake_case)]
    fn IsSet(&self, py: Python) -> bool {
        !self.expr.is_none(py)
    }

    #[allow(non_snake_case)]
    fn Reset(&mut self, py: Python) {
        self.expr = PyNone::get(py).into()
    }

    #[allow(non_snake_case)]
    fn Evaluate(&self, py: Python) -> PyResult<PyRlocInt> {
        if self.expr.is_none(py) {
            return Err(PyRuntimeError::new_err("Forward not initialized"));
        }
        self.expr
            .call_method0(py, intern!(py, "Evaluate"))?
            .extract::<PyRlocInt>(py)
    }

    #[pyo3(signature = (*py_args, **py_kwargs))]
    fn __call__(
        &self,
        py: Python,
        py_args: &PyTuple,
        py_kwargs: Option<&PyDict>,
    ) -> PyResult<PyObject> {
        self.expr.call(py, py_args, py_kwargs)
    }

    fn __getattr__(&self, py: Python, name: &PyString) -> PyResult<PyObject> {
        self.expr.getattr(py, name)
    }

    fn __getitem__(&self, py: Python, name: &PyAny) -> PyResult<PyObject> {
        Ok(self.expr.as_ref(py).get_item(name)?.into_py(py))
    }

    fn __setitem__(&self, py: Python, name: &PyAny, newvalue: PyObject) -> PyResult<()> {
        self.expr.as_ref(py).set_item(name, newvalue)
    }
}

/// Evaluate expressions
#[pyfunction]
#[pyo3(name = "Evaluate")]
pub fn evaluate(x: &PyAny) -> PyResult<PyRlocInt> {
    if let Ok(expr) = x.extract::<PyRlocInt>() {
        Ok(PyRlocInt(expr.0))
    } else if let Ok(expr) = x.extract::<i64>() {
        Ok(PyRlocInt(RlocInt::new(expr as i32, 0)))
    } else {
        let expr = x.call_method0(intern!(x.py(), "Evaluate"))?;
        expr.extract::<PyRlocInt>()
    }
}

#[pyfunction]
#[pyo3(name = "IsConstExpr")]
pub fn is_constexpr(mut x: &PyAny) -> PyResult<bool> {
    let exprproxy = EXPRPROXY.get(x.py())?;
    while x.is_instance(exprproxy)? {
        x = x.getattr(intern!(x.py(), "_value"))?;
    }
    Ok(x.is_instance_of::<PyInt>()
        || x.is_instance_of::<PyRlocInt>()
        || x.is_instance_of::<PyConstExpr>())
}
