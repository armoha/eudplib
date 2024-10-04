// source: https://github.com/wc3tools/stormlib-rs/blob/master/crates/stormlib/src/lib.rs

use std::ffi::*;
use std::mem;
use std::path::Path;
use std::ptr;
use stormlib_sys::*;

#[macro_use]
mod util;

mod constants;
pub use constants::*;

pub mod error;
use error::*;

/// MPQ archive
#[derive(Debug)]
pub struct Archive {
    handle: HANDLE,
}

impl Archive {
    /// Opens a MPQ archive
    pub fn open<P: AsRef<Path>>(path: P, flags: OpenArchiveFlags) -> Result<Self> {
        #[cfg(not(target_os = "windows"))]
        let cpath = {
            let pathstr = path.as_ref().to_str().ok_or_else(|| StormError::NonUtf8)?;
            CString::new(pathstr)?
        };
        #[cfg(target_os = "windows")]
        let cpath = {
            use widestring::U16CString;
            U16CString::from_os_str(path.as_ref())
                .map_err(|_| StormError::InteriorNul)?
                .into_vec()
        };
        let mut handle: HANDLE = ptr::null_mut();
        unsafe_try_call!(SFileOpenArchive(
            cpath.as_ptr(),
            0,
            flags.bits(),
            &mut handle as *mut HANDLE,
        ));
        Ok(Archive { handle })
    }

    /// Creates a MPQ archive
    pub fn create<P: AsRef<Path>>(path: P, sector_size: u32, file_count: u32) -> Result<Self> {
        #[cfg(not(target_os = "windows"))]
        let cpath = {
            let pathstr = path.as_ref().to_str().ok_or_else(|| StormError::NonUtf8)?;
            CString::new(pathstr)?
        };
        #[cfg(target_os = "windows")]
        let cpath = {
            use widestring::U16CString;
            U16CString::from_os_str(path.as_ref())
                .map_err(|_| StormError::InteriorNul)?
                .into_vec()
        };
        let mut handle: HANDLE = ptr::null_mut();
        let mut create_info = SFILE_CREATE_MPQ {
            cbSize: mem::size_of::<SFILE_CREATE_MPQ>() as u32,
            dwMpqVersion: 0,
            pvUserData: ptr::null_mut(),
            cbUserData: 0,
            dwStreamFlags: 0,
            dwFileFlags1: 0,
            dwFileFlags2: 0,
            dwFileFlags3: 0,
            dwAttrFlags: 0,
            dwSectorSize: 1 << (9 + sector_size),
            dwRawChunkSize: 0,
            dwMaxFileCount: file_count,
        };
        unsafe_try_call!(SFileCreateArchive2(
            cpath.as_ptr(),
            &mut create_info,
            &mut handle as *mut HANDLE
        ));
        Ok(Archive { handle })
    }

    /// Quick check if the file exists within MPQ archive, without opening it
    pub fn has_file(&mut self, path: &str) -> Result<bool> {
        let cpath = CString::new(path)?;
        unsafe {
            let r = SFileHasFile(self.handle, cpath.as_ptr());
            let err = GetLastError();
            if !r && err != ERROR_FILE_NOT_FOUND {
                return Err(From::from(ErrorCode(err)));
            }
            Ok(r)
        }
    }

