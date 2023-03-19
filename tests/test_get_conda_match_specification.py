import re
from contextlib import nullcontext
from typing import Optional

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
            CondaPackageMatchSpecification("python", ""),
            None,
        ),
        (
            "python >=3.9",
            CondaPackageMatchSpecification("python", ">=3.9"),
            None,
        ),
        (
            "requests[security, socks]",
            None,
            re.escape("Extras are not supported."),
        ),
        (
            "requests; extra == 'http'",
            None,
            re.escape("Markers are not supported."),
        ),
        (
            "requests; python_version > '3.7'",
            None,
            re.escape("Markers are not supported."),
        ),
        (
            "local-lib @ file:///local-lib",
            None,
            re.escape("URLs are not supported."),
        ),
        (
            "pip @ https://github.com/pypa/pip/archive/1.3.1.zip",
            None,
            re.escape("URLs are not supported."),
        ),
        (
            "poetry @ git+https://github.com/python-poetry/poetry.git",
            None,
            re.escape("URLs are not supported."),
        ),
    ],
)
def test_get_conda_package_match_specification(
    python_dependency_specification: str,
    expected_conda_package_match_specification: Optional[
        CondaPackageMatchSpecification
    ],
    expected_error_pattern: Optional[str],
) -> None:
    context_manager = (
        nullcontext()
        if expected_conda_package_match_specification
        else pytest.raises(
            Exception,
            match=re.escape(
                f"Could not convert `{python_dependency_specification}` to Conda version specification."
            ),
        )
    )

    with context_manager as exc_info:
        conda_version_specification = get_conda_package_match_specification(
            python_dependency_specification
        )
        assert conda_version_specification == expected_conda_package_match_specification

    if expected_error_pattern:
        assert exc_info
        assert re.search(expected_error_pattern, str(exc_info.value.__cause__))
