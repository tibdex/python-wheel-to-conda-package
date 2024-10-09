import re
from dataclasses import replace
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from python_wheel_to_conda_package._get_dist_info_folder_name import (
    get_dist_info_folder_name,
)
from python_wheel_to_conda_package._read_zip_file import read_zip_file
from python_wheel_to_conda_package._wheel_dist_info import (
    _RECORD_FILENAME,
    _WHEEL_FILENAME,
    Record,
    RecordItem,
    Wheel,
)


def add_build_tag_to_wheel(wheel_path: Path, build_tag: str, /) -> None:
    with (
        pytest.warns(UserWarning, match=re.escape("Duplicate name")),
        ZipFile(wheel_path, mode="a", compression=ZIP_DEFLATED) as zip_file,
    ):
        file_paths = zip_file.namelist()

        dist_info_folder_name = get_dist_info_folder_name(file_paths)

        wheel_file_path = f"{dist_info_folder_name}/{_WHEEL_FILENAME}"

        wheel = Wheel.parse(read_zip_file(zip_file, wheel_file_path).decode().rstrip())
        wheel_with_build_tag = replace(wheel, build_tag=build_tag)

        record_file_path = f"{dist_info_folder_name}/{_RECORD_FILENAME}"
        record = Record.parse(
            read_zip_file(zip_file, record_file_path),
            dist_info_folder_name=dist_info_folder_name,
        )
        record_with_changed_wheel = replace(
            record,
            items=[
                RecordItem.from_file_path_and_record(
                    item.file_path, bytes(str(wheel_with_build_tag), "utf-8")
                )
                if item.file_path == wheel_file_path
                else item
                for item in record.items
            ],
        )

        for file_path, new_value in {
            wheel_file_path: wheel_with_build_tag,
            record_file_path: record_with_changed_wheel,
        }.items():
            zip_file.writestr(file_path, str(new_value))
