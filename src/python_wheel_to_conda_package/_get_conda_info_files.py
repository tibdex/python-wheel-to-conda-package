from __future__ import annotations

import json
import re
from collections.abc import Collection
from typing import Any

from ._get_conda_package_match_specification import (
    get_conda_package_match_specification,
)
from ._get_wheel_path_to_conda_path import get_wheel_path_to_conda_path
from ._wheel_dist_info import RecordItem, WheelDistInfo

_JSON_INDENT = 2


def _get_build_number_and_string(build_tag: str | None, /) -> tuple[int, str]:
    build_number: int = 0
    build_string: str = "py_0"

    if build_tag:
        match = re.match(
            r"^(?P<build_number>\d+)_(?P<build_string>[a-z0-9]+)",
            build_tag,
        )

        if match:
            int(match.group("build_number"))
            build_string = match.group("build_string")
        else:
            build_string = build_tag

    forbidden_character = "-"
    if forbidden_character in build_string:
        # See https://docs.conda.io/projects/conda-build/en/latest/resources/define-metadata.html#build-number-and-string.
        raise ValueError(
            f"The build string cannot contain `{forbidden_character}`, got `{build_string}`."
        )

    return build_number, build_string


def _get_index_json(
    *,
    timestamp: int,
    wheel_dist_info: WheelDistInfo,
) -> str:
    build_number, build_string = _get_build_number_and_string(
        wheel_dist_info.wheel.build_tag
    )

    requirements: dict[str, str] = {}

    for python_dependency_specification in [
        f"python {wheel_dist_info.metadata.requires_python}".rstrip(),
        *wheel_dist_info.metadata.requires_dist,
    ]:
        conda_package_match_specification = get_conda_package_match_specification(
            python_dependency_specification
        )
        if conda_package_match_specification:
            requirements[conda_package_match_specification.package_name] = (
                conda_package_match_specification.version
            )

    index: dict[str, Any] = {
        "arch": None,
        "build": build_string,
        "build_number": build_number,
        "depends": [
            f"{package_name} {version_specification}".rstrip()
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
    record_items: Collection[RecordItem],
    /,
    *,
    data_folder_name: str | None = None,
) -> str:
    paths: dict[str, Any] = {
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
    data_folder_name: str | None = None,
    timestamp: int,
    wheel_dist_info: WheelDistInfo,
) -> dict[str, str]:
    return {
        "index.json": _get_index_json(
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
