import ollama
import sys
import argparse
import os
from typing import List, Optional

def chat_with_ollama(model: str, message: str, images: Optional[List[bytes]] = None, verbose: bool = False):
    """
    Sends a message, optionally with images, to a local Ollama model and streams the response.

    Args:
        model (str): The name of the model to use (e.g., 'llava', 'gemma3').
        message (str): The prompt or message to send to the model.
        images (Optional[List[bytes]]): A list of image data as bytes.
        verbose (bool): If True, prints statistics at the end of the session.
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

        final_chunk = {}
        # Print each chunk of the response as it arrives
        for chunk in stream:
            print(chunk['message']['content'], end='', flush=True)
            final_chunk = chunk
        
        print("\n\n--- End of response ---")

        if verbose and final_chunk.get('done'):
            print("\n--- Statistics ---")
            # Convert nanoseconds to seconds for readability
            total_duration_s = final_chunk.get('total_duration', 0) / 1e9
            load_duration_s = final_chunk.get('load_duration', 0) / 1e9
            prompt_eval_duration_s = final_chunk.get('prompt_eval_duration', 0) / 1e9
            eval_duration_s = final_chunk.get('eval_duration', 0) / 1e9

            stats = {
                "Model": final_chunk.get('model'),
                "Created At": final_chunk.get('created_at'),
                "Done": final_chunk.get('done'),
                "Total Duration": f"{total_duration_s:.2f}s",
                "Load Duration": f"{load_duration_s:.2f}s",
                "Prompt Eval Count": final_chunk.get('prompt_eval_count'),
                "Prompt Eval Duration": f"{prompt_eval_duration_s:.2f}s",
                "Eval Count": final_chunk.get('eval_count'),
                "Eval Duration": f"{eval_duration_s:.2f}s",
            }
            for key, value in stats.items():
                if value is not None:
                    print(f"{key}: {value}")
            print("------------------")

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
    parser = argparse.ArgumentParser(
        description="A simple command-line tool to interact with local Ollama models.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Examples:
  # Get a joke from the default gemma3 model
  python ochat.py

  # Ask a question to a specific model
  python ochat.py -m llama3 "What is the capital of France?"

  # Send an image to a multimodal model for description
  python ochat.py -m llava -i my_image.png "What do you see in this image?"

  # Use an alias for the image flag and get verbose stats
  python ochat.py -m llava -f my_image.png -v "Describe this."
"""
    )
    parser.add_argument("message", nargs='*', help="The prompt to send to the model. Defaults to 'Tell me a funny joke.' if not provided.")
    parser.add_argument("-m", "--model", default='gemma3', help="The name of the model to use (e.g., 'llava', 'gemma3').")
    parser.add_argument("-i", "--image", nargs='+', help="Optional path(s) to one or more image files to include in the chat.")
    parser.add_argument("-f", "--file", nargs='+', help="Alias for --image.")
    parser.add_argument("-v", "--verbose", action='store_true', help="Print all statistics at the end of the session.")
    args = parser.parse_args()

    # If a message is provided, join it. Otherwise, use the default joke.
    if args.message:
        message = " ".join(args.message)
    else:
        message = "Tell me a funny joke."

    image_paths = []
    if args.image:
        image_paths.extend(args.image)
    if args.file:
        image_paths.extend(args.file)
    
    # Remove duplicates that might result from using both flags
    if image_paths:
        image_paths = list(set(image_paths))

    images_data = []
    if image_paths:
        for image_path in image_paths:
            if not os.path.exists(image_path):
                print(f"Error: Image file not found at '{image_path}'", file=sys.stderr)
                sys.exit(1)
            with open(image_path, "rb") as f:
                images_data.append(f.read())

    # The question is defined, the images are read, and now we call the chat function.
    chat_with_ollama(model=args.model, message=message, images=images_data if images_data else None, verbose=args.verbose)

if __name__ == "__main__":
    main()
