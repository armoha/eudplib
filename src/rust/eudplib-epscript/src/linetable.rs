use pyo3::prelude::*;
use pyo3::sync::GILOnceCell;
use pyo3::types::PyIterator;
use regex::Regex;
use std::borrow::Cow;
use std::collections::BTreeMap;
use std::iter::Iterator;
use std::str;

static LINENO_REGEX: GILOnceCell<Regex> = GILOnceCell::new();

#[allow(dead_code)]
fn print_entries(linetable_bytes: Vec<u8>) {
    let linetable_reader = LinetableReader {
        data: linetable_bytes,
        cursor: 0,
    };
    for entry in linetable_reader {
        let head = entry[0];
        let code = (head & 0x78) >> 3;
        let num_bytecode = (head & 0x07) + 1;
        print!("code is: {code:2}, num_bytecode is: {num_bytecode:2},");
        for byte in entry {
            print!(" {byte:08b}");
        }
        println!();
    }
}

/// generate_linetable(data, linetable, positions, /)
/// --
///
/// Returns a Python 3.11+ co_linetable from data and co_positions.
///
/// # Arguments
///
/// * `data` - UTF-8 encoded python source code compiled from .eps
/// * `linetable` - `codeObj.co_linetable` bytes
/// * `positions` - `codeObj.co_positions()` iterator
#[pyfunction]
pub fn generate_linetable<'a>(
    data: &'a [u8],
    linetable: Vec<u8>,
    positions: &Bound<'a, PyIterator>,
) -> PyResult<Cow<'a, [u8]>> {
    let line_regex = LINENO_REGEX.get_or_init(positions.py(), || {
        Regex::new(r" *# \(Line (\d+)\)").unwrap()
    });
    let mut eps_linemap: BTreeMap<u32, u32> = str::from_utf8(data)?
        .lines()
        .enumerate()
        .filter_map(|(index, line)| {
            line_regex.captures(line).and_then(|c| {
                c.get(1)?
                    .as_str()
                    .parse()
                    .ok()
                    .map(|x| (1 + index as u32, x))
            })
        })
        .collect();
    eps_linemap.insert(0, 0);

    // co_positions is iterator of (int, int, int, int)
    // = (start_line, end_line, start_column, end_column)
    // TODO: use epScript column as well for richer error message
    let epspy_lines: Vec<u32> = positions
        .iter()?
        .map(|i| {
            i.and_then(|ob: Bound<'_, PyAny>| <(u32, u32, u32, u32)>::extract_bound(&ob))
                .map(|x| x.0)
                .unwrap_or(u32::MAX)
        })
        .collect();

    let linetable_reader = LinetableReader::new(linetable);
    let mut linetable_writer = LinetableWriter::new();
    let mut code_length = 0;
    for entry in linetable_reader {
        let epspy_line = epspy_lines[code_length as usize];
        let (_, new_startline) = eps_linemap.range(..=epspy_line).next_back().unwrap();
        linetable_writer.calc_linetable(*new_startline, code_length);
        linetable_writer.update_cursor(*new_startline, code_length);

        let num_bytecode = (entry[0] & 0x07) + 1;
        code_length += num_bytecode as u32;
    }

    linetable_writer.calc_linetable(linetable_writer.cur_lineno, code_length);
    Ok(linetable_writer.linetable.into())
}

struct LinetableReader {
    data: Vec<u8>,
    cursor: usize,
}

impl LinetableReader {
    fn new(linetable: Vec<u8>) -> Self {
        Self {
            data: linetable,
            cursor: 0,
        }
    }
}

impl Iterator for LinetableReader {
    type Item = Vec<u8>;

    fn next(&mut self) -> Option<Self::Item> {
        if self.cursor >= self.data.len() {
            return None;
        }
        let mut item = Vec::new();
        for byte in &self.data[self.cursor..] {
            if !item.is_empty() && byte & 0x80 == 0x80 {
                break;
            }
            item.push(*byte);
        }
        self.cursor += item.len();
        Some(item)
    }
}

struct LinetableWriter {
    cur_lineno: u32,
    cur_bytecode: u32,
    linetable: Vec<u8>,
}

impl LinetableWriter {
    fn new() -> Self {
        Self {
            cur_lineno: 0,
            cur_bytecode: 0,
            linetable: Vec::new(),
        }
    }

    fn update_cursor(&mut self, starts_line: u32, code_length: u32) {
        self.cur_lineno = starts_line;
        self.cur_bytecode = code_length;
    }

