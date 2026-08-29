use thiserror::Error;
use std::ffi::NulError;

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