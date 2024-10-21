import os

from flask import Flask, jsonify
from pymongo import MongoClient

CONFIG = {
    "SCOREBOARD":   os.getenv('SCOREBOARD', 'http://127.0.0.1:8090'),
    "TEAM":         os.getenv('TEAM', 'Red Cadets'),
    "TYPE":         os.getenv('TYPE', 'forcad'),
    "BOT_URL":      os.getenv('BOT_URL', 'https://bot.example.com/key'),
    "MONGO_USER":   os.getenv('MONGO_USER', 'parser'),
    "MONGO_PASS":   os.getenv('MONGO_PASS', 'parser'),
    "ROUND_TIME":   int(os.getenv('ROUND_TIME', '120')),
    "EXTEND_ROUND": int(os.getenv('EXTEND_ROUND', '50'))
}

app = Flask(__name__)

mongo_client = MongoClient(
    f"mongodb://{CONFIG['MONGO_USER']}:{CONFIG['MONGO_PASS']}@mongo:27017/")
db = mongo_client.parse

info = db.data
teamInfo = db.team_info


@app.route('/api/info')
def index():
    DATA = []
    cursor = info.find({})
    for document in cursor:
        del(document['_id'])
        DATA.append(document)
    return jsonify(DATA)


@app.route('/api/team_info')
def team_info():
    DATA = []
    cursor = teamInfo.find({})
    for document in cursor:
        del(document['_id'])
        DATA.append(document)
    return jsonify(DATA)


@app.route('/api/config')
def config():
    return jsonify(CONFIG)


if __name__ == "__main__":
    app.run("0.0.0.0", 8888)
