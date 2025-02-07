// source: https://github.com/wc3tools/stormlib-rs/blob/master/crates/stormlib/src/util.rs

/// Check ffi function call result, propagates the error
macro_rules! unsafe_try_call {
    ($r:expr) => {
        #[allow(unused_unsafe)]
        unsafe {
            if !$r {
                return Err($crate::error::ErrorCode(stormlib_sys::GetLastError()).into());
            }
        }
    };
}
