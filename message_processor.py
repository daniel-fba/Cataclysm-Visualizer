import json
import os
import sys
import codecs
from dotenv import load_dotenv

load_dotenv()
save_directory = os.getenv("SAVE_DIRECTORY")
save_file = ""
file_path = ""
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)

def findSave(save_directory):
    global save_file
    found = False

    for file_name in os.listdir(save_directory):
        if ".sav" in file_name:
            save_file = file_name
            print(f"Save file found: {save_file}")
            found = True
            break
    if not found:
            print("Save file not found")

findSave(save_directory)

if save_file:
    file_path = os.path.join(save_directory, save_file)

    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            save_data = json.load(f)
        
        message_log = save_data.get("player_messages", {}).get("messages", [])
        for message in message_log:
            turn = message.get("turn")
            text = message.get("message")
            print(f"Turn: {turn}, Message: {text}")

    except FileNotFoundError:
        print(f"Error: No file found in {file_path}")
    except json.JSONDecodeError:
        print("Error: The file is not a valid JSON.")
else:
    print("No save file was found.")