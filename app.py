import streamlit as st
import openai
import anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI and Anthropic API keys
openai_api_key = st.secrets.get("OPENAI_API_KEY")
anthropic_api_key = st.secrets.get("ANTHROPIC_API_KEY")

# Initialize clients
if openai_api_key:
    openai_client = openai.OpenAI(api_key=openai_api_key)
if anthropic_api_key:
    anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)

# App title
st.title("AI Chat Interface")

# Initialize session state for messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Model configurations
openai_models = {
    "OpenAI: GPT-4o": "gpt-4o",
    "OpenAI: o4-mini": "o4-mini",
    "OpenAI: GPT-4o Search": "gpt-4o-search-preview-2025-03-11",
}

claude_models = {
    "Claude: 3.7 Sonnet": "claude-3-7-sonnet-20250219",  # Latest Claude model as of April 2025
    "Claude: 3.5 Sonnet": "claude-3-5-sonnet-20241022",

}

# Combine models for display but keep provider information
all_models = {**openai_models, **claude_models}

# Sidebar for model selection and parameters
with st.sidebar:
    st.header("Configuration")
    
    # Model selection with provider information
    selected_model_name = st.selectbox("Select Model", list(all_models.keys()))
    selected_model = all_models[selected_model_name]
    
    # Determine which provider is being used
    is_openai_model = selected_model_name.startswith("OpenAI:")
    is_claude_model = selected_model_name.startswith("Claude:")
    
    # Model parameters
    st.subheader("Model Parameters")
    
    # Checkbox to enable/disable temperature
    use_temperature = st.checkbox("Use Temperature", value=True)
    
    # Temperature slider (shown regardless of checkbox state)
    temperature = st.slider(
        "Temperature", 
        min_value=0.0, 
        max_value=2.0, 
        value=0.7, 
        step=0.1,
        disabled=not use_temperature
    )
    
    # Max tokens parameter (works for both providers)
    max_tokens = st.number_input("Max Tokens", min_value=100, max_value=4096, value=1024, step=100)
    
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
        if is_openai_model and openai_api_key:
            # Format messages for OpenAI
            openai_messages = [{"role": "system", "content": system_prompt}]
            for msg in messages:
                openai_messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Base parameters for OpenAI
            params = {
                "model": selected_model,
                "messages": openai_messages,
                "max_tokens": max_tokens,
            }
            
            # Add temperature if enabled
            if use_temperature:
                params["temperature"] = temperature
                
            # Make OpenAI API call
            response = openai_client.chat.completions.create(**params)
            return response.choices[0].message.content
            
        elif is_claude_model and anthropic_api_key:
            # Format messages for Claude - system prompt is a separate parameter
            claude_messages = []
            
            # Add user and assistant messages
            for msg in messages:
                if msg["role"] in ["user", "assistant"]:
                    claude_messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Base parameters for Claude
            params = {
                "model": selected_model,
                "messages": claude_messages,
                "system": system_prompt,  # System prompt as a separate parameter
                "max_tokens": max_tokens,
            }
            
            # Add temperature if enabled
            if use_temperature:
                params["temperature"] = temperature
            
            # Make Claude API call
            response = anthropic_client.messages.create(**params)
            return response.content[0].text
            
        else:
            return "Error: API key not found for the selected model provider."
            
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
        if (is_openai_model and not openai_api_key) or (is_claude_model and not anthropic_api_key):
            st.error(f"API key missing for selected model provider.")
        else:
            with st.spinner("Thinking..."):
                response = generate_response(st.session_state.messages)
                st.write(response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})

# Display API key warnings if not set
if not openai_api_key and not anthropic_api_key:
    st.warning("Please set your OpenAI API key and/or Anthropic API key in the secrets to use this application.")
elif not openai_api_key:
    st.info("OpenAI API key not set. Only Claude models will be available.")
elif not anthropic_api_key:
    st.info("Anthropic API key not set. Only OpenAI models will be available.")
