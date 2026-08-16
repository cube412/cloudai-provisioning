import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)
SECRET = os.getenv("PROVISIONING_SECRET", "")
CONFIG_FILE = os.getenv("CONFIG_FILE", "bot_configs.json")


def load():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def authorized():
    if not SECRET:
        return True
    return request.headers.get("Authorization") == f"Bearer {SECRET}"


@app.post("/provision")
def provision():
    if not authorized():
        return jsonify({"error": "unauthorized"}), 401

    cfg = request.get_json(silent=True) or {}
    guild_id = str(cfg.get("guild_id", "")).strip()

    if not guild_id:
        return jsonify({"error": "guild_id required"}), 400

    data = load()
    data[guild_id] = cfg
    save(data)

    return jsonify({"ok": True, "guild_id": guild_id})


@app.get("/configs/<guild_id>")
def get_config(guild_id):
    if not authorized():
        return jsonify({"error": "unauthorized"}), 401

    cfg = load().get(str(guild_id))
    if not cfg:
        return jsonify({"error": "not found"}), 404

    return jsonify(cfg)


@app.get("/health")
def health():
    return jsonify({"ok": True})


app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
