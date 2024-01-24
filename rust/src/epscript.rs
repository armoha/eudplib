use pyo3::types::PyModule;
use pyo3::{wrap_pyfunction, PyResult, Python};

mod linetable;

pub(crate) fn create_submodule(py: Python<'_>) -> PyResult<&PyModule> {
    let submod = PyModule::new(py, "epscript")?;
    submod.add_function(wrap_pyfunction!(linetable::generate_linetable, submod)?)?;

    Ok(submod)
}
