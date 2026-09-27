import re
import sqlite3
from state import AgentState
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "shopstream.db"


def retrieve_from_db(state):

    question = state["question"]

    print("\n================ DATABASE DEBUG ================")
    print("Database path:", DB_PATH)
    print("Database exists:", DB_PATH.exists())

    connection = sqlite3.connect(str(DB_PATH))
    cursor = connection.cursor()

    # Check what tables actually exist
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    )

    tables = cursor.fetchall()

    print("Tables:", tables)
    print("================================================\n")

    # Extract order ID from the user's question
    match = re.search(r"ORD\d+", question.upper())

    if not match:
        return {
            "order": {},
            "answer": "Please provide a valid order ID, such as ORD1001."
        }

    order_id = match.group()

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT order_id, customer_name, product, status
        FROM orders
        WHERE order_id = ?
        """,
        (order_id,)
    )

    row = cursor.fetchone()

    connection.close()

    # Order not found
    if row is None:
        return {
            "order": {},
            "answer": f"I could not find an order with ID {order_id}."
        }

    # Convert database row into a dictionary
    order = {
        "order_id": row[0],
        "customer_name": row[1],
        "product": row[2],
        "status": row[3]
    }

    answer = (
        f"Order {order['order_id']} for {order['product']} "
        f"is currently {order['status']}."
    )

    return {
        "order": order,
        "answer": answer
    }
