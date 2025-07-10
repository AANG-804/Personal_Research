import gradio as gr
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# --- Configuration ---
# Define the available model choices for the dropdown
MODEL_CHOICES = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
# Set a default model. It will try to get it from the environment,
# otherwise it will fall back to the first item in the list.
DEFAULT_MODEL = os.environ.get("OPENAI_MODEL_NAME", MODEL_CHOICES[0])

# --- LangChain Implementation ---

def create_chain(temperature, basemodel):
    """
    Creates a LangChain runnable chain.
    This chain takes a user's input, formats it using a prompt template,
    sends it to the specified OpenAI model, and parses the output as a string.
    """
    # The prompt template defines the structure of the input to the model.
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant that provides detailed and accurate responses."),
        ("human", "{input}")
    ])

    # Initialize the ChatOpenAI model with the specified parameters.
    # Streaming is enabled to get real-time responses.
    model = ChatOpenAI(
        temperature=temperature,
        model=basemodel,
        streaming=True
    )

    # Define the chain of operations using LangChain Expression Language (LCEL)
    chain = (
        {"input": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )
    return chain

# --- Gradio Chatbot Function ---

def respond(message, temperature, basemodel, history):
    """
    This is the core function that powers the Gradio chat interface.
    It receives the user's message and the current state of the UI,
    and yields updates back to the chatbot.
    """
    # Append the new user message to the history.
    # The history is a list of dictionaries in the OpenAI message format.
    history.append({"role": "user", "content": message})
    
    # Add a placeholder for the assistant's response.
    # This will be updated chunk by chunk.
    history.append({"role": "assistant", "content": ""})

    # Create the LangChain chain
    chain = create_chain(temperature, basemodel)
    
    full_response = ""
    # Stream the response from the model
    for chunk in chain.stream(message):
        full_response += chunk
        # Update the content of the last message (the assistant's placeholder)
        history[-1]['content'] = full_response + "▌" # Use a cursor to indicate streaming
        # Yield the updated history to the chatbot and an empty string to the textbox
        yield "", history
    
    # Final update to remove the streaming cursor
    history[-1]['content'] = full_response
    yield "", history


# --- Gradio Interface Definition ---

with gr.Blocks(theme=gr.themes.Default(primary_hue="blue"), title="LLM Interface") as demo:
    gr.Markdown("# LLM Interface (LangChain & Gradio)")
    gr.Markdown("A simple interface to interact with OpenAI models via LangChain.")

    with gr.Row():
        # The main chatbot display area
        # The `type="messages"` argument is crucial to fix the UserWarning.
        # It makes the chatbot expect data in the OpenAI format:
        # [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        chatbot = gr.Chatbot(
            height=600,
            type="messages",
            label="Chatbot",
            avatar_images=(None, "https://placehold.co/100x100/f0f0f0/000000?text=🤖")
        )

        # The column for controls
        with gr.Column(scale=1):
            temperature = gr.Slider(
                minimum=0.0,
                maximum=2.0,
                value=0.7,
                step=0.05,
                label="Temperature",
                info="Controls randomness. Higher values mean more creative responses."
            )
            basemodel = gr.Dropdown(
                choices=MODEL_CHOICES,
                value=DEFAULT_MODEL if DEFAULT_MODEL in MODEL_CHOICES else MODEL_CHOICES[0],
                label="Base Model",
                info="Select the OpenAI model to use."
            )

    # The user input area
    with gr.Row():
        msg = gr.Textbox(
            show_label=False,
            placeholder="Enter your message and press Enter",
            container=False,
            scale=8
        )
        submit = gr.Button("Send", variant="primary", scale=1)

    # --- Event Handling ---
    # Define the inputs and outputs for the `respond` function
    inputs = [msg, temperature, basemodel, chatbot]
    outputs = [msg, chatbot]

    # Link the submit button and textbox submission to the `respond` function
    submit.click(respond, inputs, outputs)
    msg.submit(respond, inputs, outputs)


if __name__ == "__main__":
    # To use, make sure you have an OPENAI_API_KEY environment variable set.
    # You can set it in a .env file in the same directory.
    # Example .env file:
    # OPENAI_API_KEY="sk-..."
    
    demo.launch()

