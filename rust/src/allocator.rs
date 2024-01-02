pub(crate) mod constexpr;
mod payload;
mod pbuffer;
pub(crate) mod rlocint;

pub(crate) fn create_submodule(py: pyo3::Python<'_>) -> pyo3::PyResult<&pyo3::types::PyModule> {
    let submod = pyo3::types::PyModule::new(py, "allocator")?;
    submod.add_class::<payload::ObjAllocator>()?;
    submod.add_class::<payload::PayloadBuilder>()?;
    submod.add_class::<pbuffer::PayloadBuffer>()?;

    submod.add_function(pyo3::wrap_pyfunction!(rlocint::py_rlocint, submod)?)?;
    submod.add_function(pyo3::wrap_pyfunction!(rlocint::to_rlocint, submod)?)?;
    submod.add_class::<rlocint::PyRlocInt>()?;

    submod.add_class::<constexpr::PyConstExpr>()?;
    submod.add_class::<constexpr::Forward>()?;
    submod.add_function(pyo3::wrap_pyfunction!(constexpr::evaluate, submod)?)?;
    submod.add_function(pyo3::wrap_pyfunction!(constexpr::is_constexpr, submod)?)?;

    Ok(submod)
}
