from typing_extensions import TypedDict
from openai import OpenAI
from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from typing import Literal
from pydantic import BaseModel


load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

# Models
class MessageState(TypedDict):
    user_query: str
    llm_result: str | None
    is_coding_query: bool
    code_accuracy: str | None
    fix_accuracy_retries: int
    

class CodingCheck(BaseModel):
    is_coding_query: bool

class CodeAccuracy(BaseModel):
    code_accuracy: str

# Defining Nodes

def classify_query(state: MessageState):
    print("🎶 classify_query")
    SYSTEM_PROMPT = """
        You are an agent which tells whether a query is a coding related query or not
    """
    
    messages = [
        {"role":"system", "content": SYSTEM_PROMPT}, 
        {"role":"user","content": state["user_query"]}
    ]
    
    response = client.chat.completions.parse(model= "gpt-4.1-nano", messages=messages, response_format=CodingCheck)
    state["is_coding_query"] = response.choices[0].message.parsed.is_coding_query
    return state

def general_query(state: MessageState):
    print("🎶 general_query")
    SYSTEM_PROMPT = """
        You are an agent which helps user in his day to day tasks
    """
    
    messages = [
        {"role":"system", "content": SYSTEM_PROMPT}, 
        {"role":"user","content": state["user_query"]}
    ]
    
    response = client.chat.completions.create(model= "gpt-4.1-mini", messages=messages)
    state["llm_result"] = response.choices[0].message.content
    return state

def coding_query(state: MessageState):
    print("🎶 coding_query")
    SYSTEM_PROMPT = """
        You are an agent which helps user writing code according to his query
    """
    
    messages = [
        {"role":"system", "content": SYSTEM_PROMPT}, 
        {"role":"user","content": state["user_query"]}
    ]
    
    response = client.chat.completions.create(model= "gpt-4.1", messages=messages)
    state["llm_result"] = response.choices[0].message.content
    return state

def code_accuracy_check(state: MessageState):
    print("🎶 code_accuracy_check")
    SYSTEM_PROMPT = f"""
        You are an agent which checks the accuracy percentage of the code asked by used in his query
        
        user_query: {state['user_query']}
        code: {state['llm_result']}
    """
    
    messages = [
        {"role":"system", "content": SYSTEM_PROMPT}, 
        {"role":"user","content": state["user_query"]}
    ]
    
    response = client.chat.completions.parse(model= "gpt-4.1", messages=messages, response_format=CodeAccuracy)
    state["code_accuracy"] = response.choices[0].message.parsed.code_accuracy
    return state

def flow_decide_general_or_code(state: MessageState) -> Literal["general_query","coding_query"]:
    print("🎶 flow_decide_general_or_code")
    if state["is_coding_query"]:
        return "coding_query"
    return "general_query"

# creating graph
graph_builder = StateGraph(MessageState)

# registering the nodes
graph_builder.add_node("classify_query", classify_query)
graph_builder.add_node("general_query",general_query)
graph_builder.add_node("coding_query",coding_query)
graph_builder.add_node("code_accuracy_check",code_accuracy_check)
graph_builder.add_node("flow_decide_general_or_code", flow_decide_general_or_code)

# Adding edges
graph_builder.add_edge(START, "classify_query")
graph_builder.add_conditional_edges("classify_query", flow_decide_general_or_code)
graph_builder.add_edge("general_query",END)
graph_builder.add_edge("coding_query", "code_accuracy_check")
graph_builder.add_edge("code_accuracy_check", END)

# compiling the graph
graph = graph_builder.compile()


if __name__=="__main__":
    path = "../../images/generated_langgraphs"
    os.makedirs(path, exist_ok=True)
    png = graph.get_graph(xray=True).draw_mermaid_png()
    with open(f"{path}/multi-agent-flow.png","wb") as f:
        f.write(png)
    
    user_query = input("> ")
    _state = {
        "user_query": user_query,
        "llm_result": None,
        "is_coding_query": False,
        "code_accuracy": None,
        "fix_accuracy_retries": 0
        
    }
    
    resposeState = graph.invoke(_state)
    print(resposeState)

