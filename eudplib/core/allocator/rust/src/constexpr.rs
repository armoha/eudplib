use crate::rlocint::RlocInt;
use pyo3::create_exception;
use pyo3::prelude::*;
use std::sync::Arc;

create_exception!(allocator, AllocError, pyo3::exceptions::PyException);
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

#[pyclass(frozen, subclass)]
pub struct ConstExpr {
    baseobj: Option<Arc<ConstExpr>>,
    offset: i32,
    rlocmode: i32,
}

#[pymethods]
impl ConstExpr {
    #[new]
    #[pyo3(signature = (baseobj, offset=0, rlocmode=4))]
    fn new(baseobj: Option<&ConstExpr>, offset: i32, rlocmode: i32) -> Self {
        Self {
            baseobj: baseobj.map_or(None, |expr| expr.baseobj.clone()),
            offset,
            rlocmode,
        }
    }

    // fn Evaluate(&self) {
    //     if let Some(expr) = self.baseobj {
    //         expr.Evaluate()
    //     }
    // }
}

#[pyclass(extends=ConstExpr)]
struct ConstExprInt {}

#[pymethods]
impl ConstExprInt {
    #[new]
    fn new(value: i32) -> (Self, ConstExpr) {
        (Self {}, ConstExpr::new(None, value, 0))
    }

    fn Evaluate(self_: PyRef<'_, Self>) -> RlocInt {
        let super_ = self_.as_ref(); // Get &BaseClass
        RlocInt(super_.offset, 0)
    }
}

#[pyclass(extends=ConstExpr)]
struct Forward {}
