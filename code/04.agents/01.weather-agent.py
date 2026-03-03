from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

def getWeather(city: str):
    
    try:
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {'q': city, 'appid': os.getenv("WEATHER_API_KEY"), 'units': 'metric'}
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data["main"]["temp"]
        else:
            print(response)
            raise Exception("Error fetching weather data")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        
tool_map = {
    "getWeather": getWeather
}

SYSTEM_PROMPT = '''
    You are an agent which resolves user's queries
    
    You work on START, PLAN, ACTION, OBSERVE, PROCESS and RESULT sequence
    
    You can use the following tools to resolve some of the user queries:
        getWeather :- takes a city and fetches the current weather of the city
    
    Output JSON can only contain the following properties:
        - step
        - content
        - function
        - input
        
    Examples:
    User: "give me the current weather of moradabad"}
    Output: {step: "START", content: "reading user's query"}
    Output: {step: "PLAN", content: "user is asking about weather of Moradabad. Moradabad is a city in Uttar Pradesh state of India, pincode 244001. Getting the weather of Moradabad"}
    Output: {step: "ACTION", function: "getWeather", input: "moradabad"}
    Output: {step: "OBSERVE", content: "24 degree celcius"}
    Output: {step: "PROCESS", content: "Moradabad's current weather is 24 degree celcius as per the source"}
    Output: {step: "RESULT", content: "Moradabad, Uttar Pradesh, India. Pin: 244001, current temp is 24 degree celcius "}    
'''

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

# while True:
query = input("> ")
messages.append(
    {"role": "user", "content": query}
)

while True:
    response =  client.chat.completions.create(model= "gpt-4.1-mini", response_format= {"type": "json_object"}, messages=messages)
    jsonOp = json.loads(response.choices[0].message.content)
    
    if jsonOp.get("step") == "ACTION":
        func = jsonOp.get("function")
        inputs = jsonOp.get("input")
        print(f"Calling the {func} function")
        messages.append({"step": "OBSERVE", "content": tool_map[func](inputs) })
        continue
    
    if jsonOp.get("step") == "RESULT":
        print("\n\n Ouput:", jsonOp.get("content"))
        break
    messages.append({"role":"assistant", "content": response.choices[0].message.content})
    print(f'         {jsonOp.get("content")}')
    