import os
from operator import itemgetter

import click
from langchain.agents import AgentExecutor, load_tools
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.cache import InMemoryCache
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader, WebBaseLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.globals import set_llm_cache
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.embeddings import Embeddings
from langchain.schema.language_model import BaseLanguageModel
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.text_splitter import CharacterTextSplitter
from langchain.tools import BaseTool
from langchain.tools.render import render_text_description
from langchain.vectorstores.qdrant import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.conversions.common_types import VectorParams
from qdrant_client.http.models import models

from threadagent.agent_template import ANSWER_PROMPT, CONDENSE_QUESTION_PROMPT, REACT_TEMPLATE
from threadagent.memory_runnable import MemoryRunnable
from threadagent.project import Agent, FilteredAgent
from threadagent.streaming_callback import StreamingClickCallbackHandler


def from_config(tool):
    if tool == "terminal":
        return "terminal"

    raise ValueError(f"Tool [{tool}] not supported!")


def create_tools(tools) -> list[BaseTool]:
    tools = [from_config(tool) for tool in tools]
    return load_tools(tools)


def convert_tools(tools):
    return "\n".join([f"{tool.name}: {tool.description}" for tool in tools])


class AgentFactory:
    def __init__(self, project):
        self.project = project

    def create(self, name) -> Agent:
        agent = self.project["agent"][name]
        model = self._create_model(agent)

        set_llm_cache(InMemoryCache())

        if "type" in agent:
            return self._create_typed_agent(name, agent, model)

        return self._create_bot(name, agent, model)

    def _create_model(self, agent) -> BaseLanguageModel:
        llm = self._get_agent_model(agent)
        (_, name) = llm.split(".")
        return self._create_model_by_name(name)

    def _create_model_by_name(self, name) -> BaseLanguageModel:
        if "openai".casefold() == name.casefold():
            model_name = self._get_model_name()

            return ChatOpenAI(
                model_name=model_name,
                openai_api_key=self.project["llm"]["openai"]["api_key"],
                openai_api_base=self.project["llm"]["openai"]["api_base"],
                streaming=True,
                callbacks=[StreamingClickCallbackHandler(click)],
                cache=True
            )

        raise ValueError(f"LLM [{name}] not supported!")

    @staticmethod
    def _get_model_name() -> str:
        return "gpt-3.5-turbo-1106"

    def _get_agent_model(self, agent: dict) -> str:
        if "model" in agent:
            return agent["model"]

        return self.project["project"]["default-model"]

    @staticmethod
    def _create_react_agent(name, agent, model: BaseLanguageModel) -> Agent:
        llm_with_stop = model.bind(stop=["\nObservation"])
        tools = create_tools(agent["tools"])
        prompt = PromptTemplate.from_template(REACT_TEMPLATE, partial_variables={
            "tools": render_text_description(tools),
            "tool_names": convert_tools(tools),
        })
        agent = {
                    "input": lambda x: x["input"],
                    "agent_scratchpad": lambda x: format_log_to_str(x['intermediate_steps']),
                    "chat_history": lambda x: x["chat_history"],
                } | prompt | llm_with_stop | ReActSingleInputOutputParser()
        memory = ConversationBufferWindowMemory(memory_key="chat_history")
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory)
        return Agent(name, agent_executor)

    def _create_bot(self, name: str, agent, model: BaseLanguageModel) -> Agent:
        if "documents" in agent:
            return self._create_qa_bot(name, agent, model)

        prompt = self.create_prompt(agent)

        memory = ConversationBufferWindowMemory(return_messages=True)
        memory.load_memory_variables({})
        chain = (RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history"))
                 | prompt
                 | model)
        user_input_key = "input"
        if 'input_key' in agent:
            user_input_key = agent['input_key']
        return Agent(name, MemoryRunnable(memory, chain), input_key=user_input_key)

    def create_prompt(self, agent):
        prompt = "{input}"
        if "prompt_template" in agent:
            prompt = agent["prompt_template"]
            return PromptTemplate.from_template(prompt)

        return ChatPromptTemplate.from_messages([
            ("system", "You are a helpful chatbot"),
            MessagesPlaceholder(variable_name="history"),
            ("human", prompt)
        ])

    def _create_qa_bot(self, name: str, agent, model: BaseLanguageModel) -> Agent:
        qa_prompt = ChatPromptTemplate.from_template(ANSWER_PROMPT)
        prompt = ChatPromptTemplate.from_template(CONDENSE_QUESTION_PROMPT)

        client = QdrantClient(location=":memory:")
        collection_name = "qa_bot"
        try:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=models.Distance.COSINE)
            )
        except ValueError:
            pass
        vectorstore = Qdrant(
            client=client,
            embeddings=self._create_embedding(agent),
            collection_name=collection_name
        )
        loaders = [TextLoader(doc) for doc in agent["documents"] if os.path.exists(doc)]
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        for loader in loaders:
            docs = text_splitter.split_documents(loader.load())
            vectorstore.add_documents(docs)

        memory = ConversationBufferWindowMemory(memory_key="history", k=5, return_messages=True)

        qa_chain = ({
                        "context": itemgetter("input")
                                   | vectorstore.as_retriever(search_type="mmr"),
                        "input": RunnablePassthrough()
                    }
                    | qa_prompt
                    | model)

        memory.load_memory_variables({})
        condense_question_chain = (RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history"))
                                   | prompt
                                   | model
                                   | StrOutputParser()
                                   | {"input": RunnablePassthrough()}
                                   )

        return Agent(name, condense_question_chain | MemoryRunnable(memory, qa_chain))

    def _create_embedding_by_name(self, name) -> Embeddings:
        if "openai".casefold() == name.casefold():
            return OpenAIEmbeddings(
                openai_api_key=self.project["llm"]["openai"]["api_key"],
                openai_api_base=self.project["llm"]["openai"]["api_base"]
            )

        raise ValueError(f"Embedding [{name}] not supported!")

    def _create_embedding(self, agent) -> Embeddings:
        llm = self._get_agent_model(agent)
        (_, name) = llm.split(".")
        return self._create_embedding_by_name(name)
        pass

    def _create_typed_agent(self, name, agent, model: BaseLanguageModel) -> Agent:
        if agent["type"] == "summarize":
            return self._create_summarize_agent(name, agent, model)

        if agent["type"] == "react":
            return self._create_react_agent(name, agent, model)

        raise ValueError(f"Agent type [{agent['type']}] not supported!")

    @staticmethod
    def _create_summarize_agent(name, agent, model: BaseLanguageModel) -> Agent:
        prompt = PromptTemplate.from_template(
            """Write a concise summary in its original language of the following:
            "{text}"

            CONCISE SUMMARY:""")
        chain = load_summarize_chain(model, chain_type="refine", question_prompt=prompt)

        def _run(message):
            loader = WebBaseLoader(web_path=message,
                                   encoding="utf-8",
                                   bs_get_text_kwargs={"strip": True})
            return loader.load()

        return FilteredAgent(name, chain, _run)
