import datetime
import random

# A list of jokes, each as a tuple of (setup, punchline)
JOKES = [
    ("Why do programmers prefer dark mode?", "Because light attracts bugs!"),
    ("Why did the computer go to the doctor?", "Because it had a virus!"),
    ("What's a computer's favorite snack?", "Microchips!"),
]

def get_random_joke(jokes_list=JOKES):
    """Selects a random joke from a list and returns it as a formatted string."""
    setup, punchline = random.choice(jokes_list)
    return f"\n{setup}\n{punchline}"

def main():
    """Prints the current date and time in the UTC+2 timezone, followed by a joke."""
    # Get the current time in UTC, which is timezone-aware
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    # Create a timezone object for UTC+2
    utc_plus_2_tz = datetime.timezone(datetime.timedelta(hours=2))

    # Convert the UTC time to our desired timezone (UTC+2)
    now_in_utc_plus_2 = now_utc.astimezone(utc_plus_2_tz)

    print(f"The current date and time in UTC+2 is: {now_in_utc_plus_2.strftime('%Y-%m-%d %H:%M:%S %z')}")

    # Print a random joke
    print(get_random_joke())

if __name__ == "__main__":
    main()