# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend/ /app/backend/

COPY frontend/ /app/frontend/

# 暴露 FastAPI (8000) 和 Flask (5000)
EXPOSE 8000 5000

# 启动脚本：同时运行 FastAPI 和 Flask
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & python /app/frontend/app.py"]