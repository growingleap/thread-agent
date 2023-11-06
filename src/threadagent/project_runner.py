import click

from threadagent.agent_runner import AgentRunner


class ProjectRunner:
    def __init__(self, project: dict):
        self.project = project

    def run(self, message: str) -> str | None:
        entry = self.project["project"]["entry"]
        (_type, name) = entry.split('.')
        if _type == "agent":
            return AgentRunner(self.project).run(name, message)

        click.echo("No entry found in project")
        return None

    def shell(self):
        self._shell_project()

    def _shell_project(self):
        entry = self.project["project"]["entry"]
        (entry_type, entry_name) = entry.split('.')
        if entry_type == "agent":
            AgentRunner(self.project).shell(entry_name)
            return

        click.echo("No entry found in project")
