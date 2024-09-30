// source: https://raw.githubusercontent.com/wc3tools/stormlib-rs/refs/heads/master/crates/stormlib/src/error.rs

use pyo3::exceptions;
use pyo3::PyErr;
use std::ffi::NulError;
use thiserror::Error;

#[derive(Debug)]
pub struct ErrorCode(pub u32);

#[derive(Error, Debug)]
pub enum StormError {
    #[error("FileNotFound")]
    FileNotFound,
    #[error("AccessDenied")]
    AccessDenied,
    #[error("InvalidHandle")]
    InvalidHandle,
    #[error("NotEnoughMemory")]
    NotEnoughMemory,
    #[error("NotSupported")]
    NotSupported,
    #[error("InvalidParameter")]
    InvalidParameter,
    #[cfg(target_os = "windows")]
    #[error("NegativeSeek")]
    NegativeSeek,
    #[error("DiskFull")]
    DiskFull,
    #[error("AlreadyExists")]
    AlreadyExists,
    #[error("InsufficientBuffer")]
    InsufficientBuffer,
    #[error("BadFormat")]
    BadFormat,
    #[error("NoMoreFiles")]
    NoMoreFiles,
    #[error("HandleEof")]
    HandleEof,
    #[error("CanNotComplete")]
    CanNotComplete,
    #[error("FileCorrupt")]
    FileCorrupt,
    #[error("UnknownCode({0:?})")]
    UnknownCode(ErrorCode),
    #[cfg(not(target_os = "windows"))]
    #[error("non-utf-8 encoding is not supported")]
    NonUtf8,
    #[error("an interior nul byte was found")]
    InteriorNul,
}

pub type Result<T, E = StormError> = std::result::Result<T, E>;

impl From<ErrorCode> for StormError {
    fn from(ErrorCode(code): ErrorCode) -> Self {
        use StormError::*;
        match code {
            stormlib_sys::ERROR_FILE_NOT_FOUND => FileNotFound,
            stormlib_sys::ERROR_ACCESS_DENIED => AccessDenied,
            stormlib_sys::ERROR_INVALID_HANDLE => InvalidHandle,
            stormlib_sys::ERROR_NOT_ENOUGH_MEMORY => NotEnoughMemory,
            stormlib_sys::ERROR_NOT_SUPPORTED => NotSupported,
            stormlib_sys::ERROR_INVALID_PARAMETER => InvalidParameter,
            #[cfg(target_os = "windows")]
            stormlib_sys::ERROR_NEGATIVE_SEEK => NegativeSeek,
            stormlib_sys::ERROR_DISK_FULL => DiskFull,
            stormlib_sys::ERROR_ALREADY_EXISTS => AlreadyExists,
            stormlib_sys::ERROR_INSUFFICIENT_BUFFER => InsufficientBuffer,
            stormlib_sys::ERROR_BAD_FORMAT => BadFormat,
            stormlib_sys::ERROR_NO_MORE_FILES => NoMoreFiles,
            stormlib_sys::ERROR_HANDLE_EOF => HandleEof,
            stormlib_sys::ERROR_CAN_NOT_COMPLETE => CanNotComplete,
            stormlib_sys::ERROR_FILE_CORRUPT => FileCorrupt,
            other => UnknownCode(ErrorCode(other)),
        }
    }
}

impl From<std::ffi::NulError> for StormError {
    fn from(_: NulError) -> Self {
        StormError::InteriorNul
    }
}

impl From<StormError> for PyErr {
    fn from(err: StormError) -> PyErr {
        use StormError::*;
        match err {
            FileNotFound => exceptions::PyFileNotFoundError::new_err(err.to_string()),
            AccessDenied => exceptions::PyPermissionError::new_err(err.to_string()),
            InvalidHandle => exceptions::PyOSError::new_err(err.to_string()),
            NotEnoughMemory => exceptions::PyMemoryError::new_err(err.to_string()),
            NotSupported => exceptions::PyNotImplementedError::new_err(err.to_string()),
            InvalidParameter => exceptions::PyValueError::new_err(err.to_string()),
            #[cfg(target_os = "windows")]
            NegativeSeek => exceptions::PyOSError::new_err(err.to_string()),
            DiskFull => exceptions::PyOSError::new_err(err.to_string()),
            AlreadyExists => exceptions::PyFileExistsError::new_err(err.to_string()),
            InsufficientBuffer => exceptions::PyOSError::new_err(err.to_string()),
            BadFormat => exceptions::PyValueError::new_err(err.to_string()),
            NoMoreFiles => exceptions::PyStopIteration::new_err(err.to_string()),
            HandleEof => exceptions::PyEOFError::new_err(err.to_string()),
            CanNotComplete => exceptions::PyOSError::new_err(err.to_string()),
            FileCorrupt => exceptions::PyIOError::new_err(err.to_string()),
            UnknownCode(_) => exceptions::PyRuntimeError::new_err(err.to_string()),
            #[cfg(not(target_os = "windows"))]
            NonUtf8 => exceptions::PyUnicodeDecodeError::new_err(err.to_string()),
            InteriorNul => exceptions::PyValueError::new_err(err.to_string()),
        }
    }
}
