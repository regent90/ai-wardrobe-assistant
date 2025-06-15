# AI 智慧衣櫥搭配助手 - 本地部署指南

本指南將引導您如何在本地電腦上部署 AI 智慧衣櫥搭配助手網站。此專案包含一個 Flask 後端和一個 React 前端。

## 1. 環境準備

在開始部署之前，請確保您的電腦上已安裝以下軟體和工具：

*   **Python 3.9+**: [下載連結](https://www.python.org/downloads/)
*   **Node.js 18+ & npm (或 pnpm)**: [下載連結](https://nodejs.org/en/download/)
    *   建議安裝 `pnpm`，它能更有效地管理前端依賴：
        ```bash
        npm install -g pnpm
        ```
*   **Git**: [下載連結](https://git-scm.com/downloads)

## 2. 專案解壓縮

1.  下載我提供的 `ai_wardrobe_assistant_website.zip` 壓縮包。
2.  將壓縮包解壓縮到您選擇的目錄，例如 `C:\ai_wardrobe_assistant_website` (Windows) 或 `~/ai_wardrobe_assistant_website` (macOS/Linux)。

    解壓縮後，您會看到兩個主要資料夾：`wardrobe_backend` (後端) 和 `wardrobe_frontend` (前端)。

## 3. 後端部署 (Flask)

1.  **開啟終端機/命令提示字元**，並導航到後端專案目錄：
    ```bash
    cd path/to/your/extracted/folder/wardrobe_backend
    cd wardrobe_backend
    ```
    (請將 `path/to/your/extracted/folder` 替換為您實際解壓縮的路徑)

2.  **建立並啟用 Python 虛擬環境** (強烈建議，以避免依賴衝突)：
    *   macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   Windows:
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```

3.  **安裝後端依賴**：
    ```bash
    pip install -r requirements.txt
    ```

4.  **配置環境變數 (Gemini API Key)**：
    *   在 `wardrobe_backend` 目錄下，找到 `src/.env.example` 檔案。
    *   將 `src/.env.example` 複製一份並重新命名為 `src/.env`。
    *   開啟 `src/.env` 檔案，並將 `GEMINI_API_KEY="YOUR_GEMINI_API_KEY"` 中的 `YOUR_GEMINI_API_KEY` 替換為您的 Google Gemini API Key。
        *   如果您沒有 Gemini API Key，可以前往 [Google AI Studio](https://aistudio.google.com/app/apikey) 獲取。

5.  **啟動後端服務**：
    ```bash
    python src/reset_db.py
    python src/main.py
    ```
    您會看到類似 `* Running on http://127.0.0.1:5000` 的輸出，表示後端服務已成功啟動並在 `http://localhost:5000` 運行。

    **請保持此終端機視窗開啟，以便後端服務持續運行。**

## 4. 前端部署 (React)

1.  **開啟另一個終端機/命令提示字元**，並導航到前端專案目錄：
    ```bash
    cd path/to/your/extracted/folder/wardrobe_frontend
    cd wardrobe_frontend
    ```
    (請將 `path/to/your/extracted/folder` 替換為您實際解壓縮的路徑)

2.  **安裝前端依賴**：
    ```bash
    pnpm install
    # 或者如果您使用 npm:
    # npm install
    ```

3.  **構建前端應用**：
    ```bash
    pnpm run build
    # 或者如果您使用 npm:
    # npm run build
    ```
    這會將前端應用程式編譯到 `dist` 資料夾中。

4.  **啟動前端開發伺服器**：
    ```bash
    pnpm run dev
    # 或者如果您使用 npm:
    # npm run dev
    ```
    您會看到類似 `Local: http://localhost:5173/` 的輸出，表示前端開發伺服器已成功啟動並在 `http://localhost:5173` 運行。

    **請保持此終端機視窗開啟，以便前端服務持續運行。**

## 5. 訪問網站

現在，您可以在瀏覽器中打開以下網址來訪問 AI 智慧衣櫥搭配助手網站：

[http://localhost:5173](http://localhost:5173)

**重要提示：**
*   請確保後端和前端服務都已成功啟動並在各自的終端機中運行。
*   如果您在訪問網站時遇到「服務連接失敗」的提示，請檢查後端服務是否正常運行，並確保您的 Gemini API Key 已正確配置。

祝您使用愉快！

