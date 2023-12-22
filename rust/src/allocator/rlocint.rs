use pyo3::exceptions::PyTypeError;
use pyo3::prelude::*;
use std::fmt;
use std::ops::{Add, Div, Mul, Rem, Sub};

#[derive(Clone)]
pub(crate) struct RlocInt {
    offset: i32,
    rlocmode: i32,
}

impl RlocInt {
    pub(crate) fn new(offset: i32, rlocmode: i32) -> Self {
        Self { offset, rlocmode }
    }
}

/// Relocatable int
#[derive(Clone)]
#[pyclass(frozen, name = "RlocInt_C")]
pub struct PyRlocInt(RlocInt);

#[pymethods]
impl PyRlocInt {
    #[new]
    fn new(offset: i32, rlocmode: i32) -> Self {
        Self(RlocInt::new(offset, rlocmode))
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
            offset: self.offset / other.offset,
            rlocmode: self.rlocmode / other.offset,
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
            offset: self.offset / other,
            rlocmode: self.rlocmode / other,
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
        self / other.offset
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
pub fn py_rlocint(offset: i32, rlocmode: i32) -> PyRlocInt {
    PyRlocInt::new(offset, rlocmode)
}

#[pyfunction]
#[pyo3(name = "toRlocInt")]
pub fn to_rlocint(x: &PyAny) -> PyResult<PyRlocInt> {
    let expr = if let Ok(expr) = x.extract::<PyRlocInt>() {
        expr.0
    } else if let Ok(expr) = x.extract::<i32>() {
        RlocInt {
            offset: expr,
            rlocmode: 0,
        }
    } else {
        return Err(PyTypeError::new_err(format!("Unsupported type: {x}")));
    };
    Ok(PyRlocInt(expr))
}
