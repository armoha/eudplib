# Copyright 2024 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from __future__ import annotations

class MPQ:
    @staticmethod
    def open(path: str) -> MPQ: ...
    @staticmethod
    def create(path: str, sector_size: int = 3, file_count: int = 1024) -> MPQ: ...
    def get_file_names_from_listfile(self) -> list[str]: ...
    def extract_file(self, file_path: str) -> bytes: ...
    def add_file(
        self, archived_name: str, file_path: str, replace_existing: bool = True
    ) -> None: ...
    @staticmethod
    def set_file_locale(file_locale: int) -> None: ...
    def get_max_file_count(self) -> int: ...
    def set_max_file_count(self, count: int) -> None: ...
    def compact(self) -> None: ...
    @staticmethod
    def clone_with_sector_size(
        input_path: str, output_path: str, sector_size: int
    ) -> MPQ: ...
