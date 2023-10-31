import click
from langchain.agents import load_tools
from langchain.tools import BaseTool

from threadagent.agent_factory import AgentFactory


def from_config(tool):
    if tool == "terminal":
        return "terminal"

    raise ValueError(f"Tool [{tool}] not supported!")


def create_tools(tools) -> list[BaseTool]:
    tools = [from_config(tool) for tool in tools]
    return load_tools(tools)


def convert_tools(tools):
    return "\n".join([f"{tool.name}: {tool.description}" for tool in tools])


class AgentRunner:
    def __init__(self, project: dict):
        self.project = project

    def run(self, name, message):
        chain = AgentFactory(self.project).create(name)
        chain.invoke({"input": message})

    def shell(self, name):
        chain = AgentFactory(self.project).create(name)
        while True:
            text = click.prompt("", prompt_suffix=">")
            if text.casefold() == "exit".casefold():
                break

            chain.invoke({"input": text})
