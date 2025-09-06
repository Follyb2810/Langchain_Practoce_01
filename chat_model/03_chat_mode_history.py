from langchain_ollama import Chatllama
from langchain_core.messages import AiMessage, HumanMessage, SystemMessage

llm = Chatllama(model="mistral", base_url="http://localhost:11434")

chat_history = []
system_message = SystemMessage(content="You are helpful ai assistance")
chat_history.append(system_message)

while True:
    query = input("you: ")
    if query.lower() in ["exist", "quit"]:
        break
    chat_history.append(HumanMessage(content=query))

    result = llm.invoke(chat_history)
    response = result.content
    chat_history.append(AiMessage(content=response))

    print(f"Ai {response}")

print(chat_history)
 