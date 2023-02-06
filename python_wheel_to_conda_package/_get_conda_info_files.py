from __future__ import annotations

import json
import re
from typing import Any, Dict, Iterable, Mapping, Optional

from ._get_conda_version_specification import get_conda_version_specification
from ._get_wheel_path_to_conda_path import get_wheel_path_to_conda_path
from ._wheel_dist_info import RecordItem, WheelDistInfo

_JSON_INDENT = 2


def _get_index_json(
    *,
    additional_requirements: Mapping[str, str],
    timestamp: int,
    wheel_dist_info: WheelDistInfo,
) -> str:
    build_number: int = 0
    build_string: str = "py_0"

    if wheel_dist_info.wheel.build_string:
        match = re.match(
            r"^(?P<build_number>\d+)_(?P<build_string>[a-z0-9]+)",
            wheel_dist_info.wheel.build_string,
        )

        if match:
            build_number = int(match.group("build_number"))
            build_string = match.group("build_string")
        else:
            build_string = wheel_dist_info.wheel.build_string

    requirements = {"python": wheel_dist_info.metadata.requires_python}

    for wheel_requirement in wheel_dist_info.metadata.requires_dist:
        package_name = wheel_requirement
        conda_version_specification = ""

        if " " in wheel_requirement:
            package_name, wheel_version_declaration = wheel_requirement.split(
                " ", maxsplit=1
            )
            conda_version_specification = get_conda_version_specification(
                wheel_version_declaration
            )

        requirements[package_name] = conda_version_specification

    requirements.update(additional_requirements)

    index: Dict[str, Any] = {
        "arch": None,
        "build": build_string,
        "build_number": build_number,
        "depends": [
            f"{package_name} {version_specification}"
            if version_specification
            else package_name
            for package_name, version_specification in requirements.items()
        ],
        "name": wheel_dist_info.metadata.package_name,
        "noarch": "python",
        "platform": None,
        "subdir": "noarch",
        "timestamp": timestamp,
        "version": wheel_dist_info.metadata.version,
    }

    return json.dumps(index, indent=_JSON_INDENT)


def _get_paths_json(
    record_items: Iterable[RecordItem],
    /,
    *,
    data_folder_name: Optional[str] = None,
) -> str:
    paths: Dict[str, Any] = {
        "paths": [
            {
                "_path": get_wheel_path_to_conda_path(
                    record_item.file_path, data_folder_name=data_folder_name
                ),
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
    *,
    additional_requirements: Mapping[str, str],
    data_folder_name: Optional[str] = None,
    timestamp: int,
    wheel_dist_info: WheelDistInfo,
) -> Dict[str, str]:
    return {
        "index.json": _get_index_json(
            additional_requirements=additional_requirements,
            timestamp=timestamp,
            wheel_dist_info=wheel_dist_info,
        ),
        "link.json": json.dumps(
            {"noarch": {"type": "python"}, "package_metadata_version": 1},
            indent=_JSON_INDENT,
        ),
        "paths.json": _get_paths_json(
            wheel_dist_info.record.items, data_folder_name=data_folder_name
        ),
    }
