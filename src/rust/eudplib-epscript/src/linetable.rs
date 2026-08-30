//! Python 3.11+ `co_linetable` rewriting for epScript.
//!
//! Rewrites the raw `co_linetable` bytes of a code object so that its line
//! numbers point to epScript source lines.
//! Each entry is decoded directly, its start line is mapped
//! through [`LineMap`], and it is re-encoded as kind 13 (no column info).
//! Entries without a location (kind 15) are preserved unchanged.
//!
//! Only applies to Python 3.11+; Python 3.10 uses the legacy `co_lnotab`
//! format, handled elsewhere.
//!
//! # References
//!
//! The `co_linetable` format is specified in
//! [`Objects/locations.md`](https://github.com/python/cpython/blob/3.13/Objects/locations.md)
//! (Python 3.11–3.13). On Python 3.14+/`main` it was inlined into
//! [`InternalDocs/code_objects.md`](https://github.com/python/cpython/blob/main/InternalDocs/code_objects.md).
//! Entry lengths are in code units (2 bytes each), so a
//! table must cover exactly `len(co_code) / 2` units.
//!
//! The decoder follows the line-state machine in
//! [`Objects/codeobject.c`](https://github.com/python/cpython/blob/3.13/Objects/codeobject.c):
//!
//! * `_PyLineTable_NextAddressRange` / `advance()` / `retreat()` /
//!   `get_line_delta` — the start-line delta of an entry is relative to the
//!   previous entry's start line, or `co_firstlineno` for the first entry;
//!   kind 15 consumes no payload and does not change the state.
//! * `advance_with_locations` — exact payload layout per kind:
//!   - 0–9 short form: one column byte, same line;
//!   - 10–12 one-line form: two column bytes, line delta `code - 10`;
//!   - 13 no column info: one signed varint;
//!   - 14 long form: start-line svarint, end-line varint, start-column varint,
//!     end-column varint (columns are stored as `value + 1`, `0` = `None`);
//!   - 15 no location: no payload.
//!
//! The writer mirrors CPython's `remove_column_info`: located entries are
//! rewritten to kind 13 keeping their length and line delta, and kind 15
//! entries are kept as-is.
//!
//! Variable-length integer helpers follow
//! [`Include/internal/pycore_code.h`](https://github.com/python/cpython/blob/3.13/Include/internal/pycore_code.h)
//! (`write_varint`, `write_signed_varint`, `write_location_entry_start`), and
//! the 1..=8 code-unit entry limit comes from the assembler
//! [`Python/compile.c`](https://github.com/python/cpython/blob/3.13/Python/compile.c)
//! (`assemble_emit_location`), which splits longer spans. Original entry
//! lengths are preserved, so no splitting is needed here.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::fmt;

const NO_COLUMNS: u8 = 13;
const NO_LOCATION: u8 = 15;

#[derive(Debug)]
enum LinetableError {
    Truncated { offset: usize, what: &'static str },
    ExpectedHeader { offset: usize },
    UnexpectedHeader { offset: usize },
    VarintOverflow { offset: usize },
    LineOverflow { line: i64 },
    CoverageMismatch { covered: usize, expected: usize },
    UnmappedLine { line: i64 },
    Internal(&'static str),
}

impl fmt::Display for LinetableError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Truncated { offset, what } => {
                write!(
                    f,
                    "unexpected end of linetable at byte {offset} while reading {what}"
                )
            }
            Self::ExpectedHeader { offset } => {
                write!(f, "expected linetable entry header at byte {offset}")
            }
            Self::UnexpectedHeader { offset } => {
                write!(
                    f,
                    "unexpected entry header at byte {offset} inside entry payload"
                )
            }
            Self::VarintOverflow { offset } => {
                write!(f, "linetable varint at byte {offset} is too large")
            }
            Self::LineOverflow { line } => write!(f, "line number overflow: {line}"),
            Self::CoverageMismatch { covered, expected } => write!(
                f,
                "linetable covers {covered} code units but co_code has {expected}"
            ),
            Self::UnmappedLine { line } => write!(f, "no epScript line mapped for line {line}"),
            Self::Internal(what) => write!(f, "internal error: {what}"),
        }
    }
}

impl From<LinetableError> for PyErr {
    fn from(error: LinetableError) -> Self {
        PyValueError::new_err(error.to_string())
    }
}

/// A sorted map from generated Python line numbers to epScript line numbers.
#[pyclass(frozen)]
pub struct LineMap {
    points: Vec<(i64, i64)>,
}

impl LineMap {
    fn from_pairs(points: Vec<(i64, i64)>) -> Self {
        let mut points = points;
        points.sort_by_key(|&(key, _)| key);
        Self { points }
    }

