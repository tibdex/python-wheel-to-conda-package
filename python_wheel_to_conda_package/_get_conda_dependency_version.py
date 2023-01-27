def get_conda_dependency_version(wheel_dependency_version: str, /) -> str:
    return wheel_dependency_version.replace("(", "").replace(")", "").rstrip()
