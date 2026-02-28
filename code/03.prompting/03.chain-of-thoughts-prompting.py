from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

# Chain of thoughts prompting
# You ask the AI to think step by step before giving the final answer.

SYSTEM_PROMPT = '''
    You are an AI agent that is good at giving info about cars.
    For the given input analyse and break down the ask into multiple steps
    
    Follow the steps in sequence : "analyse", "think", "output", "validate", and finally "result"
    Return ONLY valid JSON.
    Do not include explanations, markdown, or code blocks.
    
    Examples:
    User: Tell me about Honda Elevate
    Output: {"step": "analyse", content: "user is asking about Honda Elevate car"}
    Output: {"step": "think", content: "what type of car is honda elevate. What are its engine options. Whats its ex show room price for base and top models"}
    Output: {"step": "output", content: "Honda elevate is a compact suv. It comes with 1.5 L 4 cylinder vtec engine with 121 bhp and 145 NM torque. It starts with ₹11.60 Lakhs and goes till ₹16.67 Lakhs"}
    Output: {"step": "validate", content: "validating the output from autocar.com website"}
    Output: {"step": "result", content: "Honda Elevate is an copact suv from Honda in India. It starts from ₹11.60 Lakhs and goes till ₹16.67 Lakhs. It comes with a 1.5 L 4 cylinder vtec engine which produces 121 bhp and 145 NM torque"}
    
'''

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

user_input = input()
messages.append({"role": "user", "content": user_input})
while True:
    response = client.chat.completions.create(model= "gpt-4.1-mini", response_format= {"type": "json_object"}, messages=messages)
    jsonOpt = json.loads(response.choices[0].message.content)
    print(jsonOpt.get("step"))
    if jsonOpt.get("step") == "result":
        print("\n\nFinal Result:", jsonOpt.get("content"),"\n\n")
        break
    print("               ", response.choices[0].message.content)
    messages.append({"role": "assistant", "content": response.choices[0].message.content})