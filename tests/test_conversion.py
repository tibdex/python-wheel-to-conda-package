from pathlib import Path

from python_wheel_to_conda_package import python_wheel_to_conda_package


def test_conversion(wheel_path: Path) -> None:
    conda_package_path = python_wheel_to_conda_package(wheel_path)
    assert conda_package_path
