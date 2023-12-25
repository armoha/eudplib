use pyo3::prelude::*;

mod constexpr;
mod payload;
mod pbuffer;
mod rlocint;

pub(crate) fn create_submodule(py: Python<'_>) -> PyResult<&PyModule> {
    let submod = PyModule::new(py, "allocator")?;
    submod.add_class::<payload::ObjAllocator>()?;
    submod.add_class::<payload::PayloadBuilder>()?;
    submod.add_class::<pbuffer::PayloadBuffer>()?;

    submod.add_function(wrap_pyfunction!(rlocint::py_rlocint, submod)?)?;
    submod.add_function(wrap_pyfunction!(rlocint::to_rlocint, submod)?)?;
    submod.add_class::<rlocint::PyRlocInt>()?;

    submod.add_class::<constexpr::PyConstExpr>()?;
    submod.add_class::<constexpr::Forward>()?;
    submod.add_function(wrap_pyfunction!(constexpr::evaluate, submod)?)?;
    submod.add_function(wrap_pyfunction!(constexpr::is_constexpr, submod)?)?;

    Ok(submod)
}
