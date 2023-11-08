from __future__ import annotations


def get_wheel_path_to_conda_path(
    file_path: str, /, *, data_folder_name: str | None
) -> str:
    data_prefix = f"{data_folder_name}/"
    return (
        file_path[len(data_prefix) :]
        if data_folder_name and file_path.startswith(data_prefix)
        else f"site-packages/{file_path}"
    )
