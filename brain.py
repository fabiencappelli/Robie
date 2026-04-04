import json
import requests

PROMPT_SYSTEM = """
You are the control brain of a small home robot for children.
Return only valid JSON.

Possible intents:
- greet
- take_note
- play_sound
- unknown

Rules:
- If the user wants to store or remember something, use "take_note"
- If the user greets the robot, use "greet"
- If the user asks for a sound/noise, use "play_sound"
- Otherwise use "unknown"

JSON format:
{
  "intent": "greet|take_note|play_sound|unknown",
  "content": "string",
  "answer": "short spoken reply"
}
"""

user_text = "Robie, note that Thomas needs his coat tomorrow."

payload = {
    "model": "qwen2.5:1.5b",
    "format": "json",
    "stream": False,
    "messages": [
        {"role": "system", "content": PROMPT_SYSTEM},
        {"role": "user", "content": user_text}
    ]
}

response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
response.raise_for_status()

data = response.json()
content = data["message"]["content"]

print("Raw model output:")
print(content)

parsed = json.loads(content)
print("\nParsed JSON:")
print(json.dumps(parsed, indent=2, ensure_ascii=False))