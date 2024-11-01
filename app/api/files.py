from fastapi import APIRouter, status, HTTPException, Depends, FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from datetime import datetime
from typing import List, Annotated, Optional
import time
import shutil
import os

import models
from database import SessionLocal, Base, engine
from sqlalchemy import delete
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
    status:Optional[int]=None
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
    # 防止重複的fileName出現
    result = db.query(models.Files).filter(models.Files.fileName == file.fileName).first()
    if result:
        raise HTTPException(status_code=404, detail='This file name already exists!')

    new_file = models.Files(
        fileName=file.fileName,
        uploadedAt=int(time.time()),
        fileType=file.fileType,
        status=models.Status.Uploading.value
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return JSONResponse(
        content={"message": "success", "data": new_file.id},
        status_code=status.HTTP_201_CREATED
    )

# READ
@fileRouter.get('/api/files/{id}')
async def read_question(id:int, db:db_dependency):
    result = db.query(models.Files).filter(models.Files.id == id).first()
    if not result:
        raise HTTPException(status_code=404, detail='File not found.')
    data = {"id": result.id, "fileName": result.fileName, "uploadedAt": result.uploadedAt, "fileType": result.fileType, "status": result.status, "parsedPath": result.parsedPath} 
    return JSONResponse(content={"message": "success", "data": data})

# READ All
@fileRouter.get('/api/files')
async def read_question(db:db_dependency):
    result = db.query(models.Files).all()
    if not result:
        return JSONResponse(content={"message": "success", "data": []})
    data_list = [{"id": item.id, "fileName": item.fileName, "uploadedAt": item.uploadedAt, "fileType": item.fileType, "status": item.status, "parsedPath": item.parsedPath} for item in result]
    return JSONResponse(content={"message": "success", "data": data_list})

# DELETE
@fileRouter.delete('/api/files/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(id: int, db: db_dependency):
    # 查询要删除的文件
    file_to_delete = db.query(models.Files).filter(models.Files.id == id).first()
    
    if not file_to_delete:
        raise HTTPException(status_code=404, detail='File not found.')
    
    # 从数据库会话中删除文件
    db.delete(file_to_delete)
    db.commit()  # 提交事务以应用更改

    return JSONResponse(content={"message": "success", "data": {}})  # 返回成功消息，数据为空


UPLOAD_DIRECTORY = "./uploads"

# Upload
@fileRouter.post("/api/upload/{id}")
async def upload_file(id: int, db:db_dependency, file: UploadFile = File(...)):
    result = db.query(models.Files).filter(models.Files.id == id).first()
    if not result:
        raise HTTPException(status_code=404, detail='File not found.')
    
    if not file:
        raise HTTPException(status_code=404, detail='Please select a file.')
    
    try:
        # 上傳檔案
        if not os.path.exists(UPLOAD_DIRECTORY):
            os.makedirs(UPLOAD_DIRECTORY)

        file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)  # 保存文件

        # 修改紀錄
        result.status = models.Status.Parsing.value
        db.commit()
        db.refresh(result)

        return JSONResponse(content={"message": "success", "filename": file.filename}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Parse
@fileRouter.post("/api/parse/{id}")
async def parse_file(id: int, db:db_dependency):
    result = db.query(models.Files).filter(models.Files.id == id).first()
    if not result:
        raise HTTPException(status_code=404, detail='File not found.')
    
    file_path = UPLOAD_DIRECTORY + "/" + result.fileName
    if not (os.path.exists(file_path) and os.path.isfile(file_path)):
        db.delete(result)
        db.commit()
        raise HTTPException(status_code=404, detail="File does not exist.")
    
    
    try:



        # 修改紀錄
        result.status = models.Status.Completed.value
        db.commit()
        db.refresh(result)

        return JSONResponse(content={"message": "success"}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# RESET
@fileRouter.delete('/api/reset', status_code=status.HTTP_204_NO_CONTENT)
async def reset_system(db: db_dependency):
    # 刪除資料庫紀錄
    file_to_delete = db.query(models.Files).all()
    
    if file_to_delete:
        try:
            # 刪除特定模型表的所有資料
            db.execute(delete(models.Files))
            db.commit()
            print("所有資料已成功刪除。")
        except Exception as e:
            db.rollback()
            print(f"刪除失敗: {e}")

    # 刪除檔案
    if os.path.exists(UPLOAD_DIRECTORY):
        for filename in os.listdir(UPLOAD_DIRECTORY):
            file_path = os.path.join(UPLOAD_DIRECTORY, filename)            
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"刪除 {file_path} 時發生錯誤: {e}")

    return JSONResponse(content={"message": "success", "data": {}})  # 返回成功消息，数据为空