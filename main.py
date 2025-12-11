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

    # 1) Premier appel : EN (pour détecter la langue source)
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

    # 2) Logique de traduction
    message_text = ""

    # 🇫🇷, 🇯🇵 -> 🇬🇧
    if detected in ("FR", "JA"):
        message_text = f"🇬🇧 *Translated to English* (detected: {detected})\n{en_text}"

    # 🇬🇧 -> 🇯🇵
    elif detected == "EN":
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

        ja_text = deepl_ja["translations"][0]["text"]
        message_text = f"🇯🇵 *Translated to Japanese* (detected: EN)\n{ja_text}"

    # 🇩🇪 -> 🇬🇧 + 🇯🇵
    elif detected == "DE":
        # EN version already computed: en_text
        message_text = f"🇬🇧 *To English*:\n{en_text}\n\n"

        # then Japanese
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

        ja_text = deepl_ja["translations"][0]["text"]
        message_text += f"🇯🇵 *To Japanese*:\n{ja_text}"

    # autres langues -> EN
    else:
        message_text = f"🇬🇧 *Translated to English* (detected: {detected})\n{en_text}"

    # 3) Slack response
    response_message = {
        "response_type": "ephemeral",
        "text": message_text
    }

    requests.post(response_url, json=response_message)

    return JSONResponse({"status": "ok"})
