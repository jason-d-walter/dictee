#!/usr/bin/env python3
"""
Generate assets for the Dictée app.

This script reads words from words_of_week.txt and generates:
- Kid-friendly French sentences using Google Gemini
- Audio files for words and sentences using Google Cloud TTS
- Images representing the sentences using Google Gemini (Imagen)

Usage:
    pip install -r requirements.txt
    export GOOGLE_API_KEY=your_api_key
    python generate_assets.py
"""

import os
import json
import base64
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

# Load environment variables
load_dotenv()

# Configuration
GOOGLE_PROJECT_NAME = os.getenv("GOOGLE_PROJECT_NAME")
if not GOOGLE_PROJECT_NAME:
    raise ValueError("GOOGLE_PROJECT_NAME environment variable is required")

language_model = "gemini-2.5-flash"
image_model = "imagen-3.0-generate-002"
speech_model= "gemini-2.5-flash-tts"

# 1. Setup the Client for Vertex AI
# Ensure you have 'GOOGLE_CLOUD_PROJECT' set in your environment
client = genai.Client(
    vertexai=True, 
    project=GOOGLE_PROJECT_NAME,
    location="us-central1"
) 

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
PUBLIC_DIR = PROJECT_DIR / "public"
AUDIO_DIR = PUBLIC_DIR / "audio"
IMAGES_DIR = PUBLIC_DIR / "images"
WORDS_FILE = PUBLIC_DIR / "words_of_week.txt"
MANIFEST_FILE = PUBLIC_DIR / "manifest.json"

# Ensure directories exist
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

def read_words() -> list[str]:
    """Read words from the words file."""
    if not WORDS_FILE.exists():
        raise FileNotFoundError(f"Words file not found: {WORDS_FILE}")

    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]

    # Remove duplicates while preserving order
    seen = set()
    unique_words = []
    for word in words:
        if word.lower() not in seen:
            seen.add(word.lower())
            unique_words.append(word)

    return unique_words


def generate_sentence(word: str) -> str:
    """Generate a kid-friendly French sentence using the word."""
    the_prompt = f"""Create a simple, kid-friendly French sentence using the word "{word}".

Requirements:
- The sentence should be appropriate for a 7-year-old child
- Use simple vocabulary and grammar
- The sentence should be fun or interesting for a child
- Keep it short (5-10 words maximum)
- The word "{word}" must appear in the sentence exactly as written
- Avoid using the 'passé composé' if possible; stick to the 'présent de l'indicatif'.
    
Return ONLY the French sentence, nothing else."""

    text_response = client.models.generate_content(
        model=language_model,
        contents=the_prompt
    )

    sentence = text_response.text.strip()

    # Remove quotes if present
    if sentence.startswith('"') and sentence.endswith('"'):
        sentence = sentence[1:-1]
    if sentence.startswith("'") and sentence.endswith("'"):
        sentence = sentence[1:-1]

    return sentence

import wave

def generate_audio_tts(text: str, output_path: Path, slow: bool = False) -> bool:
    """Safe version that saves raw PCM as a playable WAV file."""
    
    # Natural language steering for speed
    prompt = f"Dites d'une voix féminine {'lentement' if slow else ''} : {text}"

    minimal_config = {
        "response_modalities": ["AUDIO"],
        "speech_config": {
            "voice_config": {
                "prebuilt_voice_config": {"voice_name": "Aoede"}
            }
        }
    }

    try:
        response = client.models.generate_content(
            model=speech_model,
            contents=prompt,
            config=minimal_config
        )
        
        # Get raw bytes
        pcm_data = response.candidates[0].content.parts[0].inline_data.data
        
        # Gemini TTS defaults: 24kHz, Mono, 16-bit PCM
        # We must save this as a .wav for afplay to understand it
        wav_path = output_path.with_suffix('.wav') 
        
        with wave.open(str(wav_path), "wb") as wf:
            wf.setnchannels(1)          # Mono
            wf.setsampwidth(2)          # 16-bit (2 bytes)
            wf.setframerate(24000)      # 24kHz is standard for Gemini-TTS
            wf.writeframes(pcm_data)
        
        print(f"  Audio saved as WAV: {wav_path.name}")
        return True
        
    except Exception as e:
        print(f"  Audio error: {e}")
        return False

