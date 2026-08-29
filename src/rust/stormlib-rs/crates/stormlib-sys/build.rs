extern crate cmake;

use std::env;

fn main() {
  // Gets StormLib source path from env STORMLIB_DIR
  let stormlib_path = env::var("STORMLIB_DIR").unwrap_or("../../deps/StormLib".to_string());

  println!("cargo:rerun-if-changed={}", stormlib_path);

  // Builds StormLib using cmake
  let mut cfg = cmake::Config::new(&stormlib_path);

  #[cfg(target_os = "windows")]
  {
    cfg.cxxflag("-D UNICODE")
    .cxxflag("-D _UNICODE");
  }

  #[cfg(target_os = "macos")]
  {
    cfg.cflag("-Wno-implicit-function-declaration");
  }

  let dst = cfg
    .define("BUILD_SHARED_LIBS", "OFF")
    .build();

  let lib = dst.join("lib");

  // For gcc should link static storm first! (before adding -l flags)
  // That's very important and I've wasted an hour finding it >_<
  // source: https://stackoverflow.com/questions/29199107/c-lz-library-link-order-undefined-reference-to-symbol-inflateinit2
  println!("cargo:rustc-link-search=native={}", lib.display());

  #[cfg(target_os = "windows")]
  {
    println!("cargo::rustc-link-lib=static=StormLib");
    println!("cargo:rustc-link-lib=user32");
  } 

  #[cfg(target_os = "macos")]
  {
    println!("cargo:rustc-link-lib=static=storm");
    println!("cargo:rustc-link-lib=dylib=c++");
    println!("cargo:rustc-link-lib=z");
    println!("cargo:rustc-link-lib=bz2");
  } 
  
  #[cfg(target_os = "linux")]
  {
    println!("cargo:rustc-link-lib=static=storm");
    println!("cargo:rustc-link-lib=stdc++");
    println!("cargo:rustc-link-lib=z");
    println!("cargo:rustc-link-lib=bz2");
  }
}
