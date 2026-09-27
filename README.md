# ShopStream Agentic AI Support System

An Agentic AI customer support system built with **LangGraph, LangChain, OpenAI, ChromaDB, and SQLite**.

The system uses an LLM-based agent to decide how each customer question should be handled. Depending on the question, it can retrieve information from a knowledge base using RAG, look up order information from SQLite, or answer directly.

---

## Features

* LLM-based request routing
* Retrieval-Augmented Generation (RAG)
* Semantic search using ChromaDB
* OpenAI embeddings
* Structured order lookup using SQLite
* Direct LLM responses for general questions
* LangGraph-based orchestration
* Gradio chat interface
* Persistent Chroma vector store
* Modular architecture for adding future tools

---

## Architecture

                         User
                           │
                           ▼
                     ┌───────────┐
                     │   Agent   │
                     │  (LLM)    │
                     └─────┬─────┘
                           │
                     What should I do?
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
           RAG       ORDER_LOOKUP      DIRECT
             │             │             │
             ▼             ▼             ▼
          ChromaDB       SQLite          LLM
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                         Answer
                           │
                           ▼
                         Gradio

---

## Project Structure

```text
My-Agentic_AI-App/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── graph.py
│   ├── state.py
│   ├── tools.py
│   └── rag.py
│
├── data/
│   ├── knowledge.txt
│    
│
|──db/
|  ├──shopstream.db
|  
├── chroma_db/
│
├── tests/
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

# How the System Works

## 1. User sends a question

Example:

```text
Where is my order ORD1001?
```

The question enters the LangGraph workflow.

---

## 2. Agent decides what capability is required

The `agent_node` analyzes the question and returns one of:

```text
RAG
ORDER_LOOKUP
DIRECT
```

### RAG

Used for questions about ShopStream knowledge.

Examples:

```text
What is the return policy?

How long does shipping take?

Can I get a refund?

What payment methods are supported?
```

### ORDER_LOOKUP

Used when the user asks about a specific order.

Examples:

```text
Where is my order ORD1001?

What is the status of ORD1003?

Tell me about order ORD1002.
```

### DIRECT

Used for general conversation.

Examples:

```text
Hello

What can you do?

Thanks!
```

---

# RAG Pipeline

The RAG component handles unstructured knowledge.

```text
User Question
      │
      ▼
    Agent
      │
      ▼
     RAG
      │
      ▼
Query Embedding
      │
      ▼
   ChromaDB
      │
      ▼
Top-K Documents
      │
      ▼
   Context
      │
      ▼
  OpenAI LLM
      │
      ▼
    Answer
```

## Knowledge Sources

The RAG system can work with documents such as:

* HTML
* PDF
* CSV
* JSON
* TXT

The documents are loaded and split into chunks before being stored in ChromaDB.

Current chunking configuration:

```python
chunk_size = 500
chunk_overlap = 50
```

---

# Order Lookup Pipeline

Order-related questions use structured data instead of semantic search.

```text
User Question
      │
      ▼
    Agent
      │
      ▼
  ORDER_LOOKUP
      │
      ▼
Extract Order ID
      │
      ▼
    SQLite
      │
      ▼
 orders table
      │
      ▼
 Order Information
      │
      ▼
    Answer
```

Example:

```text
User:
Where is my order ORD1001?

Agent:
ORDER_LOOKUP

SQLite:
ORD1001 → Wireless Headphones → Shipped

Response:
Order ORD1001 for Wireless Headphones is currently Shipped.
```

The current implementation extracts order IDs using a regular expression:

```python
r"ORD\d+"
```

This is intentionally simple. Later, this can be replaced or extended with LLM tool calling.

---

# SQLite Database

The project uses SQLite for structured order information.

Database:

```text
data/shopstream.db
```

Table:

```sql
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    product TEXT NOT NULL,
    status TEXT NOT NULL
);
```

Example records:

```text
ORD1001 | Arun Kumar   | Wireless Headphones | Shipped
ORD1002 | Priya Sharma | Smart Watch         | Delivered
ORD1003 | Rahul Kumar  | Laptop Backpack     | Processing
ORD1004 | Sneha Raj    | Bluetooth Speaker   | Out for Delivery
ORD1005 | Vikram Singh | Mechanical Keyboard | Cancelled
```

## Database Seeding

Database seeding means inserting initial/sample records into the database.

For example:

```sql
INSERT INTO orders
(order_id, customer_name, product, status)
VALUES
('ORD1001', 'Arun Kumar', 'Wireless Headphones', 'Shipped');
```

This allows the application to immediately test order lookup functionality.

---

# LangGraph Workflow

The graph is structured around conditional routing.

```text
START
  │
  ▼
agent_node
  │
  ├──────── RAG ──────────────► rag_node ──────────► END
  │
  ├──────── ORDER_LOOKUP ─────► retrieve_from_db ──► END
  │
  └──────── DIRECT ───────────► direct_answer ─────► END
```

The routing function validates the agent's decision before selecting the next node.

---

# State

The LangGraph state contains the information passed between nodes.

Conceptually:

```python
class AgentState(TypedDict):
    question: str
    answer: str
    decision: str
    documents: list
    order: dict
