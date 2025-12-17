import json
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

DEEPL_KEY = "336e1a1b-9df1-404b-b5dc-58c000424800:fx"
DEEPL_URL = "https://api-free.deepl.com/v2/translate"


@app.post("/slack/deepl")
async def deepl_menu(request: Request):
    form = await request.form()
    payload = json.loads(form["payload"])

    response_url = payload["response_url"]

    menu = {
        "response_type": "ephemeral",
        "text": "🌍 Choose the language to translate to:",
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Select target language:*"},
                "accessory": {
                    "type": "static_select",
                    "action_id": "select_language",
                    "placeholder": {"type": "plain_text", "text": "Choose a language"},
                    "options": [
                        {"text": {"type": "plain_text", "text": "English 🇬🇧"}, "value": "EN"},
                        {"text": {"type": "plain_text", "text": "Japanese 🇯🇵"}, "value": "JA"},
                        {"text": {"type": "plain_text", "text": "French 🇫🇷"}, "value": "FR"},
                        {"text": {"type": "plain_text", "text": "German 🇩🇪"}, "value": "DE"},
                    ],
                },
            }
        ],
    }

    requests.post(response_url, json=menu)
    return JSONResponse({"status": "menu_sent"})

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
