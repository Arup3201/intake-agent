import os
import streamlit as st
import pandas as pd
from openai import OpenAI

with open(".env", "r") as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])


if "chats" not in st.session_state:
    st.session_state.chats = []  # List to store chat names

if "show_textbox" not in st.session_state:
    st.session_state.show_textbox = False  # To toggle the textbox visibility

# Function to load data from uploaded Excel file
@st.cache_data
def load_excel(file):
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

agent_id = None

def update_agent(file):
    from .prompt_templates import intake_prompt
    
    # Create a file in openai
    file = client.files.create(
        file=file,
        purpose="assistants"
    )
    
    # Create a vector store from file in openai
    vector_store = client.beta.vector_stores.create(
                    name="Enegma Products", 
                    file_ids=[file.id]
                )
    
    if not agent_id:
        # Create the agent with the vector store
        agent = client.beta.assistants.create(
                        name="Intake Agent",
                        instructions=intake_prompt,
                        model="gpt-4o-mini",
                        tools="file_search", 
                        tool_resources={
                            "file_search": {
                                "vector_store_ids": [vector_store.id]
                            }
                        }
                    )
        agent_id = agent["id"]
    else:
        # Update the agent with new vector store
        client.beta.assistants.update(
                        assistant_id=agent_id, 
                        tool_resources={
                                "file_search": {
                                    "vector_store_ids": [vector_store.id]
                                }
                            }
                    )


def add_new_chat(chat_name):
    thread = client.beta.threads.create()
    chat_info = {
        "Id": thread.id, 
        "Name": chat_name, 
        "Messages": []
    }
    
    st.session_state.chats.append(chat_info)
    st.session_state.show_textbox = False


def send_message(chat, message):
    thread_id = chat["Id"]
    # Create a message in the thread
    client.beta.threads.messages.create(
                        thread_id,
                        role="user",
                        content=message,
                    )
    # Run the assistant to get response to the message
    client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=agent_id
        )
    
    # Retreive the last message which is the AI response
    messages = client.beta.threads.messages.list(
                thread_id=thread_id
            )
    ai_response = messages[-1]
    filter(lambda x: x["Id"]==chat["Id"], st.session_state.chats)


# Function to display chat details
def display_chat(chat):
    st.subheader(f"{chat['Name']} Chat Box")
    for i, msg in enumerate(chat["Messages"]):
        st.write(f"{"Me" if i%2 else "Bot"}: {msg}")
        
    # Message box to send a new message
    new_message = st.text_input("Type your message here...")
    if st.button("Send"):
        send_message(chat, new_message)

# Streamlit App Layout
st.set_page_config(layout="wide")
st.title("Chat Application")

# Layout with two columns
left_col, right_col = st.columns(2)

# Left column - Upload button and chat list
with left_col:
    file = st.file_uploader("Upload enegma products .xlsx file", type="xlsx")
    st.subheader("Chats")

    selected_chat = None

    if file:
        update_agent(file)
            
    for i, chat in enumerate(st.session_state.chats):
        if st.button(chat["Name"]):
            selected_chat = chat

    if st.button("Add New Chat"):
        st.session_state.show_textbox = True
    
# Right column - Chat details
with right_col:
    if st.session_state.show_textbox:
        chat_name = st.text_input("Enter chat name")
        add_new_chat(chat_name)
    
    if selected_chat:
        display_chat(selected_chat)
    else:
        st.write("No chat selected. Open a chat from the left column.")
