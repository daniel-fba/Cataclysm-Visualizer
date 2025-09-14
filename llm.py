import requests
import json

KOBOLD_API_ENDPOINT = "http://localhost:5001/api/v1/generate"

def generate_text(prompt: str, temperature: int = 0.8, max_length: int = 150, top_p: float = 0.9, top_k: int = 45):
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

    try:
        print(f"Sending request to {KOBOLD_API_ENDPOINT}...")
        response = requests.post(
            KOBOLD_API_ENDPOINT,
            headers=headers,
            data=json.dumps(payload),
            timeout=60
        )

        response.raise_for_status()
        response_data = response.json()
        return response_data["results"][0]["text"]
    
    except requests.exceptions.RequestException as e:
        return f"Error communicating with the API: {e}"
    except (KeyError, IndexError) as e:
        return f"Unexpected response format: {e}"
    except Exception as e:
        return f"An error occurred: {e}"
    

# Test
if __name__ == "__main__":
    system_input = (
        "You are a story narrator for the game Cataclysm: Dark Days Ahead. "
        "Based on the summary of events provided, write a short, dramatic, and immersive paragraph describing the character's situation."
    )

    user_input = "The survivor ventured into the dark forest and fought a fierce zombie."

    print("Generating narrative...")
    response = generate_text(
        prompt=system_input + user_input,
        temperature=0.7,
        max_length=150
    )

    print(f"Generated Narrative: \n{response}")