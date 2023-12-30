mod allocator;
mod eudobj;
mod types;

#[pyo3::pymodule]
fn _rust(py: pyo3::Python<'_>, m: &pyo3::types::PyModule) -> pyo3::PyResult<()> {
    m.add_submodule(allocator::create_submodule(py)?)?;
    m.add_submodule(eudobj::create_submodule(py)?)?;
    Ok(())
}
