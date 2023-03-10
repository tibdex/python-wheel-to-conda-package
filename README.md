<a href="https://pypi.org/project/python-wheel-to-conda-package" target="_blank">
  <img src="https://img.shields.io/pypi/v/python-wheel-to-conda-package" alt="Package version">
</a>

# Python Wheel to Conda package

This converts a Pure-Python Wheel to a noarch Conda package.

This tool can be used to replace `conda build` which can sometimes be very slow.
[`setup.py bdist_conda`](https://docs.conda.io/projects/conda-build/en/latest/user-guide/recipes/build-without-recipe.html) can build a Conda package without a recipe but it relies on conda-build behind the scenes and thus suffers from the same slowness.

## Usage

### As a library

```python
from python_wheel_to_conda_package import python_wheel_to_conda_package

conda_package_path = python_wheel_to_conda_package(wheel_path, output_directory=some_directory)
```

### As a command line tool

```console
$ python-wheel-to-conda-package test_lib-0.4.2.dev0-42_1337gg-py3-none-any.whl --output-directory /a/b/c/
/a/b/c/test-lib-0.4.2.dev0-1337gg.tar.bz2
```
