from setuptools import find_packages, setup

setup_args = dict(
    name="test-lib",
    version="0.4.2.dev0",
    author="test-author",
    author_email="test@email.io",
    packages=find_packages(exclude=["tests_*"]),
    package_data={
        "test_lib": [
            "data/*",
        ]
    },
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.2",
    ],
    py_modules=[],
)

if __name__ == "__main__":
    setup(**setup_args)
