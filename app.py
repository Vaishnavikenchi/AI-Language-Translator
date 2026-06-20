import requests
from requests.sessions import Session
import urllib3

# Disable SSL verification for development environments with missing local certificates
original_send = Session.send
def unverified_send(self, request, **kwargs):
    kwargs['verify'] = False
    return original_send(self, request, **kwargs)
Session.send = unverified_send
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator

app = Flask(__name__)

try:
    langs_dict = GoogleTranslator().get_supported_languages(as_dict=True)
    LANGUAGES = {code: name.title() for name, code in langs_dict.items()}
    LANGUAGES = dict(sorted(LANGUAGES.items(), key=lambda item: item[1]))
except Exception:
    # Robust fallback list if offline or lookup fails
    LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "mr": "Marathi",
        "fr": "French",
        "de": "German",
        "es": "Spanish",
        "ja": "Japanese",
        "ko": "Korean",
        "zh-cn": "Chinese"
    }

@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/translator", methods=["GET", "POST"])
def translator_app():
    translated_text = ""

    if request.method == "POST":
        text = request.form["text"]
        source_lang = request.form["source"]
        target_lang = request.form["target"]

        try:
            translated_text = GoogleTranslator(
                source=source_lang,
                target=target_lang
            ).translate(text)

        except Exception:
            translated_text = "Translation Error!"

    return render_template(
        "index.html",
        languages=LANGUAGES,
        translated_text=translated_text
    )

@app.route("/api/translate", methods=["POST"])
def translate_api():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400
        
        text = data.get("text", "")
        source_lang = data.get("source", "auto")
        target_lang = data.get("target", "en")
        
        if not text.strip():
            return jsonify({"translated_text": ""})
            
        translated_text = GoogleTranslator(
            source=source_lang,
            target=target_lang
        ).translate(text)
        
        return jsonify({"translated_text": translated_text})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)