from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a comedian who tells jokes about {topic}"),
        ("user", "Please tell me {jokes_count} jokes about {topic}."),
    ]
)

# ----------------------- APPROACH A ---------------------------------------
# Use format_messages(...) which returns a LIST of message objects.
# This list can be passed directly to llm.invoke(messages).

# 1) Convert input dict -> list[BaseMessage]
format_prompt = RunnableLambda(lambda x: prompt_template.format_messages(**x))
# 2) Invoke the LLM with that messages list
invoke_model = RunnableLambda(lambda msgs: llm.invoke(msgs))
# 3) Extract text/content from the LLM response (AIMessage or similar)
extract_content = RunnableLambda(lambda ai_response: ai_response.content)

# Compose into a sequence: format_prompt -> invoke_model -> extract_content
chain_messages = RunnableSequence(
    first=format_prompt, middle=[invoke_model], last=extract_content
)

# Run it (pass a dict, it will be unpacked inside format_messages)
result_a = chain_messages.invoke({"topic": "cats", "jokes_count": 2})
print("Approach A result:", result_a)   


# ----------------------- APPROACH B ---------------------------------------
# Use format(...) which returns a PromptValue object. You must call .to_messages()
# on that PromptValue before giving it to the LLM.

# 1) Format into PromptValue (not yet messages)
format_prompt_pv = RunnableLambda(lambda x: prompt_template.format(**x))
# 2) Convert PromptValue -> messages, then invoke model
invoke_from_pv = RunnableLambda(lambda pv: llm.invoke(pv.to_messages()))
# 3) Extract the content
extract_content_b = RunnableLambda(lambda ai_response: ai_response.content)

# Compose into a sequence: format_prompt_pv -> invoke_from_pv -> extract_content_b
chain_promptvalue = RunnableSequence(
    first=format_prompt_pv, middle=[invoke_from_pv], last=extract_content_b
)

# Run it with the same input dict
result_b = chain_promptvalue.invoke({"topic": "dogs", "jokes_count": 3})
print("Approach B result:", result_b)  # also the extracted content (string)


# ----------------------- NOTES / TIPS -------------------------------------
# - Use approach A (format_messages) when you want fewer steps: it directly
#   produces the list of messages the chat model expects.
# - Use approach B (format) when you need the PromptValue object for other
#   operations (templating comparisons, storing the prompt, or using .to_string()).
# - In both runnables above, the first lambda expects a dict, so we use **kwargs
#   inside format_messages(**x) / format(**x) to expand the dict into keyword args.
# - If you ever build the same pipeline often, you can reuse the RunnableLambdas.
#
# Optional: if your LangChain version supports the pipe operator, you can do:
#   pipeline = format_prompt | llm | extract_content
# which is syntactic sugar for chaining. If that works in your environment,
# it produces an equivalent pipeline.
