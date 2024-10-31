# 使用 Python 基礎映像
FROM python:3.9-slim

# 安裝相關套件
RUN pip install fastapi pydantic sqlalchemy databases asyncpg psycopg2

# 設定工作目錄
WORKDIR /app

# 複製當前目錄內容到容器中
COPY /app /app

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 運行 FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
