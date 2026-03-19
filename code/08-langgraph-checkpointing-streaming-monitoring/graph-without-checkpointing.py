from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langgraph.graph import START, StateGraph, END


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


# This is an abstraction layer above the llm creation
llm = init_chat_model(model_provider="openai", model="gpt-4.1-mini")


def chat_node(state: State):
    response = llm.invoke(state["messages"])
    # This will append the response into the state and not overwrite it
    return {"messages": [response]}


graph_builder = StateGraph(State)
graph_builder.add_node("chat_node", chat_node)

# Adding edges
graph_builder.add_edge(START, "chat_node")
graph_builder.add_edge("chat_node", END)

# compiling the graph
graph = graph_builder.compile()

if __name__ == "__main__":
    user_query = input(">")

    # A state is created
    state = {
        "messages": [{"role": "user", "content": user_query}]
    }

    respose = graph.invoke(state)
    # The state is deleted after the invocation of the graph

    print(respose)
