use pyo3::prelude::*;

mod allocator;
mod types;

#[pymodule]
fn _rust(py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_submodule(allocator::create_submodule(py)?)?;
    Ok(())
}
