use pyo3::prelude::*;

mod linetable;

pub(crate) fn create_submodule(py: Python<'_>) -> PyResult<Bound<'_, PyModule>> {
    let submod = PyModule::new_bound(py, "epscript")?;
    submod.add_function(wrap_pyfunction!(linetable::generate_linetable, &submod)?)?;

    Ok(submod)
}
