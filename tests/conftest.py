import importlib
from pathlib import Path
from shutil import rmtree
from subprocess import run
from typing import Any, Generator, Mapping

import pytest

TEST_LIB_DIRECTORY = Path(__file__).parent / "test-lib"


@pytest.fixture(name="setup_args", scope="session")
def setup_args_fixture() -> Mapping[str, Any]:
    spec = importlib.util.spec_from_file_location(
        "setup", str(TEST_LIB_DIRECTORY / "setup.py")
    )
    assert spec
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    setup_args = getattr(module, "setup_args")
    assert isinstance(setup_args, dict)
    return setup_args


@pytest.fixture(name="build_number", scope="session")
def build_number_fixture() -> int:
    return 0


@pytest.fixture(name="build_string", scope="session")
def build_string_fixture() -> str:
    return "1337"


@pytest.fixture(name="wheel_path", scope="session")
def wheel_path_fixture(
    build_number: int, build_string: str, setup_args: Mapping[str, Any]
) -> Generator[Path, None, None]:
    wheel_build_number = f"{build_number}_{build_string}"

    run(
        ["python", "setup.py", "bdist_wheel", "--build-number", wheel_build_number],
        check=True,
        cwd=TEST_LIB_DIRECTORY,
    )

    path = Path(
        TEST_LIB_DIRECTORY
        / "dist"
        / f"""test_lib-{setup_args["version"]}-{wheel_build_number}-py3-none-any.whl"""
    )
    assert path.exists()
    yield path

    for folder in ["__pycache__", "build", "dist", "test_lib.egg-info"]:
        rmtree(TEST_LIB_DIRECTORY / folder, ignore_errors=True)
