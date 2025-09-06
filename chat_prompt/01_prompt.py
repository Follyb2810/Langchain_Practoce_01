from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_ollama import ChatOllama

##? one message
llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

prompt = "Tell me a joke about {topic}"


prompt_template = ChatPromptTemplate.from_template(prompt)

chain = prompt_template | llm


result_response = prompt_template.invoke({"topic": "why de we have 7 days"})
print(result_response)
# ? result = chain.invoke({"topic": "why de we have 7 days"})
# ? print(result.content)


##? mutile message
template_message = """ You are a helpful assistance.
Human: tell me a {adjective} story about a {animal}.
Assistance: """

prompt = ChatPromptTemplate.from_template(template_message)

result_template = prompt.invoke({"adjective": "funny", "animal": "panda"})

print(result_template)


##? ai and user

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a comedian who tell jokes about {topic}"),
        ("user", "Tell me {jokes_count} jokes"),
    ]
)
result_template = prompt.invoke({"topic": "lawyer", "jokes_count": 3})

print(result_template)

##? ai and user from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
##? work when no interpolation

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a comedian who tell jokes about {topic}"),
        HumanMessage(content="Tell me {jokes_count} jokes"),
        HumanMessage(content="Tell me 3 jokes"),
    ]
)
result_template = prompt.invoke({"topic": "lawyer", "jokes_count": 3})

print(result_template)
