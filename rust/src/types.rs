pub(crate) struct LazyPyImport {
    module: &'static str,
    names: &'static [&'static str],
    value: pyo3::sync::GILOnceCell<pyo3::PyObject>,
}

impl LazyPyImport {
    pub(crate) const fn new(module: &'static str, names: &'static [&'static str]) -> LazyPyImport {
        LazyPyImport {
            module,
            names,
            value: pyo3::sync::GILOnceCell::new(),
        }
    }

    pub(crate) fn get<'p>(&'p self, py: pyo3::Python<'p>) -> pyo3::PyResult<&'p pyo3::PyAny> {
        self.value
            .get_or_try_init(py, || {
                let mut obj = py.import(self.module)?.as_ref();
                for name in self.names {
                    obj = obj.getattr(*name)?;
                }
                obj.extract()
            })
            .map(|p| p.as_ref(py))
    }
}

pub(crate) static EXPRPROXY: LazyPyImport = LazyPyImport::new("eudplib.utils", &["ExprProxy"]);
pub(crate) static GET_OBJECT_ADDR: LazyPyImport =
    LazyPyImport::new("eudplib.core.allocator", &["GetObjectAddr"]);
