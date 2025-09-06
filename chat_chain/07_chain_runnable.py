from langchain_core.runnables import RunnableLambda, RunnableSequence, RunnableParallel
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

root_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert product reviewer."),
        ("user", "List the main features of the product {product_name}."),
    ]
)

pros_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert product reviewer."),
        ("user", "Given these features: {features}, list the pros of these features."),
    ]
)


cons_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert product reviewer."),
        ("user", "Given these features: {features}, list the cons of these features."),
    ]
)

# Simple combiner function (runs after pros & cons are ready)
def combine_pros_cons(pros: str, cons: str) -> str:
    return f"Pros:\n{pros}\n\nCons:\n{cons}"

# --- 2) Runnables for the root feature extraction -------------------------
# format_root: takes input dict like {"product_name": "MacBook Pro"} and returns list[BaseMessage]
format_root = RunnableLambda(lambda inputs: root_template.format_messages(**inputs))

# invoke_llm: accepts a list[BaseMessage] and calls the LLM -> returns AI response object
invoke_llm = RunnableLambda(lambda messages: llm.invoke(messages))

# extract_text: pulls the textual content from the AI response (e.g., ai_response.content)
extract_text = RunnableLambda(lambda ai_response: ai_response.content)

# Compose the root feature extraction chain:
# format_root -> invoke_llm -> extract_text
feature_extraction_chain = RunnableSequence(
    first=format_root,
    middle=[invoke_llm],
    last=extract_text,
)

# --- 3) Runnables for pros branch -----------------------------------------
# pros_format: formats a prompt for pros from a simple features string
pros_format = RunnableLambda(lambda features: pros_template.format_messages(features=features))

# pros_invoke and pros_extract mirror invoke_llm/extract_text but as separate runnables
pros_invoke = RunnableLambda(lambda messages: llm.invoke(messages))
pros_extract = RunnableLambda(lambda ai_response: ai_response.content)

# The pros branch sequence: pros_format -> pros_invoke -> pros_extract
pros_branch_chain = RunnableSequence(
    first=pros_format,
    middle=[pros_invoke],
    last=pros_extract,
)

# --- 4) Runnables for cons branch (same layout) ---------------------------
cons_format = RunnableLambda(lambda features: cons_template.format_messages(features=features))
cons_invoke = RunnableLambda(lambda messages: llm.invoke(messages))
cons_extract = RunnableLambda(lambda ai_response: ai_response.content)

cons_branch_chain = RunnableSequence(
    first=cons_format,
    middle=[cons_invoke],
    last=cons_extract,
)

# --- 5) Parallel branch runner -------------------------------------------
# RunnableParallel runs both branches in parallel, giving a dict result like:
# {"pros": <pros result>, "cons": <cons result>}
parallel_branches = RunnableParallel(branches={"pros": pros_branch_chain, "cons": cons_branch_chain})

# --- 6) Full pipeline: features -> parallel(pros,cons) -> combine ----------
# After feature_extraction_chain returns the features string, parallel_branches will
# be invoked with that features string as input (it passes the same input to each branch).
combine_result = RunnableLambda(lambda outputs: combine_pros_cons(outputs["pros"], outputs["cons"]))

# Compose everything sequentially:
# 1) extract features string
# 2) run pros/cons branches in parallel on the features string
# 3) combine the results
full_chain = RunnableSequence(
    first=feature_extraction_chain,    # produces features_str
    middle=[parallel_branches],        # runs pros & cons concurrently
    last=combine_result,               # combine dict -> final string
)

# --- 7) Run the chain -----------------------------------------------------
result = full_chain.invoke({"product_name": "MacBook Pro"})
print("Final combined output:\n", result)


# -------------------- Explanations / Comments ------------------------------
# RunnableLambda: wraps a normal python function so it can be used inside a LangChain pipeline.
#   - Here we used it for formatting prompts, calling the LLM, extracting content, and combining results.
#
# RunnableSequence: compose runnables in sequence. The output of the previous becomes the input
#   of the next. We used it to create small pipelines (feature extraction, pros branch, cons branch),
#   and to compose the final pipeline.
#
# RunnableParallel: runs multiple branches in parallel (or concurrently). It passes the same input
#   to each branch and returns a dictionary mapping branch name -> branch output.
#   - Useful when you want to analyze the same input from multiple perspectives (pros/cons, short/long).
#
# Why use format_messages(...) everywhere?
#   - format_messages(**kwargs) returns a list of message objects (SystemMessage/HumanMessage),
#     which is exactly what chat-style LLMs expect as input to `llm.invoke(...)`.
#
# Alternative: If you prefer PromptValue objects you can use prompt_template.format(**kwargs)
#   and then call .to_messages() before passing to the LLM (less direct).
#
# Optional: Output parsers
#   - If you want more structured parsing (e.g., parse to JSON or list), replace the simple
#     `extract_text` RunnableLambda with a real output parser (e.g., a StrOutputParser or JSON parser)
#     if your LangChain version provides them. Example:
#       extract_text = StrOutputParser()    # if this class is available and compatible
#
# Pipe operator: some LangChain versions allow `|` composition:
#   pros_branch_chain = RunnableLambda(lambda f: pros_template.format_messages(features=f)) | llm | RunnableLambda(lambda r: r.content)
#   If supported, that is syntactic sugar for the same composition we created with RunnableSequence.
