from __future__ import annotations

from dataclasses import dataclass

from packaging.markers import Marker
from packaging.requirements import Requirement


@dataclass(frozen=True, kw_only=True)
class CondaPackageMatchSpecification:
    package_name: str
    version: str

    def __post_init__(self) -> None:
        assert (
            " " not in self.version
        ), "The Conda version specification cannot contain spaces (see https://conda.io/projects/conda/en/latest/user-guide/concepts/pkg-specs.html#package-match-specifications)."


def _is_extra_marker(marker: Marker, /) -> bool:
    return all(
        isinstance(_marker, tuple)
        and str(_marker[0]) == "extra"
        and str(_marker[1]) == "=="
        for _marker in marker._markers  # noqa: SLF001
    )


def get_conda_package_match_specification(
    python_dependency_specification: str, /
) -> CondaPackageMatchSpecification | None:
    try:
        requirement = Requirement(python_dependency_specification)

        if requirement.extras:
            raise ValueError("Extra not supported.")

        if requirement.marker:
            if _is_extra_marker(requirement.marker):
                return None

            raise ValueError("Marker not supported.")

        if requirement.url:
            raise ValueError("URL not supported.")
    except ValueError as error:
        raise ValueError(
            f"Could not convert `{python_dependency_specification}` to Conda version specification."
        ) from error
    else:
        return CondaPackageMatchSpecification(
            package_name=requirement.name,
            version=str(requirement.specifier),
        )
