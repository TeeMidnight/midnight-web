# frontend/app.py
from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

#
API_BASE = "http://localhost:8000/api"

def fetch_data(endpoint):
    try:
        resp = requests.get(f"{API_BASE}/{endpoint}", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
        return []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/team")
def team():
    organizations = fetch_data("organizations")
    return render_template("team.html", organizations=organizations)

@app.route("/about")
def about():
    philosophy = fetch_data("philosophy")
    goals = fetch_data("goals")
    return render_template("about.html", philosophy=philosophy, goals=goals)

@app.route("/status")
def status():
    servers = fetch_data("servers")
    return render_template("status.html", servers=servers)

@app.route("/rules")
def rules():
    rules = fetch_data("rules")
    return render_template("rules.html", rules=rules)

# 错误处理
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)