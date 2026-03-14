import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Telegram message limit is 4096 characters
MAX_MESSAGE_LENGTH = 4096
JOBS_PER_CHUNK = 10

def escape_html(text):
    """Escape HTML special characters."""
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def format_telegram_message(jobs, chunk_index=0, total_chunks=1):
    """Format a list of job dicts into an HTML message."""
    if not jobs:
        return ""
    
    header = f"🚀 <b>Found {len(jobs)} New Jobs!</b>"
    if total_chunks > 1:
        header += f" (Part {chunk_index + 1}/{total_chunks})"
    header += "\n\n"
    
    msg = header
    for idx, job in enumerate(jobs, 1):
        title = escape_html(job.get('title', 'Unknown Title'))
        company = escape_html(job.get('company', 'Unknown Company'))
        location = escape_html(job.get('location', 'Unknown Location'))
        url = escape_html(job.get('url', '#'))
        source = escape_html(job.get('source', 'Unknown Source'))
        
        msg += f"<b>{idx}. {title}</b>\n"
        msg += f"🏢 {company} | 📍 {location}\n"
        msg += f"🔗 <a href='{url}'>Apply here on {source}</a>\n\n"
        
    return msg

def chunk_jobs(jobs, chunk_size=JOBS_PER_CHUNK):
    """Split jobs list into smaller chunks to fit Telegram's message limit."""
    for i in range(0, len(jobs), chunk_size):
        yield jobs[i:i + chunk_size]

def send_telegram_message(text, bot_token=None, chat_id=None):
    """Send formatted text to Telegram. Handles single message."""
    token = bot_token or TELEGRAM_BOT_TOKEN
    cid = chat_id or TELEGRAM_CHAT_ID

    if not token or not cid:
        print("[Telegram] Skip delivery: Bot token or Chat ID not configured.")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": cid,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload)
        if not response.ok:
            print(f"Error sending to Telegram: {response.status_code} - {response.text}")
        response.raise_for_status()
        return True
    except Exception as e:
        # We already printed the error details above if it was a 4xx/5xx
        if not isinstance(e, requests.exceptions.HTTPError):
            print(f"Network error sending to Telegram: {e}")
        return False

def send_jobs_to_telegram(jobs, bot_token=None, chat_id=None):
    """Send all jobs to Telegram, automatically splitting into chunks if needed.
    Returns True if all messages were sent successfully."""
    if not jobs:
        return True
    
    chunks = list(chunk_jobs(jobs))
    total_chunks = len(chunks)
    all_sent = True
    
    for i, chunk in enumerate(chunks):
        message = format_telegram_message(chunk, chunk_index=i, total_chunks=total_chunks)
        
        if not send_telegram_message(message, bot_token=bot_token, chat_id=chat_id):
            all_sent = False
            print(f"[Telegram] Failed to send chunk {i + 1}/{total_chunks}")
    
    return all_sent
