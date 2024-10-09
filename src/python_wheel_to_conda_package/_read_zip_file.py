from zipfile import ZipFile


def read_zip_file(zip_file: ZipFile, file_path: str, /) -> bytes:
    with zip_file.open(file_path) as file:
        return file.read()
