from dataclasses import dataclass

from poetry.core.packages.dependency import Dependency


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
        dependency = Dependency.create_from_pep_508(python_dependency_specification)

        if dependency.is_directory():
            raise ValueError("Directory dependencies are not supported.")

        if dependency.is_file():
            raise ValueError("Files dependencies are not supported.")

        if dependency.is_url():
            raise ValueError("URL dependencies are not supported.")

        if dependency.is_vcs():
            raise ValueError("VCS dependencies are not supported.")

        if dependency.extras:
            raise ValueError("Extras are not supported.")

        if not dependency.marker.is_any():
            raise ValueError("Markers are not supported.")

        return CondaPackageMatchSpecification(
            dependency.name, str(dependency.constraint)
        )
    except ValueError as error:
        raise ValueError(
            f"Could not convert `{python_dependency_specification}` to Conda version specification."
        ) from error
