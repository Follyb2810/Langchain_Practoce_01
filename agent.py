import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.base import RunnableSerializable
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# === Import Tools ===
from tools.get_user_profile import get_user_profile
from tools.check_existing_consultation import check_existing_consultation
from tools.classify_triage import classify_triage
from tools.assign_doctor import assign_doctor
from tools.final_answer import final_answer

tools = [get_user_profile, check_existing_consultation, classify_triage, assign_doctor, final_answer]

# === LLM ===
llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

# === Prompt ===
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a structured health triage assistant. "
                "Follow this EXACT 5-step dialogue:\n"
                "1. Greet the user by fetching their name using get_user_profile.\n"
                "2. Wait for user response.\n"
                "3. Ask: 'I’ll quickly gather some details to check your health status. Ready to begin?'\n"
                "4. Wait for user response.\n"
                "5. Ask them to submit their vitals as JSON.\n"
                "6. When user provides vitals → classify using classify_triage.\n"
                "7. Check if they already have a consultation (check_existing_consultation).\n"
                "   - If yes, direct them to same doctor.\n"
                "   - If no, assign a doctor with assign_doctor.\n"
                "8. End with final_answer (include triage result + doctor info)."
            ),
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        {"user": "{input}"},
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# === Agent ===
agent: RunnableSerializable = (
    {
        "input": lambda x: x["input"],
        "chat_history": lambda x: x["chat_history"],
        "agent_scratchpad": lambda x: x.get("agent_scratchpad", []),
    }
    | prompt
    | llm.bind_tools(tools, tool_choice="any")
)

# === Executor ===
class CustomAgentExecutor:
    def __init__(self, max_iterations: int = 5):
        self.chat_history: list[BaseMessage] = []
        self.max_iterations = max_iterations
        self.agent = agent
        self.name2tool = {t.name: t.func for t in tools}

    async def invoke(self, input: str, verbose=True) -> dict:
        agent_scratchpad = []
        count = 0

        while count < self.max_iterations:
            out = self.agent.invoke(
                {
                    "input": input,
                    "chat_history": self.chat_history,
                    "agent_scratchpad": agent_scratchpad,
                }
            )

            if out.tool_calls[0]["name"] == "final_answer":
                break

            tool_name = out.tool_calls[0]["name"]
            tool_args = out.tool_calls[0]["args"]

            try:
                tool_out = self.name2tool[tool_name](**tool_args)
            except Exception as e:
                tool_out = {"error": str(e)}

            if verbose:
                print(f"[Step {count}] {tool_name} returned {tool_out}")

            agent_scratchpad.append(out)
            agent_scratchpad.append(
                {"role": "tool", "content": str(tool_out), "tool_call_id": out.tool_calls[0]["id"]}
            )
            count += 1

        final_answer = out.tool_calls[0]["args"]
        final_answer_str = json.dumps(final_answer)
        self.chat_history.append({"input": input, "output": final_answer_str})
        self.chat_history.extend([HumanMessage(content=input), AIMessage(content=final_answer_str)])

        return final_answer
