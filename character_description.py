import json
import os
import sys
import codecs
import os
from llm import generate_text, initialize_google_client, initialize_openai_client
from llm import GEMINI_API_KEY, OPENAI_API_KEY, KOBOLD_API_ENDPOINT
from image_gen import image_gen
from image_gen import STABILITY_API_KEY

game_directory = ""
save_directory = ""
save_folder = []
save_file = ""
save_path = ""
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
llm_mode = "Local-Kobold"
llm_model = "local-model"
image_mode = "Local"
image_model = "local-model"

def set_env_variable(key, value):
    env_content = []
    found = False
    try:
        with open(".env", "r", encoding="utf-8") as env_file:
            env_content = env_file.readlines()
    except FileNotFoundError:
        pass
    with open(".env", "w", encoding="utf-8") as env_file:
        for line in env_content:
            if line.strip().startswith(f"{key}="):
                env_file.write(f"{key}={value}\n")
                found = True
            else:
                env_file.write(line)
        if not found:
            env_file.write(f"{key}={value}\n")

#TODO: Add option to change comfyui endpoint
def set_api_key():
    global GEMINI_API_KEY, OPENAI_API_KEY, KOBOLD_API_ENDPOINT, STABILITY_API_KEY
    
    while True:
        clear_console()
        print("Set API for LLM services.")
        print(f"Current settings:\nLocal endpoint = {KOBOLD_API_ENDPOINT}\nGemini API key = {'Set' if GEMINI_API_KEY else 'Not set'}\nOpenAI API key = {'Set' if OPENAI_API_KEY else 'Not set'}\nStability API key = {'Set' if STABILITY_API_KEY else 'Not set'}\n")
        print("1 - Change local endpoint.")
        print("2 - Change Gemini API key.")
        print("3 - Change OpenAI API key.")
        print("4 - Change Stability API key.")
        print("5 - Back to main menu.")

        choice = input("Select an option (1-5): ")
        match choice:
            case "1":
                print("Current local endpoint:", KOBOLD_API_ENDPOINT)
                new_endpoint = input("Enter new local endpoint: ").strip()
                if new_endpoint:
                    set_env_variable("KOBOLD_API_ENDPOINT", new_endpoint)
                    KOBOLD_API_ENDPOINT = new_endpoint
                    os.environ["KOBOLD_API_ENDPOINT"] = KOBOLD_API_ENDPOINT
                    print("Local endpoint updated.")
                else:
                    print("No endpoint provided.")
            case "2":
                print("Enter your Gemini API key: ")
                new_gemini_key = input().strip()
                if new_gemini_key:
                    set_env_variable("GEMINI_API_KEY", new_gemini_key)
                    GEMINI_API_KEY = new_gemini_key
                    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
                    initialize_google_client()
                    print("Gemini API key updated.")
                else:
                    print("No Gemini API key provided.")

            case "3":
                print("Enter your OpenAI API key: ")
                new_openai_key = input().strip()
                if new_openai_key:
                    set_env_variable("OPENAI_API_KEY", new_openai_key)
                    OPENAI_API_KEY = new_openai_key
                    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
                    initialize_openai_client()
                    print("OpenAI API key updated.")
                else:
                    print("No OpenAI API key provided.")
            case "4":
                print("Enter your Stability API key: ")
                new_stability_key = input().strip()
                if new_stability_key:
                    set_env_variable("STABILITY_API_KEY", new_stability_key)
                    STABILITY_API_KEY = new_stability_key
                    os.environ["STABILITY_API_KEY"] = STABILITY_API_KEY
                    print("Stability API key updated.")
                else:
                    print("No Stability API key provided.")
            case "5":
                return print("Returning to main menu.")
            case _:
                print("Invalid option.\n")

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
        print(f"{index + 1} - {name}")  
    try:
        choice = int(input())
        global save_path
        save_path = os.path.join(save_directory, save_folder[choice - 1])
        print(f"Save path set to: {save_path}")
        find_save_file()
    except (ValueError, IndexError):
        print("Invalid selection.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

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
            with open("Character/character.txt", "w", encoding="utf-8") as char_file:
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

def change_llm_settings():
    global llm_mode, llm_model

    #TODO: Add option to select different models in external services
    while True:
        clear_console()
        print(f"Current settings: llm_mode = {llm_mode}, llm_model = {llm_model}\n")
        print("1 - Local with KoboldCpp.")
        print("2 - Google - Gemini 2.5 Flash.")
        print("3 - OpenAI - GPT-5.")
        print("4 - Keep current settings.")
        llm_mode = (input(f"\nChoose new llm_mode (1-4): "))
        match llm_mode:
            case "1":
                llm_mode = "Local-Kobold"
                llm_model = "local-model"
                break
            case "2":
                llm_mode = "Google"
                llm_model = "gemini-2.5-flash"
                break
            case "3":
                llm_mode = "OpenAI"
                llm_model = "gpt-5"
                break
            case "4":
                return print(f"Keeping current settings. {llm_mode}, {llm_model}")
            case _:
                print("Invalid option.\n")
    print(f"Settings updated: llm_mode = {llm_mode}, llm_model = {llm_model}")

def change_image_settings():
    global image_mode, image_model

    #TODO: Add option to select different models in external services
    while True:
        clear_console()
        print(f"Current settings: image_mode = {image_mode}, image_model = {image_model}\n")
        print("1 - Local with ComfyUI.")
        print("2 - Stability AI - Stable Diffusion 3.5.")
        print("3 - Keep current settings.")
        image_mode = (input(f"\nChoose new Image Mode (1-3): "))
        match image_mode:
            case "1":
                image_mode = "Local"
                image_model = "local-model"
                break
            case "2":
                image_mode = "Stability AI"
                image_model = "stable-image-core"
                break
            case "3":
                return print(f"Keeping current settings. {image_mode}, {image_model}")
            case _:
                print("Invalid option.\n")
    print(f"Settings updated: Image Mode = {image_mode}, Image Model = {image_model}")

def describe_character():
    temperature = 1.5
    max_length = 200
    top_p = 0.9
    top_k = 45

    SYSTEM_PROMPT = (
    "You are assistant that helps people describe their Cataclysm Dark Days Ahead game character."
    "You will be provided with information about the character, use it to generate a description to be used for image generation. "
    "Use phrases rather than long sentences. "
    "Do not generate any information that is not explicitly present in the provided character data. "
    )

    #TODO: Explain the settings
    while True:
        clear_console()
        print(f"Current settings: LLM Mode = {llm_mode}, LLM Model = {llm_model}, Temperature = {temperature}, Max Length = {max_length}, Top-p = {top_p}, Top-k = {top_k}")
        print("\nGenerate with current settings or change them?\n")
        print(f"1 - Generate with current settings.")
        print(f"2 - Change LLM Mode and LLM Model.")
        print(f"3 - Change temperature.")
        print(f"4 - Change max length.")
        print(f"5 - Change top-p.")
        print(f"6 - Change top-k.")
        print(f"7 - Back to main menu.")
        choice = input("Choose an option: ")

        match choice:
            case "1":
                break
            case "2":
                change_llm_settings()
            case "3":
                temperature = float(input(f"Enter new temperature: "))
            case "4":
                max_length = int(input("Enter new max length: "))
            case "5":
                top_p = float(input("Enter new top-p: "))
            case "6":
                top_k = int(input("Enter new top-k: "))
            case "7":
                return print("Returning to main menu.")
            case _:
                print("Invalid option.")

    try:
        with open(f"Character/character.txt", "r", encoding="utf-8") as char_file:
            description_text = char_file.read().replace("\n", " ").replace("-", "")
        print("Here is the character:\n", description_text)

        print("Generating prompt...")
        response = generate_text(
            llm_mode=llm_mode,
            llm_model=llm_model,
            prompt=SYSTEM_PROMPT + description_text,
            temperature=temperature,
            max_length=max_length,
            top_p=top_p,
            top_k=top_k,
        )

        print(f"Prompt: \n{response}")

        backup_file = "Character Descriptions/character_description_old.txt"
        try:
            with open("Character Descriptions/character_description.txt", "r", encoding="utf-8") as original_file:
                original_content = original_file.read()
        except FileNotFoundError as e:
            original_content = ""
        
        with open(backup_file, "w", encoding="utf-8") as backup:
                backup.write(original_content)
        with open("Character Descriptions/character_description.txt", "w", encoding="utf-8") as desc_file:
            desc_file.write(response)
            print("Character description saved to Character Descriptions/character_description.txt")


    except FileNotFoundError:
        print("Error: character.txt not found. Please process the save file first (Option 3).")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def custom_description():
    filename = "custom_description.txt"
    custom_desc = ""

    while True:
        clear_console()
        print("Custom Description Menu")
        print(f"1 - View current custom description.")
        print(f"2 - Enter a new custom description.")
        print(f"3 - Back to main menu.")

        choice = input("Choose an option: ")

        match choice:
            case "1":
                if os.path.exists(filename):
                    try:
                        with open(filename, "r", encoding="utf-8") as file:
                            custom_desc = file.read()
                            print(f"Current custom description:\n{custom_desc}")
                    except Exception as e:
                        print(f"Error reading the file: {e}")
                else:
                    print("No custom description exists yet.")
                input("Press Enter to continue...")
            case "2":
                print("Enter your custom description: ")
                custom_desc = input()
                try:
                    with open(filename, "w", encoding="utf-8") as desc_file:
                        desc_file.write(custom_desc)
                    print(f"Custom character description saved to {filename}")
                except Exception as e:
                    print(f"Error writing to the file: {e}")
            case "3":
                return print("Returning to main menu.")
            case _:
                print("Invalid option.\n")

def generate_image():

    SYSTEM_PROMPT = (
    "You are assistant that helps people describe their Cataclysm Dark Days Ahead game character in a concise way."
    "You will be provided with information about the character, make it simpler and more concise, "
    "to be used for image generation."
    "Add an optional list of negative prompts to avoid unwanted elements in the image."
    )
    local_batch_size = 1
    #TODO: Add option to change image size with presets (256x256, 512x512, 768x768, 1024x1024)
    #TODO: Add option to select what description to use (custom/old/last)
    #TODO: Add option to randomize/set seed in comfyui
    #TODO: Add option to select workflow in comfyui
    while True:
        clear_console()
        print(f"Current settings: Image Mode = {image_mode}, Image Model = {image_model}, Local Batch Size = {local_batch_size}")
        print("\nGenerate with current settings or change them?\n")
        print(f"1 - Generate with current settings.")
        print(f"2 - Change batch size (only for Local mode).")
        print(f"3 - Change Image Mode and Image Model.")
        print(f"4 - Back to main menu.")

        choice = input("Choose an option: ")
        match choice:
            case "1":
                break
            case "2":
                local_batch_size = int(input("Enter new batch size: "))
            case "3":
                change_image_settings()
            case "4":
                return print("Returning to main menu.")
            case _:
                print("Invalid option.")

    try:
        with open("Character Descriptions/character_description.txt", "r", encoding="utf-8") as char_file:
            description_text = char_file.read()
        print("Here is the character:\n", description_text)

        full_prompt = SYSTEM_PROMPT + description_text

        print("Generating image...")
        image_gen(
            prompt=full_prompt,
            mode=image_mode,
            batch_size=local_batch_size
        )
    except FileNotFoundError:
        print("Error: character_description.txt not found. Please describe the character first (Option 4).")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

while True:
    
    print("\n--- Cataclysm Visualizer Menu ---")
    print(f"1 - Pick the game directory.")
    print(f"2 - Pick the save file.")
    print(f"3 - Process the save file.")
    print(f"4 - Generate description from game save.")
    print(f"5 - Enter a custom description.")
    print(f"6 - Generate image from description.")
    print(f"7 - Change AI Models settings.")
    print(f"8 - Set API keys.")
    print(f"9 - Exit.")
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
            custom_description()
        case "6":
            generate_image()
        case "7":
            clear_console()
            print("1 - Change LLM settings.")
            print("2 - Change Image settings.")
            sub_choice = input("Choose an option: ")
            match sub_choice:
                case "1":
                    change_llm_settings()
                case "2":
                    change_image_settings()
                case _:
                    print("Invalid option.")
        case "8":
            set_api_key()
        case "9":
            print("Bye.")
            break
        case _:
            print("Invalid option.")
    clear_console()