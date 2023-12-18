use pyo3::prelude::*;

mod rlocint;
mod constexpr;
mod payload;

pub(crate) fn create_submodule(py: Python<'_>) -> PyResult<&PyModule> {
    let submod = PyModule::new(py, "allocator")?;
    submod.add_function(wrap_pyfunction!(payload::alloc_objects, submod)?)?;
    submod.add_class::<payload::ObjAllocator>()?;
    submod.add_class::<constexpr::ConstExpr>()?;

    Ok(submod)
}
