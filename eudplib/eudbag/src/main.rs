use std::fmt;
use std::fs::File;
use std::io::{BufWriter, Write};

#[deny(non_snake_case)]
#[derive(Clone, Debug)]
enum Item {
    Space(u16),
    NextPtr,
    NoCondType,
    NoCondFlag,
    BitMask(u16),
    DestValueUnitActTypeModifierActFlagSC(u16),
    NoActType,
    NoActFlag,
    TrgFlag,
    Breakpoint,
}

impl Item {
    fn size(&self) -> u16 {
        use Item::*;
        match self {
            Breakpoint => 0,
            Space(spaces) => *spaces,
            NoCondType | NoCondFlag | NoActType | NoActFlag | TrgFlag => 1,
            NextPtr | BitMask(_) => 4,
            DestValueUnitActTypeModifierActFlagSC(_) => 16,
        }
    }
    fn is_zero(&self) -> bool {
        use Item::*;
        match self {
            NoCondType | NoCondFlag | NoActType | NoActFlag => true,
            _ => false,
        }
    }
}

struct Layout {
    layout: Vec<Item>,
    actno: u16,
    distance: u16,
}
impl Layout {
    fn find_insert(&self, index: u16, new_item: Item) -> Option<(usize, Vec<Item>)> {
        use Item::*;
        match new_item {
            Space(_) => panic!("Space can't be inserted"),
            NextPtr | NoCondType | NoCondFlag => {
                panic!("Inserted initial items: {:?}", new_item)
            }
            _ => (),
        };
        let size = new_item.size();
        let mut pos = 0;
        for (n, item) in self.layout.iter().enumerate() {
            if new_item.is_zero() && pos == index && item.is_zero() {
                return Some((n, vec![new_item]));
            }
            if pos <= index && pos + item.size() >= index + size {
                if size == 0 {
                    return if pos + item.size() == index {
                        Some((n, vec![item.clone(), new_item]))
                    } else if pos == index {
                        return Some((n, vec![new_item, item.clone()]));
                    } else {
                        match item {
                            Space(spaces) => {
                                let mut ret = vec![];
                                if pos < index {
                                    ret.push(Space(index - pos));
                                }
                                ret.push(new_item);
                                if pos + spaces > index {
                                    ret.push(Space(spaces - (index - pos)));
                                }
                                return Some((n, ret));
                            }
                            _ => None,
                        }
                    };
                }
                match item {
                    Space(spaces) => {
                        let mut ret = vec![];
                        if pos < index {
                            ret.push(Space(index - pos));
                        }
                        ret.push(new_item);
                        if pos + spaces > index + size {
                            ret.push(Space(spaces - (index - pos + size)));
                        }
                        return Some((n, ret));
                    }
                    _ => (),
                }
            }
            pos += item.size();
        }
        None
    }
    fn insert(&mut self, offset: u16, item: Item) -> Option<()> {
        println!("insert {item:?} at {offset}");
        match self.find_insert(offset, item) {
            Some((n, ret)) => {
                self.layout.remove(n);
                println!("... Ok! {ret:?} at {n}");
                for item in ret.into_iter().rev() {
                    self.layout.insert(n, item);
                }
                Some(())
            }
            None => None,
        }
    }
    fn with_action_count_and_distance(actno: u16, distance: u16) -> Option<Layout> {
        use Item::*;
        let mut layout = Layout {
            layout: vec![
                NextPtr,
                Space(15),
                NoCondType,
                Space(1),
                NoCondFlag,
                Space(distance - 22),
            ],
            actno: actno,
            distance: distance,
        };
        for k in 0..actno {
            layout.insert((k * 32 + 324) % distance, BitMask(k))?;
            layout.insert(
                (k * 32 + 340) % distance,
                DestValueUnitActTypeModifierActFlagSC(k),
            )?;
        }
        if 1 <= actno && actno < 64 {
            layout.insert((actno * 32 + 350) % distance, NoActType)?;
            layout.insert((actno * 32 + 352) % distance, NoActFlag)?;
        }
        layout.insert(2372 % distance, TrgFlag)?;
        if 2376 % distance != 0 {
            layout.insert(2376 % distance, Breakpoint)?;
        }
        Some(layout)
    }
}