    /// Opens a file from MPQ archive
    pub fn open_file<'a>(&'a mut self, path: &str) -> Result<File<'a>> {
        let mut file_handle: HANDLE = ptr::null_mut();
        let cpath = CString::new(path)?;
        unsafe_try_call!(SFileOpenFileEx(
            self.handle,
            cpath.as_ptr(),
            0,
            &mut file_handle as *mut HANDLE
        ));
        Ok(File {
            archive: self,
            file_handle,
            size: None,
            need_reset: false,
        })
    }

    pub fn add_file<P: AsRef<Path>>(
        &mut self,
        file_path: P,
        archived_name: &str,
        replace_existing: bool,
    ) -> Result<()> {
        #[cfg(not(target_os = "windows"))]
        let cpath = {
            let pathstr = file_path
                .as_ref()
                .to_str()
                .ok_or_else(|| StormError::NonUtf8)?;
            CString::new(pathstr)?
        };
        #[cfg(target_os = "windows")]
        let cfile_path = {
            use widestring::U16CString;
            U16CString::from_os_str(file_path.as_ref())
                .map_err(|_| StormError::InteriorNul)?
                .into_vec()
        };
        let carchived_name = CString::new(archived_name)?;
        let flags = if replace_existing {
            MPQ_FILE_COMPRESS | MPQ_FILE_ENCRYPTED | MPQ_FILE_REPLACEEXISTING
        } else {
            MPQ_FILE_COMPRESS | MPQ_FILE_ENCRYPTED
        };
        unsafe_try_call!(SFileAddFileEx(
            self.handle,
            cfile_path.as_ptr(),
            carchived_name.as_ptr(),
            flags,
            MPQ_COMPRESSION_ZLIB,
            MPQ_COMPRESSION_ZLIB
        ));
        Ok(())
    }

    /// Gets the limit for number of files that can be stored in the MPQ archive.
    pub fn get_max_file_count(&mut self) -> u32 {
        unsafe { SFileGetMaxFileCount(self.handle) }
    }

    /// Changes the limit for number of files that can be stored in the MPQ archive
    pub fn set_max_file_count(&mut self, count: u32) -> Result<()> {
        unsafe_try_call!(SFileSetMaxFileCount(self.handle, count));
        Ok(())
    }

    /// Performs a complete archive rebuild, effectively defragmenting the MPQ archive
    pub fn compact(&mut self) -> Result<()> {
        unsafe_try_call!(SFileCompactArchive(self.handle, ptr::null(), false));
        Ok(())
    }

    pub fn set_file_locale(file_locale: u32) {
        unsafe { SFileSetLocale(file_locale) };
    }
}

impl std::ops::Drop for Archive {
    fn drop(&mut self) {
        unsafe {
            SFileCloseArchive(self.handle);
        }
    }
}

/// Opened file
#[derive(Debug)]
pub struct File<'a> {
    #[allow(dead_code)]
    archive: &'a Archive,
    file_handle: HANDLE,
    size: Option<u64>,
    need_reset: bool,
}

impl<'a> File<'a> {
    /// Retrieves a size of the file within archive
    pub fn get_size(&mut self) -> Result<u64> {
        if let Some(size) = self.size.clone() {
            Ok(size)
        } else {
            let mut high: DWORD = 0;
            let low = unsafe { SFileGetFileSize(self.file_handle, &mut high as *mut DWORD) };
            if low == SFILE_INVALID_SIZE {
                return Err(From::from(ErrorCode(unsafe { GetLastError() })));
            }
            let high = (high as u64) << 32;
            let size = high | (low as u64);
            self.size = Some(size);
            return Ok(size);
        }
    }

    /// Reads all data from the file
    pub fn read_all(&mut self) -> Result<Vec<u8>> {
        if self.need_reset {
            unsafe {
                if SFileSetFilePointer(self.file_handle, 0, ptr::null_mut(), 0)
                    == SFILE_INVALID_SIZE
                {
                    return Err(From::from(ErrorCode(GetLastError())));
                }
            }
        }

        let size = self.get_size()?;
        let mut buf = Vec::<u8>::with_capacity(size as usize);
        buf.resize(buf.capacity(), 0);
        let mut read: DWORD = 0;
        self.need_reset = true;
        unsafe_try_call!(SFileReadFile(
            self.file_handle,
            std::mem::transmute(buf.as_mut_ptr()),
            size as u32,
            &mut read as *mut DWORD,
            ptr::null_mut(),
        ));
        if (read as u64) < size {
            buf.truncate(read as usize);
        }
        Ok(buf)
    }
}

impl<'a> std::ops::Drop for File<'a> {
    fn drop(&mut self) {
        unsafe {
            SFileCloseFile(self.file_handle);
        }
    }
}