    fn encode_varint(buffer: &mut Vec<u8>, mut num: u32) {
        let continue_flag: u8 = 1 << 6;

        while num >= 0x40 {
            buffer.push((num & 0x3F) as u8 | continue_flag);
            num >>= 6;
        }
        buffer.push((num as u8) & !continue_flag);
    }

    fn encode_svarint(buffer: &mut Vec<u8>, num: i32) {
        let unsigned_value = if num < 0 {
            ((-num as u32) << 1) | 1
        } else {
            (num as u32) << 1
        };
        Self::encode_varint(buffer, unsigned_value)
    }

    fn encode_bytecode_to_entries(&mut self, line_offset: i32, byte_offset: u32) {
        if byte_offset == 0 {
            return;
        }
        if 0 < byte_offset && byte_offset <= 8 {
            // code: 13 (No column info)
            #[allow(clippy::unusual_byte_groupings)]
            let entry_head: u8 = (0b1_1101_000 | (byte_offset - 1)) as u8;
            self.linetable.push(entry_head);
            Self::encode_svarint(&mut self.linetable, line_offset);
            return;
        }
        self.encode_bytecode_to_entries(line_offset, 8);
        self.encode_bytecode_to_entries(line_offset, byte_offset - 8);
    }

    fn calc_linetable(&mut self, starts_line: u32, code_length: u32) {
        let line_offset = (starts_line - self.cur_lineno) as i32;
        let byte_offset = code_length - self.cur_bytecode;
        self.encode_bytecode_to_entries(line_offset, byte_offset);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_linetables() -> PyResult<()> {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| -> PyResult<()> {
            let positions = py.eval_bound("iter([(0, 1, 0, 0), (2, 2, 0, 21), (2, 2, 0, 21), (2, 2, 0, 21), (2, 2, 0, 21), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (6, 6, 6, 11), (6, 6, 6, 11), (6, 6, 12, 23), (6, 6, 12, 23), (6, 6, 25, 26), (6, 6, 6, 27), (6, 6, 6, 27), (6, 6, 6, 27), (6, 6, 6, 27), (6, 6, 6, 27), (6, 6, 6, 27), (6, 6, 6, 27), (6, 6, 28, 29), (6, 6, 6, 30), (6, 6, 6, 30), (6, 6, 6, 30), (6, 6, 6, 30), (6, 6, 6, 30), (6, 6, 0, 3), (6, 6, 0, 3), (6, 6, 0, 3)])", None, None)?;
            let data = std::fs::read("src/epscript/test/data1")?;
            let linetable_before = std::fs::read("src/epscript/test/linetable_before1")?;
            let linetable = generate_linetable(&data, linetable_before, positions.downcast()?)?;
            let linetable_after = std::fs::read("src/epscript/test/linetable_after1")?;
            assert_eq!(linetable, linetable_after);

            let positions = py.eval_bound("iter([(0, 1, 0, 0), (2, 2, 0, 21), (2, 2, 0, 21), (2, 2, 0, 21), (2, 2, 0, 21), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (3, 3, 0, 118), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (4, 4, 0, 129), (6, 6, 0, 13), (6, 6, 0, 13), (6, 6, 0, 13), (6, 6, 0, 13), (8, 8, 0, 16), (8, 8, 0, 16), (8, 8, 0, 16), (8, 8, 0, 16), (10, 10, 0, 29), (10, 10, 0, 29), (10, 10, 0, 29), (10, 10, 0, 29), (10, 10, 0, 29), (10, 10, 0, 29), (12, 12, 12, 17), (12, 12, 12, 17), (12, 12, 18, 59), (12, 12, 18, 59), (12, 12, 61, 62), (12, 12, 12, 63), (12, 12, 12, 63), (12, 12, 12, 63), (12, 12, 12, 63), (12, 12, 12, 63), (12, 12, 12, 63), (12, 12, 12, 63), (12, 12, 64, 65), (12, 12, 12, 66), (12, 12, 12, 66), (12, 12, 12, 66), (12, 12, 12, 66), (12, 12, 12, 66), (12, 12, 0, 9), (14, 14, 1, 8), (15, 153, 0, 35), (15, 153, 0, 35), (14, 14, 1, 8), (14, 14, 1, 8), (14, 14, 1, 8), (14, 14, 1, 8), (14, 14, 1, 8), (14, 14, 1, 8), (14, 14, 1, 8), (15, 153, 0, 35), (157, 157, 1, 8), (158, 211, 0, 35), (158, 211, 0, 35), (157, 157, 1, 8), (157, 157, 1, 8), (157, 157, 1, 8), (157, 157, 1, 8), (157, 157, 1, 8), (157, 157, 1, 8), (157, 157, 1, 8), (158, 211, 0, 35), (215, 215, 5, 10), (215, 215, 5, 10), (215, 215, 11, 34), (215, 215, 11, 34), (215, 215, 36, 37), (215, 215, 5, 38), (215, 215, 5, 38), (215, 215, 5, 38), (215, 215, 5, 38), (215, 215, 5, 38), (215, 215, 5, 38), (215, 215, 5, 38), (215, 215, 39, 40), (215, 215, 5, 41), (215, 215, 5, 41), (215, 215, 5, 41), (215, 215, 5, 41), (215, 215, 5, 41), (215, 215, 0, 2), (217, 217, 1, 8), (218, 240, 0, 18), (218, 240, 0, 18), (217, 217, 1, 8), (217, 217, 1, 8), (217, 217, 1, 8), (217, 217, 1, 8), (217, 217, 1, 8), (217, 217, 1, 8), (217, 217, 1, 8), (218, 240, 0, 18), (244, 244, 1, 8), (245, 325, 0, 35), (245, 325, 0, 35), (244, 244, 1, 8), (244, 244, 1, 8), (244, 244, 1, 8), (244, 244, 1, 8), (244, 244, 1, 8), (244, 244, 1, 8), (244, 244, 1, 8), (245, 325, 0, 35), (330, 330, 10, 15), (330, 330, 10, 15), (330, 330, 16, 115), (330, 330, 16, 115), (330, 330, 117, 118), (330, 330, 10, 119), (330, 330, 10, 119), (330, 330, 10, 119), (330, 330, 10, 119), (330, 330, 10, 119), (330, 330, 10, 119), (330, 330, 10, 119), (330, 330, 120, 121), (330, 330, 10, 122), (330, 330, 10, 122), (330, 330, 10, 122), (330, 330, 10, 122), (330, 330, 10, 122), (330, 330, 0, 7), (332, 332, 13, 18), (332, 332, 13, 18), (332, 332, 19, 92), (332, 332, 19, 92), (332, 332, 94, 95), (332, 332, 13, 96), (332, 332, 13, 96), (332, 332, 13, 96), (332, 332, 13, 96), (332, 332, 13, 96), (332, 332, 13, 96), (332, 332, 13, 96), (332, 332, 97, 98), (332, 332, 13, 99), (332, 332, 13, 99), (332, 332, 13, 99), (332, 332, 13, 99), (332, 332, 13, 99), (332, 332, 0, 10), (334, 334, 12, 17), (334, 334, 12, 17), (334, 334, 18, 81), (334, 334, 18, 81), (334, 334, 83, 84), (334, 334, 12, 85), (334, 334, 12, 85), (334, 334, 12, 85), (334, 334, 12, 85), (334, 334, 12, 85), (334, 334, 12, 85), (334, 334, 12, 85), (334, 334, 86, 87), (334, 334, 12, 88), (334, 334, 12, 88), (334, 334, 12, 88), (334, 334, 12, 88), (334, 334, 12, 88), (334, 334, 0, 9), (336, 336, 5, 10), (336, 336, 5, 10), (336, 336, 11, 34), (336, 336, 11, 34), (336, 336, 36, 37), (336, 336, 5, 38), (336, 336, 5, 38), (336, 336, 5, 38), (336, 336, 5, 38), (336, 336, 5, 38), (336, 336, 5, 38), (336, 336, 5, 38), (336, 336, 39, 40), (336, 336, 5, 41), (336, 336, 5, 41), (336, 336, 5, 41), (336, 336, 5, 41), (336, 336, 5, 41), (336, 336, 0, 2), (338, 338, 1, 8), (339, 398, 0, 35), (339, 398, 0, 35), (338, 338, 1, 8), (338, 338, 1, 8), (338, 338, 1, 8), (338, 338, 1, 8), (338, 338, 1, 8), (338, 338, 1, 8), (338, 338, 1, 8), (339, 398, 0, 35), (339, 398, 0, 35), (339, 398, 0, 35)])", None, None)?;
            let data = std::fs::read("src/epscript/test/data2")?;
            let linetable_before = std::fs::read("src/epscript/test/linetable_before2")?;
            let linetable = generate_linetable(&data, linetable_before, positions.downcast()?)?;
            let linetable_after = std::fs::read("src/epscript/test/linetable_after2")?;
            assert_eq!(linetable, linetable_after);

            Ok(())
        })
    }
}
