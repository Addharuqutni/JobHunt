# 🕵️ JobSentinel

JobSentinel is a powerful, automated job scraping and aggregation platform. It continuously monitors multiple job portals for specific keywords, stores the results, and sends real-time notifications via Telegram. It features a modern React dashboard for managing configurations and viewing scraped data, powered by a robust Python FastAPI backend and Playwright-based scraper engine.

## ✨ Features

- **Multi-Source Scraping**: Scrapes job listings from Jobstreet, Kalibrr, and Glints (with more easily addable).
- **Automated Pipeline**: Headless browsers (Playwright) navigate and extract job data.
- **Deduplication**: Uses SHA-256 hashing to ensure the same job isn't processed twice.
- **Telegram Integration**: Automatically chunks and sends newly found jobs directly to a configured Telegram chat.
- **Centralized Dashboard**: A beautiful, modern React application (Vite + TypeScript) to view stats, filter all jobs, and manage settings.
- **Dynamic Configuration**: Adjust keywords, scraper toggles, and Telegram settings directly from the UI, persisting instantly to the backend.
- **Security First**: 
  - Parameterized SQLite queries to prevent SQL Injection.
  - Strict CORS policy to prevent CSRF attacks.
  - Global API Key authentication (`X-API-Key`) for all endpoints.
  - Thread-locking mechanism to prevent DoS attacks on the scraper trigger.

## 🏗️ Architecture

- **Frontend**: React 18, Vite, TypeScript, Lucide React (Icons), Vanilla CSS (Custom modern design system).
- **Backend & API**: Python 3.13, FastAPI, Uvicorn (ASGI server).
- **Database**: SQLite3 (`jobs.db` with `jobs` and `settings` tables).
- **Scraper Engine**: Playwright (Headless Chromium), BeautifulSoup4 for parsing.

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)

### 1. Backend Setup

Navigate to the `backend` directory:
```bash
cd backend
```

Create a virtual environment (optional but recommended):
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

Start the FastAPI server:
```bash
python api.py
```
*The API will run on `http://localhost:8000`.*

### 2. Frontend Setup

Navigate to the root directory (or open a new terminal):
```bash
# From the project root
npm install
```

Start the Vite development server:
```bash
npm run dev
```
*The dashboard will be available at `http://localhost:5173`.*

## 🔒 Security Configuration

The backend is secured with an API key. By default, development uses `dev-secret-key-123`.

To change this in production:
1. Set the `API_KEY` environment variable before running `api.py`.
2. Create a `.env` file in the project root for the frontend and set:
   ```env
   VITE_API_KEY=your-production-secret-key
   VITE_API_URL=https://your-production-api-url.com
   ```

## ⚙️ Usage

1. Open the **Settings** page in the dashboard.
2. Enter your **Telegram Bot Token** and **Chat ID**.
3. Configure your search keywords (comma-separated, e.g., `react developer, frontend, python`).
4. Enable the scrapers you want to use and set the maximum depth (Pages).
5. Click **Save Settings**.
6. Click **Run Scraper Now** to trigger an immediate scrape, or let the scheduled pipeline run automatically.
7. View new jobs in your Telegram app and on the **All Jobs** page!

---
*Built as a strategic tool for proactive job hunting.*
