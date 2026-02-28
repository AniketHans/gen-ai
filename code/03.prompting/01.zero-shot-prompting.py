from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

# zero shot prompting
# We dont provide any examples to the agent.
# Also, here we have restricted the agent to discuss only about cars

SYSTEM_PROMPT = '''
    You are an AI agent that is good at giving info about cars.
    Dont cater any other request which is not about cars. 
'''

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

user_input = input()
messages.append({"role": "user", "content": user_input})
while True:
    response = client.chat.completions.create(model= "gpt-4.1-mini", messages=messages)
    print(response.choices[0].message.content)
    messages.append({"role": "assistant", "content": response.choices[0].message.content})
    user_input = input()
    messages.append({"role": "user", "content": user_input})