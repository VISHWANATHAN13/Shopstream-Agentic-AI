import gradio as gr

from graph import graph


def chat(message, history):
    state = {
        "question": message,
        "answer": "",
        "use_rag": False,
        "documents": []
    }

    result = graph.invoke(state)

    return result["answer"]


demo = gr.ChatInterface(
    fn=chat,
    title="ShopStream AI Support",
    description="Ask questions about ShopStream products, policies, orders, and support.",
    textbox=gr.Textbox(
        placeholder="Ask your question...",
        container=True
    ),
)


# if __name__ == "__main__":
#     demo.launch()
