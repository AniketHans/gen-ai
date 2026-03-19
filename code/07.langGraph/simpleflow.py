from typing_extensions import TypedDict
from openai import OpenAI
from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END


load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

class State(TypedDict):
    user_query: str
    llm_result: str | None
    
# Defining nodes
def process_user_query(state:State):
    SYSTEM_PROMPT = """
        You are an agent which helps user in his day to day tasks
    """
    
    messages = [
        {"role":"system", "content": SYSTEM_PROMPT}, 
        {"role":"user","content": state["user_query"]}
    ]
    
    response = client.chat.completions.create(model= "gpt-4.1-nano", messages=messages)
    state["llm_result"] = response.choices[0].message.content
    return state


# Build workflow
graph_builder = StateGraph(State)

# Add nodes
graph_builder.add_node("process_user_query", process_user_query)

# Add edges to connect nodes
graph_builder.add_edge(START, "process_user_query")
graph_builder.add_edge("process_user_query", END)

# Compile the agent
graph = graph_builder.compile()

if __name__=="__main__":
    path = "../../images/generated_langgraphs"
    os.makedirs(path, exist_ok=True)
    png = graph.get_graph(xray=True).draw_mermaid_png()
    with open(f"{path}/simplegraph.png","wb") as f:
        f.write(png)
    
    user_query = input("> ")
    _state = {
        "user_query": user_query,
        "llm_result": None
    }
    
    resposeState = graph.invoke(_state)
    print(resposeState)