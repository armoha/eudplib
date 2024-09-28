use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::prelude::*;
use std::fmt;
use std::ops::{Add, Div, Mul, Rem, Sub};

// div_floor is not stabilized yet
pub(crate) trait DivFloor {
    type Num;
    fn div_floor(&self, rhs: Self::Num) -> Self::Num;
    fn rem_floor(&self, rhs: Self::Num) -> Self::Num;
    fn divrem_floor(&self, rhs: Self::Num) -> (Self::Num, Self::Num);
}

impl DivFloor for i32 {
    type Num = i32;

    fn div_floor(&self, rhs: i32) -> i32 {
        if rhs < 0 {
            -((-self).div_euclid(rhs))
        } else {
            self.div_euclid(rhs)
        }
    }

    fn rem_floor(&self, rhs: i32) -> i32 {
        let quotient = if rhs < 0 {
            -((-self).div_euclid(rhs))
        } else {
            self.div_euclid(rhs)
        };
        self - quotient * rhs
    }

    fn divrem_floor(&self, rhs: i32) -> (i32, i32) {
        let quotient = if rhs < 0 {
            -((-self).div_euclid(rhs))
        } else {
            self.div_euclid(rhs)
        };
        (quotient, self - quotient * rhs)
    }
}

impl DivFloor for i64 {
    type Num = i64;

    fn div_floor(&self, rhs: i64) -> i64 {
        if rhs < 0 {
            -((-self).div_euclid(rhs))
        } else {
            self.div_euclid(rhs)
        }
    }

    fn rem_floor(&self, rhs: i64) -> i64 {
        let quotient = if rhs < 0 {
            -((-self).div_euclid(rhs))
        } else {
            self.div_euclid(rhs)
        };
        self - quotient * rhs
    }

    fn divrem_floor(&self, rhs: i64) -> (i64, i64) {
        let quotient = if rhs < 0 {
            -((-self).div_euclid(rhs))
        } else {
            self.div_euclid(rhs)
        };
        (quotient, self - quotient * rhs)
    }
}

#[derive(Clone, Debug)]
pub(crate) struct RlocInt {
    pub(crate) offset: i32,
    pub(crate) rlocmode: i32,
}

impl RlocInt {
    pub(crate) fn new(offset: i32, rlocmode: i32) -> Self {
        Self { offset, rlocmode }
    }
}

/// Relocatable int
#[derive(Clone)]
#[pyclass(frozen, name = "RlocInt_C", module = "eudplib.core.allocator")]
pub struct PyRlocInt(pub(crate) RlocInt);

#[pymethods]
impl PyRlocInt {
    #[new]
    fn new(offset: i32, rlocmode: i32) -> Self {
        Self(RlocInt::new(offset, rlocmode))
    }

    #[getter]
    fn offset(&self) -> i32 {
        self.0.offset
    }

    #[getter]
    fn rlocmode(&self) -> i32 {
        self.0.rlocmode
    }

