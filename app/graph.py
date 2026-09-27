from langgraph.graph import StateGraph, START, END
from state import AgentState
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from rag import retrive_chunks
from tools import retrieve_from_db

load_dotenv()

llm = ChatOpenAI(
    model = "gpt-4o-mini",
    max_tokens=200
)

# -----------   debug   ---------------
def process_question(state : AgentState):

    question = state['question']
    answer = f"You asked : {question}"

    return{
        "answer": answer
    }
# -----------   debug   ---------------


# Agent node
def agent_node(state : AgentState):

    question = state['question']
    print(question)

    prompt = f"""
    You are the routing agent for a ShopStream customer support system.

    Your job is to determine which capability should handle the user's question.

    Available capabilities:

    1. RAG
    Use RAG when the user asks about information contained in the
    ShopStream knowledge base, such as:
    - Return and refund policies
    - Shipping policies
    - Payment information
    - Product information
    - General ShopStream FAQs

    2. ORDER_LOOKUP
    Use ORDER_LOOKUP when the user asks about a specific order,
    such as:
    - Order status
    - Order tracking
    - Delivery status
    - Information about an order
    The question will normally contain an order ID such as ORD1001.

    3. DIRECT
    Use DIRECT for greetings, casual conversation, or questions
    that do not require the ShopStream knowledge base or an order lookup.

    Return ONLY ONE of these values:
    RAG
    ORDER_LOOKUP
    DIRECT

    Do not provide any explanation.

    User question:
    {question}
    """


    formatted_prompt = prompt.format(
        question=question
    )
    response = llm.invoke(formatted_prompt)

    # use_rag = response.content.upper().strip() == "RAG"
    decision = response.content.upper().strip()
    

    return {
        "decision":decision
    }

# RAG call
def rag_node(state: AgentState):

    result = retrive_chunks(state)

    documents = result["documents"]

    context = "\n\n".join(
        doc.page_content
        for doc in documents
    )

    prompt = f"""
    You are a Shopstream customer support assistant.

    Answer the user's question only using the provided context.

    Don't create your own answers.
    If there's no enough context, tell them that you don't have relevant data to give answer for that.

    Context:
    {context}

    User question:
    {state['question']}

    """
    response = llm.invoke(prompt)
    return {
        "answer": response.content,
        "documents": documents
    }


# LLM KB call
def direct_answer(state: AgentState):

    question = state['question']

    response = llm.invoke(question)

    return {
        "answer": response.content
    }


# conditional agent
def route_question(state: AgentState):

    #`if use_rag == True`
    decision = state['decision']

    if decision == "RAG":
        return "RAG"
    elif decision == "ORDER_LOOKUP":
        return "ORDER_LOOKUP"

    return "DIRECT"




# graph
# --------------------------------------------------------------------------------
builder = StateGraph(AgentState)

# define nodes

builder.add_node("agent_node",agent_node)
builder.add_node("rag_node",rag_node)
builder.add_node("direct_answer", direct_answer)
# app.tools
builder.add_node("retrieve_from_db",retrieve_from_db)


# add edge
builder.add_edge(START,"agent_node")
builder.add_conditional_edges(
    "agent_node",
    route_question,
    {
        "RAG":"rag_node",
        "ORDER_LOOKUP":"retrieve_from_db",
        "DIRECT":"direct_answer"
    }
)

builder.add_edge("rag_node",END)
builder.add_edge("retrieve_from_db",END)
builder.add_edge("direct_answer",END)

# compile graph
graph = builder.compile()
