mod allocator;
mod epscript;
mod eudobj;
mod mpqapi;
mod types;

use pyo3::prelude::*;

#[pymodule]
mod _rust {
    #[pymodule_export]
    use crate::allocator::allocator_mod;
    #[pymodule_export]
    use crate::epscript::epscript_mod;
    #[pymodule_export]
    use crate::eudobj::eudobj_mod;
    #[pymodule_export]
    use crate::mpqapi::mpqapi_mod;
}
