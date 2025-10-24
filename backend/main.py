# backend/main.py
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from . import twinfo
from contextlib import asynccontextmanager

import markdown

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ORGANIZATIONS: dict
PHILOSOPHY: dict
GOALS: dict
RULES: str


def load_json(filename: str):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_markdown(filename: str):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return markdown.markdown(f.read())

# ======== Lifespan 管理器 ========
@asynccontextmanager
async def lifespan(app: FastAPI):
    global ORGANIZATIONS, PHILOSOPHY, GOALS, RULES
    print("应用正在启动...")

    # 启动时执行
    ORGANIZATIONS = load_json("organizations.json")
    PHILOSOPHY = load_json("philosophy.json")
    GOALS = load_json("goals.json")
    RULES = load_markdown("rules.md")

    await twinfo.init()

    print("应用初始化完成，已加载数据并建立会话。")
    yield

    print("应用正在关闭...")
    await twinfo.shutdown()
    print("会话已关闭。")

# ======== 创建 FastAPI 实例 ========
app = FastAPI(
    title="Mid·Night Teeworlds 官网 API",
    description="基于 JSON 的轻量级后端",
    version="1.0.0",
    lifespan=lifespan
)

# ======== 添加中间件 ========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === API 路由 ===
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

@app.get("/api/servers")
async def get_server_status():
    return await twinfo.get_server_list()

@app.get("/api/organizations")
def get_organizations():
    return ORGANIZATIONS

@app.get("/api/philosophy")
def get_philosophy():
    return PHILOSOPHY

@app.get("/api/goals")
def get_goals():
    return GOALS

@app.get("/api/rules")
def get_rules():
    return RULES

@app.get("/")
def home():
    return {"message": "Mid·Night API is running. Visit /docs for Swagger UI."}

