from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableBranch
from langchain_ollama import ChatOllama

llm = ChatOllama(model="mistral", base_url="http://localhost:11434")


positive_feedback_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("human", "Generate a thank you note for this positive feedback: {feedback}"),
    ]
)

negative_feedback_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("human", "Generate a response addressing this negative feedback: {feedback}"),
    ]
)

neutral_feedback_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        (
            "human",
            "Generate a request for more details for this neutral feedback: {feedback}",
        ),
    ]
)

escalate_feedback_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("human", "Generate a message to escalate to a human agent: {feedback}"),
    ]
)


classification_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        (
            "human",
            "Classify the sentiment of this feedback as positive, negative, neutral, or escalate: {feedback}",
        ),
    ]
)


branches = RunnableBranch(
    (
        lambda x: "positive" in x.lower(),
        positive_feedback_template | llm | StrOutputParser(),
    ),
    (
        lambda x: "negative" in x.lower(),
        negative_feedback_template | llm | StrOutputParser(),
    ),
    (
        lambda x: "neutral" in x.lower(),
        neutral_feedback_template | llm | StrOutputParser(),
    ),
    escalate_feedback_template | llm | StrOutputParser(),
)

classification_chain = classification_template | llm | StrOutputParser()
chain = classification_chain | branches

review = (
    "The product is terrible. It broke after just one use and the quality is very poor."
)
result = chain.invoke({"feedback": review})

print("Classification result → Response:\n")

review = (
    "The product is excellent. I really enjoyed using it and found it very helpful."
)
result = chain.invoke({"feedback": review})

print("Classification result → Response:\n")
review = "The product is okay. It works as expected but nothing exceptional."
result = chain.invoke({"feedback": review})

print("Classification result → Response:\n")
review = "I'm not sure about the product yet. Can you tell me more about its features and benefits?"
result = chain.invoke({"feedback": review})

print("Classification result → Response:\n")
print(result)
