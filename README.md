# Python Wheel to Conda package

This convert a Pure-Python Wheel to a noarch Conda package.

This tool can be used to replace `conda build` which can sometimes be very slow.

## Usage

### As a library

```python
from python_wheel_to_conda_package import python_wheel_to_conda_package

conda_package_path = python_wheel_to_conda_package(wheel_path, output_directory=some_directory)
```

### As a command line tool

```console
$ python_wheel_to_conda_package test_lib-0.4.2-0_1337-py3-none-any.whl --output-directory /some/directory/
/some/directory/test-lib-0.4.2-1337.tar.bz2
```
