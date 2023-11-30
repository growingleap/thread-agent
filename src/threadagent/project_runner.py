import click

from threadagent.project import Project


class ProjectRunner:
    def __init__(self, project: Project):
        self.project = project

    def run(self, message: str) -> str | None:
        return self.project.invoke(message)

    def shell(self):
        self._shell_project()

    def _shell_project(self):
        while True:
            text = click.prompt("", prompt_suffix=">")
            if text.casefold() == "exit".casefold():
                break

            self.project.invoke(text)
