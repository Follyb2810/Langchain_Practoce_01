from langchain_ollama import Chatllama
from langchain_core.messages import AiMessage,HumanMessage,SystemMessage

llm = Chatllama(model='mistral',base_url='http://localhost:11434')

message =[
    SystemMessage(content="Solve the following math question"),
    HumanMessage(content="What is 81 divide by 9"),
]

result = llm.invoke(message)
print(result)
print(result.content )

message =[
    SystemMessage(content="Solve the following math question"),
    HumanMessage(content="What is 81 divide by 9"),
    SystemMessage(content="81 divide by 9 is 9"),
    HumanMessage(content="What is 11 times 3"),
]

result = llm.invoke(message)
print(result)
print(result.content )
