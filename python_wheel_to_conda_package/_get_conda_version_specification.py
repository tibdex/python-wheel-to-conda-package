def get_conda_version_specification(wheel_version_declaration: str, /) -> str:
    conda_version_specification = (
        wheel_version_declaration.replace("(", "")
        .replace(")", "")
        .rstrip()
        .replace("==", "")
    )

    assert (
        " " not in conda_version_specification
    ), "The Conda version specification cannot contain spaces (see https://conda.io/projects/conda/en/latest/user-guide/concepts/pkg-specs.html#package-match-specifications)."

    return conda_version_specification
