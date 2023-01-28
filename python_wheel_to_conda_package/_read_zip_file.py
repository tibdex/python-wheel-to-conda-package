from zipfile import ZipFile


def read_zip_file(zip: ZipFile, file_path: str, /) -> str:
    with zip.open(file_path) as file:
        return file.read().decode("utf-8")
