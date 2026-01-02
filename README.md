A simple Python script I wrote out of curiosity to explore running AI models locally and integrating generative workflows.

1. **Extraction:** It reads a CDDA save file (.sav) to extract character data such as name, age, height, traits, mutations, and worn clothing.

2. **Description:** This data is fed into a Large Language Model (LLM) to generate a detailed character description.

3. **Visualization:** The description is sent to an Image Generation Model to create a visual representation of your survivor.

## Requirements
The project can run entirely on the machine or via cloud services.

### Local Generation

**KoboldCpp:** For LLM text generation.

https://github.com/LostRuins/koboldcpp

**ComfyUI:** For Stable Diffusion image generation.

https://github.com/comfyanonymous/ComfyUI

### Online Generation

Alternatively, the script supports professional APIs (requires API keys):

**LLM:** Google Gemini or OpenAI.

**Image:** Stability AI.