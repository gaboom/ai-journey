import ollama
import sys
import argparse
import os
from typing import List, Optional

def chat_with_ollama(model: str, message: str, images: Optional[List[bytes]] = None):
    """
    Sends a message, optionally with images, to a local Ollama model and streams the response.

    Args:
        model (str): The name of the model to use (e.g., 'llava', 'gemma3').
        message (str): The prompt or message to send to the model.
        images (Optional[List[bytes]]): A list of image data as bytes.
    """
    try:
        # Prepare the message payload
        payload = [{'role': 'user', 'content': message}]
        
        # Add images to the payload if they exist
        if images:
            # The ollama library can handle bytes directly
            payload[0]['images'] = images
            print(f"--- Asking '{model}' (with {len(images)} image(s)): {message} ---\n")
        else:
            print(f"--- Asking '{model}': {message} ---\n")

        # Start the chat and get a streaming response
        stream = ollama.chat(
            model=model,
            messages=payload,
            stream=True,
        )

        # Print each chunk of the response as it arrives
        for chunk in stream:
            print(chunk['message']['content'], end='', flush=True)
        print("\n\n--- End of response ---")

    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)
        if images:
            print("\nWhen providing an image, make sure you are using a multimodal model (e.g., 'llava').", file=sys.stderr)
        print("\nPlease make sure the Ollama application is running and you have pulled the model.", file=sys.stderr)
        print("You can pull a model using a command like: 'ollama pull llava'", file=sys.stderr)
        sys.exit(1)

def main():
    """
    Main function to parse arguments, read optional images, and initiate a chat.
    """
    parser = argparse.ArgumentParser(description="Chat with a local Ollama model, with optional image support.")
    parser.add_argument("message", nargs='*', help="The prompt to send to the model. Defaults to 'Tell me a funny joke.' if not provided.")
    parser.add_argument("--model", default='gemma3', help="The name of the model to use (e.g., 'llava', 'gemma3').")
    parser.add_argument("--image", nargs='+', help="Optional path(s) to one or more image files to include in the chat.")
    args = parser.parse_args()

    # If a message is provided, join it. Otherwise, use the default joke.
    if args.message:
        message = " ".join(args.message)
    else:
        message = "Tell me a funny joke."

    images_data = []
    if args.image:
        for image_path in args.image:
            if not os.path.exists(image_path):
                print(f"Error: Image file not found at '{image_path}'", file=sys.stderr)
                sys.exit(1)
            with open(image_path, "rb") as f:
                images_data.append(f.read())

    # The question is defined, the images are read, and now we call the chat function.
    chat_with_ollama(model=args.model, message=message, images=images_data if images_data else None)

if __name__ == "__main__":
    main()