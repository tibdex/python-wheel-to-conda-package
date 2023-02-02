import pytest

from python_wheel_to_conda_package._get_conda_version_specification import (
    get_conda_version_specification,
)


@pytest.mark.parametrize(
    ["wheel_version_declaration", "expected_conda_version_specification"],
    [
        ("(~=17.0)", "~=17.0"),
        ("(==0.7.3.dev0)", "0.7.3.dev0"),
        ("(<11.0,>=8.0)", "<11.0,>=8.0"),
    ],
)
def test_get_conda_version_specification(
    wheel_version_declaration: str, expected_conda_version_specification: str
) -> None:
    conda_version_specification = get_conda_version_specification(
        wheel_version_declaration
    )
    assert conda_version_specification == expected_conda_version_specification
