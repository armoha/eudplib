use std::collections::btree_map::Values;

use pyo3::exceptions::PyValueError;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::{PyList, PyTuple};

/// Buffer where EUDObject should write to.
#[pyclass]
pub struct PayloadBuffer {
    datastart: usize,
    datacur: usize,
    data: Vec<u8>,
    prttable: Vec<usize>,
    orttable: Vec<usize>,
}

impl PayloadBuffer {
    pub(crate) fn new(totlen: usize) -> Self {
        Self {
            datastart: 0,
            datacur: 0,
            data: vec![0; totlen],
            prttable: Vec::new(),
            orttable: Vec::new(),
        }
    }

    pub(crate) fn start_write(&mut self, writeaddr: usize) {
        self.datastart = writeaddr;
        self.datacur = writeaddr;
    }

    pub(crate) fn end_write(&self) -> usize {
        self.datacur - self.datastart
    }

    pub(crate) fn create_payload(&mut self) -> (Vec<u8>, Vec<usize>, Vec<usize>) {
        (
            std::mem::take(&mut self.data),
            std::mem::take(&mut self.prttable),
            std::mem::take(&mut self.orttable),
        )
    }
}

#[pymethods]
impl PayloadBuffer {
    #[allow(non_snake_case)]
    fn WriteByte(&mut self, number: i32) {
        self.data[self.datacur] = number.to_le_bytes()[0];
        self.datacur += 1;
    }

    #[allow(non_snake_case)]
    fn WriteWord(&mut self, number: i32) {
        self.data[self.datacur..self.datacur + 2].copy_from_slice(&number.to_le_bytes()[0..2]);
        self.datacur += 2;
    }

    #[allow(non_snake_case)]
    fn WriteDword(&mut self, number: &PyAny) -> PyResult<()> {
        let evaluate: Py<PyAny> =
            PyModule::import(number.py(), "eudplib.core.allocator.constexpr")?
                .getattr("Evaluate")?
                .into();
        let arg = PyTuple::new(number.py(), &[number]);
        let rlocint = evaluate.call1(number.py(), arg)?;
        let rlocmode = rlocint
            .getattr(number.py(), intern!(number.py(), "rlocmode"))?
            .extract::<i64>(number.py())?;
        let offset = rlocint
            .getattr(number.py(), intern!(number.py(), "offset"))?
            .extract::<i64>(number.py())?;

        if rlocmode != 0 {
            assert!(
                self.datacur % 4 == 0,
                "Non-const dwords must be aligned to 4byte"
            );
            if rlocmode == 1 {
                self.prttable.push(self.datacur);
            } else if rlocmode == 4 {
                self.orttable.push(self.datacur);
            } else {
                return Err(PyValueError::new_err(format!(
                    "rlocmode should be 1 or 4, not {rlocmode}"
                )));
            }
        }

        self.data[self.datacur..self.datacur + 4].copy_from_slice(&offset.to_le_bytes()[0..4]);
        self.datacur += 4;
        Ok(())
    }

    #[allow(non_snake_case)]
    fn WritePack(&mut self, structformat: &str, arglist: &PyList) -> PyResult<()> {
        let evaluate: Py<PyAny> =
            PyModule::import(arglist.py(), "eudplib.core.allocator.constexpr")?
                .getattr("Evaluate")?
                .into();

        for (b, number) in structformat.bytes().zip(arglist.iter()) {
            let argsize = match b {
                66 => 1, // 'B'
                72 => 2, // 'H'
                73 => 4, // 'I'
                _ => panic!("Unknown struct format: {b}"),
            };
            let arg = PyTuple::new(number.py(), &[number]);
            let rlocint = evaluate.call1(arglist.py(), arg)?;
            let rlocmode = rlocint
                .getattr(arglist.py(), intern!(arglist.py(), "rlocmode"))?
                .extract::<i64>(arglist.py())?;
            let offset = rlocint
                .getattr(arglist.py(), intern!(arglist.py(), "offset"))?
                .extract::<i64>(arglist.py())?;

            if !(rlocmode == 0 || (argsize == 4 && self.datacur % 4 == 0)) {
                return Err(PyValueError::new_err(
                    "Cannot write non-const in byte/word/nonalligned dword.",
                ));
            }

            if rlocmode == 1 {
                self.prttable.push(self.datacur);
            } else if rlocmode == 4 {
                self.orttable.push(self.datacur);
            }

            if argsize == 1 {
                self.data[self.datacur] = offset.to_le_bytes()[0];
                self.datacur += 1;
            } else if argsize == 2 {
                self.data[self.datacur..self.datacur + 2]
                    .copy_from_slice(&offset.to_le_bytes()[0..2]);
                self.datacur += 2;
            } else {
                self.data[self.datacur..self.datacur + 4]
                    .copy_from_slice(&offset.to_le_bytes()[0..4]);
                self.datacur += 4;
            }
        }
        Ok(())
    }

    #[allow(non_snake_case)]
    fn WriteBytes(&mut self, b: &[u8]) {
        self.data[self.datacur..self.datacur + b.len()].copy_from_slice(b);
        self.datacur += b.len();
    }

    #[allow(non_snake_case)]
    fn WriteSpace(&mut self, spacesize: usize) {
        self.datacur += spacesize;
    }
}
