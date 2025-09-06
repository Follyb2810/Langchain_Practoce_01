from langchain_ollama import Chatllama

llm = Chatllama(model="mistral", base_url="http://localhost:11434")
prompt = "what is 2 +8"
result = llm.invoke(prompt)
print(result)
print(result.content)
