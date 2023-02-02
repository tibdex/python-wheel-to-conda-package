import importlib
from pathlib import Path
from shutil import copyfile, copytree
from subprocess import run
from typing import Any, Mapping

import pytest

from python_wheel_to_conda_package import python_wheel_to_conda_package


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
        / f"""{setup_args["name"].replace("-", "_")}-{setup_args["version"]}-{wheel_build_number}-py3-none-any.whl"""
    )
    assert path.exists()
    return path


@pytest.fixture(name="additional_requirements", scope="session")
def additional_requirements_fixture() -> Mapping[str, str]:
    return {"requests": "2.28.1"}


@pytest.fixture(name="conda_package_path", scope="session")
def conda_package_path_fixture(
    additional_requirements: Mapping[str, str],
    tmp_path_factory: pytest.TempPathFactory,
    wheel_path: Path,
) -> Path:
    package_directory = tmp_path_factory.mktemp("conda-package")
    return python_wheel_to_conda_package(
        wheel_path,
        additional_requirements=additional_requirements,
        output_directory=package_directory,
    )


@pytest.fixture(name="local_conda_channel_path", scope="session")
def local_conda_channel_path_fixture(
    conda_package_path: Path, tmp_path_factory: pytest.TempPathFactory
) -> Path:
    channel_directory = tmp_path_factory.mktemp("conda-channel")
    noarch_directory = channel_directory / "noarch"
    noarch_directory.mkdir()
    copyfile(conda_package_path, noarch_directory / conda_package_path.name)

    run(
        ["conda", "index", str(channel_directory.absolute())],
        check=True,
    )

    return channel_directory
