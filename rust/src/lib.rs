use pyo3::prelude::*;

mod rlocint;
mod constexpr;

#[pyfunction]
fn stack_objects(dwoccupmap_list: Vec<Vec<i32>>) -> Vec<u32> {
    let dwoccupmap_max_size = dwoccupmap_list.iter().fold(0, |acc, x| acc + x.len());
    let mut dwoccupmap_sum  = vec![-1; dwoccupmap_max_size];
    let mut lallocaddr = 0;
    let mut alloctable = Vec::with_capacity(dwoccupmap_max_size);
    for py_dwoccupmap in dwoccupmap_list {

        // preprocess dwoccupmap
        let mut dwoccupmap = Vec::new();
        dwoccupmap.push(if py_dwoccupmap[0] == 0 {
            -1
        } else {
            0
        });
        for (i, (a, b)) in py_dwoccupmap.iter().zip(py_dwoccupmap.iter().skip(1)).enumerate() {
            dwoccupmap.push(
                if *b == 0 {
                    -1
                } else if *a == -1 {
                    1 + i as i32
                } else {
                    *a
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
    }
    alloctable
}

#[pymodule]
fn _rust(py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(stack_objects, m)?)?;
    m.add_class::<constexpr::ConstExpr>()?;
    Ok(())
}