```

Example:

```python
{
    "question": "Where is my order ORD1001?",
    "answer": "",
    "decision": "ORDER_LOOKUP",
    "documents": [],
    "order": {}
}
```

After the database node:

```python
{
    "question": "Where is my order ORD1001?",
    "answer": "Order ORD1001 for Wireless Headphones is currently Shipped.",
    "decision": "ORDER_LOOKUP",
    "documents": [],
    "order": {
        "order_id": "ORD1001",
        "customer_name": "Arun Kumar",
        "product": "Wireless Headphones",
        "status": "Shipped"
    }
}
```

---

# Technologies

| Technology    | Purpose                   |
| ------------- | ------------------------- |
| Python        | Application development   |
| LangGraph     | Agent orchestration       |
| LangChain     | LLM and RAG integration   |
| OpenAI        | LLM and embeddings        |
| ChromaDB      | Vector database           |
| SQLite        | Structured order database |
| Gradio        | Chat interface            |
| python-dotenv | Environment configuration |

---

# Installation

## 1. Clone the project

```bash
git clone <your-repository-url>
cd My-Agentic_AI-App
```

---

## 2. Create a virtual environment

Windows:

```powershell
python -m venv .myagenticai(you can use your own name)
```

Activate it:

```powershell
.<your_venv_folder_name>\Scripts\activate
ex: .myagenticai\Scripts\activate
```

---

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

If dependencies have not yet been added to `requirements.txt`, install:

```powershell
pip install langgraph langchain langchain-openai langchain-chroma python-dotenv gradio
```

---

# Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key

LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=shopstream_knowledge

SQLITE_DB_PATH=./data/shopstream.db
```

Never commit your real API key.

Add `.env` to `.gitignore`:

```text
.env
.myagenticai/
__pycache__/
chroma_db/
*.pyc
```

---

# Running the Application

From the project root:

```powershell
python app/main.py
```

Gradio will start locally:

```text
http://127.0.0.1:7860
```

Open the URL in your browser.

---

# Example Questions

## RAG Questions

```text
What is the return policy?

How long does shipping take?

What payment methods are supported?

Can I get a refund?
```

## Order Questions

```text
Where is my order ORD1001?

What is the status of ORD1002?

Tell me about ORD1003.

Where is ORD9999?
```

## Direct Questions

```text
Hello

What can you do?

Thanks for your help.
```

---

# Example Output

### RAG

```text
User:
What is the return policy?

Agent:
RAG

Answer:
Customers can request a return for eligible products within
7 days of delivery.
```

### Order Lookup

```text
User:
Where is my order ORD1001?

Agent:
ORDER_LOOKUP

Database:
ORD1001 → Wireless Headphones → Shipped

Answer:
Order ORD1001 for Wireless Headphones is currently Shipped.
```

### Unknown Order

```text
User:
Where is my order ORD9999?

Agent:
ORDER_LOOKUP

Database:
No matching order

Answer:
I could not find an order with ID ORD9999.
```

---

# Why Use Different Retrieval Methods?

The system deliberately uses different capabilities for different types of information.

### Unstructured information

Policies, FAQs, product descriptions, and general documentation are better suited to:

```text
Embeddings
   ↓
Vector Search
   ↓
  RAG
```

### Structured information

Order information is stored in rows and columns:

```text
order_id
customer_name
product
status
```

For this type of data, a direct SQL query is more appropriate:

```sql
SELECT *
FROM orders
WHERE order_id = ?;
```

This is an important principle in Agentic AI systems:

> The agent should choose the appropriate capability instead of forcing every question through the same retrieval method.

---

# Current Limitations

The current implementation is intentionally simple.

### 1. Routing depends on LLM output

The agent must return exactly:

```text
RAG
ORDER_LOOKUP
DIRECT
```

Unexpected output is treated as an invalid routing decision.

### 2. Order ID extraction uses regex

Currently:

```python
r"ORD\d+"
```

This works for the project's current order ID format but is not a general natural-language entity extraction system.

### 3. Order response is template-based

The database node currently generates a simple response from the retrieved row.

A future version can use an LLM to generate the final response.

### 4. No conversation memory yet

Each request is currently processed independently.

### 5. No advanced agent tool calling yet

The current architecture explicitly routes between capabilities.

Future versions can allow the LLM to select tools and provide their arguments dynamically.

---

# Future Improvements

Planned improvements include:

* LLM tool calling
* More database tools
* Order cancellation tool
* Refund processing tool
* Product search tool
* Hybrid retrieval
* Reranking
* RAGAS evaluation
* Conversation memory
* Agent tracing
* Better error handling
* Multi-agent architecture
* Human escalation
* CrewAI implementation
* LangGraph vs CrewAI comparison
* Automated database seeding
* Automated tests
* Production deployment

---

# Learning Goals

This project is also a practical learning project for understanding Agentic AI.

The main concepts demonstrated are:

```text
LLM
 │
 ├── Decision Making
 │
 ├── Tool Selection
 │
 ├── RAG
 │
 ├── Structured Database Retrieval
 │
 └── Direct Response
```

The project progresses from a simple router to a more capable agentic architecture.

---

# Development Roadmap

```text
[✓] Basic LangGraph setup
        │
[✓] Agent routing
        │
[✓] RAG capability
        │
[✓] ChromaDB retrieval
        │
[✓] SQLite order lookup
        │
[✓] Gradio interface
        │
[ ] LLM tool calling
        │
[ ] Multiple tools
        │
[ ] Tool error handling
        │
[ ] Agent memory
        │
[ ] Evaluation
        │
[ ] Multi-agent workflow
        │
[ ] CrewAI version
```

---

# Project Concept

The main idea is not to build another chatbot that throws every question at an LLM and hopes for the best.

Instead, the system demonstrates an agentic pattern:

                    User
                      │
                      ▼
                   Agent
                      │
             ┌────────┼────────┐
             │        │        │
             ▼        ▼        ▼
            RAG      SQL     Direct
             │        │        │
             └────────┼────────┘
                      │
                      ▼
                    Answer

The **agent decides what action should be performed**, while specialized components perform that action.

This separation makes the system easier to extend with additional tools and workflows.
