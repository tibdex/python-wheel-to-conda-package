from __future__ import annotations

import json
import tarfile
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from ._get_conda_info_files import get_conda_info_files
from ._get_dist_info_folder_name import get_dist_info_folder_name
from ._get_wheel_folder_path import get_wheel_folder_path
from ._get_wheel_path_to_conda_path import get_wheel_path_to_conda_path
from ._read_zip_file import read_zip_file
from ._wheel_dist_info import WheelDistInfo


def python_wheel_to_conda_package(
    wheel_path: Path,
    /,
    *,
    output_directory: Path | None = None,
) -> Path:
    """Convert a Pure-Python Wheel to a noarch Conda package.

    Args:
        wheel_path: The path to the Wheel file to convert.
        output_directory: The directory in which the Conda package will be created.
            If ``None``, the directory of the input Wheel is used.

    Returns:
        The path of the created Conda package.
    """
    if not wheel_path.is_file():
        raise ValueError(f"`{wheel_path}` does not point to an existing path.")

    if output_directory:
        if not output_directory.exists():
            output_directory.mkdir(exist_ok=True, parents=True)
        elif not output_directory.is_dir():
            raise ValueError(f"`{output_directory}` is not a directory.")
    else:
        output_directory = wheel_path.parent

    timestamp = round(wheel_path.stat().st_mtime * 1000)

    with ZipFile(wheel_path) as zip_file:
        file_paths = zip_file.namelist()

        dist_info_folder_name = get_dist_info_folder_name(file_paths)

        data_folder_name = get_wheel_folder_path(file_paths, folder_type="data/data")

        dist_info_files = {
            file_path.split("/")[-1]: read_zip_file(zip_file, file_path)
            for file_path in file_paths
            if file_path.startswith(f"{dist_info_folder_name}/")
        }

        wheel_dist_info = WheelDistInfo.parse(
            dist_info_files, dist_info_folder_name=dist_info_folder_name
        )
        conda_info_files = get_conda_info_files(
            data_folder_name=data_folder_name,
            timestamp=timestamp,
            wheel_dist_info=wheel_dist_info,
        )

        build_number: str = json.loads(conda_info_files["index.json"])["build"]
        conda_package_file_name = f"{wheel_dist_info.metadata.package_name}-{wheel_dist_info.metadata.version}-{build_number}.tar.bz2"
        conda_package_path = output_directory / conda_package_file_name

        with tarfile.open(conda_package_path, mode="w:bz2") as tar:
            for file_path, file_content in conda_info_files.items():
                file_bytes = bytes(file_content, "utf-8")

                tar_info = tarfile.TarInfo(f"info/{file_path}")
                tar_info.size = len(file_bytes)

                tar.addfile(tar_info, BytesIO(file_bytes))

            for record_item in wheel_dist_info.record.items:
                tar_info = tarfile.TarInfo(
                    get_wheel_path_to_conda_path(
                        record_item.file_path, data_folder_name=data_folder_name
                    )
                )
                tar_info.size = record_item.size_in_bytes

                tar.addfile(tar_info, zip_file.open(record_item.file_path))

    return conda_package_path
