from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langgraph.graph import START, StateGraph, END
from langgraph.checkpoint.mongodb import MongoDBSaver #for checkpointing in mongodb
from pymongo import MongoClient

load_dotenv()

# TypedDict means a dictionary with fixed keys and types.

class State(TypedDict):
    '''
        Here, messages is a list and add_messages tells LangGraph how to merge updates into this list
        Initial state:
            { "messages": [HumanMessage("Hi")] }
        
        Node returns:
            {"messages": [AIMessage("Hello!")]}
            
        Final state becomes:
            {
                "messages": [
                    HumanMessage("Hi"),
                    AIMessage("Hello!")
                ]
            }
        
        Without add messages, the node output would overwrite the entire list
        
        Why LangGraph Uses Annotated:
            - Annotated lets you attach metadata / behavior to a type.
            - Annotated[type, behavior]
                - Here: type = list, behavior = add_messages
    '''
    messages: Annotated[list, add_messages] 
    
llm = init_chat_model(model_provider="openai", model="gpt-4.1-mini") # This is an abstraction layer above the llm creation
# Connect to your MongoDB cluster
client = MongoClient("mongodb://admin:admin@mongodb:27017")



def chat_node(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]} # This will append the response into the state and not overwrite it

graph_builder = StateGraph(State)
graph_builder.add_node("chat_node", chat_node)

# Adding edges
graph_builder.add_edge(START, "chat_node")
graph_builder.add_edge("chat_node", END)

# compiling the graph with checkpointer

def getGraphWithCheckpointer(checkpointer):
    graph = graph_builder.compile(checkpointer=checkpointer)
    return graph

if __name__ == "__main__":
    user_query = input(">")
    DB_URI = "mongodb://admin:admin@mongodb:27017"
    with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
        # Initialize the MongoDB checkpointer
        checkpointer = MongoDBSaver(client)
        state = {
            "messages":[{"role": "user", "content": user_query}]
        }
        config = {
            "configurable":{
                "thread_id": "1"
            }
        }
        graph_with_checkpointer = getGraphWithCheckpointer(checkpointer)
        # response = graph_with_checkpointer.invoke(state, config)
        # for message in response["messages"]:
        #     print(message.content)

        #streaming
        for event in graph_with_checkpointer.stream(state, config):
            print("Event", event)