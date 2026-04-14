from ollama import chat


def get_temperature(city: str) -> str:
    temperatures = {
        "New York": "22°C",
        "London": "15°C",
        "Tokyo": "18°C",
    }
    return temperatures.get(city, "Unknown")


messages = [{"role": "user", "content": "What is the temperature in Tokyo?"}]

response = chat(model="gemma4:e2b", messages=messages, tools=[get_temperature], think=True)

messages.append(response.message)
if response.message.tool_calls:
    call = response.message.tool_calls[0]
    result = get_temperature(**call.function.arguments)
    messages.append({"role": "tool", "tool_name": call.function.name, "content": str(result)})

    final_response = chat(model="gemma4:e2b", messages=messages, tools=[get_temperature], think=True)
    print(final_response.message.content)
