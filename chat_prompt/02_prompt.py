from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_ollama import ChatOllama

llm = ChatOllama(model="mistral", base_url="http://localhost:11434")
###? simgle
template = "Tell me a short joke about {topic}"

prompt_template = ChatPromptTemplate.from_template(template)

prompt = prompt_template.invoke({"topic": "cat"})
result = llm.invoke(prompt)
print(result.content)

###? multiple

template = """ You are an helpful assistance
Human: Tell me a {adjective} story about a {animal}.
Assistant: """
prompt_template = ChatPromptTemplate.from_template(template)
prompt = prompt_template.invoke({"adjective": "funny", "animal": "cat"})
result = llm.invoke(prompt)
print(result.content)


### with from me from_messages

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a comedian who tell jokes about {topic}"),
        ("user", "Tell me {jokes_count} jokes"),
    ]
)

prompt = prompt_template.invoke({"topic": "software developer", "jokes_count": 3})
result = llm.invoke(prompt)
print(result.content)

### from

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a comedian who tell jokes about {topic}"),
        HumanMessage(content="Tell me 3 jokes"),
    ]
)

prompt = prompt_template.invoke({"topic": "software developer", "jokes_count": 3})
result = llm.invoke(prompt)
print(result.content)
