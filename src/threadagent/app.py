import os.path
import sys

import click

from threadagent.project_loader import ProjectLoader, load_project_config

current_path = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.split(current_path)[0]
sys.path.append(root_path)

from threadagent.project_initializer import ProjectInitializer  # noqa:E402
from threadagent.project_runner import ProjectRunner  # noqa:E402


@click.group()
def app():
    """thread agent is a tool for building AI agents."""
    pass


@click.group("add")
def add_command():
    """add a new agent or workflow to a project."""
    pass


@click.command("agent")
@click.argument("project_name", nargs=1)
def add_agent_command(project_name):
    """add a new agent to a project."""
    ProjectInitializer(project_name).add_agent()


@click.command("workflow")
@click.argument("project_name", nargs=1)
def add_workflow_command(project_name):
    """add a new workflow to a project."""
    ProjectInitializer(project_name).add_workflow()


@click.command("new")
@click.argument("project_name", nargs=1)
def new_project_command(project_name):
    """create a new project."""
    ProjectInitializer(project_name).initialize()


@click.command("run")
@click.argument("filename", nargs=1)
@click.option("-m", "--message", "message")
def run_project_command(filename, message):
    """run the project with single message."""
    config = load_project_config(filename)
    project = ProjectLoader(config).load_project()
    ProjectRunner(project).run(message)


@click.command("shell")
@click.argument("filename", nargs=1)
def shell_project_command(filename):
    """run the project in a shell."""
    config = load_project_config(filename)
    project = ProjectLoader(config).load_project()
    ProjectRunner(project).shell()


add_command.add_command(add_agent_command)
add_command.add_command(add_workflow_command)
app.add_command(add_command)
app.add_command(new_project_command)
app.add_command(run_project_command)
app.add_command(shell_project_command)

if __name__ == "__main__":
    app()
