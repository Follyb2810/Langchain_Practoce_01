from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from langchain.schema.runnable import RunnableLambda, RunnableSequence, RunnableParallel
from langchain.schema.output_parser import StrOutputParser

llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert product reviewer."),
        ("human", "List the main features of the product {product_name}."),
    ]
)


def analyze_pros(features):
    pros_template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are expert product reviewer."),
            (
                "human",
                "Given these features: {features}, list the pros of these features",
            ),
        ]
    )
    # ✅ corrected: use pros_template instead of prompt_template
    return pros_template.format_messages(features=features)


def analyze_cons(features):
    cons_template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are expert product reviewer."),
            (
                "human",
                "Given the features: {features}, list the cons of these features",
            ),
        ]
    )
    # ✅ corrected: fixed parenthesis and use format_messages
    return cons_template.format_messages(features=features)


def combine_pros_cons(pros, cons):
    return f"Pros:\n{pros}\n\nCons:\n{cons}"


# ✅ each branch formats, invokes llm, parses text
cons_branch_chain = RunnableLambda(lambda x: analyze_cons(x)) | llm | StrOutputParser()
pros_branch_chain = RunnableLambda(lambda x: analyze_pros(x)) | llm | StrOutputParser()

# ✅ RunnableParallel outputs {"pros": ..., "cons": ...}, not inside ["branches"]
chain = (
    prompt_template
    | llm
    | StrOutputParser()
    | RunnableParallel(branches={"pros": pros_branch_chain, "cons": cons_branch_chain})
    | RunnableLambda(lambda x: combine_pros_cons(x["pros"], x["cons"]))
)

result = chain.invoke({"product_name": "MacBook Pro"})

# Output
print(result)
