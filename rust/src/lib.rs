mod allocator;
mod epscript;
mod eudobj;
mod types;

use pyo3::prelude::*;


#[pymodule]
fn _rust(py: pyo3::Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_submodule(&allocator::create_submodule(py)?)?;
    m.add_submodule(&epscript::create_submodule(py)?)?;
    m.add_submodule(&eudobj::create_submodule(py)?)?;
    Ok(())
}
