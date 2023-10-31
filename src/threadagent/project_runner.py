import click

from threadagent.agent_runner import AgentRunner
from threadagent.project_loader import ProjectLoader


class ProjectRunner(ProjectLoader):
    def __init__(self, name: str):
        super().__init__(name)

    def run(self, message: str):
        project = self.load_project()
        if project is None:
            return

        self._run_project(project, message)

    @staticmethod
    def _run_project(project: dict, message: str):
        entry = project["project"]["entry"]
        (_type, name) = entry.split('.')
        if _type == "agent":
            AgentRunner(project).run(name, message)
            return

        click.echo("No entry found in project")

    def shell(self):
        project = self.load_project()
        if project is None:
            return

        self._shell_project(project)

    @staticmethod
    def _shell_project(project):
        entry = project["project"]["entry"]
        (entry_type, entry_name) = entry.split('.')
        if entry_type == "agent":
            AgentRunner(project).shell(entry_name)
            return

        click.echo("No entry found in project")
