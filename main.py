
import json
import requests
from fastapi import FastAPI, Request

app = FastAPI()

DEEPL_KEY = "336e1a1b-9df1-404b-b5dc-58c000424800:fx"   # <-- ta clé DeepL ici
DEEPL_URL = "https://api-free.deepl.com/v2/translate"


@app.post("/slack/deepl")
async def deepl_translate(request: Request):

    form = await request.form()
    payload = json.loads(form["payload"])

    original_text = payload["message"]["text"]
    response_url = payload["response_url"]

    # ======= APPEL À DEEPL =======
    headers = {"Authorization": f"DeepL-Auth-Key {DEEPL_KEY}"}
    data = {
        "text": original_text,
        "target_lang": "EN"   # tu peux mettre EN, DE, ES, etc.
    }

    deepl_result = requests.post(DEEPL_URL, headers=headers, data=data).json()

    # En cas d’erreur DeepL
    if "translations" not in deepl_result:
        message = {
            "response_type": "ephemeral",
            "text": f"❌ Erreur DeepL : {deepl_result}"
        }
        requests.post(response_url, json=message)
        return {}

    translated_text = deepl_result["translations"][0]["text"]

    # ======= ENVOI À SLACK =======
    message = {
        "response_type": "ephemeral",
        "text": f"🟦 *Traduction DeepL :*\n{translated_text}"
    }

    requests.post(response_url, json=message)

    # Slack exige une réponse vide ici
    return {}

