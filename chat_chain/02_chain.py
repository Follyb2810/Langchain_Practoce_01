from langchain_core.runnables import (
    RunnableLambda,
    RunnableSequence,
    RunnableSerializable,
)
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a comedian who tells jokes about {topic}"),
        ("user", "tell me {jokes_count} jokes"),
    ]
)


# ? RunnableLambda
def double_number(x: int) -> int:
    return x * 2


double_runnable = RunnableLambda(double_number)
print(double_runnable.invoke(5))  # -> 10

# ? Runnable pipeline with LLM
# Step 1: format prompt into list of messages
format_prompt = RunnableLambda(lambda x: prompt_template.format_messages(**x))
print(format_prompt)

# Step 2: pass messages into LLM
invoke_model = RunnableLambda(lambda msgs: llm.invoke(msgs))
print(invoke_model)

# Step 3: extract the LLM response content
parser_output = RunnableLambda(lambda x: x.content)
print(parser_output)

chain = RunnableSequence(first=format_prompt, middle=[invoke_model], last=parser_output)

response = chain.invoke({"topic": "youtube influencer", "jokes_count": 2})
print("LLM response:", response)

#! --- Example 3: Simple math pipeline
double = RunnableLambda(lambda x: x * 2)
to_string = RunnableLambda(lambda x: f"Result: {x}")
pipeline = RunnableSequence(first=double, last=to_string)

print(pipeline.invoke(5))
