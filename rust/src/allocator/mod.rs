use pyo3::prelude::*;

mod rlocint;
mod constexpr;

#[pyfunction]
fn stack_objects(dwoccupmap_list: Vec<Vec<bool>>) -> (Vec<u32>, usize) {
    let dwoccupmap_max_size = dwoccupmap_list.iter().fold(0, |acc, x| acc + x.len());
    let mut dwoccupmap_sum  = vec![-1; dwoccupmap_max_size];
    let mut lallocaddr = 0;
    let mut payload_size = 0;
    let mut alloctable = Vec::with_capacity(dwoccupmap_max_size);
    for py_dwoccupmap in dwoccupmap_list {

        // preprocess dwoccupmap (example)
        // py_dwoccupmap = [T,  F, T, T,  F,  F, T, T, T]
        //   dwoccupmap  = [0, -1, 2, 2, -1, -1, 6, 6, 6]
        let mut dwoccupmap = Vec::new();
        dwoccupmap.push(if py_dwoccupmap[0] {
            0
        } else {
            -1
        });
        for (i, (a, b)) in py_dwoccupmap.iter().zip(py_dwoccupmap.iter().skip(1)).enumerate() {
            dwoccupmap.push(
                if *b == false {
                    -1
                } else if *a == false {
                    1 + i as i32
                } else {
                    // Safety: dwoccupmap can't be empty
                    unsafe { *dwoccupmap.last().unwrap_unchecked() }
                }
            );
        }

        // Find appropriate position to allocate object
        let mut i = 0;
        while i < py_dwoccupmap.len() {
            // Update on conflict map
            if dwoccupmap[i] != -1 && dwoccupmap_sum[lallocaddr + i] != -1 {
                lallocaddr = (dwoccupmap_sum[lallocaddr + i] - dwoccupmap[i]) as usize;
                i = 0;
            } else {
                i += 1;
            }
        }

        // Apply occupation map
        for i in (0..py_dwoccupmap.len()).rev() {
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
        if (lallocaddr + py_dwoccupmap.len()) * 4 > payload_size {
            payload_size = (lallocaddr + py_dwoccupmap.len()) * 4
        }
    }
    (alloctable, payload_size)
}

pub(crate) fn create_submodule(py: Python<'_>) -> PyResult<&PyModule> {
    let submod = PyModule::new(py, "allocator")?;
    submod.add_function(wrap_pyfunction!(stack_objects, submod)?)?;
    submod.add_class::<constexpr::ConstExpr>()?;

    Ok(submod)
}
