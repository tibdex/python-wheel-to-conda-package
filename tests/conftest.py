from pathlib import Path
from shutil import rmtree

import pytest
from flit_core.config import LoadedConfig, read_flit_config
from flit_core.wheel import make_wheel_in

from ._add_build_tag_to_wheel import add_build_tag_to_wheel

_PYPROJECT_TOML_FILENAME = "pyproject.toml"


@pytest.fixture(name="test_lib_directory", scope="session")
def test_lib_directory_fixture() -> Path:
    return Path(__file__).parent / "test-lib"


@pytest.fixture(name="pyproject", scope="session")
def pyproject_fixture(test_lib_directory: Path) -> LoadedConfig:
    return read_flit_config(test_lib_directory / _PYPROJECT_TOML_FILENAME)


@pytest.fixture(name="build_number", scope="session")
def build_number_fixture() -> int:
    return 42


@pytest.fixture(name="build_string", scope="session")
def build_string_fixture() -> str:
    return "1337gg"


@pytest.fixture(name="wheel_path", scope="session")
def wheel_path_fixture(
    build_number: int,
    build_string: str,
    test_lib_directory: Path,
) -> Path:
    dist_directory = test_lib_directory / "dist"

    rmtree(dist_directory, ignore_errors=True)
    dist_directory.mkdir()

    wheel_path: Path = make_wheel_in(
        test_lib_directory / _PYPROJECT_TOML_FILENAME, wheel_directory=dist_directory
    ).file

    add_build_tag_to_wheel(wheel_path, f"{build_number}_{build_string}")

    return wheel_path
