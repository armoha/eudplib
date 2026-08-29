use bitflags::bitflags;
use stormlib_sys;

bitflags! {
  pub struct OpenArchiveFlags: u32 {
    const STREAM_PROVIDER_PARTIAL   = stormlib_sys::STREAM_PROVIDER_PARTIAL;
    const STREAM_PROVIDER_MPQE      = stormlib_sys::STREAM_PROVIDER_MPQE;
    const STREAM_PROVIDER_BLOCK4    = stormlib_sys::STREAM_PROVIDER_BLOCK4;
    const STREAM_PROVIDER_MASK      = stormlib_sys::STREAM_PROVIDER_MASK;

    const BASE_PROVIDER_FILE        = stormlib_sys::BASE_PROVIDER_FILE;
    const BASE_PROVIDER_MAP         = stormlib_sys::BASE_PROVIDER_MAP ;
    const BASE_PROVIDER_HTTP        = stormlib_sys::BASE_PROVIDER_HTTP;
    const BASE_PROVIDER_MASK        = stormlib_sys::BASE_PROVIDER_MASK;

    const STREAM_FLAG_READ_ONLY     = stormlib_sys::STREAM_FLAG_READ_ONLY;
    const STREAM_FLAG_WRITE_SHARE   = stormlib_sys::STREAM_FLAG_WRITE_SHARE;

    const MPQ_OPEN_NO_LISTFILE      = stormlib_sys::MPQ_OPEN_NO_LISTFILE;
    const MPQ_OPEN_NO_ATTRIBUTES    = stormlib_sys::MPQ_OPEN_NO_ATTRIBUTES;
    const MPQ_OPEN_NO_HEADER_SEARCH = stormlib_sys::MPQ_OPEN_NO_HEADER_SEARCH;
    const MPQ_OPEN_FORCE_MPQ_V1     = stormlib_sys::MPQ_OPEN_FORCE_MPQ_V1;
    const MPQ_OPEN_CHECK_SECTOR_CRC = stormlib_sys::MPQ_OPEN_CHECK_SECTOR_CRC;
  }
}
