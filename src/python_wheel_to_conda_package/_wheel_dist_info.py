from __future__ import annotations

import hashlib
from base64 import urlsafe_b64decode
from collections.abc import Mapping, Sequence
from contextlib import suppress
from dataclasses import dataclass
from typing import ClassVar

_RECORD_FILENAME = "RECORD"
_WHEEL_FILENAME = "WHEEL"


def _validate_metadata_version(version: str, /) -> str:
    expected_major_version = 2

    if not version.startswith(f"{expected_major_version}."):
        raise ValueError(
            f"Expected metadata version's major number to be `{expected_major_version}` but got `{version}`."
        )

    return version


@dataclass(frozen=True, kw_only=True)
class Metadata:
    package_name: str
    requires_dist: Sequence[str]
    requires_python: str
    version: str

    @classmethod
    def parse(cls, metadata: str, /) -> Metadata:
        lines = metadata.splitlines()

        empty_line_index = len(lines)

        with suppress(
            # No empty line which means there are no long description and all the lines follow the `name: value` format.
            ValueError
        ):
            empty_line_index = lines.index("")

        # Ignore the long description which is separated by the `key: value` lines by an empty line.
        lines = lines[:empty_line_index]

        metadata_version: str | None = None
        package_name: str | None = None
        requires_dist: list[str] = []
        requires_python: str = ""
        version: str | None = None

        metadata_version_key = "Metadata-Version"

        for line in lines:
            key, value = line.split(": ", maxsplit=1)

            match key:
                case key if key == metadata_version_key:
                    metadata_version = _validate_metadata_version(value)
                case "Name":
                    package_name = value
                case "Version":
                    version = value
                case "Requires-Python":
                    requires_python = value
                case "Requires-Dist":
                    requires_dist.append(value)

        if not metadata_version:
            raise ValueError(f"Missing `{metadata_version_key}` metadata.")

        if not package_name:
            raise ValueError("Missing package name.")

        if not version:
            raise ValueError("Missing version.")

        return cls(
            package_name=package_name,
            requires_dist=requires_dist,
            requires_python=requires_python,
            version=version,
        )


@dataclass(frozen=True, kw_only=True)
class RecordItem:
    _SEPARATOR: ClassVar[str] = ","
    _SHA256_PREFIX: ClassVar[str] = "sha256="

    file_path: str
    sha256: str
    size_in_bytes: int

    @classmethod
    def from_file_path_and_record(cls, file_path: str, record: bytes, /) -> RecordItem:
        return cls(
            file_path=file_path,
            sha256=hashlib.sha256(record).hexdigest(),
            size_in_bytes=len(record),
        )

    @classmethod
    def parse(
        cls, line: str, /, *, dist_info_folder_name: str, record: bytes
    ) -> RecordItem:
        file_path, _sha256, _size_in_bytes = line.split(",")

        if _sha256 and _size_in_bytes:
            # Reverse logic of https://github.com/pypa/pip/blob/c9df690f3b5bb285a855953272e6fe24f69aa08a/src/pip/_internal/wheel.py#L71-L84.
            sha256 = urlsafe_b64decode(
                f"{_sha256[len(cls._SHA256_PREFIX) :]}=".encode("latin1")
            ).hex()
            size_in_bytes = int(_size_in_bytes)

            return cls(
                file_path=file_path,
                sha256=sha256,
                size_in_bytes=size_in_bytes,
            )

        record_path = f"{dist_info_folder_name}/{_RECORD_FILENAME}"
        if file_path != record_path:
            raise RuntimeError(
                f"`{record_path}` is the only file that can have empty sha256 and size information but got `{file_path}`."
            )

        return cls.from_file_path_and_record(file_path, record)

    def __str__(self) -> str:
        return self._SEPARATOR.join(
            [
                self.file_path,
                f"{self._SHA256_PREFIX}{self.sha256}",
                str(self.size_in_bytes),
            ]
        )


@dataclass(frozen=True, kw_only=True)
class Record:
    items: Sequence[RecordItem]

    @classmethod
    def parse(cls, record: bytes, /, *, dist_info_folder_name: str) -> Record:
        return cls(
            items=[
                RecordItem.parse(
                    line, dist_info_folder_name=dist_info_folder_name, record=record
                )
                for line in record.decode().rstrip().splitlines()
            ]
        )

    def __str__(self) -> str:
        return "\n".join([*[str(item) for item in self.items], ""])


@dataclass(frozen=True, kw_only=True)
class Wheel:
    EXPECTED_ENTRIES: ClassVar[Mapping[str, str]] = {
        "Root-Is-Purelib": "true",
        "Tag": "py3-none-any",
        "Wheel-Version": "1.0",
    }

    _BUILD_KEY: ClassVar[str] = "Build"
    """See https://peps.python.org/pep-0427/#file-contents."""

    _SEPARATOR: ClassVar[str] = ": "

    build_tag: str | None = None

    @classmethod
    def parse(cls, wheel: str, /) -> Wheel:
        entries: dict[str, str] = {}

        for line in wheel.splitlines():
            key, value = line.split(cls._SEPARATOR, maxsplit=1)
            entries[key] = value

        for key, expected_value in cls.EXPECTED_ENTRIES.items():
            actual_value = entries.get(key)

            if actual_value != expected_value:
                raise ValueError(
                    f"Expected `{key}` to be `{expected_value}` but got `{actual_value}`."
                )

        build_tag = entries.get(cls._BUILD_KEY)

        return cls(build_tag=build_tag)

    def __str__(self) -> str:
        entries: dict[str, str] = {}

        if self.build_tag:
            entries[self._BUILD_KEY] = self.build_tag

        entries.update(self.EXPECTED_ENTRIES)

        return "\n".join(
            [*[f"{key}{self._SEPARATOR}{value}" for key, value in entries.items()], ""]
        )


@dataclass(frozen=True, kw_only=True)
class WheelDistInfo:
    metadata: Metadata
    record: Record
    wheel: Wheel

    @classmethod
    def parse(
        cls, dist_info_files: Mapping[str, bytes], /, *, dist_info_folder_name: str
    ) -> WheelDistInfo:
        return cls(
            metadata=Metadata.parse(dist_info_files["METADATA"].decode()),
            record=Record.parse(
                dist_info_files[_RECORD_FILENAME],
                dist_info_folder_name=dist_info_folder_name,
            ),
            wheel=Wheel.parse(dist_info_files[_WHEEL_FILENAME].decode().rstrip()),
        )