    fn __repr__(&self) -> String {
        format!("{:?}", self.0)
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn __add__(&self, rhs: &Bound<'_, PyAny>) -> PyResult<PyRlocInt> {
        let rlocint = if let Ok(rhs) = rhs.extract::<PyRlocInt>() {
            RlocInt::new(
                self.0.offset + rhs.0.offset,
                self.0.rlocmode + rhs.0.rlocmode,
            )
        } else if let Ok(rhs) = rhs.extract::<i32>() {
            RlocInt::new(self.0.offset + rhs, self.0.rlocmode)
        } else {
            return Err(PyTypeError::new_err(format!(
                "unsupported operand type(s) for +: 'eudplib.core.allocator.RlocInt_C' and '{rhs}'"
            )));
        };
        Ok(PyRlocInt(rlocint))
    }

    fn __radd__(&self, rhs: &Bound<'_, PyAny>) -> PyResult<PyRlocInt> {
        self.__add__(rhs)
    }

    fn __sub__(&self, rhs: &Bound<'_, PyAny>) -> PyResult<PyRlocInt> {
        let rlocint = if let Ok(rhs) = rhs.extract::<PyRlocInt>() {
            RlocInt::new(
                self.0.offset - rhs.0.offset,
                self.0.rlocmode - rhs.0.rlocmode,
            )
        } else if let Ok(rhs) = rhs.extract::<i32>() {
            RlocInt::new(self.0.offset - rhs, self.0.rlocmode)
        } else {
            return Err(PyTypeError::new_err(format!(
                "unsupported operand type(s) for -: 'eudplib.core.allocator.RlocInt_C' and '{rhs}'"
            )));
        };
        Ok(PyRlocInt(rlocint))
    }

    fn __rsub__(&self, rhs: &Bound<'_, PyAny>) -> PyResult<PyRlocInt> {
        let rlocint = if let Ok(rhs) = rhs.extract::<PyRlocInt>() {
            RlocInt::new(
                rhs.0.offset - self.0.offset,
                rhs.0.rlocmode - self.0.rlocmode,
            )
        } else if let Ok(rhs) = rhs.extract::<i32>() {
            RlocInt::new(rhs - self.0.offset, -self.0.rlocmode)
        } else {
            return Err(PyTypeError::new_err(format!(
                "unsupported operand type(s) for -: 'eudplib.core.allocator.RlocInt_C' and '{rhs}'"
            )));
        };
        Ok(PyRlocInt(rlocint))
    }

    fn __mul__(&self, rhs: &Bound<'_, PyAny>) -> PyResult<PyRlocInt> {
        let rhs = if let Ok(rhs) = rhs.extract::<PyRlocInt>() {
            if rhs.0.rlocmode != 0 {
                return Err(PyTypeError::new_err(
                    "Cannot multiply RlocInt with non-const",
                ));
            }
            rhs.0.offset
        } else if let Ok(rhs) = rhs.extract::<i32>() {
            rhs
        } else {
            return Err(PyTypeError::new_err(format!(
                "unsupported operand type(s) for *: 'eudplib.core.allocator.RlocInt_C' and '{rhs}'"
            )));
        };
        Ok(PyRlocInt(RlocInt::new(
            self.0.offset * rhs,
            self.0.rlocmode * rhs,
        )))
    }

    fn __rmul__(&self, rhs: &Bound<'_, PyAny>) -> PyResult<PyRlocInt> {
        self.__mul__(rhs)
    }

    fn __floordiv__(&self, rhs: &Bound<'_, PyAny>) -> PyResult<PyRlocInt> {
        let rhs = if let Ok(rhs) = rhs.extract::<PyRlocInt>() {
            if rhs.0.rlocmode != 0 {
                return Err(PyTypeError::new_err("Cannot divide RlocInt with non-const"));
            }
            rhs.0.offset
        } else if let Ok(rhs) = rhs.extract::<i32>() {
            rhs
        } else {
            return Err(PyTypeError::new_err(format!(
                "unsupported operand type(s) for *: 'eudplib.core.allocator.RlocInt_C' and '{rhs}'"
            )));
        };
        Ok(PyRlocInt(RlocInt::new(
            DivFloor::div_floor(&self.0.offset, rhs),
            DivFloor::div_floor(&self.0.rlocmode, rhs),
        )))
    }

    fn __and__(&self, rhs: &Bound<'_, PyAny>) -> PyResult<PyRlocInt> {
        if self.0.rlocmode != 0 && self.0.rlocmode != 4 {
            return Err(PyValueError::new_err(format!(
                "unsupported rlocmode for &: '{}'",
                self.0.rlocmode
            )));
        }
        let rlocint = if let Ok(rhs) = rhs.extract::<PyRlocInt>() {
            if self.0.rlocmode != 0 || rhs.0.rlocmode != 0 {
                return Err(PyTypeError::new_err(
                    "Cannot bitwise & RlocInt with non-const",
                ));
            }
            RlocInt::new(self.0.offset & rhs.0.offset, 0)
        } else if let Ok(rhs) = rhs.extract::<i32>() {
            if self.0.rlocmode == 4 && rhs & 3 != rhs {
                return Err(PyValueError::new_err(format!(
                    "non-const ptr RlocInt can only compute bitwise & from 0 to 3"
                )));
            }
            RlocInt::new(self.0.offset & rhs, self.0.rlocmode)
        } else {
            return Err(PyTypeError::new_err(format!(
                "unsupported operand type(s) for &: 'eudplib.core.allocator.RlocInt_C' and '{rhs}'"
            )));
        };
        Ok(PyRlocInt(rlocint))
    }

    fn __rand__(&self, rhs: &Bound<'_, PyAny>) -> PyResult<PyRlocInt> {
        self.__and__(rhs)
    }

    fn __or__(&self, rhs: &Bound<'_, PyAny>) -> PyResult<PyRlocInt> {
        if self.0.rlocmode != 0 && self.0.rlocmode != 4 {
            return Err(PyValueError::new_err(format!(
                "unsupported rlocmode for |: '{}'",
                self.0.rlocmode
            )));
        }
        let rlocint = if let Ok(rhs) = rhs.extract::<PyRlocInt>() {
            if self.0.rlocmode != 0 || rhs.0.rlocmode != 0 {
                return Err(PyTypeError::new_err(
                    "Cannot bitwise | RlocInt with non-const",
                ));
            }
            RlocInt::new(self.0.offset | rhs.0.offset, 0)
        } else if let Ok(rhs) = rhs.extract::<i32>() {
            if self.0.rlocmode == 4 && rhs & 3 != rhs {
                return Err(PyValueError::new_err(format!(
                    "non-const ptr RlocInt can only compute bitwise | from 0 to 3"
                )));
            }
            RlocInt::new(self.0.offset | rhs, self.0.rlocmode)
        } else {
            return Err(PyTypeError::new_err(format!(
                "unsupported operand type(s) for &: 'eudplib.core.allocator.RlocInt_C' and '{rhs}'"
            )));
        };
        Ok(PyRlocInt(rlocint))
    }

    fn __ror__(&self, rhs: &Bound<'_, PyAny>) -> PyResult<PyRlocInt> {
        self.__and__(rhs)
    }

    fn __invert__(&self) -> PyResult<PyRlocInt> {
        if self.0.rlocmode != 0 {
            return Err(PyValueError::new_err(format!(
                "unsupported rlocmode for ~: '{}'",
                self.0.rlocmode
            )));
        }
        Ok(PyRlocInt(RlocInt::new(!self.0.offset, 0)))
    }

    fn __neg__(&self) -> PyResult<PyRlocInt> {
        if self.0.rlocmode != 0 && self.0.rlocmode != 4 {
            return Err(PyValueError::new_err(format!(
                "unsupported rlocmode for -: '{}'",
                self.0.rlocmode
            )));
        }
        Ok(PyRlocInt(RlocInt::new(-self.0.offset, 0)))
    }

    fn _is_aligned_ptr(&self) -> bool {
        self.0.rlocmode == 4 && self.0.offset % 4 == 0
    }

    fn _is_ptr(&self) -> bool {
        self.0.rlocmode == 4
    }

    fn _is_epd(&self) -> bool {
        self.0.rlocmode == 1
    }
}

impl fmt::Display for RlocInt {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        // Write strictly the first element into the supplied output
        // stream: `f`. Returns `fmt::Result` which indicates whether the
        // operation succeeded or failed. Note that `write!` uses syntax which
        // is very similar to `println!`.
        write!(f, "RlocInt({:#08X}, {})", self.offset, self.rlocmode)
    }
}

