from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
)
from langchain.schema.output_parser import StrOutputParser


llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

sys_prompt = SystemMessagePromptTemplate.from_template(
    "You are a comedian who tells jokes about {topic}"
)

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a comedian who tells jokes about {topic}"),
        ("human", "Tell me {joke_count} jokes")
    ]
)

chain = prompt_template | llm | StrOutputParser()

result = chain.invoke({"topic": "Software developer", "joke_count": 2})
print(result)
