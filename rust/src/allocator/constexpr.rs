use crate::allocator::rlocint::RlocInt;
use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyNone;
use std::sync::Arc;

// use crate::rlocint::RlocInt;

// div_floor is not stabilized yet
trait DivFloor {
    fn div_floor(&self, rhs: i32) -> i32;
}

impl DivFloor for i32 {
    fn div_floor(&self, rhs: i32) -> i32 {
        if rhs < 0 {
            -((-self).div_euclid(rhs))
        } else {
            self.div_euclid(rhs)
        }
    }
}

pub(crate) struct ConstExpr {
    baseobj: Option<Arc<Self>>,
    offset: i32,
    rlocmode: i32,
}

impl ConstExpr {
    fn new(baseobj: Option<Arc<Self>>, offset: i32, rlocmode: i32) -> Self {
        Self {
            baseobj,
            offset,
            rlocmode,
        }
    }
    fn evaluate(&self) -> RlocInt {
        if let Some(expr) = &self.baseobj {
            expr.evaluate() * self.rlocmode / 4 + self.offset
        } else {
            assert!(self.rlocmode == 0);
            RlocInt::new(self.offset, 0)
        }
    }
}

#[derive(Clone)]
#[pyclass(frozen, subclass, name = "ConstExpr")]
pub struct PyConstExpr(Arc<ConstExpr>);

#[pymethods]
impl PyConstExpr {
    #[new]
    #[pyo3(signature = (baseobj, offset=0, rlocmode=4))]
    fn new(baseobj: &PyAny, offset: i32, rlocmode: i32) -> PyResult<Self> {
        let expr = if let Ok(expr) = baseobj.extract::<PyConstExpr>() {
            ConstExpr::new(Some(expr.0.clone()), offset, rlocmode)
        } else if baseobj.is(PyNone::get(baseobj.py())) {
            assert!(rlocmode == 0);
            ConstExpr::new(None, offset, 0)
        } else {
            return Err(PyTypeError::new_err(format!("{baseobj} is not a ConstExpr")));
        };
        Ok(Self(Arc::new(expr)))
    }

    fn __add__(&self, rhs: i32) -> Self {
        Self(Arc::new(ConstExpr {
            baseobj: self.0.baseobj.clone(),
            offset: self.0.offset + rhs,
            rlocmode: self.0.rlocmode,
        }))
    }

    fn __radd__(&self, rhs: i32) -> Self {
        self.__add__(rhs)
    }

    fn __sub__(&self, rhs: i32) -> Self {
        Self(Arc::new(ConstExpr {
            baseobj: self.0.baseobj.clone(),
            offset: self.0.offset - rhs,
            rlocmode: self.0.rlocmode,
        }))
    }

    fn __rsub__(&self, rhs: i32) -> Self {
        Self(Arc::new(ConstExpr {
            baseobj: self.0.baseobj.clone(),
            offset: rhs - self.0.offset,
            rlocmode: -self.0.rlocmode,
        }))
    }

    fn __mul__(&self, rhs: i32) -> Self {
        Self(Arc::new(ConstExpr {
            baseobj: self.0.baseobj.clone(),
            offset: self.0.offset * rhs,
            rlocmode: self.0.rlocmode * rhs,
        }))
    }

    fn __rmul__(&self, rhs: i32) -> Self {
        self.__mul__(rhs)
    }

    fn __floordiv__(&self, rhs: i32) -> PyResult<Self> {
        if self.0.rlocmode != 0 && self.0.rlocmode % rhs != 0 {
            return Err(PyValueError::new_err("Address not divisible"));
        }
        Ok(Self(Arc::new(ConstExpr {
            baseobj: self.0.baseobj.clone(),
            offset: self.0.offset / rhs,
            rlocmode: self.0.rlocmode / rhs,
        })))
    }

    fn __mod__(&self, rhs: i32) -> PyResult<i32> {
        if self.0.rlocmode != 4 || 4 % rhs != 0 {
            return Err(PyValueError::new_err("Address not divisible"));
        }
        Ok(self.0.offset % rhs)
    }

    fn __divmod__(&self, rhs: i32) -> PyResult<(Self, i32)> {
        if self.0.rlocmode != 4 || 4 % rhs != 0 {
            return Err(PyValueError::new_err("Address not divisible"));
        }
        Ok((
            Self(Arc::new(ConstExpr {
                baseobj: self.0.baseobj.clone(),
                offset: self.0.offset / rhs,
                rlocmode: self.0.rlocmode / rhs,
            })),
            self.0.offset % rhs,
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
