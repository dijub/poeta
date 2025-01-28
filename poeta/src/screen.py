from pathlib import Path
from typing import Callable


class Command:
    def __init__(
        self,
        cmd: str,
        full_cmd: str,
        description: str,
        validation: Callable | None = None,
    ):
        self.cmd = cmd
        self.full_cmd = full_cmd
        self.description = description
        self.cmd_str = f"{cmd}, {full_cmd}"
        self.validation = validation

    def get_value_from_full_cmd(self):
        return self.full_cmd.split("=")[1].lower()

    def get_cmd(self):
        return self.full_cmd.split("=")[0].strip().lower()

    def get_clean_cmd(self):
        return self.full_cmd.split("=")[0].strip("-").lower().replace("-", "_")


class Menu:
    def __init__(self):
        self.LIST_CMD = [
            Command(
                "-f",
                "--framework=FRAMEWORK",
                "Select the framework to use. Choices: FastAPI, Django, Flask, or omit for no framework. (Optional)",
                self._handle_framework,
            ),
            Command(
                "-p",
                "--project-name=PROJECT_NAME",
                "Specify the name of the project. (Required)",
            ),
            Command(
                "-d",
                "--directory=DIRECTORY",
                "Specify the directory where the project will be created. If omitted, the current directory is used. (Optional)",
                self.__handle_directory,
            ),
            Command("-h", "--help", "Show this help message and exit."),
        ]

    def _get_cmd(self, cmd_check: str):
        for cmd in self.LIST_CMD:
            if cmd.get_cmd() == cmd_check or cmd.cmd == cmd_check:
                return cmd
        raise ValueError(f"Invalid command: {cmd_check}")

    def create_menu(self):
        template = Template(
            length_cmd_str=self.get_length_cmd(),
            length_description=self.get_length_description(),
        )

        print("Usage: ")
        print("  poeta -f FRAMEWORK -p PROJECT_NAME [-d DIRECTORY]")
        print()
        print("Options:")
        for cmd in self.LIST_CMD:
            print(template(cmd))

    def get_length_cmd(self):
        return max(len(cmd.cmd_str) for cmd in self.LIST_CMD)

    def get_length_description(self):
        return max(len(cmd.description) for cmd in self.LIST_CMD)

    def handle_args(self, args):
        root_dir = args[0]

        if len(args) == 2:
            if args[1] in ["-h", "--help"]:
                self.create_menu()
                return
            raise ValueError(f"No valid command: {args[1]}")

        poeta_args = {"directory": root_dir}

        for i, arg in enumerate(args[1:], 1):
            if "=" in arg:
                cmd, value = arg.split("=", 1)
                cmd_obj = self._get_cmd(cmd)
                poeta_args[cmd_obj.get_clean_cmd()] = value.lower()
            elif "-" in arg:
                cmd_obj = self._get_cmd(arg)
                value = args[i + 1]
                if cmd_obj.validation:
                    cmd_obj.validation(value)
                poeta_args[cmd_obj.get_clean_cmd()] = value
            else:
                continue

        return poeta_args

    def _handle_framework(self, value: str):
        if value.lower() not in ["fastapi", "django", "flask"]:
            raise ValueError("Invalid framework")

        return value

    def __handle_directory(self, value: str):
        return Path(value)


class Template:
    def __init__(self, length_cmd_str: int, length_description: int):
        self.length_description = length_description
        self.length_cmd_str = length_cmd_str

    def __call__(self, cmd: Command):
        return f"  {cmd.cmd_str:<{self.length_cmd_str}} - {cmd.description}"
