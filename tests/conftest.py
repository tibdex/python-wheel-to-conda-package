from pathlib import Path
from shutil import rmtree

import pytest
from hatchling.builders.wheel import WheelBuilder
from hatchling.metadata.core import ProjectMetadata
from hatchling.plugin.manager import PluginManagerBound

from ._add_build_tag_to_wheel import add_build_tag_to_wheel


@pytest.fixture(name="project_metadata", scope="session")
def pyproject_fixture() -> ProjectMetadata[PluginManagerBound]:
    return ProjectMetadata(str(Path(__file__).parent / "test-lib"), None)


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
    project_metadata: ProjectMetadata[PluginManagerBound],
) -> Path:
    dist_directory = Path(project_metadata.root) / "dist"

    rmtree(dist_directory, ignore_errors=True)
    dist_directory.mkdir()

    wheel_path: Path = Path(next(WheelBuilder(project_metadata.root).build()))

    add_build_tag_to_wheel(wheel_path, f"{build_number}_{build_string}")

    return wheel_path
