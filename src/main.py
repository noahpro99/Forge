import argparse
import json
import os
import socket
import subprocess
import threading
import time
import winsound

import bpy
import speech_recognition as sr
from dotenv import load_dotenv
from openai import OpenAI

from get_response import get_ai_response

HOST = "localhost"
PORT = 8081
SCENE_INFO_FILE = (
    r"C:\\Users\noahp\tmp\scene_info.json"  # Path to the scene information file
)
PHOTO_FILE = r"C:\\Users\noahp\tmp\image.png"  # Path to the photo file
AUDIO_FILE = r"C:\\Users\noahp\tmp\audio.wav"  # Path to the audio file
ENTRY_SOUND_PATH = r"sounds\entry.wav"
EXIT_SOUND_PATH = r"sounds\exit.wav"


def extract_bpy_script(response: str) -> str:
    """Collect all code snippets from the response and return them as a single string."""
    code_snippets = []
    inside_code_block = False

    for line in response.split("\n"):
        if line.strip().startswith("```python"):
            inside_code_block = True
            code_snippets.append("")
        elif line.strip().startswith("```") and inside_code_block:
            inside_code_block = False
        elif inside_code_block:
            code_snippets[-1] += line + "\n"

    return "\n".join(code_snippets)


def send_command(command):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(10)  # Set a timeout to prevent indefinite waiting
    try:
        client_socket.connect((HOST, PORT))
        client_socket.sendall(command.encode("utf-8"))
        print(f"Command '{command}' sent to Blender server.")
    except socket.timeout:
        print("Connection timed out. Blender server may not be responding.")
    except Exception as e:
        print(f"Error during socket communication: {e}")
    finally:
        client_socket.close()


def send_script(script):
    send_command(f"run script {script}")

    # Wait a short time to allow Blender to save the scene information
    time.sleep(3)  # Adjust as necessary depending on Blender script execution time

    # Read the scene information from the file
    try:
        with open(SCENE_INFO_FILE, "r") as file:
            scene_info = json.load(file)
            print("Scene information loaded from file:")
            print(scene_info)
    except FileNotFoundError:
        print(f"Scene information file {SCENE_INFO_FILE} not found.")
    except json.JSONDecodeError:
        print(
            "Failed to decode the scene information file. It may be incomplete or corrupted."
        )


def take_photo():
    send_command("take photo")

    # Wait for the photo to be saved
    time.sleep(2)  # Adjust as necessary depending on Blender script execution time

    # Check if the photo file exists
    if not os.path.exists(PHOTO_FILE):
        print(f"Photo file {PHOTO_FILE} not found.")
        return None
    print(f"Photo taken and saved to {PHOTO_FILE}.")
    return PHOTO_FILE


def load_scene_info():
    try:
        with open(SCENE_INFO_FILE, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "{}"  # Return an empty JSON object if no scene info is available


def takeCommand(client: OpenAI) -> str | None:

    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        send_command("fairy listening")

        def play_entry_sound():
            winsound.PlaySound(
                ENTRY_SOUND_PATH,
                winsound.SND_FILENAME,
            )

        # Create a new thread for playing the entry sound
        entry_sound_thread = threading.Thread(target=play_entry_sound)
        entry_sound_thread.start()
        print("Listening...")
        audio = r.listen(source)
        # save to tmp file
        with open(AUDIO_FILE, "wb") as f:
            f.write(audio.get_wav_data())

    send_command("fairy processing")

    try:
        print("Recognizing...")
        # query = r.recognize_google(audio, language="en-in")  # type: ignore
        audio_file = open(AUDIO_FILE, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
        query = transcription.text

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
    # wipe the files
    with open(SCENE_INFO_FILE, "w") as f:
        f.write("{}")

    while True:

        query = takeCommand(client)
        if query is None:
            continue

        keywords = ["forge", "orange", "ford", "force", "fourth", "four", "george"]
        if not any(keyword in query.lower() for keyword in keywords):
            continue

        winsound.PlaySound(
            EXIT_SOUND_PATH,
            winsound.SND_FILENAME,
        )

        # Take a photo of the current scene
        photo_path = take_photo()
        if photo_path is None:
            continue

        scene_info = load_scene_info()
        print("Scene info:")
        print(scene_info)

        response = get_ai_response(client, query, scene_info, photo_path)
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
