import json
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

DEEPL_KEY = "336e1a1b-9df1-404b-b5dc-58c000424800:fx"
DEEPL_URL = "https://api-free.deepl.com/v2/translate"


@app.post("/slack/language")
async def deepl_translate_selected(request: Request):
    form = await request.form()
    payload = json.loads(form["payload"])

    # DEBUG utile dans les logs Render
    print("INTERACTIVITY PAYLOAD TYPE:", payload.get("type"))

    # Langue choisie
    target_lang = payload["actions"][0]["selected_option"]["value"]

    # Texte original (Slack le fournit normalement ici)
    original_text = payload.get("message", {}).get("text", "")

    if not original_text:
        return JSONResponse({
            "response_type": "ephemeral",
            "text": "❌ I couldn't read the original message text from Slack payload."
        })

    headers = {"Authorization": f"DeepL-Auth-Key {DEEPL_KEY}"}
    data = {"text": original_text, "target_lang": target_lang}

    deepl_result = requests.post(DEEPL_URL, headers=headers, data=data).json()

    if "translations" not in deepl_result:
        return JSONResponse({
            "response_type": "ephemeral",
            "text": f"❌ DeepL error: {deepl_result}"
        })

    translated_text = deepl_result["translations"][0]["text"]

    return JSONResponse({
        "response_type": "ephemeral",
        "text": f"✅ *Translation ({target_lang}):*\n{translated_text}"
    })

@app.post("/slack/language")
async def deepl_translate_selected(request: Request):
    form = await request.form()
    payload = json.loads(form["payload"])

    # Langue choisie
    target_lang = payload["actions"][0]["selected_option"]["value"]

    # Texte original (Slack le met généralement ici)
    original_text = payload["message"]["text"]

    headers = {"Authorization": f"DeepL-Auth-Key {DEEPL_KEY}"}
    data = {"text": original_text, "target_lang": target_lang}

    deepl_result = requests.post(DEEPL_URL, headers=headers, data=data).json()

    if "translations" not in deepl_result:
        # IMPORTANT: on renvoie l'erreur directement à Slack
        return JSONResponse({
            "response_type": "ephemeral",
            "text": f"❌ DeepL error: {deepl_result}"
        })

    translated_text = deepl_result["translations"][0]["text"]

    # IMPORTANT: renvoyer DIRECTEMENT la réponse à Slack
    return JSONResponse({
        "response_type": "ephemeral",
        "text": f"✅ *Translation ({target_lang}):*\n{translated_text}"
    })
