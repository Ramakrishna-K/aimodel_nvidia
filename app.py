

import requests
import os
import json
from dotenv import load_dotenv

# -----------------------------------
# LOAD ENV VARIABLES
# -----------------------------------
load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")

# -----------------------------------
# NVIDIA API URL
# -----------------------------------
invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"

# -----------------------------------
# MEMORY FILE
# -----------------------------------
MEMORY_FILE = "memory.json"


# -----------------------------------
# LOAD MEMORY
# -----------------------------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as file:
                return json.load(file)
        except:
            return {}
    return {}


# -----------------------------------
# SAVE MEMORY
# -----------------------------------
def save_memory(memory):
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)


# -----------------------------------
# LOAD USER MEMORY
# -----------------------------------
memory = load_memory()

# -----------------------------------
# ASK NAME FIRST TIME ONLY
# -----------------------------------
if "name" not in memory:

    print("Hello! I'm Meethra.")
    user_name = input("What is your name? ").strip()

    memory["name"] = user_name
    save_memory(memory)

else:
    user_name = memory["name"]

# -----------------------------------
# SYSTEM PROMPT
# -----------------------------------
messages = [
    {
        "role": "system",
        "content": f"""
You are Meethra.

The user's name is {user_name}.

Rules:
- Always reply in English.
- Be friendly and helpful.
- Remember the user's name.
- Address the user by name occasionally.
- Keep responses conversational.
"""
    }
]

# -----------------------------------
# HEADER
# -----------------------------------
print("\n===================================")
print("      MEETHRA AI ASSISTANT")
print("===================================")
print(f"Welcome back, {user_name}!")
print("Type 'exit' to quit.\n")

# -----------------------------------
# CHAT LOOP
# -----------------------------------
while True:

    user_input = input(f"{user_name}: ").strip()

    # -----------------------------------
    # EXIT
    # -----------------------------------
    if user_input.lower() == "exit":
        print(f"\nMeethra: Goodbye {user_name}! 👋")
        break

    # -----------------------------------
    # CHANGE NAME
    # My name is X
    # -----------------------------------
    if user_input.lower().startswith("my name is "):

        new_name = user_input[11:].strip()

        if new_name:

            memory["name"] = new_name
            save_memory(memory)

            user_name = new_name

            messages[0]["content"] = f"""
You are Meethra.

The user's name is {user_name}.

Rules:
- Always reply in English.
- Be friendly and helpful.
- Remember the user's name.
- Address the user by name occasionally.
"""

            print(
                f"\nMeethra: Nice to meet you, {user_name}! I will remember your name.\n"
            )

            continue

    # -----------------------------------
    # CALL ME X
    # -----------------------------------
    if user_input.lower().startswith("call me "):

        new_name = user_input[8:].strip()

        if new_name:

            memory["name"] = new_name
            save_memory(memory)

            user_name = new_name

            messages[0]["content"] = f"""
You are Meethra.

The user's name is {user_name}.

Rules:
- Always reply in English.
- Be friendly and helpful.
- Remember the user's name.
- Address the user by name occasionally.
"""

            print(
                f"\nMeethra: Sure! I'll call you {user_name} from now on.\n"
            )

            continue

    # -----------------------------------
    # SAVE USER MESSAGE
    # -----------------------------------
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # -----------------------------------
    # REQUEST PAYLOAD
    # -----------------------------------
    payload = {
        "model": "meta/llama-3.3-70b-instruct",
        "messages": messages,
        "temperature": 0.7,
        "top_p": 1.0,
        "max_tokens": 1000,
        "stream": True
    }

    # -----------------------------------
    # HEADERS
    # -----------------------------------
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "text/event-stream",
        "Content-Type": "application/json"
    }

    try:

        response = requests.post(
            invoke_url,
            headers=headers,
            json=payload,
            stream=True
        )

        print("\nMeethra: ", end="")

        assistant_reply = ""

        # -----------------------------------
        # STREAM RESPONSE
        # -----------------------------------
        for line in response.iter_lines():

            if not line:
                continue

            decoded_line = line.decode("utf-8")

            if decoded_line.startswith("data: "):
                decoded_line = decoded_line[6:]

            if decoded_line == "[DONE]":
                continue

            try:

                data = json.loads(decoded_line)

                delta = data["choices"][0]["delta"]

                if "content" in delta:

                    content = delta["content"]

                    assistant_reply += content

                    print(content, end="", flush=True)

            except:
                pass

        print("\n")

        # -----------------------------------
        # SAVE ASSISTANT RESPONSE
        # -----------------------------------
        messages.append(
            {
                "role": "assistant",
                "content": assistant_reply
            }
        )

    except Exception as e:
        print("\nError:", e)