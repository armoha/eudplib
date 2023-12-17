use pyo3::prelude::*;

mod rlocint;
mod constexpr;

#[pyfunction]
fn stack_objects(found_objects: PyDict, dwoccupmap_dict: PyDict, alloctable: PyDict) {
}

#[pymodule]
fn _rust(py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(stack_objects, module)?)?;
    m.add_class::<constexpr::ConstExpr>()?;
    Ok(())
}
