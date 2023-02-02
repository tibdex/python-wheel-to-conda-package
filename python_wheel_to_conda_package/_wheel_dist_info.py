from __future__ import annotations

import hashlib
from base64 import urlsafe_b64decode
from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence

_RECORD_FILENAME = "RECORD"


def _validate_metadata_version(version: str, /) -> str:
    expected_version = "2.1"

    if version == expected_version:
        return version

    raise ValueError(
        f"Expected metadata version to be `{expected_version}` but got `{version}`."
    )


@dataclass(frozen=True)
class Metadata:
    package_name: str
    requires_dist: Sequence[str]
    requires_python: str
    version: str

    @classmethod
    def parse(cls, metadata: str, /) -> Metadata:
        lines = metadata.splitlines()

        empty_line_index = len(lines)

        try:
            empty_line_index = lines.index("")
        except ValueError:
            # No empty line which means there are no long description and all the lines follow the `name: value` format.
            ...

        # Ignore the long description which is separated by the `key: value` lines by an empty line.
        lines = lines[:empty_line_index]

        metadata_version: Optional[str] = None
        package_name: Optional[str] = None
        requires_dist: List[str] = []
        requires_python: Optional[str] = None
        version: Optional[str] = None

        metadata_version_key = "Metadata-Version"

        for line in lines:
            key, value = line.split(": ", maxsplit=1)

            if key == metadata_version_key:
                metadata_version = _validate_metadata_version(value)
            elif key == "Name":
                package_name = value
            elif key == "Version":
                version = value
            elif key == "Requires-Python":
                requires_python = value
            elif key == "Requires-Dist":
                requires_dist.append(value)
            elif key == "Provides-Extra":
                # The extra requirements in a Python Wheel do not have an equivalent in a Conda package.
                break

        if not metadata_version:
            raise ValueError(f"Missing `{metadata_version_key}` metadata.")

        if not package_name:
            raise ValueError("Missing package name.")

        if not requires_python:
            raise ValueError("Missing Python requirement")

        if not version:
            raise ValueError("Missing version.")

        return Metadata(
            package_name=package_name,
            requires_dist=requires_dist,
            requires_python=requires_python,
            version=version,
        )


@dataclass(frozen=True)
class RecordItem:
    file_path: str
    sha256: str
    size_in_bytes: int

    @classmethod
    def parse(
        cls, line: str, /, *, dist_info_folder_name: str, record: bytes
    ) -> RecordItem:
        file_path, _sha256, _size_in_bytes = line.split(",")

        if _sha256 and _size_in_bytes:
            # Reverse logic of https://github.com/pypa/pip/blob/c9df690f3b5bb285a855953272e6fe24f69aa08a/src/pip/_internal/wheel.py#L71-L84.
            sha256 = urlsafe_b64decode(
                f"{_sha256[len('sha256=') :]}=".encode("latin1")
            ).hex()
            size_in_bytes = int(_size_in_bytes)
        else:
            record_path = f"{dist_info_folder_name}/{_RECORD_FILENAME}"
            if file_path != record_path:
                raise RuntimeError(
                    f"`{record_path}` is the only file that can have empty sha256 and size information but got `{file_path}`."
                )

            sha256 = hashlib.sha256(record).hexdigest()
            size_in_bytes = len(record)

        return RecordItem(
            file_path=file_path,
            sha256=sha256,
            size_in_bytes=size_in_bytes,
        )


@dataclass(frozen=True)
class Record:
    items: Sequence[RecordItem]

    @classmethod
    def parse(cls, record: bytes, /, *, dist_info_folder_name: str) -> Record:
        return Record(
            items=[
                RecordItem.parse(
                    line, dist_info_folder_name=dist_info_folder_name, record=record
                )
                for line in record.decode().rstrip().splitlines()
            ]
        )


@dataclass(frozen=True)
class Wheel:
    build_string: Optional[str] = None

    @classmethod
    def parse(cls, wheel: str, /) -> Wheel:
        entries: Dict[str, str] = {}

        for line in wheel.splitlines():
            key, value = line.split(": ", maxsplit=1)
            entries[key] = value

        expected_entries = {
            "Root-Is-Purelib": "true",
            "Tag": "py3-none-any",
            "Wheel-Version": "1.0",
        }

        for key, expected_value in expected_entries.items():
            actual_value = entries.get(key)

            if actual_value != expected_value:
                raise ValueError(
                    f"Expected `{key}` to be `{expected_value}` but got `{actual_value}`."
                )

        build_string = entries.get("Build")

        return Wheel(build_string=build_string)


@dataclass(frozen=True)
class WheelDistInfo:
    metadata: Metadata
    module_name: str
    record: Record
    wheel: Wheel

    @classmethod
    def parse(
        cls, dist_info_files: Mapping[str, bytes], /, *, dist_info_folder_name: str
    ) -> WheelDistInfo:
        return WheelDistInfo(
            metadata=Metadata.parse(dist_info_files["METADATA"].decode()),
            module_name=dist_info_files["top_level.txt"].decode().rstrip(),
            record=Record.parse(
                dist_info_files[_RECORD_FILENAME],
                dist_info_folder_name=dist_info_folder_name,
            ),
            wheel=Wheel.parse(dist_info_files["WHEEL"].decode().rstrip()),
        )