def generate_image(sentence: str, word: str, output_path: Path) -> bool:
    """Generate an image with a fallback strategy if the first attempt is blocked."""
    
    # Use 'ALLOW_ALL' for person_generation to permit images of children
    image_config = {
        "number_of_images": 1,
        "person_generation": "ALLOW_ALL", 
        "aspect_ratio": "1:1",
        "safety_filter_level": "BLOCK_ONLY_HIGH" # Least restrictive setting
    }

    # Attempt 1: The original creative prompt
    prompts_to_try = [
        f"A whimsical, child-friendly cartoon illustration of: {sentence}. Bright colors, simple shapes. The image should be representative of the sentence and not include the sentence text. Image only.",
        f"A simple, cheerful drawing of the object: {word}. High quality 2D art. The image should be representative of the word and not include the word text. Image only." # Fallback prompt
    ]

    for attempt, prompt in enumerate(prompts_to_try):
        try:
            print(f"    Image attempt {attempt + 1}...")
            response = client.models.generate_images(
                model=image_model, 
                prompt=prompt, 
                config=image_config
            )

            if response.generated_images:
                image_bytes = response.generated_images[0].image.image_bytes
                with open(output_path, "wb") as f:
                    f.write(image_bytes)
                return True
            else:
                print(f"    Attempt {attempt + 1} was blocked by safety filters.")

        except Exception as e:
            print(f"    Attempt {attempt + 1} error: {e}")
            continue

    # Level 3 Fallback: If both fail, you could copy a local 'placeholder.png' here
    print(f"  CRITICAL: All image generation attempts failed for '{word}'.")
    return False
    
def process_word(word: str) -> dict:
    """Process a single word and generate all assets."""
    print(f"\nProcessing: {word}")

    result = {
        "id": word,
        "text": word,
    }

    # Generate sentence
    print(f"  Generating sentence...")
    try:
        sentence = generate_sentence(word)
        result["sentence"] = sentence
        print(f"  Sentence: {sentence}")
    except Exception as e:
        print(f"  Error generating sentence: {e}")
        result["sentence"] = f"Le mot est {word}."  # Fallback

    # Generate word audio
    word_audio_path = AUDIO_DIR / f"{word}_word.wav"
    print(f"  Generating word audio...")
    if generate_audio_tts(word, word_audio_path, slow=True):
        result["audioWord"] = f"/audio/{word}_word.wav"
        print(f"  Word audio saved: {word_audio_path.name}")
    else:
        print(f"  Failed to generate word audio")

    # Generate sentence audio
    sentence_audio_path = AUDIO_DIR / f"{word}_sentence.wav"
    print(f"  Generating sentence audio...")
    if generate_audio_tts(result.get("sentence", word), sentence_audio_path):
        result["audioSentence"] = f"/audio/{word}_sentence.wav"
        print(f"  Sentence audio saved: {sentence_audio_path.name}")
    else:
        print(f"  Failed to generate sentence audio")

    # Generate image
    image_path = IMAGES_DIR / f"{word}.png"
    print(f"  Generating image...")
    if generate_image(result.get("sentence", word), word, image_path):
        result["image"] = f"/images/{word}.png"
        print(f"  Image saved: {image_path.name}")
    else:
        print(f"  Failed to generate image (continuing without it)")

    return result


def main():
    """Main function to generate all assets."""
    print("=" * 50)
    print("Dictée Asset Generator")
    print("=" * 50)

    # Read words
    words = read_words()
    print(f"\nFound {len(words)} words to process:")
    for word in words:
        print(f"  - {word}")

    # Process each word
    results = []
    for word in words:
        result = process_word(word)
        results.append(result)

    # Generate manifest
    manifest = {
        "generatedAt": datetime.now().isoformat(),
        "words": results
    }

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 50)
    print(f"Generated manifest: {MANIFEST_FILE}")
    print(f"Total words processed: {len(results)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
