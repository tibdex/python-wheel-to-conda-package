from __future__ import annotations

import re
from contextlib import nullcontext

import pytest

from python_wheel_to_conda_package._get_conda_package_match_specification import (
    CondaPackageMatchSpecification,
    get_conda_package_match_specification,
)


@pytest.mark.parametrize(
    (
        "python_dependency_specification",
        "expected_conda_package_match_specification",
        "expected_error_pattern",
    ),
    [
        (
            "python",
            CondaPackageMatchSpecification(package_name="python", version=""),
            None,
        ),
        (
            "python >=3.9",
            CondaPackageMatchSpecification(package_name="python", version=">=3.9"),
            None,
        ),
        (
            "requests[security, socks]",
            None,
            re.escape("Extra not supported."),
        ),
        (
            "requests; extra == 'http'",
            None,
            None,
        ),
        (
            "requests >=2.31.0 ; extra == 'http'",
            None,
            None,
        ),
        (
            "requests; python_version > '3.7'",
            None,
            re.escape("Marker not supported."),
        ),
        (
            "local-lib @ file:///local-lib",
            None,
            re.escape("URL not supported."),
        ),
        (
            "pip @ https://github.com/pypa/pip/archive/1.3.1.zip",
            None,
            re.escape("URL not supported."),
        ),
    ],
)
def test_get_conda_package_match_specification(
    python_dependency_specification: str,
    expected_conda_package_match_specification: CondaPackageMatchSpecification | None,
    expected_error_pattern: str | None,
) -> None:
    context_manager = (
        pytest.raises(
            Exception,
            match=re.escape(
                f"Could not convert `{python_dependency_specification}` to Conda version specification."
            ),
        )
        if expected_error_pattern
        else nullcontext()
    )

    with context_manager as exc_info:
        conda_version_specification = get_conda_package_match_specification(
            python_dependency_specification
        )
        assert conda_version_specification == expected_conda_package_match_specification

    if expected_error_pattern:
        assert exc_info
        assert re.search(expected_error_pattern, str(exc_info.value.__cause__))
