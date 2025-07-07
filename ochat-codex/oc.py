#!/usr/bin/env python3
"""Send a question to a local Ollama LLM and print the response.
Optionally pass file(s) to the model (e.g. images)."""
import sys
import argparse

from ollama import chat, RequestError, ResponseError


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Send a question to a local Ollama model and print the response. "
            "Optionally pass file(s) to the model (e.g. images)."
        )
    )
    parser.add_argument(
        "-m", "--model",
        default="gemma3",
        help="Name of the local model (default: gemma3)",
    )
    parser.add_argument(
        "-f", "--files",
        nargs="+",
        help="File(s) to pass to the model (e.g. images)",
    )
    parser.add_argument(
        "question",
        nargs="+",
        help="Question to ask the model",
    )
    args = parser.parse_args()
    question = " ".join(args.question)

    try:
        chat_kwargs = {
            "model": args.model,
            "messages": [{"role": "user", "content": question}],
            "stream": True,
        }
        if args.files:
            chat_kwargs["files"] = args.files
        for chunk in chat(**chat_kwargs):
            if chunk.message.content is not None:
                print(chunk.message.content, end="", flush=True)
        print()
    except RequestError as e:
        print(f"Request error: {e}", file=sys.stderr)
        return 1
    except ResponseError as e:
        print(f"Response error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())