    fn map(&self, line: i64) -> Option<i64> {
        let index = self.points.partition_point(|&(key, _)| key <= line);
        if index == 0 {
            None
        } else {
            Some(self.points[index - 1].1)
        }
    }
}

#[pymethods]
impl LineMap {
    #[new]
    fn new(points: Vec<(i64, i64)>) -> Self {
        Self::from_pairs(points)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Entry {
    length: u8,
    start_line: Option<i64>,
}

struct Reader<'a> {
    data: &'a [u8],
    pos: usize,
}

impl Reader<'_> {
    fn byte(&mut self, what: &'static str) -> Result<u8, LinetableError> {
        let byte = *self.data.get(self.pos).ok_or(LinetableError::Truncated {
            offset: self.pos,
            what,
        })?;
        self.pos += 1;
        Ok(byte)
    }

    fn payload(&mut self, what: &'static str) -> Result<u8, LinetableError> {
        let offset = self.pos;
        let byte = self.byte(what)?;
        if byte & 0x80 != 0 {
            return Err(LinetableError::UnexpectedHeader { offset });
        }
        Ok(byte)
    }

    fn uvarint(&mut self) -> Result<i64, LinetableError> {
        let offset = self.pos;
        let mut value = 0u64;
        let mut chunks = 0u32;
        loop {
            if chunks == 10 {
                return Err(LinetableError::VarintOverflow { offset });
            }
            let byte = self.payload("varint")?;
            value |= u64::from(byte & 0x3f) << (chunks * 6);
            chunks += 1;
            if byte & 0x40 == 0 {
                return Ok(value as i64);
            }
        }
    }

    fn svarint(&mut self) -> Result<i64, LinetableError> {
        let encoded = self.uvarint()?;
        if encoded & 1 != 0 {
            Ok(-(encoded >> 1))
        } else {
            Ok(encoded >> 1)
        }
    }
}

/// Decodes a Python 3.11+ `co_linetable` into entries.
///
/// Column information is discarded; only the start line of each entry and its
/// length in code units are kept. Entries with no location (kind 15) keep
/// `start_line == None` and do not affect the line state of following entries.
fn decode_entries(table: &[u8], firstlineno: i64) -> Result<(Vec<Entry>, usize), LinetableError> {
    let mut reader = Reader {
        data: table,
        pos: 0,
    };
    let mut entries = Vec::new();
    let mut current_line = firstlineno;
    let mut covered = 0usize;
    while reader.pos < table.len() {
        let offset = reader.pos;
        let header = reader.byte("location entry header")?;
        if header & 0x80 == 0 {
            return Err(LinetableError::ExpectedHeader { offset });
        }
        let kind = (header >> 3) & 0x0f;
        let length = (header & 0x07) + 1;
        let start_line = match kind {
            0..=9 => {
                reader.payload("short form column byte")?;
                Some(current_line)
            }
            10..=12 => {
                current_line = current_line
                    .checked_add(i64::from(kind) - 10)
                    .ok_or(LinetableError::LineOverflow { line: current_line })?;
                reader.payload("one line form start column")?;
                reader.payload("one line form end column")?;
                Some(current_line)
            }
            13 => {
                current_line = current_line
                    .checked_add(reader.svarint()?)
                    .ok_or(LinetableError::LineOverflow { line: current_line })?;
                Some(current_line)
            }
            14 => {
                current_line = current_line
                    .checked_add(reader.svarint()?)
                    .ok_or(LinetableError::LineOverflow { line: current_line })?;
                reader.uvarint()?;
                reader.uvarint()?;
                reader.uvarint()?;
                Some(current_line)
            }
            15 => None,
            _ => unreachable!("kind is masked to 4 bits"),
        };
        covered += usize::from(length);
        entries.push(Entry { length, start_line });
    }
    Ok((entries, covered))
}

fn encode_varint(out: &mut Vec<u8>, mut value: u64) {
    loop {
        let chunk = (value & 0x3f) as u8;
        value >>= 6;
        if value == 0 {
            out.push(chunk);
            return;
        }
        out.push(chunk | 0x40);
    }
}

fn encode_svarint(out: &mut Vec<u8>, value: i64) -> Result<(), LinetableError> {
    let encoded = if value < 0 {
        let magnitude = value
            .checked_neg()
            .ok_or(LinetableError::LineOverflow { line: value })? as u64;
        (magnitude << 1) | 1
    } else {
        (value as u64) << 1
    };
    if encoded >> 60 != 0 {
        return Err(LinetableError::LineOverflow { line: value });
    }
    encode_varint(out, encoded);
    Ok(())
}

