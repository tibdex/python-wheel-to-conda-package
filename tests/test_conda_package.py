import json
from datetime import timedelta
from shutil import copyfile
from pathlib import Path, PurePosixPath
from subprocess import check_output, run
from textwrap import dedent
from typing import Any, Dict, List, Mapping

from ._get_module_name import get_module_name
from python_wheel_to_conda_package import python_wheel_to_conda_package

import pytest


@pytest.fixture(name="conda_package_path", scope="module")
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


@pytest.fixture(name="indexed_local_conda_channel_path", scope="module")
def indexed_local_conda_channel_path_fixture(
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


@pytest.fixture(name="additional_requirements", scope="module")
def additional_requirements_fixture() -> Mapping[str, str]:
    return {"graphviz": "2.50.0"}


def _get_installed_conda_packages() -> Dict[str, str]:
    output = check_output(
        [
            "conda",
            "list",
            "--json",
        ],
        text=True,
    )
    installed_packages: List[Dict[str, str]] = json.loads(output)
    return {
        str(installed_package["name"]): str(installed_package["version"])
        for installed_package in installed_packages
    }


def _install_conda_package(
    package_name: str, /, *, local_conda_channel_path: Path
) -> None:
    run(
        [
            "conda",
            "install",
            "--channel",
            f"file:/{local_conda_channel_path.absolute()}",
            "--yes",
            package_name,
        ],
        check=True,
    )


@pytest.fixture(autouse=True, scope="module")
def conda_package_installed_fixture(
    additional_requirements: Mapping[str, str],
    indexed_local_conda_channel_path: Path,
    setup_args: Mapping[str, Any],
) -> None:
    package_name = setup_args["name"]

    installed_packages = _get_installed_conda_packages()

    # Check that the Conda environment does not have these packages before the upcoming installation.
    assert package_name not in installed_packages
    for requirement_name in additional_requirements:
        assert requirement_name not in installed_packages

    _install_conda_package(
        package_name, local_conda_channel_path=indexed_local_conda_channel_path
    )


@pytest.fixture(name="installed_conda_packages", scope="module")
def installed_conda_packages_fixture() -> Mapping[str, str]:
    return _get_installed_conda_packages()


def test_conda_package_installation(
    installed_conda_packages: Mapping[str, str],
    setup_args: Mapping[str, Any],
) -> None:
    assert setup_args["name"] in installed_conda_packages


def test_additional_requirements_installation(
    additional_requirements: Mapping[str, str],
    installed_conda_packages: Mapping[str, str],
) -> None:
    for requirement_name, required_version in additional_requirements.items():
        assert installed_conda_packages[requirement_name] == required_version


@pytest.fixture(name="conda_env_directory", scope="module")
def conda_env_directory_fixture() -> Path:
    output = check_output(["conda", "info", "--json"])
    info: Dict[str, Any] = json.loads(output)
    active_prefix = info.get("active_prefix")
    return Path(str(active_prefix or info["default_prefix"]))


def test_data_files(
    conda_env_directory: Path, setup_args: Mapping[str, Any], test_lib_directory: Path
) -> None:
    for path_in_package, local_file_relative_paths in setup_args["data_files"]:
        directory_inside_conda_env = conda_env_directory / PurePosixPath(
            path_in_package
        )
        for local_file_relative_path in local_file_relative_paths:
            local_file_path = test_lib_directory / PurePosixPath(
                local_file_relative_path
            )
            expected_content = local_file_path.read_bytes()

            assert len(expected_content) > 0

            path_inside_conda_env = directory_inside_conda_env / local_file_path.name
            content = path_inside_conda_env.read_bytes()

            assert content == expected_content


def _run_python_module_inside_conda_env(
    module_name: str, /, *, timeout: timedelta
) -> str:
    return check_output(
        ["conda", "run", "python", "-m", module_name],
        text=True,
        timeout=timeout.total_seconds(),
    )


def test_module_execution(setup_args: Mapping[str, Any]) -> None:
    output = _run_python_module_inside_conda_env(
        get_module_name(setup_args["name"]), timeout=timedelta(seconds=10)
    )

    assert (
        output.strip()
        == dedent(
            """
            id      name
        0  abc     watch
        1  def     phone
        2  ghi  computer
    """
        ).strip()
    )
