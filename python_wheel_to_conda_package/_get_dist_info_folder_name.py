import re
from typing import Iterable


def get_dist_info_folder_name(file_paths: Iterable[str], /) -> str:
    try:
        return next(
            file_path.split("/")[0]
            for file_path in file_paths
            if re.match(
                r"^(?P<name>[^-]+)-(?P<version>([a-zA-Z0-9]+\.)+)dist-info\/", file_path
            )
        )
    except StopIteration as error:
        raise RuntimeError(
            "Could not find `dist.info` folder name from the given file paths."
        ) from error
