import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Telegram message limit is 4096 characters
MAX_MESSAGE_LENGTH = 4096
JOBS_PER_CHUNK = 10

def format_telegram_message(jobs, chunk_index=0, total_chunks=1):
    """Format a list of job dicts into a markdown message."""
    if not jobs:
        return ""
    
    header = f"🚀 **Found {len(jobs)} New Jobs!**"
    if total_chunks > 1:
        header += f" (Part {chunk_index + 1}/{total_chunks})"
    header += "\n\n"
    
    msg = header
    for idx, job in enumerate(jobs, 1):
        title = job.get('title', 'Unknown Title')
        company = job.get('company', 'Unknown Company')
        location = job.get('location', 'Unknown Location')
        url = job.get('url', '#')
        source = job.get('source', 'Unknown Source')
        
        msg += f"**{idx}. {title}**\n"
        msg += f"🏢 {company} | 📍 {location}\n"
        msg += f"🔗 [Apply here on {source}]({url})\n\n"
        
    return msg

def chunk_jobs(jobs, chunk_size=JOBS_PER_CHUNK):
    """Split jobs list into smaller chunks to fit Telegram's message limit."""
    for i in range(0, len(jobs), chunk_size):
        yield jobs[i:i + chunk_size]

def send_telegram_message(text):
    """Send formatted text to Telegram. Handles single message."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Telegram Demo] No token/chat_id set. Would send:\n")
        print(text)
        return True
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return False

def send_jobs_to_telegram(jobs):
    """Send all jobs to Telegram, automatically splitting into chunks if needed.
    Returns True if all messages were sent successfully."""
    if not jobs:
        return True
    
    chunks = list(chunk_jobs(jobs))
    total_chunks = len(chunks)
    all_sent = True
    
    for i, chunk in enumerate(chunks):
        message = format_telegram_message(chunk, chunk_index=i, total_chunks=total_chunks)
        
        if not send_telegram_message(message):
            all_sent = False
            print(f"[Telegram] Failed to send chunk {i + 1}/{total_chunks}")
    
    return all_sent
