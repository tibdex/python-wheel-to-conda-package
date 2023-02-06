import importlib
from pathlib import Path
from shutil import copytree
from subprocess import run
from typing import Any, Mapping

import pytest


from ._get_module_name import get_module_name


@pytest.fixture(name="test_lib_directory", scope="session")
def test_lib_directory_fixture(tmp_path_factory: pytest.TempPathFactory) -> Path:
    test_lib_folder = "test-lib"
    test_lib_directory = tmp_path_factory.mktemp(test_lib_folder)
    copytree(
        Path(__file__).parent / test_lib_folder, test_lib_directory, dirs_exist_ok=True
    )
    return test_lib_directory


@pytest.fixture(name="setup_args", scope="session")
def setup_args_fixture(test_lib_directory: Path) -> Mapping[str, Any]:
    spec = importlib.util.spec_from_file_location(
        "setup", str(test_lib_directory / "setup.py")
    )
    assert spec
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    setup_args = getattr(module, "SETUP_ARGS")
    assert isinstance(setup_args, dict)
    return setup_args


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
    setup_args: Mapping[str, Any],
    test_lib_directory: Path,
) -> Path:
    wheel_build_number = f"{build_number}_{build_string}"

    run(
        ["python", "setup.py", "bdist_wheel", "--build-number", wheel_build_number],
        check=True,
        cwd=test_lib_directory,
    )

    path = Path(
        test_lib_directory
        / "dist"
        / f"""{get_module_name(setup_args["name"])}-{setup_args["version"]}-{wheel_build_number}-py3-none-any.whl"""
    )
    assert path.exists()
    return path
