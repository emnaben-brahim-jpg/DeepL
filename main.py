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

    headers = {"Authorization": f"DeepL-Auth-Key {DEEPL_KEY}"}

    # 1) Premier appel : on demande EN pour récupérer la langue détectée
    data_en = {
        "text": original_text,
        "target_lang": "EN",
    }

    deepl_en = requests.post(DEEPL_URL, headers=headers, data=data_en).json()

    if "translations" not in deepl_en:
        requests.post(response_url, json={
            "response_type": "ephemeral",
            "text": f"❌ DeepL error (EN): {deepl_en}"
        })
        return JSONResponse({"status": "error"})

    detected = deepl_en["translations"][0]["detected_source_language"]  # ex: "FR", "EN", "DE", "JA"
    en_text = deepl_en["translations"][0]["text"]

    # 2) Nouvelle logique :
    # FR, JA, DE -> EN
    # EN         -> JA
    # autres     -> EN (par défaut)
    translated_text = None
    target_label = ""

    if detected in ("FR", "JA", "DE"):
        # on garde la traduction anglaise
        translated_text = en_text
        target_label = f"🇬🇧 *Translated to English* (detected: {detected})"
    elif detected == "EN":
        # on traduit vers le japonais
        data_ja = {
            "text": original_text,
            "target_lang": "JA",
        }
        deepl_ja = requests.post(DEEPL_URL, headers=headers, data=data_ja).json()

        if "translations" not in deepl_ja:
            requests.post(response_url, json={
                "response_type": "ephemeral",
                "text": f"❌ DeepL error (JA): {deepl_ja}"
            })
            return JSONResponse({"status": "error"})

        translated_text = deepl_ja["translations"][0]["text"]
        target_label = "🇯🇵 *Translated to Japanese* (detected: EN)"
    else:
        # fallback
        translated_text = en_text
        target_label = f"🇬🇧 *Translated to English (default for {detected})*"

    # 3) Envoi à Slack
    message = {
        "response_type": "ephemeral",
        "text": f"{target_label}\n{translated_text}"
    }

    requests.post(response_url, json=message)

    return JSONResponse({"status": "ok"})
