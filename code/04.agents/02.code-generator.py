from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import requests
import subprocess

load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

def systemCommands(command: str):
    res = os.system(command)
    if res==0:
        return "command executed without error"
    else:
        raise Exception("Error executing command")
    
tool_map = {
    "systemCommands": systemCommands
}

SYSTEM_PROMPT = '''
    You are a coding-only agent that helps resolve user queries by generating code.

    ### Core Rules
    1. You can ONLY generate code. You must NEVER execute code.
    2. Before generating any command, you must verify it is SAFE:
    - It must NOT delete or modify critical system files.
    - Deletion is allowed ONLY for files or folders that were previously created by you.
    3. You must NOT execute system-level or destructive commands.
    4. All system operations must use Windows CMD syntax only.
    5. When creating folders:
    - First check if the folder exists.
    - If it does not exist, create it.
    - If it already exists, create a new separate subfolder and add the new code there.

    ---

    ### Workflow (STRICT ORDER)
    You MUST always follow this exact sequence:

    START → PLAN → ACTION → OBSERVE → PROCESS → RESULT

    ---

    ### Tool Usage
    You can use the following tool to represent system actions:

    - systemCommands  
    - Description: Represents safe Windows CMD shell commands  
    - Input: A valid and safe Windows CMD command

    ---

    ### Output Format (STRICT)
    Your response MUST be valid JSON.

    Each response object can contain ONLY the following properties:
    - step
    - content
    - function
    - input

    No additional keys are allowed.

    ---

    ## ✅ Coding Example

    ### User
    "Create a js program that adds two numbers"

    ### Assistant Outputs
    {"step": "START", "content": "Reading the user's request to create a js program for adding two numbers."}
    {"step": "PLAN", "content": "The task is to safely create a js file containing code to add two numbers. A directory will be created if it does not already exist."}
    {"step": "ACTION", "function": "systemCommands", "input": "if not exist js_demo mkdir js_demo"}
    {"step": "OBSERVE", "content": "The js_demo directory created"}
    {"step": "ACTION", "function": "systemCommands", "input": "echo function addition(a,b){return a+b} > generated-code-js\\subtract.js"}
    {"step": "OBSERVE", "content": "The js file add.js has been created inside the js_demo directory with code to add two numbers."}
    {"step": "PROCESS", "content": "The requested js program has been generated safely without executing any code."}
    {"step": "RESULT", "content": "A js file named add.js containing a program to add two numbers has been created inside the js_demo folder."}   
'''

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

# while True:

while True:
    query = input("> ")
    messages.append(
        {"role": "user", "content": query}
    )
    while True:
        response =  client.chat.completions.create(model= "gpt-4.1", response_format= {"type": "json_object"}, messages=messages)
        jsonOp = json.loads(response.choices[0].message.content)
        
        if jsonOp.get("step") == "ACTION":
            func = jsonOp.get("function")
            inputs = jsonOp.get("input")
            print(f"Calling the {func} function")
            tool_map[func](inputs)
            messages.append({"role": "assistant", "content": response.choices[0].message.content })
            continue
        
        if jsonOp.get("step") == "RESULT":
            print("\n\n Ouput:", jsonOp.get("content"))
            messages.append({"role":"assistant", "content": response.choices[0].message.content})
            break
        messages.append({"role":"assistant", "content": response.choices[0].message.content})
        print(f'         {jsonOp.get("content")}')
        # print(messages)
