import json
from collections.abc import Mapping
from datetime import timedelta
from pathlib import Path
from shutil import copyfile
from subprocess import check_output, run
from textwrap import dedent
from typing import Any

import pytest
from hatchling.metadata.core import ProjectMetadata
from hatchling.plugin.manager import PluginManagerBound

from python_wheel_to_conda_package import python_wheel_to_conda_package


@pytest.fixture(name="conda_package_path", scope="module")
def conda_package_path_fixture(
    tmp_path_factory: pytest.TempPathFactory,
    wheel_path: Path,
) -> Path:
    package_directory = tmp_path_factory.mktemp("conda-package")
    return python_wheel_to_conda_package(
        wheel_path,
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


def _get_installed_conda_packages() -> dict[str, str]:
    output = check_output(
        [
            "conda",
            "list",
            "--json",
        ],
        text=True,
    )
    installed_packages: list[dict[str, str]] = json.loads(output)
    return {
        str(installed_package["name"]): str(installed_package["version"])
        for installed_package in installed_packages
    }


def _install_conda_package(
    package_name: str, /, *, local_conda_channel_path: Path
) -> str:
    return check_output(
        [
            "conda",
            "install",
            "--channel",
            f"file:/{local_conda_channel_path.absolute()}",
            "--yes",
            package_name,
        ],
        text=True,
    )


@pytest.fixture(autouse=True, scope="module")
def conda_package_installed_fixture(
    build_string: str,
    indexed_local_conda_channel_path: Path,
    project_metadata: ProjectMetadata[PluginManagerBound],
) -> None:
    installed_packages = _get_installed_conda_packages()

    # Check that the Conda environment does not have these packages before the upcoming installation.
    assert project_metadata.name not in installed_packages

    output = _install_conda_package(
        project_metadata.name, local_conda_channel_path=indexed_local_conda_channel_path
    )
    assert build_string in output


@pytest.fixture(name="installed_conda_packages", scope="module")
def installed_conda_packages_fixture() -> Mapping[str, str]:
    return _get_installed_conda_packages()


def test_conda_package_installation(
    installed_conda_packages: Mapping[str, str],
    project_metadata: ProjectMetadata[PluginManagerBound],
) -> None:
    assert project_metadata.name in installed_conda_packages


@pytest.fixture(name="conda_env_directory", scope="module")
def conda_env_directory_fixture() -> Path:
    output = check_output(["conda", "info", "--json"])
    info: dict[str, Any] = json.loads(output)
    active_prefix = info.get("active_prefix")
    return Path(str(active_prefix or info["default_prefix"]))


def test_shared_data_files(
    conda_env_directory: Path, project_metadata: ProjectMetadata[PluginManagerBound]
) -> None:
    shared_data = project_metadata.hatch.build_targets["wheel"]["shared-data"]
    assert isinstance(shared_data, dict)
    for data_folder, shared_data_folder in shared_data.items():
        assert isinstance(data_folder, str)
        assert isinstance(shared_data_folder, str)

        data_directory = Path(project_metadata.root) / data_folder
        shared_data_directory = conda_env_directory / shared_data_folder

        for file_path in data_directory.glob("**/*"):
            if file_path.is_dir():
                continue

            shared_file_path = shared_data_directory / file_path.relative_to(
                data_directory
            )

            expected_content = file_path.read_bytes()
            assert len(expected_content) > 0
            content = shared_file_path.read_bytes()
            assert content == expected_content


def _run_python_module_inside_conda_env(
    module_name: str, /, *, timeout: timedelta
) -> str:
    return check_output(
        ["conda", "run", "python", "-m", module_name],
        text=True,
        timeout=timeout.total_seconds(),
    )


def test_module_execution(
    project_metadata: ProjectMetadata[PluginManagerBound],
) -> None:
    output = _run_python_module_inside_conda_env(
        project_metadata.name.replace("-", "_"),
        timeout=timedelta(seconds=10),
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
