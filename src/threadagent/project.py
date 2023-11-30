from abc import ABC, abstractmethod

from langchain.schema.runnable import Runnable


class Invocable(ABC):
    @abstractmethod
    def invoke(self, message) -> str | None:
        pass


class Project(Invocable):
    def __init__(self, name, agents, workflows):
        self.name = name
        self.agents = agents
        self.workflows = workflows
        self.entry = None

    def setup_entry(self, _type, name):
        if _type == "agent":
            self.entry = self.agents[name]
            return

        if _type == "workflow":
            self.entry = self.workflows[name]
            return

        raise ValueError(f"Entry type [{_type}] not supported!")

    def invoke(self, message) -> str | None:
        return self.entry.invoke(message)


class Agent(Invocable):
    def __init__(self, name: str, chain: Runnable, input_key="input"):
        self.name = name
        self.chain = chain
        self.user_input_key = input_key

    def invoke(self, message) -> str | None:
        return self.run(message)

    def run(self, message) -> str | None:
        return self.chain.invoke({self.user_input_key: message})


class FilteredAgent(Agent):
    def __init__(self, name, chain, filter_func):
        super().__init__(name, chain)
        self.filter_func = filter_func

    def run(self, message):
        filtered = self.filter_func(message)
        return self.chain.invoke(filtered)


class Workflow(Invocable, ABC):
    def __init__(self, name: str):
        self.name = name


class SequenceWorkflow(Workflow):
    def __init__(self, name: str, agents: list[Agent]):
        super().__init__(name)
        self.agents = agents

    def invoke(self, message) -> str | None:
        for agent in self.agents:
            message = agent.invoke(message)

        return message
