REACT_TEMPLATE = """Answer the following questions as best you can. \
You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

CONDENSE_QUESTION_PROMPT = """Given the following conversation and a follow up question, \
rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{history}
Follow Up Input: {input}
Standalone question:"""

ANSWER_PROMPT = """Answer the question based only on the following context:
{context}

Question: {input}"""
