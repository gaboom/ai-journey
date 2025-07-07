# OChat: Ollama Chat CLI

A simple command-line interface to chat with local Ollama models, with support for multimodal interactions including images.

## Features

-   Chat with any Ollama model (e.g., `gemma3`, `llava`).
-   Pass a message as a command-line argument.
-   Include one or more images in the chat.
-   Streams responses from the model.

## Prerequisites

-   Python 3.6+
-   Ollama installed and running. You can download it from [https://ollama.com/](https://ollama.com/).
-   A pulled Ollama model (e.g., `ollama pull gemma3` or `ollama pull llava`).

## Installation

1.  Clone this repository or download the `ochat.py` script.
2.  Install the required Python package:

    ```bash
    pip install ollama
    ```

## Usage

To use the script, run `ochat.py` from your terminal, followed by your message.

### Basic Usage

```bash
python ochat.py "Why is the sky blue?"
```

If you don't provide a message, it will default to asking for a joke:

```bash
python ochat.py
```

### Using a Different Model

You can specify a different model using the `--model` argument.

```bash
python ochat.py "What is the capital of France?" --model gemma3
```

### Sending Images

To send one or more images, use the `--image` argument followed by the path(s) to your image(s). This is best used with a multimodal model like `llava`.

**Single Image:**

```bash
python ochat.py "What is in this image?" --image /path/to/your/image.png --model llava
```

**Multiple Images:**

```bash
python ochat.py "Describe these images." --image /path/to/image1.jpg /path/to/image2.png --model llava
```

### Help

To see all available options, use the `--help` argument.

```bash
python ochat.py --help
```
