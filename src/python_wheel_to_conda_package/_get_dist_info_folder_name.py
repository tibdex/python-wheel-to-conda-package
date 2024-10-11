from collections.abc import Collection

from ._get_wheel_folder_path import get_wheel_folder_path

_DIST_INFO_FOLDER_TYPE = "dist-info"


def get_dist_info_folder_name(file_paths: Collection[str], /) -> str:
    dist_info_folder_name = get_wheel_folder_path(
        file_paths, folder_type=_DIST_INFO_FOLDER_TYPE
    )

    if not dist_info_folder_name:
        raise RuntimeError(f"Could not find `{_DIST_INFO_FOLDER_TYPE}` folder name.")

    return dist_info_folder_name
