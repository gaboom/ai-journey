# OChat: Ollama Chat CLI

A simple command-line interface to chat with local Ollama models, with support for multimodal interactions including images.

## Features

-   Chat with any Ollama model (e.g., `gemma3`, `llava`).
-   Pass a message as a command-line argument.
-   Include one or more images in the chat.
-   Streams responses from the model.
-   Verbose mode to print session statistics.

## Prerequisites

-   Python 3.6+
-   Ollama installed and running. You can download it from [https://ollama.com/](https://ollama.com/).
-   A pulled Ollama model (e.g., `ollama pull gemma3` or `ollama pull llava`).

## Installation

1.  Navigate to the `ochat` directory.
2.  Install the required Python package:

    ```bash
    pip install ollama
    ```

## Usage

To use the script, run `python ochat.py` from your terminal, followed by your message.

### Basic Usage

If you don't provide a message, it will default to asking for a joke:

```bash
python ochat.py
```

To ask a question:
```bash
python ochat.py "Why is the sky blue?"
```

### Using a Different Model

You can specify a different model using the `-m` or `--model` argument.

```bash
python ochat.py -m llama3 "What is the capital of France?"
```

### Sending Images

To send one or more images, use the `-i`, `--image`, `-f`, or `--file` argument followed by the path(s) to your image(s). This is best used with a multimodal model like `llava`.

**Single Image:**

```bash
python ochat.py -m llava -i /path/to/your/image.png "What is in this image?"
```

**Multiple Images:**

```bash
python ochat.py -m llava -f /path/to/image1.jpg /path/to/image2.png "Describe these images."
```

### Verbose Output

To see session statistics after the response, use the `-v` or `--verbose` flag.

```bash
python ochat.py -v "Tell me a short story."
```

### Help

To see all available options, use the `--help` argument.

```bash
python ochat.py --help
```