impl Add<RlocInt> for RlocInt {
    type Output = Self;

    fn add(self, other: Self) -> Self {
        Self {
            offset: self.offset.wrapping_add(other.offset),
            rlocmode: self.rlocmode.wrapping_add(other.rlocmode),
        }
    }
}

impl Add<i32> for RlocInt {
    type Output = Self;

    fn add(self, other: i32) -> Self {
        Self {
            offset: self.offset.wrapping_add(other),
            rlocmode: self.rlocmode,
        }
    }
}

impl Add<RlocInt> for i32 {
    type Output = RlocInt;

    fn add(self, other: RlocInt) -> RlocInt {
        RlocInt {
            offset: self.wrapping_add(other.offset),
            rlocmode: other.rlocmode,
        }
    }
}

impl Sub<RlocInt> for RlocInt {
    type Output = Self;

    fn sub(self, other: Self) -> Self {
        Self {
            offset: self.offset.wrapping_sub(other.offset),
            rlocmode: self.rlocmode.wrapping_sub(other.rlocmode),
        }
    }
}

impl Sub<i32> for RlocInt {
    type Output = Self;

    fn sub(self, other: i32) -> Self {
        Self {
            offset: self.offset.wrapping_sub(other),
            rlocmode: self.rlocmode,
        }
    }
}

impl Sub<RlocInt> for i32 {
    type Output = RlocInt;

    fn sub(self, other: RlocInt) -> RlocInt {
        RlocInt {
            offset: self.wrapping_sub(other.offset),
            rlocmode: -other.rlocmode,
        }
    }
}

impl Mul<RlocInt> for RlocInt {
    type Output = Self;

