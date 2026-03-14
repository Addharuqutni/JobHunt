# 🕵️ JobSentinel: Advanced Job Aggregator & Notifier

**JobSentinel** is a robust, production-ready job scraping and alerting ecosystem. It transforms the tedious task of job hunting into a fully automated, real-time experience. Built for scalability and speed, it monitors premium job portals, deduplicates listings, and streams notifications directly to your Telegram.

---

## ✨ Key Features

### 🚀 Scalability & Performance (Phase 4)
- **Hybrid Architecture**: Runs seamlessly on a single machine or scales into a distributed system using **Docker Compose**.
- **Background Workers**: Heavy scraping tasks are offloaded to **Celery** workers, ensuring the API remains lightning-fast.
- **Message Broker**: Powered by **Redis** for task queuing and distributed locking.
- **Real-Time Progress**: Watch the scraper work in real-time via integrated **FastAPI WebSockets**.

### 🔍 intelligent Scraping
- **Multi-Source Support**: Deep integration with Jobstreet (Seek Asia), Kalibrr, Glints, and **Dealls**.
- **SHA-256 Deduplication**: Smart hashing prevents duplicate notifications for the same job across different runs.
- **Dynamic Depth**: Configure exactly how many pages to scrape per source directly from the UI.

### 🔔 Smart Notifications
- **Telegram Integration**: Beautifully formatted HTML messages sent directly to your phone.
- **Auto-Chunking**: Automatically splits large result sets into multiple messages to respect Telegram's character limits.

### 🛡️ Enterprise-Grade Security
- **Strict Authentication**: Global `X-API-Key` protection for all endpoints and WebSocket connections.
- **Robustness**: Local-first fallback mode ensures the app runs even without Redis/Celery.
- **Clean Architecture**: Refactored for clean code, reusable services, and modular routing.

---

## 🏗️ Architecture Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 18, Vite, TypeScript, Lucide, Custom Vanilla CSS |
| **Backend** | Python 3.13, FastAPI (Asynchronous API) |
| **Broker** | Redis (Task Queue & Pub/Sub) |
| **Worker** | Celery (Background Processing) |
| **Database** | PostgreSQL (Production) / SQLite (Local Dev) |
| **Scraper** | Playwright (Headless Chromium), BeautifulSoup4 |

---

## 🚀 Installation & Setup

### Option A: Standard Local Setup (Fastest for Dev)
Use this if you don't want to use Docker. The app will automatically fall back to **Local Threading** and **SQLite**.

**1. Backend:**
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
playwright install chromium
python api.py
```

**2. Frontend:**
```bash
# From project root
npm install
npm run dev
```

---

### Option B: Production Setup (Docker Compose)
The full power of JobSentinel with Redis, Celery, and PostgreSQL.

```bash
docker-compose up --build -d
```
*Access the Dashboard at `http://localhost`, and the API at `http://localhost:8000/docs`.*

---

## ⚙️ Configuration & Settings

Manage these directly from the **Dashboard > Settings** page:

| Setting | Description |
| :--- | :--- |
| **Keywords** | Comma-separated list of roles (e.g., `React Developer, Python`). |
| **Telegram Bot Token** | Obtain this from @BotFather on Telegram. |
| **Telegram Chat ID** | Your internal ID (Get it from @userinfobot). |
| **Scraper Toggles** | Enable/Disable specific sources and set Page Depth. |
| **Schedule Interval** | How often the background worker should fire (Hours). |

---

## 🛡️ Security & Environment

Create a `.env` in the root (for Docker) or set these in your OS:

- `API_KEY`: Secret string for API authentication.
- `USE_REDIS`: Set to `true` to enable Celery/WebSocket (Default: `false`).
- `DB_URL`: Database connection string (e.g., `postgresql://user:pass@db:5432/jobs`).
- `VITE_API_KEY`: Must match the backend `API_KEY`.

---

## 🛠️ Troubleshooting

- **Telegram "Chat Not Found"**: You MUST send `/start` to your bot first before it can message you.
- **Connection Gagal**: Ensure `port 8000` is not being used by another application.
- **Playwright Errors**: Run `playwright install` to ensure browser binaries are present.

---
*Built for hackers, developers, and proactive job seekers.*

