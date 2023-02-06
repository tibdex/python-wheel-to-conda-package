from typing import Optional


def get_wheel_path_to_conda_path(
    file_path: str, /, *, data_folder_name: Optional[str]
) -> str:
    data_prefix = f"{data_folder_name}/"
    return (
        file_path[len(data_prefix) :]
        if data_folder_name and file_path.startswith(data_prefix)
        else f"site-packages/{file_path}"
    )
