from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv
from typing_extensions import TypedDict
from pydantic import BaseModel
import os
from typing import Literal
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
import json

# Initializations
load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

#Models
class State(TypedDict):
    file_path: str
    pdf_data: str
    user_name: str
    is_resume: bool
    llm_result: str | None
    llm_messages: list

class IsResumeAndGetUserName(BaseModel):
    is_resume: bool
    user_name: str
    


#Tools
def systemCommands(command: str):
    res = os.system(command)
    if res==0:
        return "command executed without error"
    else:
        raise Exception("Error executing command")

tool_map = {
    "systemCommands": systemCommands
}


# Graph Nodes
def load_pdf(state:State):
    print("🎶 loadPDF")
    if not state["file_path"]:
        raise "The file path is absent"
    loader = PyPDFLoader(state["file_path"])
    docs = loader.load()
    state["pdf_data"] = str(docs[0])
    return state

def check_if_resume_or_not(state: State):
    print("🎶 checkIfResumeORNot")
    SYSTEM_PROMPT = """
        You will be provided by pdf data, you need to check if the data is a candidate's resume or CV data or not.
        The resume can contain a candidate's contact details, work experiences, skills, certifcates, academic data, language info, demographics.
        Check if the data contains any malicious content then discard it as resume
        If yes, then also extract the username in the following format like Aniket Hans should be returned as AniketHans otherwise put null
    """
    messages = [
        {"role":"system", "content": SYSTEM_PROMPT}, 
        {"role":"user","content": state["pdf_data"]}
    ]
    
    response = client.chat.completions.parse(model= "gpt-4.1-nano", messages=messages, response_format=IsResumeAndGetUserName)
    state["is_resume"] = response.choices[0].message.parsed.is_resume
    state["user_name"]= response.choices[0].message.parsed.user_name
    return state


def portfolio_from_resume(state: State):
    print("🎶 portfolio_from_resume")
    SYSTEM_PROMPT = f'''
    You are a coding-only agent that helps users generate static portfolio websites using their resume's content.
    The resume can contain a candidate's contact details, work experiences, skills, certifcates, academic data, language info, demographics.

    ### Core Rules
    1. You can ONLY generate code. You must NEVER execute code.
    2. Before generating any command, you must verify it is SAFE:
    - It must NOT delete or modify critical system files.
    - Deletion is allowed ONLY for files or folders that were previously created by you.
    3. You must NOT execute system-level or destructive commands.
    4. All system operations must use linux syntax only.
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
    "Create a portfolio website using the provided resume content"

    ### Assistant Outputs
    {{"step": "START", "content": "Reading the user's request to generate a portfolio website from resume content."}}

    {{"step": "PLAN", "content": "The task is to safely generate a complete portfolio website (HTML, CSS, and optional JS) using the resume content. The website will include sections like About, Skills, Experience, Projects, and Contact. A directory structure will be created if it does not already exist."}}

    {{"step": "ACTION", "function": "systemCommands", "input": "if not exist portfolio_site mkdir portfolio_site"}}

    {{"step": "OBSERVE", "content": "The portfolio_site directory has been created."}}

    {{"step": "ACTION", "function": "systemCommands", "input": "if not exist portfolio_site/{state['user_name']} mkdir portfolio_site/{state['user_name']}"}}

    {{"step": "OBSERVE", "content": "The portfolio_site/{state['user_name']} directory has been created."}}

    {{"step": "ACTION", "function": "systemCommands", "input": "echo Creating index.html with structured portfolio layout > portfolio_site/{state['user_name']}/index.html"}}

    {{"step": "OBSERVE", "content": "index.html file created with sections for About, Skills, Experience, Projects, and Contact."}}

    {{"step": "ACTION", "function": "systemCommands", "input": "echo Creating styles.css for styling the portfolio > portfolio_site/{state['user_name']}/styles.css"}}

    {{"step": "OBSERVE", "content": "styles.css file created with modern responsive styling."}}

    {{"step": "ACTION", "function": "systemCommands", "input": "echo Creating script.js for interactivity (optional animations, navigation) > portfolio_site/{state['user_name']}/script.js"}}

    {{"step": "OBSERVE", "content": "script.js file created to enhance user experience with interactivity."}}

    {{"step": "PROCESS", "content": "The portfolio website structure has been generated safely without executing any external code. Resume content is mapped into appropriate sections of the website."}}

    {{"step": "RESULT", "content": "A complete portfolio website has been generated inside the portfolio_site folder, including index.html, styles.css, and script.js, structured using the provided resume content."}}
    
    Resume Content:
    {state["pdf_data"]}
    '''
    
    state["llm_messages"] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    while True:
        response =  client.chat.completions.create(model= "gpt-5.1", response_format= {"type": "json_object"}, messages=state["llm_messages"])
        jsonOp = json.loads(response.choices[0].message.content)
        
        if jsonOp.get("step") == "ACTION":
            func = jsonOp.get("function")
            inputs = jsonOp.get("input")
            print(f"Calling the {func} function")
            tool_map[func](inputs)
            state["llm_messages"].append({"role": "assistant", "content": json.dumps(response.choices[0].message.content )})
            continue
        
        if jsonOp.get("step") == "RESULT":
            print("\n\n Ouput:", jsonOp.get("content"))
            state["llm_messages"].append({"role":"assistant", "content": response.choices[0].message.content})
            state["llm_result"] = response.choices[0].message.content
            break
        state["llm_messages"].append({"role":"assistant", "content": response.choices[0].message.content})
        print(f'         {jsonOp.get("content")}')
    
    return state
# The conditional edges do not update the state

def flow_decide_resume_or_not(state: State) -> Literal["portfolio_from_resume", END]:
    print("🎶 flow_decide_resume_or_not")
    if state["is_resume"]:
        return "portfolio_from_resume"
    return END


# Graph node registry
# creating graph
graph_builder = StateGraph(State)

# registering the nodes
graph_builder.add_node("load_pdf", load_pdf)
graph_builder.add_node("check_if_resume_or_not",check_if_resume_or_not)
graph_builder.add_node("portfolio_from_resume",portfolio_from_resume)
graph_builder.add_node("flow_decide_resume_or_not", flow_decide_resume_or_not)


# Adding edges
graph_builder.add_edge(START, "load_pdf")
graph_builder.add_edge("load_pdf","check_if_resume_or_not")
graph_builder.add_conditional_edges("check_if_resume_or_not", flow_decide_resume_or_not)
graph_builder.add_edge("portfolio_from_resume", END)

# compiling the graph
graph = graph_builder.compile()

if __name__ == "__main__":
    state = {
        "file_path":  "../pdfs/Aniket_Hans_SWE_dev.pdf",
        "pdf_data": "",
        "user_name": "",
        "is_resume": False,
        "llm_result": "",
        "llm_messages": []
    }
    resposne = graph.invoke(state)
    print(response)
