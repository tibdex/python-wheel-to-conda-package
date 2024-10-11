from pathlib import Path
from subprocess import check_output


def test_cli(tmp_path: Path, wheel_path: Path) -> None:
    output_directory = tmp_path / "folder-to-create"
    output = check_output(
        [
            "uv",
            "run",
            "python-wheel-to-conda-package",
            str(wheel_path),
            "--output-directory",
            str(output_directory),
        ],
        text=True,
    )
    conda_package_path = Path(output.rstrip())
    assert conda_package_path.is_file()
    assert conda_package_path.parent == output_directory
