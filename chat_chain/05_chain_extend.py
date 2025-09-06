from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a comedian who tell jokes about {topic}."),
        ("user", "Tell me {joke_count} jokes"),
    ]
)

uppercase_output = RunnableLambda(lambda x: x.upper())
count_words = RunnableLambda(lambda x: f"Words Count {len(x.split())}\n{x}")

chain = prompt_template | llm | StrOutputParser() | uppercase_output | count_words

response = chain.invoke({"topic": "software developer", "joke_count": 3})
print(response)

