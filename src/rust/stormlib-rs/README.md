[![Rust](https://github.com/wc3tools/stormlib-rs/actions/workflows/rust.yml/badge.svg)](https://github.com/wc3tools/stormlib-rs/actions/workflows/rust.yml)

Rust [StormLib](https://github.com/ladislav-zezula/StormLib) binding for working with Blizzard MPQ archives
-

```rust
fn test_read_utf8() {
  let mut archive = Archive::open(
    "../../samples/中文.w3x",
    OpenArchiveFlags::MPQ_OPEN_NO_LISTFILE | OpenArchiveFlags::MPQ_OPEN_NO_ATTRIBUTES,
  )
  .unwrap();
  let mut f = archive.open_file("war3map.j").unwrap();
  assert_eq!(
    f.read_all().unwrap(),
    std::fs::read("../../samples/war3map.j").unwrap()
  );
}
```
