use chumsky::prelude::*;

#[derive(Clone)]
enum Instr {
    Left,
    Right,
    Incr,
    Decr,
    Read,
    Write,
    Loop(Vec<Self>),
}

fn parser() -> impl Parser<char, Vec<Instr>, Error = Simple<char>> {
    recursive(|bf| {
        choice((
            just('<').to(Instr::Left),
            just('>').to(Instr::Right),
            just('+').to(Instr::Incr),
            just('-').to(Instr::Decr),
            just(',').to(Instr::Read),
            just('.').to(Instr::Write),
            bf.delimited_by(just('['), just(']')).map(Instr::Loop),
        ))
        .repeated()
    })
}

#[test]
fn test() {}
