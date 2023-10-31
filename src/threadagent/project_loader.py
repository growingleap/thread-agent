import os
import tomllib

import click


class ProjectLoader:
    name: str

    def __init__(self, name):
        self.name = name

    def load_project(self) -> dict | None:
        config_file = f"{self.name}.toml"
        if not os.path.exists(config_file):
            click.echo(f"No project [{self.name}] found!")
            return None

        with open(config_file, "rb") as f:
            return tomllib.load(f)
