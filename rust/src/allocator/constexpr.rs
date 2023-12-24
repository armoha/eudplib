use crate::allocator::rlocint::{PyRlocInt, RlocInt};
use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::PyNone;

// use crate::rlocint::RlocInt;

// div_floor is not stabilized yet
trait DivFloor {
    fn div_floor(&self, rhs: i32) -> i32;
    fn divrem_floor(&self, rhs: i32) -> (i32, i32);
}

impl DivFloor for i32 {
    fn div_floor(&self, rhs: i32) -> i32 {
        if rhs < 0 {
            -((-self).div_euclid(rhs))
        } else {
            self.div_euclid(rhs)
        }
    }

    fn divrem_floor(&self, rhs: i32) -> (i32, i32) {
        if rhs < 0 {
            (-((-self).div_euclid(rhs)), -((-self).rem_euclid(rhs)))
        } else {
            (self.div_euclid(rhs), self.rem_euclid(rhs))
        }
    }
}

#[derive(Clone)]
pub(crate) struct ConstExpr {
    baseobj: PyObject,
    offset: i32,
    rlocmode: i32,
}

impl ConstExpr {
    fn new(baseobj: PyObject, offset: i32, rlocmode: i32) -> Self {
        Self {
            baseobj,
            offset,
            rlocmode,
        }
    }
    fn evaluate(&self, py: Python) -> PyResult<RlocInt> {
        if self.rlocmode == 0 {
            Ok(RlocInt::new(self.offset, 0))
        } else {
            Ok(self
                .baseobj
                .call_method0(py, intern!(py, "Evaluate"))?
                .extract::<PyRlocInt>(py)?
                .0
                * self.rlocmode
                / 4
                + self.offset)
        }
    }
}

#[derive(Clone)]
#[pyclass(frozen, subclass, name = "ConstExpr")]
pub struct PyConstExpr(ConstExpr);

#[pymethods]
impl PyConstExpr {
    #[new]
    #[pyo3(signature = (baseobj, offset=0, rlocmode=4))]
    fn new(baseobj: PyObject, offset: i32, rlocmode: i32) -> PyResult<Self> {
        Ok(Self(ConstExpr::new(baseobj, offset, rlocmode)))
    }

    fn __add__(slf: PyRef<Self>, py: Python, rhs: i32) -> Self {
        let offset = slf.0.offset + rhs;
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

    fn __radd__(slf: PyRef<Self>, py: Python, rhs: i32) -> Self {
        Self::__add__(slf, py, rhs)
    }

    fn __sub__(slf: PyRef<Self>, py: Python, rhs: i32) -> Self {
        let offset = slf.0.offset - rhs;
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

    fn __rsub__(slf: PyRef<Self>, py: Python, rhs: i32) -> Self {
        let offset = rhs - slf.0.offset;
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
        let offset = slf.0.offset.div_floor(rhs);
        let rlocmode = slf.0.rlocmode.div_floor(rhs);
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
        Ok(self.0.offset % rhs)
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
}

#[pyclass(extends = PyConstExpr)]
pub struct Forward {
    expr: Option<PyConstExpr>,
}

/*
#[pymethods]
impl Forward {
    #[new]
    fn new() -> (Self, PyConstExpr) {
        let expr = ConstExpr::new(Some(Arc::new(expr)), 0, 4);
        (Self { expr: None }, PyConstExpr(Arc::new(expr)))
    }
}
*/
