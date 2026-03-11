# MemeStrategy Digital Asset Platform — MVP

## Tech Stack

- **Backend:** Python / Flask + SQLAlchemy (SQLite)
- **Frontend:** Vue.js 3 + Vue Router + Axios + Chart.js
- **API:** RESTful JSON API with session-based auth

## Features

### 1. User Authentication
- 註冊（email + username + password，含驗證）
- 登入 / 登出
- Session-based 認證 + route guard

### 2. Portfolio Dashboard
- 錢包總覽：BTC、ETH、SOL、MEMESTR、USD
- 即時模擬價格（含隨機波動）
- 資產總值計算
- Fund holdings 顯示

### 3. Trading (模擬交易)
- Buy / Sell 切換
- 4 種資產可交易
- 30 天模擬價格走勢圖 (Chart.js)
- 訂單執行 + 餘額即時更新
- 訂單歷史

### 4. Pokemon Card Tokenized Fund (寶可夢卡代幣化基金)
- 模擬 MemeStrategy 最新的 Van Gogh Pikachu 代幣化基金
- Fund info：NAV、卡片取得進度、代幣供應量
- Subscribe（認購）/ Redeem（贖回）
- 持倉管理 + P&L 計算

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py  # Runs on http://localhost:5001

# Frontend (另一個 terminal)
cd frontend
npm install
npm run dev  # Runs on http://localhost:5173
```

## API Endpoints

### Auth
- `POST /api/auth/register` — 註冊
- `POST /api/auth/login` — 登入
- `POST /api/auth/logout` — 登出
- `GET /api/auth/me` — 取得目前用戶

### Wallet
- `GET /api/wallet` — 取得錢包 + 資產組合

### Market
- `GET /api/market/prices` — 所有資產價格
- `GET /api/market/price/<symbol>` — 單一資產價格
- `GET /api/market/history/<symbol>` — 30 天價格歷史

### Trading
- `POST /api/trade` — 下單 (body: symbol, side, quantity)
- `GET /api/orders` — 訂單歷史

### Pokemon Fund
- `GET /api/fund/info` — 基金資訊
- `POST /api/fund/subscribe` — 認購 (body: tokens)
- `POST /api/fund/redeem` — 贖回 (body: tokens)
- `GET /api/fund/holdings` — 持倉

### Health
- `GET /api/health` — 健康檢查

## Project Structure

```
memestrategy-platform/
├── backend/
│   ├── app.py              # Flask app (models, routes, API)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api.js          # Axios instance
│   │   ├── router/index.js # Vue Router config
│   │   ├── App.vue         # Layout (sidebar + main)
│   │   ├── assets/main.css # Global styles
│   │   └── views/
│   │       ├── LoginView.vue
│   │       ├── RegisterView.vue
│   │       ├── DashboardView.vue
│   │       ├── TradeView.vue
│   │       ├── FundView.vue
│   │       └── OrdersView.vue
│   └── package.json
└── README.md
```
