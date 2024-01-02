use pyo3::types::PyModule;
use pyo3::{wrap_pyfunction, PyResult, Python};

mod linetable;

pub(crate) fn create_submodule(py: Python<'_>) -> PyResult<&PyModule> {
    let submod = PyModule::new(py, "epscript")?;
    submod.add_function(wrap_pyfunction!(linetable::calculate_linetable, submod)?)?;
    submod.add_function(wrap_pyfunction!(linetable::print_linetable, submod)?)?;

    Ok(submod)
}
