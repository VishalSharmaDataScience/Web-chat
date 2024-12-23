# app/interaction.py
import requests
import json
from cache import Cache

cache = Cache()

def query_ollama(model_name, prompt):
    """Query the locally running Ollama server and handle streaming JSON responses."""
    try:
        url = f"http://localhost:11434/api/generate"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": model_name,
            "prompt": prompt
        }

        # Send the request with stream=True to handle streaming
        response = requests.post(url, json=payload, headers=headers, stream=True)

        # Handle streaming response
        complete_response = ""
        for line in response.iter_lines():
            if line:  # Avoid empty lines
                try:
                    # Parse the JSON line
                    json_line = json.loads(line)
                    # Append the partial response
                    complete_response += json_line.get("response", "")
                    # Stop when "done" is True
                    if json_line.get("done", False):
                        break
                except json.JSONDecodeError as e:
                    print(f"Error decoding line: {line} - {e}")

        return complete_response.strip()
    except Exception as e:
        return f"Error querying Ollama: {str(e)}"


def generate_response(user_input, context, chat_history, website_url):
    """Generates a conversational response using Mistral via Ollama."""
    model_name = "mistral"

    # Check if context is empty
    if not context.strip():
        return "I'm unable to find relevant information from the provided URL. Could you clarify or provide more details?"

    # Prepare the conversation history and context
    history = "\n".join([f"Human: {chat['user']}\nAI: {chat['bot']}" for chat in chat_history])
    prompt = f"""
    The user is asking a question about the content of the file hosted at the following URL: {website_url}.
    Below is the context retrieved from the URL:
    {context}
    
 

    Based on this context, answer the user's question accurately and include the source of the information:
    Human: {user_input}
    AI:
    """

    # Query Mistral via Ollama
    response = query_ollama(model_name, prompt)

    # Add source to response
    return f"{response}\n\n**Source**: {website_url}"

