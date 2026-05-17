import ollama
from robie.intents import Intent


def parse_with_qwen(transcript: str, available_titles: list[str]) -> Intent:
    schema = Intent.model_json_schema()

    prompt = f"""
Tu es le module de reconnaissance d'intention de Robie.

Phrase entendue :
{transcript}

Titres disponibles sur le disque :
{available_titles}

Tu dois choisir une intention.
Pour un audiobook, choisis uniquement un titre présent dans la liste.
Produis une question de confirmation courte en français.
Exemple :
"Tu veux lire Les Royaumes de feu tome 4 depuis le début ?"
"""

    response = ollama.chat(
        model="qwen2.5:0.5b",
        messages=[{"role": "user", "content": prompt}],
        format=schema,
    )

    return Intent.model_validate_json(response["message"]["content"])