/// Re-encodes entries with line numbers mapped through `line_map`.
///
/// Located entries are emitted as kind 13 (no column info); entries without a
/// location are preserved as kind 15 so that they keep covering their code
/// units without affecting the line state of following entries.
fn rewrite_entries(
    entries: &[Entry],
    new_firstlineno: i64,
    line_map: &LineMap,
) -> Result<Vec<u8>, LinetableError> {
    let mut out = Vec::with_capacity(entries.len() * 2);
    let mut current_line = new_firstlineno;
    for entry in entries {
        match entry.start_line {
            None => {
                out.push(0x80 | (NO_LOCATION << 3) | (entry.length - 1));
            }
            Some(line) => {
                let mapped = line_map
                    .map(line)
                    .ok_or(LinetableError::UnmappedLine { line })?;
                out.push(0x80 | (NO_COLUMNS << 3) | (entry.length - 1));
                let delta = mapped
                    .checked_sub(current_line)
                    .ok_or(LinetableError::LineOverflow { line: mapped })?;
                encode_svarint(&mut out, delta)?;
                current_line = mapped;
            }
        }
    }
    Ok(out)
}

/// generate_linetable(line_map, linetable, code, firstlineno, /)
/// --
///
/// Rewrites a Python 3.11+ `co_linetable` so that its line numbers point to
/// epScript source lines, using the given line map.
///
/// Returns a `(new_firstlineno, new_linetable)` tuple.
///
/// # Arguments
///
/// * `line_map` - `LineMap` of generated Python line to epScript line
/// * `linetable` - `codeobj.co_linetable` bytes
/// * `code` - `codeobj.co_code` bytes, used to validate table coverage
/// * `firstlineno` - `codeobj.co_firstlineno`
#[pyfunction]
#[pyo3(signature = (line_map, linetable, code, firstlineno, /))]
pub fn generate_linetable<'py>(
    py: Python<'py>,
    line_map: PyRef<'_, LineMap>,
    linetable: &[u8],
    code: &[u8],
    firstlineno: i64,
) -> PyResult<(i64, Bound<'py, PyBytes>)> {
    if code.len() % 2 != 0 {
        return Err(PyValueError::new_err(
            "co_code length must be a multiple of two",
        ));
    }
    let code_units = code.len() / 2;
    let new_firstlineno = line_map
        .map(firstlineno)
        .ok_or(LinetableError::UnmappedLine { line: firstlineno })?;

    let (entries, covered) = decode_entries(linetable, firstlineno)?;
    if covered != code_units {
        return Err(LinetableError::CoverageMismatch {
            covered,
            expected: code_units,
        }
        .into());
    }

    let new_table = rewrite_entries(&entries, new_firstlineno, &line_map)?;

    let (redecoded, recovered) = decode_entries(&new_table, new_firstlineno)?;
    if recovered != code_units {
        return Err(LinetableError::CoverageMismatch {
            covered: recovered,
            expected: code_units,
        }
        .into());
    }
    for (entry, redecoded_entry) in entries.iter().zip(redecoded.iter()) {
        if entry.length != redecoded_entry.length {
            return Err(LinetableError::Internal("entry length mismatch").into());
        }
        match (entry.start_line, redecoded_entry.start_line) {
            (None, None) => {}
            (Some(line), Some(new_line)) => {
                if line_map.map(line) != Some(new_line) {
                    return Err(LinetableError::Internal("entry line mismatch").into());
                }
            }
            _ => {
                return Err(LinetableError::Internal("entry location mismatch").into());
            }
        }
    }

    Ok((new_firstlineno, PyBytes::new(py, &new_table)))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_decode_all_kinds() {
        let table = [
            0xD0, 0x05, 0x07, // kind 10, 1 unit, +0
            0xD9, 0x01, 0x02, // kind 11, 2 units, +1
            0x91, 0x35, // kind 2 (short form), 2 units, same line
            0xF0, 0x00, 0x02, 0x01, 0x01, // kind 14, 1 unit, +0
            0xF8, // kind 15, 1 unit
        ];
        let (entries, covered) = decode_entries(&table, 3).unwrap();
        assert_eq!(covered, 7);
        assert_eq!(
            entries,
            vec![
                Entry {
                    length: 1,
                    start_line: Some(3)
                },
                Entry {
                    length: 2,
                    start_line: Some(4)
                },
                Entry {
                    length: 2,
                    start_line: Some(4)
                },
                Entry {
                    length: 1,
                    start_line: Some(4)
                },
                Entry {
                    length: 1,
                    start_line: None
                },
            ]
        );
    }

    #[test]
    fn test_no_location_preserves_line_state() {
        let table = [
            0xE8, 0x08, // kind 13, +4 -> line 5
            0xF8, // kind 15, no line state change
            0xE8, 0x02, // kind 13, +1 -> line 6
        ];
        let (entries, covered) = decode_entries(&table, 1).unwrap();
        assert_eq!(covered, 3);
        assert_eq!(
            entries,
            vec![
                Entry {
                    length: 1,
                    start_line: Some(5)
                },
                Entry {
                    length: 1,
                    start_line: None
                },
                Entry {
                    length: 1,
                    start_line: Some(6)
                },
            ]
        );
    }

    #[test]
    fn test_decode_errors() {
        assert!(matches!(
            decode_entries(&[0xE8, 0x40], 1),
            Err(LinetableError::Truncated { .. })
        ));
        assert!(matches!(
            decode_entries(&[0xE8, 0x80], 1),
            Err(LinetableError::UnexpectedHeader { .. })
        ));
        assert!(matches!(
            decode_entries(&[0x00], 1),
            Err(LinetableError::ExpectedHeader { .. })
        ));
        let mut overflow = vec![0xE8];
        overflow.extend(std::iter::repeat(0x40).take(10));
        assert!(matches!(
            decode_entries(&overflow, 1),
            Err(LinetableError::VarintOverflow { .. })
        ));
    }

    #[test]
    fn test_line_map_lookup() {
        let line_map = LineMap::from_pairs(vec![(0, 0), (3, 30), (7, 70)]);
        assert_eq!(line_map.map(-1), None);
        assert_eq!(line_map.map(0), Some(0));
        assert_eq!(line_map.map(2), Some(0));
        assert_eq!(line_map.map(3), Some(30));
        assert_eq!(line_map.map(6), Some(30));
        assert_eq!(line_map.map(7), Some(70));
        assert_eq!(line_map.map(1000), Some(70));
        assert_eq!(LineMap::from_pairs(vec![]).map(1), None);
    }

    #[test]
    fn test_generate_linetable_roundtrip() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let line_map = Py::new(
                py,
                LineMap::from_pairs(vec![(0, 0), (1, 10), (2, 20), (5, 50)]),
            )
            .unwrap();
            let table = [
                0xE8, 0x00, // kind 13, 1 unit, +0 -> line 1
                0xF8, // kind 15, 1 unit
                0xE9, 0x08, // kind 13, 2 units, +4 -> line 5
                0xE8, 0x07, // kind 13, 1 unit, -3 -> line 2
            ];
            let code = [0u8; 10];
            let (new_firstlineno, new_table) =
                generate_linetable(py, line_map.borrow(py), &table, &code, 1).unwrap();
            assert_eq!(new_firstlineno, 10);
            assert_eq!(
                new_table.as_bytes(),
                [0xE8, 0x00, 0xF8, 0xE9, 0x50, 0x01, 0xE8, 0x3D]
            );
            let (entries, covered) = decode_entries(new_table.as_bytes(), 10).unwrap();
            assert_eq!(covered, 5);
            assert_eq!(
                entries,
                vec![
                    Entry {
                        length: 1,
                        start_line: Some(10)
                    },
                    Entry {
                        length: 1,
                        start_line: None
                    },
                    Entry {
                        length: 2,
                        start_line: Some(50)
                    },
                    Entry {
                        length: 1,
                        start_line: Some(20)
                    },
                ]
            );
        });
    }

    #[test]
    fn test_generate_linetable_errors() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let line_map = Py::new(py, LineMap::from_pairs(vec![(0, 0)])).unwrap();
            let empty_map = Py::new(py, LineMap::from_pairs(vec![])).unwrap();

            assert!(
                generate_linetable(py, line_map.borrow(py), &[0xE8, 0x00], &[0, 1, 2], 1).is_err()
            );
            assert!(
                generate_linetable(py, line_map.borrow(py), &[0xE8, 0x00], &[0, 1, 2, 3], 1)
                    .is_err()
            );
            assert!(
                generate_linetable(py, empty_map.borrow(py), &[0xE8, 0x00], &[0, 1], 1).is_err()
            );
            assert!(generate_linetable(py, line_map.borrow(py), &[0xE8], &[0, 1], 1).is_err());
        });
    }

    #[test]
    fn test_fixture_tables() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            for name in ["linetable_before1", "linetable_before2"] {
                let table = std::fs::read(format!("test/{name}")).unwrap();
                let (entries, covered) = decode_entries(&table, 1).unwrap();
                assert!(!entries.is_empty());
                assert!(covered > 0);
                assert_eq!(
                    entries
                        .iter()
                        .map(|entry| usize::from(entry.length))
                        .sum::<usize>(),
                    covered
                );

                let line_map = Py::new(py, LineMap::from_pairs(vec![(i64::MIN, 0)])).unwrap();
                let code = vec![0u8; covered * 2];
                let (new_firstlineno, new_table) =
                    generate_linetable(py, line_map.borrow(py), &table, &code, 1).unwrap();
                assert_eq!(new_firstlineno, 0);
                let (redecoded, recovered) = decode_entries(new_table.as_bytes(), 0).unwrap();
                assert_eq!(recovered, covered);
                assert_eq!(redecoded.len(), entries.len());
            }
        });
    }
}
