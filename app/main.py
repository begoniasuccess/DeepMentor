from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

from api.files import fileRouter
from api.questions import questionRouter

app = FastAPI()

# 設定靜態資源路徑
app.mount("/static", StaticFiles(directory="static"), name="static")

# @app.get("/", response_class=FileResponse)
# async def read_root():
#     file_path = os.path.join("templates", "index.html")
#     return FileResponse(file_path)

# 註冊路由
app.include_router(fileRouter)
app.include_router(questionRouter)

@app.get("/", response_class=FileResponse)
async def read_root():
    file_path = os.path.join("templates", "index.html")
    return FileResponse(file_path)