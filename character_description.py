import json
import os
import sys
import codecs
import os
from llm import generate_text

game_directory = ""
save_directory = ""
save_folder = []
save_file = ""
save_path = ""
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
# regex = r"<.*?>"

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def find_game_directory():
    global game_directory, save_directory
    clear_console()

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

    clear_console()
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
            
# def get_all_items(item_list):
#     all_items = []
#     for item in item_list:
#         all_items.append(item)
#         if "contents" in item and isinstance(item.get("contents"), list):
#             nested_items = get_all_items(item["contents"])
#             all_items.extend(nested_items)
#     return all_items

def get_proficiencies(prof_list):
    proficiencies = {"known": [], "learning": []}

    known_profs = prof_list.get("known", [])
    if known_profs:
        proficiencies["known"].extend(known_profs)
    
    learning_profs = prof_list.get("learning", [])
    for prof in learning_profs:
        if "id" in prof:
            proficiencies["learning"].extend(learning_profs)

    return proficiencies

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

        player_data = save_data.get("player", {})
        # all_inventory_items = get_all_items(player_data)
        worn = player_data.get("worn", {}).get("worn", [])
        wielded = player_data.get("weapon", {})
        skills = player_data.get("skills", {})
        proficiencies = get_proficiencies(player_data.get("proficiencies", {}))
        traits = player_data.get("traits", [])
        mutations = player_data.get("mutations", {})
        # print(f"Inventory items: {len(all_inventory_items)}", flush=True)

        try:
            with open("character.txt", "w", encoding="utf-8") as char_file:
                print(f"Character Name: {player_data.get('name', 'Unknown')}", flush=True)
                char_file.write(f"Character Name: {player_data.get('name', 'Unknown')}\n")
                char_file.write(f"Character age: {player_data.get('base_age', 'Unknown')}\n")
                char_file.write(f"Character height: {player_data.get('base_height', 'Unknown')}\n")

                print(f"Wielded item: {wielded.get('typeid')}", flush=True)
                char_file.write(f"Wielded Item: {wielded.get('typeid', 'None')}\n")

                print(f"Worn items:", flush=True)
                for item in worn:
                    print(f"  - {item.get('typeid')}")
                char_file.write(f"Worn Items: {', '.join(item.get('typeid', 'None') for item in worn)}\n")
                
                print(f"Traits:", flush=True)
                char_file.write("Traits:\n")
                for name in traits:
                    print(f"  - {name}")
                    char_file.write(f"  - {name}\n")

                print(f"Mutations:", flush=True)
                char_file.write("Mutations:\n")
                for name, data in mutations.items():
                    if name in traits and 'variant-id' in data:
                        print(f"  - {name}: {data.get('variant-id')}")
                        char_file.write(f"  - {name}: {data.get('variant-id')}\n")

                # char_file.write("Skills:\n")
                # print("Skills:")
                # for name, data in skills.items():
                #     level = data.get('level', 0)
                #     if level > 0:
                #         print(f"  - {name}: {level}")
                #         char_file.write(f"  - {name}: {level}\n")
                
                # char_file.write("Proficiencies:\n")
                # print(f"Proficiencies:", flush=True)
                # for prof in proficiencies.get("known", []):
                #     print(f"  - Known: {prof}")
                #     char_file.write(f"  - Known: {prof}\n")
                # for prof in proficiencies.get("learning", []):
                #     if prof.get("practiced", 0) > 0:
                #         print(f"  - Learning: {prof}")
        except Exception as e:
                print(f"Error writing to character.txt: {e}")
        
        
    except FileNotFoundError:
        print(f"Error: No file found in {save_file}")
    except json.JSONDecodeError:
        print("Error: The file is not a valid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def describe_character():
    temperature = 1.5
    max_length = 200
    top_p = 0.9
    top_k = 45

    SYSTEM_PROMPT = (
    "You are assistant that helps people describe their Cataclysm Dark Days Ahead game character."
    "You will be provided with information about the character, use it to generate a description "
    "to be used for image generation. "
    "Do not generate any information that is not explicitly present in the provided character data. "
    "Focus on the character. "
    )

    while True:
        clear_console()
        print(f"Current settings: Temperature={temperature}, Max Length={max_length}, Top-p={top_p}, Top-k={top_k}")
        print("Generate with current settings or change them?")
        print(f"1 - Generate with current settings.")
        print(f"2 - Change temperature.")
        print(f"3 - Change max length.")
        print(f"4 - Change top-p.")
        print(f"5 - Change top-k.")
        choice = input("Choose an option: ")

        match choice:
            case "1":
                break
            case "2":
                temperature = float(input(f"Enter new temperature: "))
            case "3":
                max_length = int(input("Enter new max length: "))
            case "4":
                top_p = float(input("Enter new top-p: "))
            case "5":
                top_k = int(input("Enter new top-k: "))
            case _:
                print("Invalid option.")

    try:
        with open("character.txt", "r", encoding="utf-8") as char_file:
            description_text = char_file.read().replace("\n", " ").replace("-", "")
        print("Here is the character:\n", description_text)

        print("Generating prompt...")
        response = generate_text(
            prompt=SYSTEM_PROMPT + description_text,
            temperature=temperature,
            max_length=max_length,
            top_p=top_p,
            top_k=top_k,
        )

        print(f"Prompt: \n{response}")

        backup_file = "character_description_old.txt"
        try:
            with open("character_description.txt", "r", encoding="utf-8") as original_file:
                original_content = original_file.read()
        except FileNotFoundError as e:
            original_content = ""
        
        with open(backup_file, "w", encoding="utf-8") as backup:
                backup.write(original_content)
        with open("character_description.txt", "w", encoding="utf-8") as desc_file:
            desc_file.write(response)
            print("Character description saved to character_description.txt")
            

    except FileNotFoundError:
        print("Error: character.txt not found. Please process the save file first (Option 3).")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def simplify():
    temperature = 1.5
    max_length = 200
    top_p = 0.9
    top_k = 45

    SYSTEM_PROMPT = (
    "You are assistant that helps people describe their Cataclysm Dark Days Ahead game character in a concise way."
    "You will be provided with information about the character, make it simpler and more concise, "
    "to be used for image generation."
    "Add an optional list of negative prompts to avoid unwanted elements in the image."
    )

    while True:
        clear_console()
        print(f"Current settings: Temperature={temperature}, Max Length={max_length}, Top-p={top_p}, Top-k={top_k}")
        print("Generate with current settings or change them?")
        print(f"1 - Generate with current settings.")
        print(f"2 - Change temperature.")
        print(f"3 - Change max length.")
        print(f"4 - Change top-p.")
        print(f"5 - Change top-k.")
        choice = input("Choose an option: ")

        match choice:
            case "1":
                break
            case "2":
                temperature = float(input("Enter new temperature: "))
            case "3":
                max_length = int(input("Enter new max length: "))
            case "4":
                top_p = float(input("Enter new top-p: "))
            case "5":
                top_k = int(input("Enter new top-k: "))
            case _:
                print("Invalid option.")

    try:
        if os.path.isfile("custom_description.txt"):
            print("Custom description found. Simplify custom description or generated description?")
            choice = input(f"1 - Simplify generated description.\n2 - Simplify custom description.\nChoose an option: ")
            if choice == "1":
                with open("character_description.txt", "r", encoding="utf-8") as char_file:
                    description_text = char_file.read().replace("\n", " ").replace("-", "")
            elif choice == "2":
                with open("simple_description.txt", "r", encoding="utf-8") as char_file:
                    description_text = char_file.read().replace("\n", " ").replace("-", "")
            else:
                print("Invalid option.")
                return
        
        with open("character_description.txt", "r", encoding="utf-8") as char_file:
            description_text = char_file.read().replace("\n", " ").replace("-", "")
        print("Generating prompt...")
        response = generate_text(
            prompt=SYSTEM_PROMPT + description_text,
            temperature=temperature,
            max_length=max_length,
            top_p=top_p,
            top_k=top_k,
        )

        print(f"Prompt: \n{response}")

        backup_file = "simple_description_old.txt"
        try:
            with open("simple_description.txt", "r", encoding="utf-8") as original_file:
                original_content = original_file.read()
        except FileNotFoundError as e:
            original_content = ""

        with open(backup_file, "w", encoding="utf-8") as backup:
                backup.write(original_content)
        with open("simple_description.txt", "w", encoding="utf-8") as desc_file:
            desc_file.write(response)
            print("Simple character description saved to simple_description.txt")

    except FileNotFoundError:
        print("Error: character_description.txt not found. Please describe the character first (Option 4).")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def custom_description():
    filename = "custom_description.txt"
    if os.path.exists(filename):
        print("A custom description already exists. Do you want to edit the existing description? (y/n)")
        choice = input().lower()
        if choice == 'y':
            try:
                with open(filename, "r", encoding="utf-8") as file:
                    custom_desc = file.read()
                    print(f"Current custom description:\n", {custom_desc})
                    print("\nEnter your new custom description: ")
                    custom_desc = input()
            except Exception as e:
                print(f"Error reading the file: {e}")
                return
        else:
            print("Enter your custom description: ")
            custom_desc = input()
    else:
        print("Enter your custom description: ")
        custom_desc = input()
    
    try:
        with open("custom_description.txt", "w", encoding="utf-8") as desc_file:
            desc_file.write(custom_desc)
        print(f"Custom character description saved to {filename}")
        return custom_desc
    except Exception as e:
        print(f"Error writing to the file: {e}")
        return


while True:
    clear_console()
    print("\n--- Cataclysm Visualizer Menu ---")
    print(f"1 - Pick the game directory.")
    print(f"2 - Pick the save file.")
    print(f"3 - Process the save file.")
    print(f"4 - Generate description from game save.")
    print(f"5 - Simplify the generated description.")
    print(f"6 - Enter a custom description.")
    print(f"7 - Exit.")
    print(f"Current save file: {save_file or "Not set"}")

    match input("Choose an option: "):
        case "1":
            find_game_directory()
        case "2":
            choose_save_file()
        case "3":
            process_save_file(save_file)
        case "4":
            describe_character()
        case "5":
            simplify()
        case "6":
            custom_description()
        case "7":
            print("Bye.")
            break
        case _:
            print("Invalid option.")