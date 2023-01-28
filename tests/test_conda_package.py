from datetime import timedelta
from pathlib import Path
from subprocess import check_output, run
from textwrap import dedent
from typing import Any, Mapping

from ._get_module_name import get_module_name


def _install_conda_package(
    package_name: str, /, *, local_conda_channel_path: Path
) -> None:
    run(
        [
            "conda",
            "install",
            "--channel",
            f"file:/{local_conda_channel_path.absolute()}",
            "--yes",
            package_name,
        ],
        check=True,
    )


def _run_python_module_inside_conda_env(module_name: str, *, timeout: timedelta) -> str:
    return check_output(
        ["conda", "run", "python", "-m", module_name],
        text=True,
        timeout=timeout.total_seconds(),
    )


def test_conda_package(
    local_conda_channel_path: Path, setup_args: Mapping[str, Any]
) -> None:
    package_name = setup_args["name"]

    _install_conda_package(
        package_name, local_conda_channel_path=local_conda_channel_path
    )

    output = _run_python_module_inside_conda_env(
        get_module_name(package_name), timeout=timedelta(seconds=10)
    )

    assert (
        output.strip()
        == dedent(
            """
            id      name
        0  abc     watch
        1  def     phone
        2  ghi  computer
    """
        ).strip()
    )
