from dataclasses import dataclass

from packaging.requirements import Requirement


@dataclass(frozen=True)
class CondaPackageMatchSpecification:
    package_name: str
    version: str

    def __post_init__(self) -> None:
        assert (
            " " not in self.version
        ), "The Conda version specification cannot contain spaces (see https://conda.io/projects/conda/en/latest/user-guide/concepts/pkg-specs.html#package-match-specifications)."


def get_conda_package_match_specification(
    python_dependency_specification: str, /
) -> CondaPackageMatchSpecification:
    try:
        requirement = Requirement(python_dependency_specification)

        if requirement.extras:
            raise ValueError("Extras are not supported.")

        if requirement.marker:
            raise ValueError("Markers are not supported.")

        if requirement.url:
            raise ValueError("URLs are not supported.")
    except ValueError as error:
        raise ValueError(
            f"Could not convert `{python_dependency_specification}` to Conda version specification."
        ) from error
    else:
        return CondaPackageMatchSpecification(
            requirement.name, str(requirement.specifier)
        )
