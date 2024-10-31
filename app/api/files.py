from fastapi import APIRouter, FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

router = APIRouter()

# 模擬的資料庫
files_db = {}

# Pydantic 模型定義
class File(BaseModel):
    id: int
    fileName: str
    uploadedAt: int
    fileType: int
    status: int
    paresdFile: str = None

# 取得(All)
@router.get("/api/files", response_model=List[File])
async def get_files():
    # return list(files_db.values())
    return JSONResponse(content={"message": "Developing！"}, status_code=500)

# 取得
@router.get('/api/files/{file_id}', response_model=File)
async def get_file(file_id: int):
    # file = files_db.get(file_id)
    # if file is None:
    #     raise HTTPException(status_code=404, detail="file not found")
    # return file
    return JSONResponse(content={"message": "Developing！"}, status_code=500)

# 新增
# @files_bp.route('/api/files', methods=['POST'])
@router.post("/api/files", response_model=File, status_code=status.HTTP_201_CREATED)
async def insert_file(file: File):
    print(File)
    # file_id = len(files_db) + 1
    # files_db[file_id] = file
    # return file
    return JSONResponse(content={"message": "Developing！"}, status_code=500)


# 刪除
@router.delete("/api/files/{files_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(files_id: int):
    # if files_id not in files_db:
    #     raise HTTPException(status_code=404, detail="file not found")
    # del files_db[files_id]
    # return {"detail": "file deleted"}
    return JSONResponse(content={"message": "Developing！"}, status_code=500)

# Upload
@router.post("/api/upload/{files_id}", status_code=status.HTTP_204_NO_CONTENT)
async def upload_file(files_id: int):

    return JSONResponse(content={"message": "Developing！"}, status_code=500)