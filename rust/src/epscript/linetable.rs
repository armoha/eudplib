use pyo3::prelude::*;

#[pyfunction]
pub fn calculate_linetable(data: Vec<u8>, linetable: Vec<u8>) -> Vec<u8> {
    Vec::new()
}
#[pyfunction]
pub fn print_linetable(data: Vec<u8>, linetable: Vec<u8>) {
    println!("before: {:?}\nafter: {:?}", data, linetable);
}

struct LinetableReader {
    data: Vec<u8>,
    cursor: usize,
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
        print!("\n");
    }
}
fn get_entries(linetable_bytes: Vec<u8>) -> Vec<Vec<u8>> {
    let linetable_reader = LinetableReader {
        data: linetable_bytes,
        cursor: 0,
    };
    linetable_reader.collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Result as IoResult;

    #[test]
    fn test_linetables() -> IoResult<()> {
        let data = std::fs::read("src/epscript/test/data")?;
        let linetable_before = std::fs::read("src/epscript/test/co_linetable_before")?;
        let linetable_after = std::fs::read("src/epscript/test/co_linetable_after")?;
        print_entries(linetable_after.clone());
        let before = get_entries(linetable_before);
        let after = get_entries(linetable_after);
        assert_eq!(before.len(), after.len());
        Ok(())
    }
}
