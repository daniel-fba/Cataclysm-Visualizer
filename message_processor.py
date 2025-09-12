import json
import os
import sys
import codecs
from dotenv import load_dotenv
import re
import os
import time

load_dotenv()
game_directory = ""
save_directory = ""
save_folder = []
save_file = ""
save_path = ""
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
regex = r"<.*?>"

def detect_file_changes(file_to_watch, interval=2):
    if not os.path.exists(file_to_watch):
        print(f"Error: Cannot watch file. Path not found: {file_to_watch}")
        return
    
    print(f"Watching for changes in {file_to_watch}")
    last_modified = os.path.getmtime(file_to_watch)
    while True:
        time.sleep(1)
        current_modified = os.path.getmtime(file_to_watch)
        if current_modified != last_modified:
            print("File has changed! Reprocessing...", flush=True)
            process_save_file(file_to_watch)
            last_modified = current_modified
        time.sleep(interval)

def find_game_directory():
    global game_directory, save_directory

    print("Type where is the game directory: ")
    game_directory = input()
    if not os.path.isdir(game_directory):
        print("Error: Directory not found.")
        return
    
    save_directory = os.path.join(game_directory, "save")
    print(f"Looking for saves in {save_directory}.")
    save_folder.clear()
    for file_name in os.listdir(save_directory):
        save_folder.append(file_name)
    if save_folder:
        choose_save_file()
    else:
        print("No save folders found.")

def choose_save_file():
    global save_path
    if not save_folder:
        print("Please pick the game directory first (Option 1).")
        return

    print("Pick a save file: ")
    for index, name in enumerate(save_folder):
        print(f"{index} - {name}")  
    try:
        choice = int(input())
        global save_path
        save_path = os.path.join(save_directory, save_folder[choice])
        print(f"Save path set to: {save_path}")
        find_save_file()
    except (ValueError, IndexError):
        print("Invalid selection.")
    else:
        print("No save file found.")

def find_save_file():
    global save_file
    found = False

    for file_name in os.listdir(save_path):
        if ".sav" in file_name:
            save_file = os.path.join(save_path, file_name)
            print(f"Save file found: {save_file}", flush=True)
            found = True
            break
    if not found:
            print("Save file (.sav) not found.")
            save_file = ""

def process_save_file(save_file):
    if not save_file:
        print("Error: No save file selected. Use options 1 and 2 first.")
        return
    
    try:
        with open(save_file, 'r', encoding="utf-8") as f:
            content = f.read()
            json_start = content.find('{')
            if json_start == -1:
                print("Error: No JSON object found in the file.")
                return None
            json_content = content[json_start:]
            save_data = json.loads(json_content)

        message_log = save_data.get("player_messages", {}).get("messages", [])
        with open("message_logs.txt", "w", encoding="utf-8") as log:
            for message in message_log:
                # turn = message.get("turn")
                text = re.sub(regex, "", message.get("message"))
                log.write(text + "\n")
                # print(f"Turn: {turn}, Message: {text}", flush=True)
        print(f"Successfully processed messages to message_logs.txt")

    except FileNotFoundError:
        print(f"Error: No file found in {save_file}")
    except json.JSONDecodeError:
        print("Error: The file is not a valid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

while True:
    print("\n--- Cataclysm Visualizer Menu ---")
    print(f"1 - Pick the game directory.")
    print(f"2 - Pick the save file.")
    print(f"3 - Process the game logs.")
    print(f"4 - Start monitoring save file for changes.")
    print(f"5 - Exit.")
    print(f"Current save file: {save_file or "Not set"}")

    match input("Choose an option: "):
        case "1":
            find_game_directory()
        case "2":
            choose_save_file()
        case "3":
            process_save_file(save_file)
        case "4":
            try:
                detect_file_changes(save_file)
            except KeyboardInterrupt:
                print("\nMonitoring stopped.")
        case "5":
            print("Bye.")
            break
        case _:
            print("Invalid option.")