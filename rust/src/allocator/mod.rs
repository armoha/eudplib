use pyo3::prelude::*;

mod constexpr;
mod payload;
mod pbuffer;
mod rlocint;

pub(crate) fn create_submodule(py: Python<'_>) -> PyResult<&PyModule> {
    let submod = PyModule::new(py, "allocator")?;
    submod.add_function(wrap_pyfunction!(payload::alloc_objects, submod)?)?;
    submod.add_class::<payload::ObjAllocator>()?;
    submod.add_class::<pbuffer::PayloadBuffer>()?;

    submod.add_function(wrap_pyfunction!(rlocint::RlocInt, submod)?)?;
    submod.add_class::<rlocint::RlocInt_C>()?;

    submod.add_class::<constexpr::ConstExpr>()?;

    Ok(submod)
}
