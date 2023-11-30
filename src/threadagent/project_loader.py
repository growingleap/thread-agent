import os
import tomllib

import click

from threadagent.agent_factory import AgentFactory
from threadagent.project import Agent, Project, SequenceWorkflow, Workflow


def load_project_config(config_file) -> dict | None:
    if not os.path.exists(config_file):
        click.echo(f"No file [{config_file}] found!")
        return None

    with open(config_file, "rb") as f:
        return tomllib.load(f)


class ProjectLoader:
    def __init__(self, config: dict):
        self.config = config

    def load_project(self) -> Project | None:
        agents = self.load_agents()
        workflows = self.load_workflows(agents)
        project = Project(self.config["project"]["name"], agents, workflows)

        entry = self.config["project"]["entry"]
        (_type, name) = entry.split('.')
        project.setup_entry(_type, name)

        return project

    def load_agents(self) -> dict[Agent]:
        if "agent" not in self.config:
            return {}

        return {name: AgentFactory(self.config).create(name) for (name, agent_config) in
                self.config["agent"].items()}

    def load_workflows(self, agents) -> dict[Workflow]:
        if "workflow" not in self.config:
            return {}

        return {name: self.create_workflow(name, agents) for (name, agent_config) in
                self.config["workflow"].items()}

    def create_workflow(self, name, agents) -> Workflow:
        config = self.config["workflow"][name]
        if config["type"] == "sequence":
            targets = [self.as_target(target, agents) for target in config["agents"]]
            return SequenceWorkflow(name, targets)

        raise ValueError(f"Workflow type [{config['type']}] not supported!")

    def as_target(self, name, agents):
        (_type, target) = name.split('.')
        if _type == "agent":
            return agents[target]

        raise ValueError(f"Target type [{_type}] not supported!")
