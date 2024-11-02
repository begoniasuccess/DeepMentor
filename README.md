## 專案說明

本專案是一個基於 FastAPI 開發的PDF文件轉換服務，使用 PostgreSQL 作為後端資料庫，提供文件的上傳與管理功能。
此外，本專案藉由 Docker 和 Docker Compose 整合 PostgreSQL、pgAdmin 與 FastAPI 應用，便於開發者及協作者快速部署和測試此服務。

## 開發環境設定

### 前置需求
- [Docker](https://docs.docker.com/get-docker/)（包含 Docker Compose）
- [Git](https://git-scm.com/)

### 設置步驟
1. **專案複製到本地**：
   ```bash
   git clone https://github.com/begoniasuccess/DeepMentor.git
   cd DeepMentor

2. **Docker Compose 啟動專案**： 
    在專案目錄下執行以下命令以啟動所有服務（包括 FastAPI、PostgreSQL 和 pgAdmin）：
    ```bash
    docker compose up -d

3. **訪問服務**： 
    FastAPI 應用程式: http://localhost:8000
    pgAdmin 管理界面: http://localhost（預設帳號為 admin@admin.com，密碼為 admin）