    fn mul(self, other: Self) -> Self {
        assert!(
            other.rlocmode == 0,
            "Cannot multiply RlocInt with non-const"
        );
        Self {
            offset: self.offset.wrapping_mul(other.offset),
            rlocmode: self.rlocmode.wrapping_mul(other.offset),
        }
    }
}

impl Mul<i32> for RlocInt {
    type Output = Self;

    fn mul(self, other: i32) -> Self {
        Self {
            offset: self.offset.wrapping_mul(other),
            rlocmode: self.rlocmode.wrapping_mul(other),
        }
    }
}

impl Mul<RlocInt> for i32 {
    type Output = RlocInt;

    fn mul(self, other: RlocInt) -> RlocInt {
        RlocInt {
            offset: self.wrapping_mul(other.offset),
            rlocmode: self.wrapping_mul(other.rlocmode),
        }
    }
}

impl Div<RlocInt> for RlocInt {
    type Output = Self;

    fn div(self, other: Self) -> Self {
        assert!(other.rlocmode == 0, "Cannot divide RlocInt with non-const");
        assert!(other.offset != 0, "Divide by zero");
        assert!(
            self.rlocmode == 0
                || (self.offset % other.offset == 0 && self.rlocmode % other.offset == 0),
            "{self} is not divisible by {other}"
        );
        Self {
            offset: DivFloor::div_floor(&self.offset, other.offset),
            rlocmode: DivFloor::div_floor(&self.rlocmode, other.offset),
        }
    }
}

impl Div<i32> for RlocInt {
    type Output = Self;

    fn div(self, other: i32) -> Self {
        assert!(other != 0, "Divide by zero");
        assert!(
            self.rlocmode == 0 || (self.offset % other == 0 && self.rlocmode % other == 0),
            "{self} is not divisible by {other}"
        );
        Self {
            offset: DivFloor::div_floor(&self.offset, other),
            rlocmode: DivFloor::div_floor(&self.rlocmode, other),
        }
    }
}

impl Div<RlocInt> for i32 {
    type Output = i32;

    fn div(self, other: RlocInt) -> i32 {
        assert!(other.rlocmode == 0, "Cannot divide RlocInt with non-const");
        assert!(other.offset != 0, "Divide by zero");
        assert!(
            self % other.offset == 0,
            "{self} is not divisible by {other}"
        );
        DivFloor::div_floor(&self, other.offset)
    }
}

impl Rem<RlocInt> for RlocInt {
    type Output = Self;

    fn rem(self, other: Self) -> Self {
        assert!(other.rlocmode == 0, "Cannot divide RlocInt with non-const");
        assert!(other.offset != 0, "Divide by zero");
        assert!(
            self.rlocmode == 0
                || (self.offset % other.offset == 0 && self.rlocmode % other.offset == 0),
            "{self} is not divisible by {other}"
        );
        Self {
            offset: self.offset / other.offset,
            rlocmode: self.rlocmode / other.offset,
        }
    }
}

impl Rem<i32> for RlocInt {
    type Output = Self;

    fn rem(self, other: i32) -> Self {
        assert!(other != 0, "Divide by zero");
        assert!(
            self.rlocmode == 0 || (self.offset % other == 0 && self.rlocmode % other == 0),
            "{self} is not divisible by {other}"
        );
        Self {
            offset: self.offset / other,
            rlocmode: self.rlocmode / other,
        }
    }
}

impl Rem<RlocInt> for i32 {
    type Output = i32;

    fn rem(self, other: RlocInt) -> i32 {
        assert!(other.rlocmode == 0, "Cannot divide RlocInt with non-const");
        assert!(other.offset != 0, "Divide by zero");
        assert!(
            self % other.offset == 0,
            "{self} is not divisible by {other}"
        );
        self / other.offset
    }
}

#[pyfunction]
#[pyo3(name = "RlocInt")]
pub fn py_rlocint(offset: i64, rlocmode: i32) -> PyRlocInt {
    PyRlocInt::new(offset as i32, rlocmode)
}

/// Convert int/RlocInt to rlocint
#[pyfunction]
#[pyo3(name = "toRlocInt")]
pub fn to_rlocint(x: &Bound<'_, PyAny>) -> PyResult<PyRlocInt> {
    let expr = if let Ok(expr) = x.extract::<PyRlocInt>() {
        expr.0
    } else if let Ok(expr) = x.extract::<i64>() {
        RlocInt {
            offset: expr as i32,
            rlocmode: 0,
        }
    } else {
        return Err(PyTypeError::new_err(format!("Unsupported type: {x}")));
    };
    Ok(PyRlocInt(expr))
}
