from playwright.sync_api import sync_playwright

def dump(url, filename, selector=None):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        try:
            page.goto(url, timeout=30000)
            if selector:
                try:
                    page.wait_for_selector(selector, timeout=10000)
                except:
                    print(f"Selector {selector} not found for {url}")
            # wait a bit
            page.wait_for_timeout(3000)
            html = page.content()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Dumped {url} to {filename}")
        except Exception as e:
            print(f"Error accessing {url}: {e}")
        browser.close()

if __name__ == "__main__":
    dump("https://www.jobstreet.co.id/id/job-search/react-developer-jobs", "jobstreet_pw.html")
    dump("https://www.kalibrr.com/job-board/te/it-software/q/react-developer/1", "kalibrr_pw.html")
