import os
from pathlib import Path
from typing import Optional

from .run_cmd import RunCMD


class Poeta:
    DEV_LIBS = ["pytest", "pytest-cov", "ruff", "isort", "taskipy"]
    DOC_LIBS = ["mkdocs-material", "mkdocstrings", "mkdocstrings-python"]
    FASTAPI_LIBS = [
        "fastapi[standard]",
        "pydantic",
        "pydantic-settings",
        "sqlalchemy",
        "alembic",
    ]
    DJANGO_LIBS = ["django", "django-extensions"]

    FLASK_LIBS = ["flask", "flask-restful"]
    PYTHON_LIBS = [""]

    SETUP = {"run_cmd": "", "exclude_cmd": "", "folder_name": ""}
    POETA_PATH = Path(__file__).parent.parent

    def __init__(
        self, directory: Path, project_name: str, framework: Optional[str] = None
    ):
        self.root = directory
        self.root_path = self.root / project_name
        self.project_name = project_name
        self.framework = framework.lower() if framework else None
        self.poetry_cmd = f"poetry -C {self.root_path}"
        self.WEB_SETUP = {
            "fastapi": self._fastapi_setup,
            "django": self._django_setup,
            "flask": self._flask_setup,
        }

    def _create_src_folder(self):
        folder_name = self.project_name.replace(
            "-", "_"
        )  # if self.framework else "src"
        src_path = self.root_path / folder_name
        if not src_path.exists():
            src_path.mkdir()
        return src_path

    def _init_git(self):
        RunCMD.run(f"git init {self.root_path}")
        gitignore = RunCMD.run("ignr -p python", get_output=True)
        with open(self.root_path / ".gitignore", "a") as f:
            f.write(gitignore)

    def _set_config(self, setup: dict):
        with open(self.root_path / "pyproject.toml", "a") as f:
            with open(self.POETA_PATH / "config", "r") as config_file:
                f.write(config_file.read().format_map(setup))

    def _add_libs(self, libs: Optional[list] = None):
        for lib in self.DEV_LIBS:
            print(f"Adding {lib} to dev group")
            RunCMD.run(f"{self.poetry_cmd} add --group dev {lib}")

        for lib in self.DOC_LIBS:
            print(f"Adding {lib} to docs group")
            RunCMD.run(f"{self.poetry_cmd} add --group docs {lib}")

        if libs:
            for lib in libs:
                print(f"Adding {lib} to project")
                RunCMD.run(f"{self.poetry_cmd} add {lib}")

    def _django_setup(self, src_folder: str):
        os.remove(self.root_path / src_folder / "__init__.py")
        self._add_libs(libs=self.DJANGO_LIBS)
        RunCMD.run(f"{self.poetry_cmd} run django-admin startproject core {src_folder}")

        setup = self.SETUP.copy()
        setup["run_cmd"] = f"python {src_folder}/manage.py runserver"
        setup["folder_name"] = src_folder

        self._set_config(setup)

    def _fastapi_setup(self, src_folder: str):
        self._add_libs(libs=self.FASTAPI_LIBS)
        setup = self.SETUP.copy()
        setup["run_cmd"] = f"fastapi dev {src_folder}"
        setup["exclude_cmd"] = "migrations"
        setup["folder_name"] = src_folder

        self._set_config(setup)

    def _default_setup(self, src_folder: str):
        self._add_libs(libs=self.PYTHON_LIBS)
        setup = self.SETUP.copy()
        setup["folder_name"] = src_folder
        setup["run_cmd"] = f"python {src_folder}/main.py"

        self._set_config(setup)

    def _flask_setup(self, src_folder: str):
        pass

    def create_project(self):
        RunCMD.run(f"poetry new {self.project_name}")
        src_path = self._create_src_folder()
        self._init_git()
        setup_function = self.WEB_SETUP.get(self.framework, self._default_setup)
        setup_function(src_path)
        RunCMD.run(f"{self.poetry_cmd} install")

        # RunCMD.run(f"{self.poetry_cmd} shell")
