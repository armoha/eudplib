use crate::allocator::constexpr::{ConstExpr, PyConstExpr};
use crate::types::GET_OBJECT_ADDR;
use pyo3::exceptions::PyNotImplementedError;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::PyNone;

/// Class for standalone object on memory
///
/// .. note::
///     Object collection occurs in three steps:
///
///     - Collecting phase : collects object used in map generation. Object
///     used in WritePayload method are being collected. Methods Evaluate
///     and WritePayload are called during this phase.
///     - Allocating phase : Object have their offset assigned. GetDataSize
///     method is called on this phase, so if GetDataSize is being called,
///     it means that every object required in map has been collected.
///     WritePayload and GetDataSize method should behave exactly the same as
///     it should on Writing phase here.
///     - Writing phase : Object is written into payload.
#[derive(Clone)]
#[pyclass(subclass, frozen, extends = PyConstExpr, name = "EUDObject", module = "eudplib.core.eudobj")]
pub struct PyEUDObject;

#[pymethods]
impl PyEUDObject {
    #[new]
    fn new(py: Python) -> (Self, PyConstExpr) {
        let expr = ConstExpr::new(PyNone::get_bound(py).into_py(py), 0, 4);
        (Self {}, PyConstExpr(expr))
    }

    /// Whether function is constructed dynamically.
    ///
    /// Dynamically constructed EUDObject may have their dependency list
    /// generated during object construction. So their dependency list is
    /// re-examined before allocation phase.
    #[allow(non_snake_case)]
    fn DynamicConstructed(&self) -> bool {
        false
    }

    /// What this object should be evaluated to when used in eudplib program.
    ///
    /// :return: Default) Memory address of this object.
    ///
    /// .. note::
    ///     In overriding this method, you can use
    ///     :func:`eudplib.GetObjectAddr`.
    #[allow(non_snake_case)]
    fn Evaluate(slf: PyRef<Self>, py: Python) -> PyResult<PyObject> {
        let get_object_addr = GET_OBJECT_ADDR.get(py)?;
        let addr = get_object_addr.call1((slf.into_py(py),))?;
        Ok(addr.into_py(py))
    }

    /// Memory size of object.
    #[allow(non_snake_case)]
    fn GetDataSize(&self) -> PyResult<usize> {
        Err(PyNotImplementedError::new_err(
            "GetDataSize must be overridden",
        ))
    }

    #[allow(non_snake_case)]
    fn CollectDependency(slf: Py<Self>, _pbuf: &Bound<'_, PyAny>) -> PyResult<()> {
        slf.call_method1(_pbuf.py(), intern!(_pbuf.py(), "WritePayload"), (_pbuf,))?;
        Ok(())
    }

    /// Write object
    #[allow(non_snake_case)]
    fn WritePayload(&self, _pbuf: &Bound<'_, PyAny>) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(
            "WritePayload must be overridden",
        ))
    }
}

pub(crate) fn create_submodule(py: Python<'_>) -> PyResult<Bound<'_, PyModule>> {
    let submod = PyModule::new_bound(py, "eudobj")?;
    submod.add_class::<PyEUDObject>()?;

    Ok(submod)
}
