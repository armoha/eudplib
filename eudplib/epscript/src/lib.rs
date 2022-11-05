use cpython::{py_fn, py_module_initializer, PyResult, Python};
use i18n_embed::{
    fluent::{fluent_language_loader, FluentLanguageLoader},
    DesktopLanguageRequester,
};
use i18n_embed_fl::fl;
use rust_embed::RustEmbed;

#[derive(RustEmbed)]
#[folder = "i18n"]
struct Localizations;

mod parser;
use std::marker::PhantomData;
use std::sync::atomic::{AtomicBool, Ordering};
static LIBRARY_IN_USE: AtomicBool = AtomicBool::new(false);
struct Lib {
    _not_send: PhantomData<*const ()>,
}
impl Drop for Lib {
    fn drop(&mut self) {
        LIBRARY_IN_USE.store(false, Ordering::SeqCst);
    }
}
impl Lib {
    fn new() -> Self {
        if LIBRARY_IN_USE.compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst)
            == Ok(false)
        {
            Lib {
                _not_send: PhantomData,
            }
        } else {
            panic!("The library is already in use")
        }
    }
    fn set_param(&mut self) -> SetParam<'_> {
        SetParam { _library: self }
    }
}
struct SetParam<'lib> {
    _library: &'lib mut Lib,
}
impl<'lib> SetParam<'lib> {
    pub fn boolean(&mut self, _name: &str, _value: bool) -> &mut Self {
        unimplemented!()
    }
}

// TODO: add docstrings for functions
py_module_initializer!(epScript, |py, m| {
    m.add(py, "__doc__", "epScript module implemented in Rust.")?;
    m.add(
        py,
        "setDebugMode",
        py_fn!(py, sum_as_string_py(a: i64, b: i64)),
    )?;
    m.add(
        py,
        "registerPlibConstants",
        py_fn!(py, sum_as_string_py(a: i64, b: i64)),
    )?;
    m.add(
        py,
        "getErrorCount",
        py_fn!(py, sum_as_string_py(a: i64, b: i64)),
    )?;
    m.add(
        py,
        "compileString",
        py_fn!(py, sum_as_string_py(a: i64, b: i64)),
    )?;
    m.add(
        py,
        "freeCompiledResult",
        py_fn!(py, sum_as_string_py(a: i64, b: i64)),
    )?;
    Ok(())
});

fn debug_mode_py(_: Python, mode: bool) -> PyResult<()> {
    // magic
}

fn add_global_py(_: Python, globals: Vec<String>) -> PyResult<()> {
    for global in globals {
        // magic
    }
}

fn sum_as_string(a: i64, b: i64) -> String {
    format!("{}", a + b).to_string()
}

fn sum_as_string_py(_: Python, a: i64, b: i64) -> PyResult<String> {
    let out = sum_as_string(a, b);
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    static_assertions::assert_not_impl_any!(Lib: Send, Sync);

    fn main() {
        let loader: FluentLanguageLoader = fluent_language_loader!();
        let requested_languages = DesktopLanguageRequester::requested_languages();
        i18n_embed::select(&loader, &Localizations, &requested_languages);
        assert_eq!(
            "안녕 \u{2068}Bob 23\u{2069}!",
            fl!(loader, "hello-arg", name = format!("Bob {}", 23))
        )
    }
}
