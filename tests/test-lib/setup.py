from setuptools import find_packages, setup  # noqa: INP001

_NAME = "test-lib"

SETUP_ARGS = {
    "name": _NAME,
    "version": "0.4.2.dev0",
    "author": "test-author",
    "author_email": "test@email.io",
    "data_files": [
        (
            "share/test-lib",
            ["data/test.txt"],
        )
    ],
    "packages": find_packages(),
    "package_data": {
        "test_lib": [
            "resources/*",
        ]
    },
    "python_requires": ">=3.8",
    "install_requires": [
        "pandas>=1.2",
    ],
    "py_modules": [],
}

if __name__ == "__main__":
    setup(**SETUP_ARGS)
