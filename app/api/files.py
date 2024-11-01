from fastapi import APIRouter, FastAPI, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from datetime import datetime
from typing import List, Annotated, Optional
import time

import models
from database import SessionLocal, Base, engine
from sqlalchemy.orm import Session

fileRouter = APIRouter()

# 在資料庫中建立剛剛models中設定好的資料結構
models.Base.metadata.create_all(bind=engine)

# Pydantic 模型定義
class FileBase(BaseModel):
    # id:int
    fileName:str
    uploadedAt: Optional[int]=None
    fileType:int
    status:int
    parsedPath:Optional[str] = None

# 獲取資料庫會話
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# CREATE
@fileRouter.post("/api/files")
async def create_files(file: FileBase, db:db_dependency):
    new_file = models.Files(
        fileName=file.fileName,
        uploadedAt=int(time.time()),
        fileType=file.fileType,
        status=file.status,
        parsedPath=file.parsedPath
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return JSONResponse(
        content={"message": "success", "data": {"id": new_file.id}},
        status_code=status.HTTP_201_CREATED
    )

# READ
@fileRouter.get('/api/files/{file_id}')
async def read_question(file_id:int, db:db_dependency):
    result = db.query(models.Files).filter(models.Files.id == file_id).first()
    if not result:
        raise HTTPException(status_code=404, detail='File is not found.')
    data = {"id": result.id, "fileName": result.fileName, "uploadedAt": result.uploadedAt, "fileType": result.fileType, "status": result.status, "parsedPath": result.parsedPath} 
    return JSONResponse(content={"message": "success", "data": data})

# READ All
@fileRouter.get('/api/files')
async def read_question(db:db_dependency):
    result = db.query(models.Files).all()
    if not result:
        raise HTTPException(status_code=404, detail='No file exists.')
    data_list = [{"id": item.id, "fileName": item.fileName, "uploadedAt": item.uploadedAt, "fileType": item.fileType, "status": item.status, "parsedPath": item.parsedPath} for item in result]
    return JSONResponse(content={"message": "success", "data": data_list})

# DELETE
@fileRouter.delete('/api/files/{file_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_id: int, db: db_dependency):
    # 查询要删除的文件
    file_to_delete = db.query(models.Files).filter(models.Files.id == file_id).first()
    
    if not file_to_delete:
        raise HTTPException(status_code=404, detail='File not found.')
    
    # 从数据库会话中删除文件
    db.delete(file_to_delete)
    db.commit()  # 提交事务以应用更改

    return JSONResponse(content={"message": "success", "data": {}})  # 返回成功消息，数据为空