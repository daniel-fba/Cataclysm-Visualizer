import requests
import json
from google import genai
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def initialize_google_client():
    global google_client
    try:
        google_client = genai.Client(api_key=GEMINI_API_KEY)
        print("Google client initialized successfully.")
    except Exception as e:
        print(f"Error initializing Google client: {e}")
        input("Press Enter to continue...")

def initialize_openai_client():
    global openai_client
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("OpenAI client initialized successfully.")
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        input("Press Enter to continue...")

if os.getenv("KOBOLD_API_ENDPOINT"):
    KOBOLD_API_ENDPOINT = os.getenv("KOBOLD_API_ENDPOINT")
else:
    KOBOLD_API_ENDPOINT = "http://localhost:5000/api/v1/generate"

if os.getenv("GEMINI_API_KEY"):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    initialize_google_client()
else:
    GEMINI_API_KEY = ""

if os.getenv("OPENAI_API_KEY"):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    initialize_openai_client()
else:
    OPENAI_API_KEY = ""

def generate_text(llm_mode: str, llm_model: str, prompt: str, temperature: int = 0.8, max_length: int = 150, top_p: float = 0.9, top_k: int = 45):
    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "prompt": prompt, # The input text to send to the language model
        "temperature": temperature, # Controls the randomness of the output. Higher values make the output more random, lower values make it more deterministic.
        "max_length": max_length, # The maximum number of tokens to generate in the response
        "top_p": top_p, # Nucleus sampling parameter. The model considers only the tokens with a cumulative probability mass up to this value. Helps to control the diversity of the output.
        "top_k": top_k, # The model considers only the top k most likely tokens at each step of the generation.
    }

    response = None

    match llm_mode:
        case "Local-Kobold":
            try:
                response = requests.post(KOBOLD_API_ENDPOINT,
                headers=headers,
                data=json.dumps(payload),
                timeout=60
                )
                print(f"Sending request to {KOBOLD_API_ENDPOINT}...")
            except Exception as e:
                return f"Error communicating with the local API: {e}"
        case "Google":
            try:
                response = google_client.models.generate_content(
                    model=llm_model, contents=prompt
                )
                print(f"Sending request to Google API...")
            except Exception as e:
                return f"Error communicating with the Google API: {e}"
        case "OpenAI":
            try:
                response = openai_client.chat.completions.create(
                    model=llm_model, messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                print(f"Sending request to OpenAI API...")
            except Exception as e:
                return f"Error communicating with the OpenAI API: {e}"

    try:
        if response:
            if llm_mode == "Local-Kobold":
                response.raise_for_status()
                response_data = response.json()
                return response_data["results"][0]["text"]
            elif llm_mode == "Google":
                return response.text
            elif llm_mode == "OpenAI":
                return response.choices[0].message.content
        else:
            return "No response received from the API."
    except requests.exceptions.RequestException as e:
        return f"Error communicating with the API: {e}"
    except (KeyError, IndexError) as e:
        return f"Unexpected response format: {e}"
    except Exception as e:
        return f"An error occurred: {e}"