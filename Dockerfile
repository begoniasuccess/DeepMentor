# 使用官方的 Ubuntu 基底映像
FROM ubuntu:22.04

# 安裝 Python 和 pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip libgl1 && \
    apt-get clean
    
# 設定工作目錄
WORKDIR /code

# 複製 requirements.txt 到容器中
COPY ./requirements.txt /code/requirements.txt

# 安裝所需的依賴
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt
# RUN pip install fastapi pydantic sqlalchemy databases asyncpg

COPY ./app /code/app

# 設定環境變數
ENV PYTHONUNBUFFERED=1

# 暴露應用的端口
EXPOSE 8000

# 指定啟動應用的命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
