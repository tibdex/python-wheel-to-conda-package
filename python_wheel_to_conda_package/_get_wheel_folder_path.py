import re
from typing import Iterable, Optional


def get_wheel_folder_path(
    file_paths: Iterable[str], /, *, folder_type: str
) -> Optional[str]:
    for file_path in file_paths:
        match = re.match(
            f"^(?P<folder_path>(?P<module_name>[^-]+)-(?P<version>([^.]+\\.)+){re.escape(folder_type)})\\/",
            file_path,
        )
        if match:
            return match.group("folder_path")

    return None
