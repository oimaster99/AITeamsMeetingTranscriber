from pathlib import Path
import sys
from ollama import chat

def summarize_meeting(transcript):
    response = chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a meeting assistant. "
                    "Summarize the provided transcript using "
                    "these sections: Meeting Summary, "
                    "Key Decisions, Action Items, and "
                    "Next Steps. Do not invent details."
                )
            },
            {
                "role": "user",
                "content": transcript
            }
        ]
    )

    return response.message.content


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python app.py <transcript.txt>")
        sys.exit(1)

    transcript = Path(sys.argv[1]).read_text(
        encoding="utf-8"
    )

    print("\nGenerating meeting summary...\n")
    print(summarize_meeting(transcript))
