# app/ui.py
import streamlit as st
from utils import simulate_human_interaction,check_website_exists
from interaction import generate_response
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()
BING_API_KEY = os.getenv("BING_API_KEY")


# Load external CSS
def load_css(file_path):

    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_ui():
    
    """
    Renders the user interface for the "Chat with Websites" application.

    This function sets up the page configuration, loads custom CSS,
    and constructs the main UI components, including the title, input
    section for the website URL, a sidebar for settings, and the main
    chat interface. It also manages the chat history session state
    and handles user input for querying and generating responses.

    The main UI components include:
    - A page title and icon.
    - An input field for the website URL.
    - A sidebar for future widgets.
    - A chat interface that displays chat history and allows for user input.
    """

    # Page config
    st.set_page_config(page_title="SproutsAI - Chat with Websites", page_icon="🤖", layout="wide")

    # Load custom CSS
    load_css("app/styles.css")

    # Title section
    st.markdown("<h1 class='title'>🤖 Chat with Websites</h1>", unsafe_allow_html=True)

    # Input section for URL
    st.markdown("<div class='input-section'><b>Enter the Website URL Below:</b></div>", unsafe_allow_html=True)
    website_url = st.text_input(
        "Website URL",
        placeholder="Enter the website URL here",
        key="url_input",
        label_visibility="collapsed"
    )

    if not website_url:
        st.info("🛈 Please enter a website URL to start chatting.")
    else:
        # Validate if the website exists
        website_exists, message = check_website_exists(website_url)
        if not website_exists:
            st.error(message)
            return
        st.success(message)

        # Initialize session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Chat input
        user_input = st.chat_input("💬 Type your message here...")
        if user_input:
            # Query Bing Search
            context = simulate_human_interaction(website_url, user_input)

            if not context.strip():
                st.error("Unable to retrieve meaningful content. Try refining your query or checking the URL.")
                return


            # Generate response
            response = generate_response(user_input, context, st.session_state.chat_history, website_url)

            # Update session history
            st.session_state.chat_history.append({"user": user_input, "bot": response})

        # Display chat history
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        for chat in st.session_state.chat_history:
            with st.chat_message("Human"):
                st.write(f"💬 **You:** {chat['user']}")
            with st.chat_message("AI"):
                st.write(f"🤖 **Bot:** {chat['bot']}")
        st.markdown("</div>", unsafe_allow_html=True)


render_ui()