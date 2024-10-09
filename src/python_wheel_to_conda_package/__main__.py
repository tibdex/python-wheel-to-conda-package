from argparse import ArgumentParser
from pathlib import Path

from . import python_wheel_to_conda_package


def main() -> None:
    docstring = python_wheel_to_conda_package.__doc__
    assert docstring

    parser = ArgumentParser(
        prog=python_wheel_to_conda_package.__name__.replace("_", "-"),
        description=docstring.splitlines()[0],
    )
    parser.add_argument("wheel_path", type=Path)
    parser.add_argument("-o", "--output-directory", type=Path)

    args = parser.parse_args()

    conda_package_path = python_wheel_to_conda_package(
        args.wheel_path,
        output_directory=args.output_directory,
    )

    print(conda_package_path.absolute())


if __name__ == "__main__":
    main()
