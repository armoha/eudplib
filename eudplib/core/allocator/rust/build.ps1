#!/bin/sh
echo `# <#`

$RootPath = $PSScriptRoot  | Split-Path
cargo build --manifest-path=$RootPath/rust/Cargo.toml --release
Remove-Item -Path "$RootPath/allocator.cp311-win_amd64.pyd"
Copy-Item "$RootPath/rust/target/release/allocator.dll" -Destination "$RootPath"
Rename-Item -Path "$RootPath/allocator.dll" -NewName "allocator.cp311-win_amd64.pyd"

exit
#> > $null

$RootPath = $PSScriptRoot  | Split-Path
cargo build --manifest-path=$RootPath/rust/Cargo.toml --release
Remove-Item -Path "$RootPath/allocator.cp311-win_amd64.pyd"
Copy-Item "$RootPath/rust/target/release/allocator.dll" -Destination "$RootPath"
Rename-Item -Path "$RootPath/allocator.dll" -NewName "allocator.cp311-win_amd64.pyd"
