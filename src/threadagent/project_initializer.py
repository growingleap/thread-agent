import os

import click
import tomli_w

from threadagent.project_loader import ProjectLoader


class ProjectInitializer(ProjectLoader):
    def __init__(self, name):
        super().__init__(name)

    def initialize(self):
        project = self._new_project()
        if project is None:
            return

        click.echo(f"Creating a new project [{self.name}]...")
        model = click.prompt("What is the default LLM model?",
                             default="openai", show_default=True, type=str)
        project["project"]["default-model"] = f"llm.{model}"
        project["llm"] = self._new_llm(model)

        prompt = click.prompt("Do you want to add an agent? (y/n)",
                              default="y", show_default=True, type=str)
        if prompt.casefold() == "Y".casefold():
            (name, agent) = self._new_agent()

            project["agent"] = {
                name: agent
            }
            project["project"]["entry"] = f"agent.{name}"

        self._save_project(project)
        click.echo("Done!")

    @staticmethod
    def _save_project(project: dict):
        with open(f"{project['project']['name']}.toml", "wb") as f:
            tomli_w.dump(project, f)

    def _new_project(self) -> dict | None:
        config_file = f"{self.name}.toml"
        if os.path.exists(config_file):
            click.echo(f"Project [{self.name}] already exists!")
            return None

        return {
            "project": {
                "name": self.name
            }
        }

    @staticmethod
    def _new_llm(model: str) -> dict:
        if model == "openai":
            api_base = click.prompt("API Base",
                                    default="https://api.openai.com/v1",
                                    show_default=True, type=str)
            api_key = click.prompt("API Key",
                                   hide_input=True, type=str)

            return {
                "openai": {
                    "api_key": api_key,
                    "api_base": api_base
                }
            }

        raise Exception(f"Unknown LLM model {model}")

    @staticmethod
    def _new_agent() -> tuple:
        name = click.prompt("Agent name")
        any_tool = click.prompt("Does the agent use any tool?[Y/N]",
                                default="n", show_default=True, type=str)
        if any_tool.casefold() != "Y".casefold():
            return (name, {
                "model": "llm.openai"
            })

        tools = []
        while True:
            tool = click.prompt("Tool name?(N to exit)",
                                default="terminal", show_default=True, type=str)
            if tool.casefold() == "N".casefold():
                break
            tools.append(tool)
        return (name, {
            "tools": tools,
            "model": "llm.openai"
        })

    def add_agent(self):
        project = self.load_project()
        if project is None:
            return

        (name, new_agent) = self._new_agent()
        if project["agent"] is None:
            project["agent"] = {}

        project["agent"][name] = new_agent
        self._save_project(project)

    def add_workflow(self):
        project = self.load_project()
        if project is None:
            return

        (name, new_workflow) = self._new_workflow()
        if "workflow" not in project:
            project["workflow"] = {}

        project["workflow"][name] = new_workflow

        entry = click.prompt("Apply this workflow as the entry point? (y/n)",
                             default="y", show_default=True, type=str)
        if entry.casefold() == "Y".casefold():
            project["project"]["entry"] = f"workflow.{name}"
        self._save_project(project)

    @staticmethod
    def _new_workflow() -> tuple | None:
        name = click.prompt("Workflow name")
        initial_agent = click.prompt("Initial agent name")

        return (name, {
            "initial_agent": f"agent.{initial_agent}"
        })
