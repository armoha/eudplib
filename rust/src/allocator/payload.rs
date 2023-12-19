use indicatif::{ProgressBar, ProgressStyle};
use pyo3::create_exception;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyList, PyTuple};

create_exception!(allocator, AllocError, pyo3::exceptions::PyException);

/// Object having PayloadBuffer-like interfaces. Collects all objects by
/// calling RegisterObject() for every related objects.
#[pyclass]
pub struct ObjAllocator {
    suboccupmap: bool,
    suboccupidx: u32,
    occupmap: Vec<i32>,
}

impl ObjAllocator {
    fn new() -> Self {
        Self {
            suboccupmap: false,
            suboccupidx: 0,
            occupmap: Vec::new(),
        }
    }

    fn start_write(&mut self) {
        self.suboccupmap = false;
        self.suboccupidx = 0;
        self.occupmap.clear();
    }

    fn end_write(&mut self) -> Vec<i32> {
        if self.suboccupidx > 0 {
            self.push(self.suboccupmap);
            self.suboccupidx = 0;
        }
        std::mem::take(&mut self.occupmap)
    }

    fn push(&mut self, suboccupmap: bool) {
        self.occupmap.push(if !suboccupmap {
            -1
        } else if *self.occupmap.last().unwrap_or(&-1) != -1 {
            // Safety: unwrap_or handles empty occupmap case
            unsafe { *self.occupmap.last().unwrap_unchecked() }
        } else {
            self.occupmap.len() as i32
        });
    }

    #[allow(dead_code)]
    fn occup0(&mut self) {
        self.suboccupidx += 1;
        if self.suboccupidx == 4 {
            self.push(self.suboccupmap);
            self.suboccupidx = 0;
            self.suboccupmap = false;
        }
    }

    fn occup1(&mut self) {
        self.suboccupmap = true;
        self.suboccupidx += 1;
        if self.suboccupidx == 4 {
            self.push(self.suboccupmap);
            self.suboccupidx = 0;
            self.suboccupmap = false;
        }
    }
}

#[pymethods]
impl ObjAllocator {
    #[allow(non_snake_case)]
    fn WriteByte(&mut self, _number: &PyAny) {
        self.occup1();
    }

    #[allow(non_snake_case)]
    fn WriteWord(&mut self, _number: &PyAny) {
        self.occup1();
        self.occup1();
    }

    #[allow(non_snake_case)]
    fn WriteDword(&mut self, _number: &PyAny) {
        self.push(true);
    }

    #[allow(non_snake_case)]
    fn WritePack(&mut self, structformat: &str, _arglist: &PyList) {
        let ssize: u32 = structformat
            .bytes()
            .map(|x| match x {
                66 => 1, // 'B'
                72 => 2, // 'H'
                73 => 4, // 'I'
                _ => panic!("Unknown struct format: {x}"),
            })
            .sum();

        for _ in 0..(ssize >> 2) {
            self.push(true);
        }
        for _ in 0..(ssize & 3) {
            self.occup1();
        }
    }

    #[allow(non_snake_case)]
    fn WriteBytes(&mut self, b: &PyBytes) -> PyResult<()> {
        let ssize = b.len()?;

        for _ in 0..(ssize >> 2) {
            self.push(true);
        }
        for _ in 0..(ssize & 3) {
            self.occup1();
        }
        Ok(())
    }

    #[allow(non_snake_case)]
    fn WriteSpace(&mut self, ssize: u32) {
        self.suboccupidx += ssize;
        if self.suboccupidx >= 4 {
            self.push(self.suboccupmap);
            self.suboccupidx -= 4;
            for _ in 0..(self.suboccupidx / 4) {
                self.push(false);
            }
            self.suboccupidx %= 4;
            self.suboccupmap = false;
        }
    }
}

fn stack_objects(dwoccupmap_list: Vec<Vec<i32>>) -> (Vec<u32>, usize) {
    let dwoccupmap_max_size = dwoccupmap_list.iter().fold(0, |acc, x| acc + x.len());
    let mut dwoccupmap_sum = vec![-1; dwoccupmap_max_size];
    let mut lallocaddr = 0;
    let mut payload_size = 0;
    let mut alloctable = Vec::with_capacity(dwoccupmap_max_size);
    for dwoccupmap in dwoccupmap_list {
        // Find appropriate position to allocate object
        let mut i = 0;
        while i < dwoccupmap.len() {
            // Update on conflict map
            if dwoccupmap[i] != -1 && dwoccupmap_sum[lallocaddr + i] != -1 {
                lallocaddr = (dwoccupmap_sum[lallocaddr + i] - dwoccupmap[i]) as usize;
                i = 0;
            } else {
                i += 1;
            }
        }

        // Apply occupation map
        for i in (0..dwoccupmap.len()).rev() {
            let curoff = lallocaddr + i;
            if dwoccupmap[i] != -1 || dwoccupmap_sum[curoff] != -1 {
                dwoccupmap_sum[curoff] = if dwoccupmap_sum[curoff + 1] == -1 {
                    curoff as i32 + 1
                } else {
                    dwoccupmap_sum[curoff + 1]
                };
            }
        }
        alloctable.push(lallocaddr as u32 * 4);
        if (lallocaddr + dwoccupmap.len()) * 4 > payload_size {
            payload_size = (lallocaddr + dwoccupmap.len()) * 4
        }
    }
    (alloctable, payload_size)
}

#[pyfunction]
pub fn alloc_objects(py: Python, found_objects: &PyDict) -> PyResult<(Vec<u32>, usize)> {
    let obja = PyCell::new(py, ObjAllocator::new())?;
    let mut dwoccupmap_list = Vec::with_capacity(found_objects.len());
    let bar = ProgressBar::new(found_objects.len() as u64);
    bar.println(" - Preprocessing objects..");
    bar.set_style(
        ProgressStyle::with_template("[{elapsed}] {bar:40.cyan/blue} {pos} / {len} objects")
            .unwrap()
            .progress_chars("##-"),
    );
    for (obj, _v) in found_objects.iter() {
        {
            let mut obja = obja.borrow_mut();
            obja.start_write();
        }
        let arg: &PyTuple = PyTuple::new(py, &[obja]);
        obj.call_method1("WritePayload", arg)?;
        let dwoccupmap = {
            let mut obja = obja.borrow_mut();
            obja.end_write()
        };
        let datasize = obj.call_method0("GetDataSize")?.extract::<usize>()?;
        if dwoccupmap.len() != (datasize + 3) >> 2 {
            let dwoccupmap_len = dwoccupmap.len();
            let datasize = (datasize + 3) >> 2;
            return Err(AllocError::new_err(format!("Occupation map length ({dwoccupmap_len}) & Object size ({datasize}) mismatch for {obj}")));
        }
        dwoccupmap_list.push(dwoccupmap);
        bar.inc(1);
    }
    bar.finish();
    println!(" - Allocating objects..");
    Ok(stack_objects(dwoccupmap_list))
}
