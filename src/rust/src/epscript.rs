use pyo3::prelude::*;

#[pymodule]
#[pyo3(name = "epscript")]
pub(crate) mod epscript_mod {
    #[pymodule_export]
    use eudplib_epscript::linetable::generate_linetable;
}
