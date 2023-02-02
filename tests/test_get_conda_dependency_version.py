import pytest

from python_wheel_to_conda_package._get_conda_dependency_version import (
    get_conda_dependency_version,
)


@pytest.mark.parametrize(
    ["wheel_dependency_version", "expected_conda_dependency_version"],
    [
        ("(~=17.0)", "~=17.0"),
        ("(==0.7.3.dev0)", "0.7.3.dev0"),
        ("(<11.0,>=8.0)", "<11.0,>=8.0"),
    ],
)
def test_get_conda_dependency_version(
    wheel_dependency_version: str, expected_conda_dependency_version: str
) -> None:
    conda_dependency_version = get_conda_dependency_version(wheel_dependency_version)
    assert conda_dependency_version == expected_conda_dependency_version
