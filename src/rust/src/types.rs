//! from https://github.com/pyca/cryptography/blob/main/src/rust/src/types.rs
use pyo3::prelude::*;
use pyo3::sync::GILOnceCell;

pub(crate) struct LazyPyImport {
    module: &'static str,
    names: &'static [&'static str],
    value: GILOnceCell<PyObject>,
}

impl LazyPyImport {
    pub(crate) const fn new(module: &'static str, names: &'static [&'static str]) -> LazyPyImport {
        LazyPyImport {
            module,
            names,
            value: GILOnceCell::new(),
        }
    }

    pub(crate) fn get<'p>(&'p self, py: Python<'p>) -> PyResult<Bound<'p, PyAny>> {
        let p = self.value.get_or_try_init(py, || {
            let mut obj = py.import_bound(self.module)?.into_any();
            for name in self.names {
                obj = obj.getattr(*name)?;
            }
            Ok::<_, PyErr>(obj.unbind())
        })?;

        Ok(p.clone_ref(py).into_bound(py))
    }
}

pub(crate) static EXPRPROXY: LazyPyImport = LazyPyImport::new("eudplib.utils", &["ExprProxy"]);
pub(crate) static GET_OBJECT_ADDR: LazyPyImport =
    LazyPyImport::new("eudplib.core.allocator", &["GetObjectAddr"]);