impl fmt::Display for Layout {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        writeln!(
            f,
            "def write{}(buf, count, nptr, val):
    for i in range({} + count):",
            self.actno,
            2375 / self.distance
        )?;
        for item in self.layout.iter() {
            use Item::*;
            match item {
                Space(size) => writeln!(f, "        buf.WriteSpace({})", size)?,
                NextPtr => writeln!(
                    f,
                    "        buf.WriteDword(nptr[i]) if i < count else buf.WriteSpace(4)"
                )?,
                NoCondType => writeln!(
                    f,
                    "        buf.WriteByte(0) if i < count else buf.WriteSpace(1)  # nocond"
                )?,
                NoCondFlag => writeln!(
                    f,
                    "        buf.WriteByte(0) if i < count else buf.WriteSpace(1)  # condflag"
                )?,
                BitMask(n) => writeln!(
                    f,
                    "        buf.WriteDword(val[i - {1}][{0}][0]) if {1} <= i < {1} + count else buf.WriteSpace(4)",
                    n,
                    (324 + 32 * n) / self.distance
                )?,
                DestValueUnitActTypeModifierActFlagSC(n) => writeln!(
                    f,
                    "        if {1} <= i < {1} + count:
            buf.WriteDword(val[i - {1}][{0}][1])
            buf.WriteDword(val[i - {1}][{0}][2])
            buf.WriteDword(val[i - {1}][{0}][3])
            buf.WriteDword(val[i - {1}][{0}][4])
        else:
            buf.WriteSpace(16)",
                    n,
                    (340 + 32 * n) / self.distance
                )?,
                NoActType => writeln!(
                    f,
                    "        buf.WriteByte(0) if {0} <= i < {0} + count else buf.WriteSpace(1)  # noact",
                    (self.actno * 32 + 350) / self.distance
                )?,
                NoActFlag => writeln!(
                    f,
                    "        buf.WriteByte(0) if {0} <= i < {0} + count else buf.WriteSpace(1)  # actflag",
                    (self.actno * 32 + 352) / self.distance
                )?,
                TrgFlag => writeln!(
                    f,
                    "        buf.WriteByte(4) if {} <= i else buf.WriteSpace(1)",
                    2375 / self.distance
                )?,
                Breakpoint => writeln!(
                    f,
                    "        if i == {} + count - 1:
            break",
                    2375 / self.distance
                )?,
            }
        }
        Ok(())
    }
}

fn main() {
    use Item::*;
    #[rustfmt::skip]
    let distance = vec![
      20,
      72,  132,  212,  228,  260,  260,  292,  292,
     616,  648,  680,  708,  740,  772,  812,  844,
     876,  908,  940,  972, 1004, 1028, 1060, 1092,
    1124, 1156, 1204, 1236, 1268, 1300, 1332, 1364,
    1396, 1428, 1460, 1492, 1524, 1556, 1588, 1620,
    1652, 1684, 1716, 1748, 1780, 1812, 1844, 1876,
    1908, 1940, 1972, 2004, 2036, 2052, 2084, 2116,
    2148, 2180, 2212, 2244, 2276, 2308, 2340, 2376];

    let f = File::create("writebuf.py").expect("Unable to create file");
    let mut f = BufWriter::new(f);
    writeln!(f, "# Generated by bufgen.rs (DO NOT MODIFY manually!)\n").unwrap();
    for n in 1..=64 {
        let layout = Layout::with_action_count_and_distance(n as u16, distance[n] as u16)
            .expect(&format!("Failed {}: {}", n, distance[n]));
        write!(f, "{layout}\n\n").unwrap();
    }
    match Layout::with_action_count_and_distance(8, 292) {
        Some(layout) => {
            println!("{}", layout);
            for item in &layout.layout {
                match item {
                    Space(size) => print!("_{size}"),
                    NextPtr => print!("N"),
                    NoCondType => print!("x"),
                    NoCondFlag => print!("f"),
                    BitMask(n) => print!("m{n}"),
                    DestValueUnitActTypeModifierActFlagSC(n) => print!("dvmS{n}"),
                    NoActType => print!("X"),
                    NoActFlag => print!("F"),
                    TrgFlag => print!("T"),
                    Breakpoint => print!("|"),
                }
            }
            println!("");
        }
        None => (),
    };
    #[rustfmt::skip]
    let layout = vec![
        NextPtr, Space(15), NoCondType, Space(2), NoActType, Space(9),
        BitMask(0), TrgFlag, Space(3), Breakpoint, Space(8), DestValueUnitActTypeModifierActFlagSC(0),
        BitMask(1), Space(12),         DestValueUnitActTypeModifierActFlagSC(1),
        BitMask(2), Space(12),         DestValueUnitActTypeModifierActFlagSC(2),
        BitMask(3), Space(12),         DestValueUnitActTypeModifierActFlagSC(3),
        BitMask(4), Space(12),         DestValueUnitActTypeModifierActFlagSC(4),
        BitMask(5), Space(12),         DestValueUnitActTypeModifierActFlagSC(5),
        BitMask(6), Space(12),         DestValueUnitActTypeModifierActFlagSC(6),
        BitMask(7), Space(12),         DestValueUnitActTypeModifierActFlagSC(7),
        Space(4),
    ];
    for item in &layout {
        match item {
            Space(size) => print!("_{size}"),
            NextPtr => print!("N"),
            NoCondType => print!("x"),
            NoCondFlag => print!("f"),
            BitMask(n) => print!("m{n}"),
            DestValueUnitActTypeModifierActFlagSC(n) => print!("dvmS{n}"),
            NoActType => print!("X"),
            NoActFlag => print!("F"),
            TrgFlag => print!("T"),
            Breakpoint => print!("|"),
        }
    }
}
