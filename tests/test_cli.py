from pathlib import Path
from subprocess import check_output


def test_cli(tmp_path: Path, wheel_path: Path) -> None:
    output = check_output(
        [
            "python-wheel-to-conda-package",
            str(wheel_path),
            "--output-directory",
            str(tmp_path),
        ],
        text=True,
    )
    conda_package_path = Path(output.rstrip())
    assert conda_package_path.exists()
    assert conda_package_path.parent == tmp_path
