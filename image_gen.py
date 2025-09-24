import requests
from dotenv import load_dotenv
import os
import json
import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import urllib.request
import urllib.parse

load_dotenv()

if os.getenv("STABILITY_API_KEY"):
    STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
else:
    STABILITY_API_KEY = ""

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt, prompt_id):
    p = {"prompt": prompt, "client_id": client_id, "prompt_id": prompt_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    urllib.request.urlopen(req).read()

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = str(uuid.uuid4())
    queue_prompt(prompt, prompt_id)
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            # If you want to be able to decode the binary stream for latent previews, here is how you can do it:
            # bytesIO = BytesIO(out[8:])
            # preview_image = Image.open(bytesIO) # This is your preview in PIL image format, store it in a global
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        images_output = []
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
        output_images[node_id] = images_output

    return output_images


def image_gen(prompt: str, mode: str, server_address: str = "127.0.0.1:8188", batch_size: int = 1):

    if mode == "Local":
        try:
            with open("Workflows/sdxlturbo.json", "r") as f:
                workflow_data = json.load(f)
            prompt_node_id = None
            batch_node_id = None

            for node_id, node_info in workflow_data.items():
                if node_info.get("class_type") == "EmptyLatentImage":
                    batch_node_id = node_id
                if node_info.get("_meta", {}).get("title") == "CLIP Text Encode (Prompt)":
                    prompt_node_id = node_id
                if prompt_node_id and batch_node_id:
                    break
            if not prompt_node_id:
                print("Error: Could not find the prompt node in the workflow.")
                return
            
            workflow_data[prompt_node_id]["inputs"]["text"] = prompt
            workflow_data[batch_node_id]["inputs"]["batch_size"] = batch_size

            ws = websocket.WebSocket()
            ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
            #print("Generating image, please wait...", flush=True)
            images = get_images(ws, workflow_data)
            ws.close()
            # for node_id in images:
            #     for image_data in images[node_id]:
            #         from PIL import Image
            #         import io
            #         image = Image.open(io.BytesIO(image_data))
            #         image.show()
            print("Image generation completed. Check the output images.")
        except Exception as e:
            print(f"Error connecting to local server: {e}")
            return
      
    elif mode == "Stability AI":
        response = requests.post(
            f"https://api.stability.ai/v2beta/stable-image/generate/core",
            headers={
                "authorization": f"Bearer {STABILITY_API_KEY}",
                "accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": f"{prompt}",
                "output_format": "webp",
            },
        )

        if response.status_code == 200:
            with open("./Generated Images/image.webp", 'wb') as file:
                file.write(response.content)
            print("Image generated and saved as image.webp")
        else:
            raise Exception(str(response.json()))