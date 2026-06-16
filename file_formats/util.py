import tempfile
import subprocess
import os


def raw_to_temp_file(data: bytes, *args, **kwargs):
    file = tempfile.NamedTemporaryFile(*args, **kwargs)
    file.write(data)
    file.flush()
    return file


class IsolatedTempFile:
    def __init__(self, *args, name=None, enter_dir=False, **kwargs):
        self.enter_dir = enter_dir
        self.prev_dir = None
        self.temp_dir = tempfile.TemporaryDirectory()
        if name is None:
            self.temp_file = tempfile.NamedTemporaryFile(
                dir=self.temp_dir.name, delete=False, *args, **kwargs
            )
        else:
            mode = kwargs.pop("mode", "w+b")
            self.temp_file = open(
                os.path.join(self.temp_dir.name, name), mode, *args, **kwargs
            )

    def __enter__(self):
        if self.enter_dir:
            self.prev_dir = os.getcwd()
            os.chdir(self.temp_dir.name)
        return (self.temp_dir, self.temp_file)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.temp_file.close()
        finally:
            self.temp_dir.cleanup()

        if self.enter_dir and self.prev_dir is not None:
            os.chdir(self.prev_dir)


def flatbuffer_binary_to_json(data: bytes, schema: str) -> str:
    with IsolatedTempFile(enter_dir=True) as (d, f):
        f.write(data)
        f.flush()
        with open(os.path.join(d.name, "schema.fbs"), "w", encoding="utf-8") as sf:
            sf.write(schema)
        subprocess.run(
            [
                "flatc",
                "--strict-json",
                "--json",
                "--defaults-json",
                "schema.fbs",
                "--",
                f.name,
                "--raw-binary",
                "--no-warnings",
            ],
            check=True,
        )
        result = os.listdir(d.name)[0]
        with open(result, "r", encoding="utf-8") as f:
            return f.read()


def json_to_flatbuffer_binary(data: str, schema: str) -> bytes:
    with IsolatedTempFile(name="data.json", enter_dir=True, mode="w") as (d, f):
        f.write(data)
        f.flush()
        with open(os.path.join(d.name, "schema.fbs"), "w", encoding="utf-8") as sf:
            sf.write(schema)
        subprocess.run(
            [
                "flatc",
                "--no-warnings",
                "--binary",
                "schema.fbs",
                f.name,
            ],
            check=True,
        )
        with open("data.bin", "rb") as r:
            return r.read()
