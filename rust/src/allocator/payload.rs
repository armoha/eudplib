use crate::allocator::pbuffer::PayloadBuffer;
use crate::allocator::rlocint::{PyRlocInt, RlocInt};
use indicatif::{ProgressBar, ProgressStyle};
use pyo3::create_exception;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyTuple};

create_exception!(allocator, AllocError, pyo3::exceptions::PyException);

/// Object having PayloadBuffer-like interfaces. Collects all objects by
/// calling object.WritePayload() for every related objects.
#[pyclass(module = "eudplib.core.allocator")]
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
    fn WritePack(&mut self, structformat: &str, _arglist: &PyAny) {
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

    fn _write_trigger(&mut self, conditions: u32, actions: u32) {
        self.push(true);  // prevptr
        self.push(true);  // nextptr

        // Conditions
        for _ in 0..(conditions * 5) {
            self.push(true);
        }
        if conditions < 16 {
            for _ in 0..5 {
                self.push(true);
            }
            self.WriteSpace(20 * (15 - conditions));
        }

        // Actions
        for _ in 0..(actions * 8) {
            self.push(true);
        }
        if actions < 64 {
            for _ in 0..8 {
                self.push(true);
            }
            self.WriteSpace(32 * (63 - actions));
        }

        // Preserved flag
        self.push(true);

        self.WriteSpace(27);
        self.occup1();
    }
}

fn stack_objects(dwoccupmap_list: Vec<Vec<i32>>) -> (Vec<u32>, usize) {
    let mut dwoccupmap_sum = vec![-1; dwoccupmap_list.iter().map(Vec::len).sum()];
    let mut alloctable = Vec::with_capacity(dwoccupmap_sum.len());
    let mut lallocaddr = 0;
    let mut payload_size = 0;

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
        for (i, &occup) in dwoccupmap.iter().enumerate().rev() {
            let curoff = lallocaddr + i;
            if occup != -1 || dwoccupmap_sum[curoff] != -1 {
                dwoccupmap_sum[curoff] = if dwoccupmap_sum[curoff + 1] == -1 {
                    curoff as i32 + 1
                } else {
                    dwoccupmap_sum[curoff + 1]
                };
            }
        }
        alloctable.push((lallocaddr * 4) as u32);

        let obj_size = lallocaddr + dwoccupmap.len();
        let obj_payload_size = obj_size * 4;
        if obj_payload_size > payload_size {
            payload_size = obj_payload_size;
        }
    }

    (alloctable, payload_size)
}

#[pyclass(module = "eudplib.core.allocator")]
pub struct PayloadBuilder {
    callbacks_on_create_payload: Vec<PyObject>,
    callbacks_after_collecting: Vec<PyObject>,
    // Allocating & Writing phase
    alloctable: Vec<u32>,
    payload_size: usize,
}

#[pymethods]
impl PayloadBuilder {
    #[new]
    fn new() -> Self {
        Self {
            callbacks_on_create_payload: Vec::new(),
            callbacks_after_collecting: Vec::new(),
            alloctable: Vec::new(),
            payload_size: 0,
        }
    }

    fn register_create_payload_callback(&mut self, callable: PyObject) {
        self.callbacks_on_create_payload.push(callable);
    }

    fn register_after_collecting_callback(&mut self, callable: PyObject) {
        self.callbacks_after_collecting.push(callable);
    }

    fn call_callbacks_on_create_payload(&mut self, py: Python) {
        for callable in self.callbacks_on_create_payload.drain(..) {
            let _ = callable.call0(py);
        }
    }

    fn call_callbacks_after_collecting(&mut self, py: Python) {
        for callable in self.callbacks_after_collecting.drain(..) {
            let _ = callable.call0(py);
        }
    }

    fn alloc_objects(&mut self, py: Python, found_objects: &PyDict) -> PyResult<()> {
        let obja = PyCell::new(py, ObjAllocator::new())?;
        let mut dwoccupmap_list = Vec::with_capacity(found_objects.len());
        let bar = ProgressBar::new(found_objects.len() as u64);
        bar.println(" - Preprocessing objects..");
        bar.set_style(
            ProgressStyle::with_template("[{elapsed}] {bar:40.cyan/blue} {pos} / {len} objects")
                .unwrap()
                .progress_chars("##-"),
        );
        let arg: &PyTuple = PyTuple::new(py, &[obja]);
        for (obj, _v) in found_objects.iter() {
            {
                let mut obja = obja.borrow_mut();
                obja.start_write();
            }
            obj.call_method1(intern!(py, "WritePayload"), arg)?;
            let dwoccupmap = {
                let mut obja = obja.borrow_mut();
                obja.end_write()
            };
            let dwoccupmap_len = dwoccupmap.len();
            let datasize = obj
                .call_method0(intern!(py, "GetDataSize"))?
                .extract::<usize>()?;
            let datasize = (datasize + 3) >> 2;
            if dwoccupmap_len != datasize {
                return Err(AllocError::new_err(format!("Occupation map length ({dwoccupmap_len}) & Object size ({datasize}) mismatch for {obj}")));
            }
            dwoccupmap_list.push(dwoccupmap);
            bar.inc(1);
        }
        bar.finish();
        println!(" - Allocating objects..");
        (self.alloctable, self.payload_size) = stack_objects(dwoccupmap_list);
        Ok(())
    }

    fn construct_payload(
        &self,
        py: Python,
        found_objects: &PyDict,
    ) -> PyResult<(Vec<u8>, Vec<usize>, Vec<usize>)> {
        let pbuf = PyCell::new(py, PayloadBuffer::new(self.payload_size))?;
        let bar = ProgressBar::new(found_objects.len() as u64);
        bar.println(" - Writing objects..");
        bar.set_style(
            ProgressStyle::with_template("[{elapsed}] {bar:40.cyan/blue} {pos} / {len} objects")
                .unwrap()
                .progress_chars("##-"),
        );
        let arg: &PyTuple = PyTuple::new(py, &[pbuf]);
        for (i, (obj, _v)) in found_objects.iter().enumerate() {
            {
                let mut pbuf = pbuf.borrow_mut();
                pbuf.start_write(self.alloctable[i] as usize);
            }
            obj.call_method1(intern!(py, "WritePayload"), arg)?;
            let written_bytes = {
                let pbuf = pbuf.borrow();
                pbuf.end_write()
            };
            let objsize = obj
                .call_method0(intern!(py, "GetDataSize"))?
                .extract::<usize>()?;
            if written_bytes != objsize {
                return Err(AllocError::new_err(format!(
                    "obj.GetDataSize() ({objsize}) != Real payload size({written_bytes}) for {obj:?}"
                )));
            }
            bar.inc(1);
        }
        bar.finish();
        Ok({
            let mut pbuf = pbuf.borrow_mut();
            pbuf.create_payload()
        })
    }

    fn get_object_addr(&self, index: usize) -> PyRlocInt {
        PyRlocInt(RlocInt::new(self.alloctable[index] as i32, 4))
    }
}
