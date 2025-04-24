import streamlit as st
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# App title
st.title("OpenAI Chat Interface")

# Initialize session state for messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Models configuration
models = [
    "gpt-4o",
    "o4-mini",
]

# Sidebar for model selection and parameters
with st.sidebar:
    st.header("Configuration")
    
    # Model selection
    selected_model = st.selectbox("Select Model", models)
    
    # Model parameters
    st.subheader("Model Parameters")
    temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1)
    max_tokens = st.number_input("Max Tokens", min_value=100, max_value=8000, value=1000, step=100)
    top_p = st.slider("Top P", min_value=0.0, max_value=1.0, value=1.0, step=0.05)
    frequency_penalty = st.slider("Frequency Penalty", min_value=-2.0, max_value=2.0, value=0.0, step=0.1)
    presence_penalty = st.slider("Presence Penalty", min_value=-2.0, max_value=2.0, value=0.0, step=0.1)
    
    # System prompt
    st.subheader("System Prompt")
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = "You are a helpful, creative, and friendly assistant."
    
    system_prompt = st.text_area("System Message", st.session_state.system_prompt, height=150)
    st.session_state.system_prompt = system_prompt
    
    # Button to clear chat history
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.success("Conversation cleared!")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function to generate response
def generate_response(messages):
    try:
        response = openai.chat.completions.create(
            model=selected_model,
            messages=[{"role": "system", "content": system_prompt}] + messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Chat input
if prompt := st.chat_input("What would you like to discuss?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(st.session_state.messages)
            st.write(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display API key warning if not set
if not os.getenv("OPENAI_API_KEY"):
    st.warning("Please set your OpenAI API key in the .env file to use this application.") 
