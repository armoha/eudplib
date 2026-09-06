use std::sync::RwLock;
use pyo3::prelude::*;

pub trait Translator: Send + Sync {
    fn translate(&self, text: &str) -> String;
}

static TRANSLATOR: RwLock<Option<Box<dyn Translator>>> = RwLock::new(None);

pub fn set_translator(t: Option<Box<dyn Translator>>) {
    if let Ok(mut lock) = TRANSLATOR.write() {
        *lock = t;
    }
}

pub fn tr(text: &str) -> String {
    if let Ok(lock) = TRANSLATOR.read() {
        if let Some(ref translator) = *lock {
            return translator.translate(text);
        }
    }
    text.to_string()
}

struct PyCallbackTranslator {
    callback: Py<PyAny>,
}

impl Translator for PyCallbackTranslator {
    fn translate(&self, text: &str) -> String {
        Python::attach(|py| {
            match self.callback.call1(py, (text,)) {
                Ok(obj) => match obj.extract::<String>(py) {
                    Ok(s) => s,
                    Err(_) => text.to_string(),
                },
                Err(_) => text.to_string(),
            }
        })
    }
}

#[pyfunction]
pub fn register_translator(callback: Option<Py<PyAny>>) {
    match callback {
        Some(cb) => set_translator(Some(Box::new(PyCallbackTranslator { callback: cb }))),
        None => set_translator(None),
    }
}
