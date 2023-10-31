from langchain.schema.runnable import Runnable, RunnableConfig
from langchain.schema.runnable.utils import Input, Output


class MemoryRunnable(Runnable):
    def __init__(self, memory, runnable):
        self.memory = memory
        self.runnable = runnable

    def invoke(self, input: Input, config: RunnableConfig = None) -> Output:
        response = self.runnable.invoke(input, config)
        self.memory.save_context(input, {"output": response.content})
        return response
