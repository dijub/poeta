import sys
from pathlib import Path

from .src import Menu, Poeta


def main():
    if len(sys.argv) > 1:
        sys.argv[0] = Path.cwd()
        args = Menu().handle_args(sys.argv)
        if args:
            Poeta(**args).create_project()


if __name__ == "__main__":
    main()
