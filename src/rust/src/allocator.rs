pub(crate) mod constexpr;
mod payload;
mod pbuffer;
pub(crate) mod rlocint;

use pyo3::prelude::*;

#[pymodule]
#[pyo3(name = "allocator")]
pub(crate) mod allocator_mod {
    #[pymodule_export]
    use super::payload::{ObjAllocator, PayloadBuilder};
    #[pymodule_export]
    use super::pbuffer::PayloadBuffer;
    #[pymodule_export]
    use super::rlocint::{py_rlocint, to_rlocint, PyRlocInt};
    #[pymodule_export]
    use super::constexpr::{PyConstExpr, Forward, evaluate, is_constexpr};
}
 