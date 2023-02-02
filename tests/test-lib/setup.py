from setuptools import find_packages, setup

_NAME = "test-lib"

SETUP_ARGS = {
    "name": _NAME,
    "version": "0.4.2.dev0",
    "author": "test-author",
    "author_email": "test@email.io",
    "packages": find_packages(exclude=["tests_*"]),
    "package_data": {
        "test_lib": [
            "data/*",
        ]
    },
    "python_requires": ">=3.8",
    "install_requires": [
        "pandas>=1.2",
    ],
    "entry_points": {
        "console_scripts": [f"""{_NAME}={_NAME.replace("-", "_")}.__main__:main"""]
    },
    "py_modules": [],
}

if __name__ == "__main__":
    setup(**SETUP_ARGS)
