import json
import tarfile
from io import BytesIO
from pathlib import Path
from typing import Mapping, Optional
from zipfile import ZipFile

from ._get_conda_info_files import get_conda_info_files
from ._get_wheel_folder_path import get_wheel_folder_path
from ._get_wheel_path_to_conda_path import get_wheel_path_to_conda_path
from ._read_zip_file import read_zip_file
from ._wheel_dist_info import WheelDistInfo

_DIST_INFO_FOLDER_TYPE = "dist-info"


def python_wheel_to_conda_package(
    wheel_path: Path,
    /,
    *,
    additional_requirements: Optional[Mapping[str, str]] = None,
    output_directory: Optional[Path] = None,
) -> Path:
    """Convert a Pure-Python Wheel to a noarch Conda package.

    Args:
        wheel_path: The path to the Wheel file to convert.
        additional_requirements: Mapping of package name to their version specification.
            These packages will be added to the Conda package's requirements.
        output_directory: The directory in which the Conda package will be created.
            If ``None``, the directory of the input Wheel is used.

    Returns:
        The path of the created Conda package.
    """
    if additional_requirements is None:
        additional_requirements = {}

    if not wheel_path.is_file():
        raise ValueError(f"`{wheel_path}` does not point to an existing path.")

    if output_directory:
        if not output_directory.is_dir():
            raise ValueError(f"`{output_directory}` is not a directory.")
    else:
        output_directory = wheel_path.parent

    timestamp = round(wheel_path.stat().st_mtime * 1000)

    with ZipFile(wheel_path) as zip:
        file_paths = zip.namelist()

        dist_info_folder_name = get_wheel_folder_path(
            file_paths, folder_type=_DIST_INFO_FOLDER_TYPE
        )

        if not dist_info_folder_name:
            raise RuntimeError(
                f"Could not find `{_DIST_INFO_FOLDER_TYPE}` folder name."
            )

        data_folder_name = get_wheel_folder_path(file_paths, folder_type="data/data")

        dist_info_files = {
            file_path.split("/")[-1]: read_zip_file(zip, file_path)
            for file_path in file_paths
            if file_path.startswith(f"{dist_info_folder_name}/")
        }

        wheel_dist_info = WheelDistInfo.parse(
            dist_info_files, dist_info_folder_name=dist_info_folder_name
        )
        conda_info_files = get_conda_info_files(
            additional_requirements=additional_requirements,
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

                tar.addfile(tar_info, zip.open(record_item.file_path))

    return conda_package_path
