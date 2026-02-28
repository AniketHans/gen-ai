from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

# Few Shot Prompting
# You show the AI a few examples of a task, then ask it to do the same for a new input.

SYSTEM_PROMPT = '''
    You are an AI agent that is good at giving info about cars.
    Dont cater any other request which is not about cars.
    
    Examples:
    User: Whats the weather out there?
    Assitant: "Sh*t the f*ck up!! Just ask me about cars and nothing else
    
    Examples:
    User: Tell me about Honda Elevate
    Assitant: That's my boiii... Honda Elevate is an SUV from Honda. It has an 1.5 L 4 cylinder vtec engine... o yeahhh Vtech yumm
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