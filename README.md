# 輿情分析助手 (Social Sentiment Agent)

AI 輿情分析對話助手，整合 QSearch API 搜尋社群媒體聲量、分析趨勢、查看熱門貼文。

## 啟動方式

```bash
# 1. 進入專案目錄
cd /Users/changjiaming/Desktop/social_agent

# 2. 啟動 conda 環境
conda activate agent

# 3. 設定環境變數
export OPENAI_API_KEY="sk-your-key"
export QSEARCH_API_KEY="your-key"

# 4. 啟動伺服器
uvicorn app.main:app --port 8000 --reload
```

開啟瀏覽器前往 `http://localhost:8000`

> ⚠️ 必須在專案根目錄執行 `uvicorn`，不能用 `python app/main.py`。

## 資料夾結構

```
social_agent/
├── README.md
├── requirements.txt          # Python 套件依賴
├── .env.example              # 環境變數範本
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI 應用程式（API + 前端服務）
│   ├── schemas.py            # Pydantic 請求/回應模型
│   ├── static/
│   │   └── index.html        # 對話介面（深色玻璃擬態風格）
│   └── agent/
│       ├── __init__.py
│       ├── agent.py           # LangChain Agent（create_agent + 系統提示）
│       ├── tools.py           # 6 個 QSearch 工具（@tool）
│       └── memory.py          # 對話記憶（MemorySaver，按 session 隔離）
└── .claude/
    └── skills/
        └── qsearch-sentiment/ # QSearch API 技能
            ├── SKILL.md
            ├── scripts/
            │   └── qsearch_client.py
            └── references/
                └── qsearch_api.md
```

## API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/` | 對話介面 |
| POST | `/api/chat` | 傳送訊息（`{message, session_id}`） |
| POST | `/api/reset` | 清除對話記錄（`{session_id}`） |
| GET | `/api/health` | 健康檢查 |
