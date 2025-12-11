import json
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

DEEPL_KEY = "336e1a1b-9df1-404b-b5dc-58c000424800:fx"
DEEPL_URL = "https://api-free.deepl.com/v2/translate"


@app.post("/slack/deepl")
async def deepl_translate(request: Request):

    form = await request.form()
    payload = json.loads(form["payload"])

    original_text = payload["message"]["text"]
    response_url = payload["response_url"]

    # ======= Traduction -> toujours en anglais =======
    headers = {"Authorization": f"DeepL-Auth-Key {DEEPL_KEY}"}
    data = {
        "text": original_text,
        "target_lang": "EN"   # <- Toujours en anglais 🇬🇧
    }

    deepl_result = requests.post(DEEPL_URL, headers=headers, data=data).json()

    # En cas d’erreur DeepL
    if "translations" not in deepl_result:
        message = {
            "response_type": "ephemeral",
            "text": f"❌ DeepL Error: {deepl_result}"
        }
        requests.post(response_url, json=message)
        return JSONResponse({"status": "error"})

    translated_text = deepl_result["translations"][0]["text"]

    # ======= Réponse Slack =======
    message = {
        "response_type": "ephemeral",
        "text": f"🇬🇧 *Translated to English:*\n{translated_text}"
    }

    requests.post(response_url, json=message)

    return JSONResponse({"status": "ok"})


# Optional: route de test Render
@app.get("/")
def home():
    return {"status": "ok", "message": "DeepL Slack translator running"}

