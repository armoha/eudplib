use eudplib_stormlib::{Archive, OpenArchiveFlags};
use pyo3::prelude::*;
use std::borrow::Cow;
use std::io::Write;
use tempfile;

/// Class for general expression with rlocints.
#[pyclass(unsendable, name = "MPQ", module = "eudplib.core.mapdata.mpqapi")]
pub struct PyMPQ(pub(crate) Archive);

#[pymethods]
impl PyMPQ {
    // FIXME: use #[classmethod]
    #[staticmethod]
    fn open(path: &str) -> PyResult<Self> {
        let archive = Archive::open(path, OpenArchiveFlags::empty())?;
        Ok(Self(archive))
    }

    #[staticmethod]
    #[pyo3(signature = (path, sector_size=3, file_count=1024))]
    fn create(path: &str, sector_size: u32, file_count: u32) -> PyResult<Self> {
        let archive = Archive::create(path, sector_size, file_count)?;
        Ok(Self(archive))
    }

    fn get_file_names_from_listfile(&mut self) -> PyResult<Vec<String>> {
        let listfile = String::from_utf8(self.0.open_file("(listfile)")?.read_all()?)?;
        Ok(listfile.lines().map(|line| line.to_string()).collect())
    }

    fn extract_file(&mut self, file_path: &str) -> PyResult<Cow<[u8]>> {
        let mut file = self.0.open_file(file_path)?;
        Ok(file.read_all()?.into())
    }

    #[pyo3(signature = (archived_name, file_path, replace_existing=true))]
    fn add_file(
        &mut self,
        archived_name: &str,
        file_path: &str,
        replace_existing: bool,
    ) -> PyResult<()> {
        Ok(self
            .0
            .add_file(file_path, archived_name, replace_existing)?)
    }

    fn get_max_file_count(&mut self) -> u32 {
        self.0.get_max_file_count()
    }

    fn set_max_file_count(&mut self, count: u32) -> PyResult<()> {
        Ok(self.0.set_max_file_count(count)?)
    }

    fn compact(&mut self) -> PyResult<()> {
        Ok(self.0.compact()?)
    }

    #[staticmethod]
    fn clone_with_sector_size(
        input_path: &str,
        output_path: &str,
        sector_size: u32,
    ) -> PyResult<Self> {
        let mut input = Archive::open(input_path, OpenArchiveFlags::MPQ_OPEN_NO_ATTRIBUTES)?;
        let file_count = input.get_max_file_count();
        let mut output = Archive::create(output_path, sector_size, file_count)?;
        let listfile = String::from_utf8(input.open_file("(listfile)")?.read_all()?)?;
        for archived_file in listfile.lines() {
            let mut file = input.open_file(archived_file)?;
            let mut tmpfile = tempfile::NamedTempFile::new()?;
            tmpfile.write_all(&file.read_all()?)?;
            output.add_file(tmpfile.path(), archived_file, true)?;
        }
        Ok(Self(output))
    }
}

#[pymodule]
#[pyo3(name = "mpqapi")]
pub(crate) mod mpqapi_mod {
    #[pymodule_export]
    use super::PyMPQ;
}
