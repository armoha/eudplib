mod allocator;
mod epscript;
mod eudobj;
mod stormlib;
mod types;

use pyo3::prelude::*;

#[pymodule]
mod _rust {
    use pyo3::types::PyModuleMethods;

    #[pymodule_export]
    use crate::allocator::allocator_mod;
    #[pymodule_export]
    use crate::epscript::epscript_mod;
    #[pymodule_export]
    use crate::stormlib::stormlib_mod;
    #[pymodule_export]
    use crate::eudobj::eudobj_mod;
}
