from typing import TypedDict
from langchain_core.documents import Document

class AgentState(TypedDict):
    question : str
    answer : str
    decision : str
    documents : list[Document]
    order : dict