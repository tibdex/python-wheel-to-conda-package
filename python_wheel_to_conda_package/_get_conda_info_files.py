from __future__ import annotations

import json
import re
from typing import Any, Dict, Iterable

from ._get_conda_dependency_version import get_conda_dependency_version
from ._get_site_packages_path import get_site_packages_path
from ._wheel_dist_info import RecordItem, WheelDistInfo

_JSON_INDENT = 2


def _get_index_json(*, timestamp: int, wheel_dist_info: WheelDistInfo) -> str:
    build_number: int = 0
    build_string: str = "py_0"

    if wheel_dist_info.wheel.build_string:
        match = re.match(
            r"^(?P<build_number>\d+)_(?P<build_string>\d+)",
            wheel_dist_info.wheel.build_string,
        )

        if match:
            build_number = int(match.group("build_number"))
            build_string = match.group("build_string")
        else:
            build_string = wheel_dist_info.wheel.build_string

    depends = [f"python {wheel_dist_info.metadata.requires_python}"]

    for wheel_dependency in wheel_dist_info.metadata.requires_dist:
        dependency_name, dependency_version = wheel_dependency.split(" ", maxsplit=1)
        depends.append(
            f"{dependency_name} {get_conda_dependency_version(dependency_version.strip())}".strip()
        )

    index: Dict[str, Any] = {
        "arch": None,
        "build": build_string,
        "build_number": build_number,
        "depends": depends,
        "name": wheel_dist_info.metadata.package_name,
        "noarch": "python",
        "platform": None,
        "subdir": "noarch",
        "timestamp": timestamp,
        "version": wheel_dist_info.metadata.version,
    }

    return json.dumps(index, indent=_JSON_INDENT)


def _get_paths_json(record_items: Iterable[RecordItem], /) -> str:
    paths: Dict[str, Any] = {
        "paths": [
            {
                "_path": get_site_packages_path(record_item.file_path),
                "path_type": "hardlink",
                "sha256": record_item.sha256,
                "size_in_bytes": record_item.size_in_bytes,
            }
            for record_item in record_items
        ],
        "paths_version": 1,
    }

    return json.dumps(paths, indent=_JSON_INDENT)


def get_conda_info_files(
    *, timestamp: int, wheel_dist_info: WheelDistInfo
) -> Dict[str, str]:
    return {
        "index.json": _get_index_json(
            timestamp=timestamp, wheel_dist_info=wheel_dist_info
        ),
        "paths.json": _get_paths_json(wheel_dist_info.record.items),
    }
