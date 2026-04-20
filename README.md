# KGI 動態測驗引擎

一個互動式微學習測驗系統，專為通勤或零碎時間設計。支援無感遙測記錄、AI 教練回饋，以及錯題報告。

## 專案架構

```
KGI_/
├── dynamic-quiz-engine/
│   └── backend/
│       ├── main.py              # FastAPI 後端主程式
│       ├── models.py            # Pydantic 資料模型
│       ├── requirements         # Python 相依套件
│       └── db/
│           └── schema.sql       # SQLite 資料庫結構
├── src/
│   ├── App.jsx                  # React 主應用程式
│   ├── components/
│   │   ├── QuizCard.jsx         # 測驗題目元件
│   │   └── AiCoachModal.jsx     # AI 教練彈窗元件
│   ├── services/
│   │   └── telemetry.js         # 遙測資料記錄服務
│   ├── main.jsx                 # React 應用程式入口
│   └── index.css                # 全域樣式
├── package.json                 # Node.js 專案設定
├── vite.config.js               # Vite 建構工具設定
└── index.html                   # HTML 模板
```

## 功能特色

- **7 分鐘微學習**：一次顯示一個問題，適合零碎時間學習
- **無感遙測**：背景記錄點擊、懸停、作答時間等互動數據
- **AI 教練**：答錯時提供鼓勵與解釋回饋
- **錯題報告**：完成測驗後顯示錯題總結
- **響應式設計**：支援桌面與行動裝置

## 技術棧

### 前端
- **React 19**：現代化 UI 框架
- **Vite**：快速建構工具
- **Bootstrap 5**：CSS 框架
- **ESLint**：程式碼品質檢查

### 後端
- **FastAPI**：高性能 Python Web 框架
- **SQLite**：輕量級資料庫
- **Pydantic**：資料驗證

## 安裝與執行

### 環境需求
- Python 3.12+
- Node.js 18+
- npm 或 yarn

### 後端設定

1. 安裝 Python 相依套件：
```bash
cd dynamic-quiz-engine/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements
```

2. 啟動後端伺服器：
```bash
uvicorn main:app --reload
```
伺服器將在 `http://127.0.0.1:8000` 運行。

3. 若要查看遙測資料：
```bash
python view_data.py
```

### 前端設定

1. 安裝 Node.js 相依套件：
```bash
npm install
```

2. 啟動開發伺服器：
```bash
npm run dev
```
前端將在 `http://localhost:5173` 運行。

### 如何測試

#### 後端
```bash
cd /Users/chenpinyu/Desktop/KGI_/dynamic-quiz-engine/backend
source venv/bin/activate
uvicorn main:app --reload
```

#### 前端
```bash
cd /Users/chenpinyu/Desktop/KGI_
npm run dev
```

前端將在 `http://localhost:5173` 運行。

#### 查看遙測資料
```bash
cd /Users/chenpinyu/Desktop/KGI_/dynamic-quiz-engine/backend
python view_data.py
```

## API 端點

### 測驗相關
- `GET /api/quiz/module/{module_id}`：獲取指定模組的題目
- `POST /api/telemetry/submit`：提交遙測數據
- `POST /api/ai/coach`：請求 AI 教練回饋

### 系統
- `GET /`：健康檢查

## 資料庫結構

### QuizQuestions
- `id`: 主鍵
- `module_id`: 模組 ID
- `content`: 題目內容
- `options_json`: 選項 JSON
- `correct_key`: 正確答案鍵

### TelemetryLogs
- `session_id`: 測驗階段 ID
- `question_id`: 題目 ID
- `event_type`: 事件類型 (select/hover)
- `event_value`: 事件值
- `elapsed_ms`: 經過時間
- `timestamp`: 時間戳

### AiFeedbackArchive
- `id`: 主鍵
- `question`: 題目
- `wrong_answer`: 錯誤答案
- `feedback`: AI 回饋

## 開發指南

### 新增題目
編輯 `backend/main.py` 的 `seed_default_questions()` 函式。

### 自訂 AI 教練
修改 `generate_ai_feedback()` 函式的 prompt。

### 樣式調整
編輯 `src/index.css` 或使用 Bootstrap 類別。

## 部署

### 建構前端
```bash
npm run build
```
靜態檔案將輸出到 `dist/` 目錄。

### 後端部署
使用 Uvicorn 或 Gunicorn 部署 FastAPI 應用程式。

### 遙測資料檢視
後端啟動後可執行：
```bash
python dynamic-quiz-engine/backend/view_data.py
```

## 授權

本專案僅供學習使用。

## 貢獻

歡迎提交 Issue 和 Pull Request！
