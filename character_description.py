import json
import os
import sys
import codecs
import os
from llm import generate_text, initialize_google_client, initialize_openai_client
from llm import GEMINI_API_KEY, OPENAI_API_KEY, KOBOLD_API_ENDPOINT
from image_gen import image_gen
from image_gen import STABILITY_API_KEY

class App:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
    def __init__(self):
        default_configs = {
            "game_directory": "",
            "save_directory": "",
            "save_folder": [],
            "save_file": "",
            "save_path": "",
            "llm_mode": "Local-Kobold",
            "llm_model": "local-model",
            "temperature": 1.5,
            "max_length": 200,
            "top_p": 0.9,
            "top_k": 45,
            "image_mode": "Local",
            "image_model": "local-model",
            "local_batch_size": 1,
            "image_style": "cartoon"
        }
        try:
            with open("configs.json", "r", encoding="utf-8") as configs_file:
                loaded_configs = json.load(configs_file)
            self.configs = default_configs | loaded_configs
        except (FileNotFoundError, json.JSONDecodeError):
            self.configs = default_configs
            self.update_configs()

        self.game_directory = self.configs.get("game_directory")
        self.save_directory = self.configs.get("save_directory")
        self.save_folder = self.configs.get("save_folder")
        self.save_file = self.configs.get("save_file")
        self.save_path = self.configs.get("save_path")
        self.llm_mode = self.configs.get("llm_mode")
        self.llm_model = self.configs.get("llm_model")
        self.temperature = self.configs.get("temperature")
        self.max_length = self.configs.get("max_length")
        self.top_p = self.configs.get("top_p")
        self.top_k = self.configs.get("top_k")
        self.image_mode = self.configs.get("image_mode")
        self.image_model = self.configs.get("image_model")
        self.local_batch_size = self.configs.get("local_batch_size")
        self.image_style = self.configs.get("image_style")
        self.STABILITY_API_KEY = STABILITY_API_KEY
        self.GEMINI_API_KEY = GEMINI_API_KEY
        self.OPENAI_API_KEY = OPENAI_API_KEY
        self.KOBOLD_API_ENDPOINT = KOBOLD_API_ENDPOINT

    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def update_configs(self):
        with open("configs.json", "w", encoding="utf-8") as configs_file:
            json.dump(self.configs, configs_file, indent=4)

    def set_env_variable(self, key, value):
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
    def set_api_key(self):        
        while True:
            self.clear_console()
            print("Set API for LLM services.")
            print(f"Current settings:\nLocal endpoint = {self.KOBOLD_API_ENDPOINT}\nGemini API key = {'Set' if self.GEMINI_API_KEY else 'Not set'}\nOpenAI API key = {'Set' if self.OPENAI_API_KEY else 'Not set'}\nStability API key = {'Set' if self.STABILITY_API_KEY else 'Not set'}\n")
            print("1 - Change local endpoint.")
            print("2 - Change Gemini API key.")
            print("3 - Change OpenAI API key.")
            print("4 - Change Stability API key.")
            print("5 - Back to main menu.")

            choice = input("Select an option (1-5): ")
            match choice:
                case "1":
                    print("Current local endpoint:", self.KOBOLD_API_ENDPOINT)
                    new_endpoint = input("Enter new local endpoint: ").strip()
                    if new_endpoint:
                        self.set_env_variable("KOBOLD_API_ENDPOINT", new_endpoint)
                        self.KOBOLD_API_ENDPOINT = new_endpoint
                        os.environ["KOBOLD_API_ENDPOINT"] = self.KOBOLD_API_ENDPOINT
                        print("Local endpoint updated.")
                    else:
                        print("No endpoint provided.")

                case "2":
                    print("Enter your Gemini API key: ")
                    new_gemini_key = input().strip()
                    if new_gemini_key:
                        self.set_env_variable("GEMINI_API_KEY", new_gemini_key)
                        self.GEMINI_API_KEY = new_gemini_key
                        os.environ["GEMINI_API_KEY"] = self.GEMINI_API_KEY
                        initialize_google_client()
                        print("Gemini API key updated.")
                    else:
                        print("No Gemini API key provided.")

                case "3":
                    print("Enter your OpenAI API key: ")
                    new_openai_key = input().strip()
                    if new_openai_key:
                        self.set_env_variable("OPENAI_API_KEY", new_openai_key)
                        self.OPENAI_API_KEY = new_openai_key
                        os.environ["OPENAI_API_KEY"] = self.OPENAI_API_KEY
                        initialize_openai_client()
                        print("OpenAI API key updated.")
                    else:
                        print("No OpenAI API key provided.")

                case "4":
                    print("Enter your Stability API key: ")
                    new_stability_key = input().strip()
                    if new_stability_key:
                        self.set_env_variable("STABILITY_API_KEY", new_stability_key)
                        self.STABILITY_API_KEY = new_stability_key
                        os.environ["STABILITY_API_KEY"] = self.STABILITY_API_KEY
                        print("Stability API key updated.")
                    else:
                        print("No Stability API key provided.")
                        
                case "5":
                    return print("Returning to main menu.")
                case _:
                    print("Invalid option.\n")

    def find_game_directory(self):
        self.clear_console()
        print("Type where is the game directory: ")
        self.game_directory = input()

        try:
            if not os.path.isdir(self.game_directory):
                print("Error: Directory not found.")
                return
            self.configs["game_directory"] = self.game_directory

            self.save_directory = os.path.join(self.game_directory, "save")
            self.configs["save_directory"] = self.save_directory
            print(f"Looking for saves in {self.save_directory}.")

            self.save_folder.clear()
            for file_name in os.listdir(self.save_directory):
                self.save_folder.append(file_name)
            if self.save_folder:
                self.configs["save_folder"] = self.save_folder
                self.choose_save_file()
            else:
                print("No save folders found.")
            self.update_configs()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def choose_save_file(self):
        if not self.save_folder:
            print("Please pick the game directory first (Option 1).")
            return

        self.clear_console()
        print("Pick a save file: ")
        for index, name in enumerate(self.save_folder):
            print(f"{index + 1} - {name}")
        try:
            choice = int(input())
            self.save_path = os.path.join(self.save_directory, self.save_folder[choice - 1])
            print(f"Save path set to: {self.save_path}")
            self.configs["save_path"] = self.save_path
            self.update_configs()
            self.find_save_file()
        except (ValueError, IndexError):
            print("Invalid selection.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def find_save_file(self):
        found = False

        for file_name in os.listdir(self.save_path):
            if ".sav" in file_name:
                self.save_file = os.path.join(self.save_path, file_name)
                print(f"Save file found: {self.save_file}")
                self.configs["save_file"] = self.save_file
                self.update_configs()
                found = True
                break
        if not found:
                print("Save file (.sav) not found.")
                self.save_file = ""
                self.configs["save_file"] = self.save_file
                self.update_configs()

    def get_proficiencies(self, prof_list):
        proficiencies = {"known": [], "learning": []}

        known_profs = prof_list.get("known", [])
        if known_profs:
            proficiencies["known"].extend(known_profs)
        
        learning_profs = prof_list.get("learning", [])
        for prof in learning_profs:
            if "id" in prof:
                proficiencies["learning"].extend(learning_profs)

        return proficiencies

    def process_save_file(self):
        if not self.save_file:
            print("Error: No save file selected. Use options 1 and 2 first.")
            return
        
        try:
            with open(self.save_file, 'r', encoding="utf-8") as f:
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
            proficiencies = self.get_proficiencies(player_data.get("proficiencies", {}))
            traits = player_data.get("traits", [])
            mutations = player_data.get("mutations", {})
            # print(f"Inventory items: {len(all_inventory_items)}", flush=True)

            try:
                with open("Character/character.txt", "w", encoding="utf-8") as char_file:
                    char_file.write(f"Character Name: {player_data.get('name', 'Unknown')}\n")
                    char_file.write(f"Character age: {player_data.get('base_age', 'Unknown')}\n")
                    char_file.write(f"Character height: {player_data.get('base_height', 'Unknown')}\n")
                    char_file.write(f"Wielded Item: {wielded.get('typeid', 'None')}\n")
                    char_file.write(f"Worn Items: {', '.join(item.get('typeid', 'None') for item in worn)}\n")

                    char_file.write("Traits:\n")
                    for name in traits:
                        char_file.write(f"  - {name}\n")

                    char_file.write("Mutations:\n")
                    for name, data in mutations.items():
                        if name in traits and 'variant-id' in data:
                            char_file.write(f"  - {name}: {data.get('variant-id')}\n")

                    # char_file.write("Skills:\n")
                    # for name, data in skills.items():
                    #     level = data.get('level', 0)
                    #     if level > 0:
                    #         char_file.write(f"  - {name}: {level}\n")
                    
                    # char_file.write("Proficiencies:\n")
                    # for prof in proficiencies.get("known", []):
                    #     char_file.write(f"  - Known: {prof}\n")
                    # for prof in proficiencies.get("learning", []):
                    #     if prof.get("practiced", 0) > 0:
                    #         char_file.write(f"  - Learning: {prof}\n")

                print(f"Character data processed and saved to Character/character.txt")
            except Exception as e:
                    print(f"Error writing to character.txt: {e}")
            
        except FileNotFoundError:
            print(f"Error: No file found in {self.save_file}")
        except json.JSONDecodeError:
            print("Error: The file is not a valid JSON.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def change_llm_settings(self):
        #TODO: Add option to select different models in external services
        while True:
            self.clear_console()
            print(f"Current settings: llm_mode = {self.llm_mode}, llm_model = {self.llm_model}\n")
            print("1 - Local with KoboldCpp.")
            print("2 - Google - Gemini 2.5 Flash.")
            print("3 - OpenAI - GPT-5.")
            print("4 - Keep current settings.")
            self.llm_mode = (input(f"\nChoose new llm_mode (1-4): "))
            match self.llm_mode:
                case "1":
                    self.llm_mode = "Local-Kobold"
                    self.llm_model = "local-model"
                    break
                case "2":
                    self.llm_mode = "Google"
                    self.llm_model = "gemini-2.5-flash"
                    break
                case "3":
                    self.llm_mode = "OpenAI"
                    self.llm_model = "gpt-5"
                    break
                case "4":
                    return print(f"Keeping current settings. {self.llm_mode}, {self.llm_model}")
                case _:
                    print("Invalid option.\n")
        print(f"Settings updated: llm_mode = {self.llm_mode}, llm_model = {self.llm_model}")
        self.configs["llm_mode"] = self.llm_mode
        self.configs["llm_model"] = self.llm_model
        self.update_configs()

    def change_image_settings(self):
        #TODO: Add option to select different models in external services
        while True:
            self.clear_console()
            print(f"Current settings: image_mode = {self.image_mode}, image_model = {self.image_model}\n")
            print("1 - Local with ComfyUI.")
            print("2 - Stability AI - Stable Diffusion 3.5.")
            print("3 - Keep current settings.")
            self.image_mode = (input(f"\nChoose new Image Mode (1-3): "))
            match self.image_mode:
                case "1":
                    self.image_mode = "Local"
                    self.image_model = "local-model"
                    break
                case "2":
                    self.image_mode = "Stability AI"
                    self.image_model = "stable-image-core"
                    break
                case "3":
                    return print(f"Keeping current settings. {self.image_mode}, {self.image_model}")
                case _:
                    print("Invalid option.\n")
        print(f"Settings updated: Image Mode = {self.image_mode}, Image Model = {self.image_model}")
        self.configs["image_mode"] = self.image_mode
        self.configs["image_model"] = self.image_model
        self.update_configs()

    def describe_character(self):
        SYSTEM_PROMPT = (
        "You will describe a Cataclysm Dark Days Ahead game character. "
        "You will be provided with information, use it to generate a paragraph description to be used for image generation. "
        "Use phrases rather than long sentences. "
        "Do not generate any information that is not explicitly present in the provided character data. "
        "Do not ask for more information. "
        "Do not speak to the user. "
        )

        #TODO: Explain the settings
        while True:
            self.clear_console()
            print(f"Current settings: LLM Mode = {self.llm_mode}, LLM Model = {self.llm_model}, Temperature = {self.temperature}, Max Length = {self.max_length}, Top-p = {self.top_p}, Top-k = {self.top_k}")
            print("\nGenerate with current settings or change them?\n")
            print(f"1 - Generate with current settings.")
            print(f"2 - Change LLM Mode and LLM Model.")
            print(f"3 - Change temperature.")
            print(f"4 - Change max length.")
            print(f"5 - Change top-p.")
            print(f"6 - Change top-k.")
            print(f"7 - Change system prompt.")
            print(f"8 - Back to main menu.")
            choice = input("Choose an option: ")

            match choice:
                case "1":
                    break
                case "2":
                    self.change_llm_settings()
                case "3":
                    self.temperature = float(input(f"Enter new temperature: "))
                    self.configs["temperature"] = self.temperature
                    self.update_configs()
                case "4":
                    self.max_length = int(input("Enter new max length: "))
                    self.configs["max_length"] = self.max_length
                    self.update_configs()
                case "5":
                    self.top_p = float(input("Enter new top-p: "))
                    self.configs["top_p"] = self.top_p
                    self.update_configs()
                case "6":
                    self.top_k = int(input("Enter new top-k: "))
                    self.configs["top_k"] = self.top_k
                    self.update_configs()
                case "7":
                    self.clear_console()
                    print("Current system prompt:", SYSTEM_PROMPT)
                    try:
                        new_SYSTEM_PROMPT = input("Enter new system prompt: ")
                        if new_SYSTEM_PROMPT:
                            SYSTEM_PROMPT = new_SYSTEM_PROMPT + " "
                            print("System prompt updated.")
                        else:
                            print("No prompt provided.")
                    except Exception as e:
                        print(f"Error reading input: {e}")
                case "8":
                    return print("Returning to main menu.")
                case _:
                    print("Invalid option.")
        if self.llm_mode == "Google" and not GEMINI_API_KEY:
            print("\nError: Gemini API key not set.")
            print("Please set it in the main menu (Option 8).")
            input("Press any key to return to the main menu...")
            return
        if self.llm_mode == "OpenAI" and not OPENAI_API_KEY:
            print("\nError: OpenAI API key not set.")
            print("Please set it in the main menu (Option 8).")
            input("Press any key to return to the main menu...")
            return

        try:
            with open(f"Character/character.txt", "r", encoding="utf-8") as char_file:
                description_text = char_file.read().replace("\n", " ").replace("-", "")
            print("Here is the character:\n", description_text)

            print("Generating prompt...")
            response = generate_text(
                llm_mode=self.llm_mode,
                llm_model=self.llm_model,
                prompt=SYSTEM_PROMPT + description_text,
                temperature=self.temperature,
                max_length=self.max_length,
                top_p=self.top_p,
                top_k=self.top_k,
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

    def custom_description(self):
        filename = "custom_description.txt"
        custom_desc = ""

        while True:
            self.clear_console()
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

    def generate_image(self):
        SYSTEM_PROMPT = (
        {self.image_style}
        )
        #TODO: Add option to change image size with presets (256x256, 512x512, 768x768, 1024x1024)
        #TODO: Add option to select what description to use (custom/old/last)
        #TODO: Add option to randomize/set seed in comfyui
        #TODO: Add option to select workflow in comfyui
        while True:
            self.clear_console()
            print(f"Current settings: Image Mode = {self.image_mode}, Image Model = {self.image_model}, Local Batch Size = {self.local_batch_size}")
            print("\nGenerate with current settings or change them?\n")
            print(f"1 - Generate with current settings.")
            print(f"2 - Change batch size (only for Local mode).")
            print(f"3 - Change image style.")
            print(f"4 - Change Image Mode and Image Model.")
            print(f"5 - Back to main menu.")

            choice = input("Choose an option: ")
            match choice:
                case "1":
                    break
                case "2":
                    self.local_batch_size = int(input("Enter new batch size: "))
                    self.configs["local_batch_size"] = self.local_batch_size
                    self.update_configs()
                case "3":
                    self.image_style = input("Enter new image style (e.g., 'highly detailed, photorealistic, 4k, intricate, sharp focus'): ")
                    self.configs["image_style"] = self.image_style
                    self.update_configs()
                case "4":
                    self.change_image_settings()
                case "5":
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
                mode=self.image_mode,
                batch_size=self.local_batch_size
            )
        except FileNotFoundError:
            print("Error: character_description.txt not found. Please describe the character first (Option 4).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def main_menu(self):
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
            print(f"Current save file: {self.save_path or "Not set"}")

            match input("Choose an option: ").strip():
                case "1":
                    self.find_game_directory()
                case "2":
                    self.choose_save_file()
                case "3":
                    self.process_save_file()
                case "4":
                    self.describe_character()
                case "5":
                    self.custom_description()
                case "6":
                    self.generate_image()
                case "7":
                    self.clear_console()
                    print("1 - Change LLM settings.")
                    print("2 - Change Image settings.")
                    print("3 - Back to main menu.")
                    sub_choice = input("Choose an option: ")
                    match sub_choice:
                        case "1":
                            self.change_llm_settings()
                        case "2":
                            self.change_image_settings()
                        case "3":
                            return print("Returning to main menu.")
                        case _:
                            print("Invalid option.")
                case "8":
                    self.set_api_key()
                case "9":
                    print("Bye.")
                    sys.exit(0)
                case _:
                    print("Invalid option.")
            self.clear_console()

    def run(self):
        while True:
            self.main_menu()

if __name__ == "__main__":
    app = App()
    app.run()