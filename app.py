import asyncio
from agent import CustomAgentExecutor


async def main():
    executor = CustomAgentExecutor()

    print("\n=== Conversation ===\n")

    # Step 1
    res1 = await executor.invoke("Hello")
    print("AI:", res1)

    # Step 2
    res2 = await executor.invoke("Hi!")
    print("AI:", res2)

    # Step 3: submit vitals
    vitals = {
        "heart_rate": 120,
        "systolic_bp": 150,
        "diastolic_bp": 95,
        "temperature": 38.2,
        "weight": 75,
        "symptoms": "shortness of breath and chest pain",
    }
    res3 = await executor.invoke(str(vitals))
    print("AI:", res3)


if __name__ == "__main__":
    asyncio.run(main())
