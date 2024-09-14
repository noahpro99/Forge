import argparse
import socket
import subprocess
import time

import bpy
import speech_recognition as sr
from dotenv import load_dotenv
from openai import OpenAI

HOST = "localhost"
PORT = 8081


def get_ai_response(client: OpenAI, query: str) -> str | None:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""
Give a ready to run blender script that does what the user asked for:
{query}
Assume the script will be run in a live console immediately.
Enclose the script in a code block like so:
```python
import bpy
bpy.ops.object.select_all(action='DESELECT')
```
""",
            }
        ],
        model="gpt-3.5-turbo",
    )
    res = chat_completion.choices[0].message.content
    return res


def extract_bpy_script(response: str) -> str:
    """Collect all code snippets from the response and return them as a single string.

    Args:
        response (str): The user response containing code snippets.

    Returns:
        str: The extracted code snippets.
    """
    # Initialize an empty list to store the code snippets
    code_snippets = []
    # A flag to track when inside a code block
    inside_code_block = False

    # Loop through each line of the response
    for line in response.split("\n"):
        # Check if a line starts a code block
        if line.strip().startswith("```python"):
            inside_code_block = True
            code_snippets.append("")
        # Check if a line ends a code block
        elif line.strip().startswith("```") and inside_code_block:
            inside_code_block = False
        # If inside a code block, append the line
        elif inside_code_block:
            code_snippets[-1] += line + "\n"

    # Join all code snippets into a single string
    return "\n".join(code_snippets)


def send_script(script):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.sendall(script.encode("utf-8"))
    client_socket.close()


def takeCommand() -> str | None:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-in")  # type: ignore
        print(f"User said: {query}\n")
    except Exception as e:
        print(e)
        print("Unable to Recognize your voice.")
        return None

    return query


def edit_loop(blender_path: str):
    bpy.app.binary_path = blender_path  # type: ignore
    load_dotenv()
    client = OpenAI()

    subprocess.Popen(
        [
            "powershell.exe",
            "-Command",
            "& 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe' --python src\\blender_server.py",
        ]
    )
    time.sleep(5)

    while True:
        query = takeCommand()
        if query is None:
            continue
        if not query.lower().startswith("hey blender"):
            continue

        response = get_ai_response(client, query)
        if response is None:
            print("No response from AI")
            continue

        script = extract_bpy_script(response)
        print(script)
        send_script(script)
        time.sleep(2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--blender-path",
        type=str,
        help="Path to the Blender executable",
        default=r"C:\Program Files (x86)\Steam\steamapps\common\Blender",
    )
    args = parser.parse_args()

    edit_loop(args.blender_path)


if __name__ == "__main__":
    main()
