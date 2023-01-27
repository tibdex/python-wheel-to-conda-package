def get_module_name(package_name: str, /) -> str:
    return package_name.replace("-", "_")
