"""
DALL-E 3 Image Generator CLI
A tool for generating images with OpenAI's DALL-E 3 API with iterative prompt refinement.
"""

import os
import json
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Validate API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in environment variables.")
    print("Please create a .env file with your API key.")
    sys.exit(1)

client = OpenAI(api_key=api_key)

# Load previous session if exists
history_file = "image-gen-history.json"
previous_prompt = None
previous_url = None

if os.path.exists(history_file):
    with open(history_file, 'r') as f:
        history = json.load(f)
        previous_prompt = history.get('last_prompt')
        previous_url = history.get('last_url')
        
    if previous_prompt:
        print(f"\n--- Previous Session ---")
        print(f"Prompt: {previous_prompt}")
        print(f"Image: {previous_url}\n")
        
        choice = input("Iterate on previous prompt? (y/n): ").lower()
        if choice == 'y':
            print(f"\nPrevious prompt: {previous_prompt}")
            prompt = input("Enter modifications (or press Enter to reuse): ").strip()
            if not prompt:
                prompt = previous_prompt
            else:
                prompt = f"{previous_prompt} {prompt}"
        else:
            prompt = input("Enter your image prompt: ")
    else:
        prompt = input("Enter your image prompt: ")
else:
    prompt = input("Enter your image prompt: ")

try:
    print("\nGenerating image...")
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1792x1024"
    )
    
    image_url = response.data[0].url
    print(f"\nGenerated image URL: {image_url}")
except Exception as e:
    print(f"\nError generating image: {e}")
    sys.exit(1)

# Save to history
with open(history_file, 'w') as f:
    json.dump({
        'last_prompt': prompt,
        'last_url': image_url
    }, f, indent=2)
