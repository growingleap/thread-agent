from langchain.schema.runnable import Runnable


class Agent:
    def __init__(self, chain: Runnable):
        self.chain = chain

    def run(self, message):
        return self.chain.invoke({"input": message})


class FilteredAgent(Agent):
    def __init__(self, chain, filter_func):
        super().__init__(chain)
        self.filter_func = filter_func

    def run(self, message):
        filtered = self.filter_func(message)
        return self.chain.invoke(filtered)
